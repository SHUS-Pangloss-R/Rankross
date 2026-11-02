
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    sys.exit(
        "cv2 not found in this interpreter.\n"
        f"  interpreter: {sys.executable}\n"
        f"  fix: {sys.executable} -m pip install opencv-python"
    )

def imread_u(path: str | Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"cannot read image: {path}")
    return img

def imwrite_u(path: str | Path, img: np.ndarray) -> None:
    ext = "." + str(path).rsplit(".", 1)[-1]
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        raise SystemExit(f"cannot encode image: {path}")
    buf.tofile(str(path))

def _largest_valid_component(mask: np.ndarray) -> np.ndarray:
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n <= 1:
        return np.zeros_like(mask)

    H, W = mask.shape
    best, best_score = None, -1.0
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < 0.001 * H * W:
            continue
        touches = (x <= 1) or (y <= 1) or (x + w >= W - 1) or (y + h >= H - 1)
        fills_width = w > 0.95 * W
        score = float(area)
        if touches:
            score *= 0.1
        if fills_width:
            score *= 0.1
        if score > best_score:
            best, best_score = i, score
    if best is None:
        return np.zeros_like(mask)
    return np.where(labels == best, 255, 0).astype(np.uint8)

def build_mask(img: np.ndarray, background: np.ndarray | None) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 0)

    if background is not None:
        b = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        b = cv2.GaussianBlur(b, (5, 5), 0)
        if b.shape != g.shape:
            b = cv2.resize(b, (g.shape[1], g.shape[0]))
        diff = cv2.absdiff(g, b)
        _, m = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        return _largest_valid_component(m)

    _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    candidates = [m, cv2.bitwise_not(m)]
    best, best_score = None, -1.0
    for c in candidates:
        c = cv2.morphologyEx(c, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        c = cv2.morphologyEx(c, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        c = _largest_valid_component(c)
        ys, xs = np.nonzero(c)
        if len(ys) == 0:
            continue
        h = ys.max() - ys.min() + 1
        w = xs.max() - xs.min() + 1

        score = float(len(ys)) * (1.0 + 0.5 * min(h / max(w, 1), 2.0))
        if score > best_score:
            best, best_score = c, score
    return best if best is not None else np.zeros_like(g)

def profile_from_mask(mask: np.ndarray):
    rows, left, right = [], [], []
    H, W = mask.shape
    for y in range(H):
        xs = np.nonzero(mask[y])[0]
        if xs.size == 0:
            continue
        rows.append(y)
        left.append(int(xs.min()))
        right.append(int(xs.max()))
    if not rows:
        raise SystemExit("empty mask: nothing detected. Check background contrast.")
    return np.array(rows), np.array(left), np.array(right)

def mask_to_profile_mm(rows, left, right, mm_per_px: float, median_w: int = 5):
    z = (rows.max() - rows).astype(np.float64) * mm_per_px
    r = (right - left).astype(np.float64) * 0.5 * mm_per_px

    if median_w and median_w > 1 and r.size >= median_w:
        r_s = cv2.medianBlur(r.astype(np.float32).reshape(-1, 1), median_w).ravel()
        r = r_s.astype(np.float64)

    order = np.argsort(z)
    return z[order], r[order]

def fit_frustum(z, r):
    A = np.vstack([z, np.ones_like(z)]).T
    coef, *_ = np.linalg.lstsq(A, r, rcond=None)
    pred = A @ coef
    return float(coef[0]), float(coef[1]), float(np.sqrt(np.mean((pred - r) ** 2)))

def fit_spline(z, r, smoothing: float | None = None):
    from scipy.interpolate import UnivariateSpline

    if smoothing is None:
        smoothing = float(len(z)) * (0.15 ** 2)
    spl = UnivariateSpline(z, r, k=3, s=smoothing)
    return spl, float(np.sqrt(np.mean((spl(z) - r) ** 2)))

def volume_of_revolution(z, r) -> float:
    z = np.asarray(z, dtype=np.float64)
    r = np.asarray(r, dtype=np.float64)
    if z.shape != r.shape:
        raise ValueError(f"z and r length mismatch: {z.shape} vs {r.shape}")
    order = np.argsort(z)
    z, r = z[order], r[order]
    return float(np.pi * np.trapezoid(r ** 2, z) / 1000.0)

CARD_ASPECT = 85.6 / 53.98

def detect_card(img: np.ndarray, aspect: float = CARD_ASPECT,
                tol: float = 0.22) -> tuple[float, float, np.ndarray] | None:
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 0)

    best = None
    best_score = 0.0
    for mask in _edge_masks(g):
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if area < 0.0005 * g.size:
                continue
            (cx, cy), (w, h), ang = cv2.minAreaRect(c)
            if w <= 1 or h <= 1:
                continue
            long_side, short_side = max(w, h), min(w, h)
            ar = long_side / short_side
            if abs(ar - aspect) > tol:
                continue

            fill = area / (w * h + 1e-6)
            if fill < 0.72:
                continue
            score = area * fill
            if score > best_score:
                box = cv2.boxPoints(((cx, cy), (w, h), ang))
                best = (float(long_side), float(short_side),
                        np.int32(box))
                best_score = score
    return best

def _edge_masks(gray: np.ndarray):
    edges = cv2.Canny(gray, 40, 120)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    yield edges
    yield otsu
    yield cv2.bitwise_not(otsu)

def mm_per_px_from_reference(ref_path: str | Path, ref_mm: float,
                             background: str | Path | None = None,
                             axis: str = "long",
                             roi: tuple[int, int, int, int] | None = None,
                             mode: str = "auto") -> tuple[float, dict]:
    if mode == "auto":
        mode = "card" if 80.0 <= ref_mm <= 92.0 else "bbox"

    ref = imread_u(ref_path)
    if roi is not None:
        x, y, w, h = roi
        ref = ref[y:y + h, x:x + w]

    H, W = ref.shape[:2]
    diag: dict = {"mode": mode, "axis": axis, "ref_mm": ref_mm}

    if mode == "card":
        found = detect_card(ref)
        if found is None:
            raise SystemExit(
                "reference image: no card found by aspect ratio.\n"
                "  - put the card on a plain area, fully inside the frame, and\n"
                "  - avoid other 1.586 rectangles, or pass --ref-mode bbox.\n"
                "  - or pass --ref-roi x,y,w,h to search only around the card."
            )
        long_px, short_px, quad = found
        diag.update({"card_long_px": round(long_px, 2),
                     "card_short_px": round(short_px, 2),
                     "ratio": round(long_px / max(short_px, 1e-9), 4)})
        long_mm, short_mm = (ref_mm, ref_mm * 53.98 / 85.6)\
            if axis == "long" else (ref_mm * 85.6 / 53.98, ref_mm)
        diag["long_mm"] = round(long_mm, 2)
        diag["short_mm"] = round(short_mm, 2)

        s_long = long_mm / long_px
        s_short = short_mm / short_px
        diag["mm_per_px_from_long"] = round(s_long, 6)
        diag["mm_per_px_from_short"] = round(s_short, 6)
        diag["self_check_pct"] = round(100 * abs(s_long - s_short) / s_long, 2)
        return float(np.mean([s_long, s_short])), diag

    bg = imread_u(background) if background else None
    m = build_mask(ref, bg)
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        raise SystemExit("reference image: nothing detected.")
    h = float(ys.max() - ys.min() + 1)
    w = float(xs.max() - xs.min() + 1)

    if h >= 0.98 * H or w >= 0.98 * W:
        print(
            "[warn] reference mask spans (almost) the whole frame. The object "
            "probably touches the border, so the size is wrong.\n"
            "       Re-shoot with margin around the sheet, or pass "
            "--ref-background if you have a matching empty frame."
        )

    extent = h if axis == "long" else w
    diag = {"ref_px_height": h, "ref_px_width": w, "axis": axis, "ref_mm": ref_mm}
    return ref_mm / extent, diag

def cut_base_contact(rows, left, right, min_jump: float = 5.0,
                     search: float = 0.12):
    w = (right - left + 1).astype(np.float64)
    n = len(w)
    if n < 12:
        return rows, left, right
    start = max(1, int(n * (1.0 - search)))
    jumps = np.diff(w)
    idx = np.arange(start, n - 1)
    if idx.size == 0:
        return rows, left, right
    strong = idx[jumps[idx] > min_jump]
    if strong.size == 0:
        return rows, left, right
    base = int(strong.max()) + 1
    if base >= n - 1:
        return rows, left, right
    return rows[:base + 1], left[:base + 1], right[:base + 1]

def fix_bad_rows(r, rel: float = 0.6):
    r = np.asarray(r, dtype=np.float64).copy()
    if r.size == 0:
        return r
    med = float(np.median(r))
    if med <= 0:
        return r
    bad = r < rel * med
    if not bad.any() or bad.all():
        return r
    good_idx = np.where(~bad)[0]
    r[bad] = np.interp(np.where(bad)[0], good_idx, r[good_idx])
    return r

def band_diameter(z, r, band: float = 0.05, where: str = "top") -> float:
    n = len(z)
    k = max(1, int(n * band))
    seg = r[n - k:] if where == "top" else r[:k]
    return float(2.0 * np.median(seg))

def pct_err(val, ref):
    if ref is None or val is None or ref == 0:
        return None
    return 100.0 * (val - ref) / ref

def main() -> int:
    ap = argparse.ArgumentParser(description="Cup_Practice Day 1: photo -> volume -> density")
    ap.add_argument("--img", required=True, help="side-on photo of the cup")
    ap.add_argument("--background", default=None, help="photo of the empty background")
    ap.add_argument("--ref-img", default=None, help="photo of the A4 sheet, alone")
    ap.add_argument("--ref-mm", type=float, default=297.0, help="known size of ref long edge (mm)")
    ap.add_argument("--ref-axis", choices=["long", "short"], default="long")
    ap.add_argument("--ref-background", default=None,
                    help="empty-background frame matching --ref-img (optional)")
    ap.add_argument("--mm-per-px", type=float, default=None, help="override the reference")
    ap.add_argument("--anchor", choices=["ref", "height"], default="ref",
                    help="'ref' = absolute scale from a reference object; "
                         "'height' = anchor the scale on the ruler-measured height "
                         "(no reference object needed; rim/base become the check)")
    ap.add_argument("--roi", default=None, metavar="x,y,w,h",
                    help="crop the cup photo before segmentation (kills background leaks)")
    ap.add_argument("--ref-roi", default=None, metavar="x,y,w,h",
                    help="crop the reference photo before detection")
    ap.add_argument("--height", type=float, default=None, help="ruler: total height (mm)")
    ap.add_argument("--rim", type=float, default=None, help="ruler: rim OUTER diameter (mm)")
    ap.add_argument("--base", type=float, default=None, help="ruler: base OUTER diameter (mm)")
    ap.add_argument("--capacity", type=float, default=None, help="jug: capacity (ml)")
    ap.add_argument("--mass", type=float, default=None, help="scale: empty cup mass (g)")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--tag", default="day1")
    args = ap.parse_args()

    img_path = Path(args.img)
    out_dir = Path(args.out_dir) if args.out_dir else img_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    def parse_roi(s):
        if s is None:
            return None
        try:
            return tuple(int(v) for v in s.split(","))
        except Exception:
            raise SystemExit(f"--roi must look like x,y,w,h (got {s!r})")

    roi = parse_roi(args.roi)
    ref_roi = parse_roi(args.ref_roi)

    img = imread_u(img_path)
    bg = imread_u(args.background) if args.background else None
    if bg is not None and bg.shape != img.shape:
        bg = cv2.resize(bg, (img.shape[1], img.shape[0]))
    if roi is not None:
        x, y, w, h = roi
        img = img[y:y + h, x:x + w]
        if bg is not None:
            bg = bg[y:y + h, x:x + w]

    mask = build_mask(img, bg)
    rows, left, right = profile_from_mask(mask)
    rows, left, right = cut_base_contact(rows, left, right)
    height_px = float(rows.max() - rows.min() + 1)

    scale_diag = {}
    if args.anchor == "height":
        if args.height is None:
            raise SystemExit("--anchor height needs --height (the ruler measurement).")
        mm_per_px = float(args.height) / height_px
        scale_src = f"anchored on ruler height ({args.height} mm / {height_px:.0f} px)"
        scale_diag = {"anchor": "height", "height_px": height_px,
                      "height_mm": args.height}
    elif args.mm_per_px is not None:
        mm_per_px = float(args.mm_per_px)
        scale_src = "manual --mm-per-px"
    elif args.ref_img:
        mm_per_px, scale_diag = mm_per_px_from_reference(
            args.ref_img, args.ref_mm,
            background=args.ref_background, axis=args.ref_axis, roi=ref_roi)
        scale_src = f"reference image ({args.ref_img})"
    else:
        raise SystemExit(
            "need one of: --anchor height --height X | --ref-img | --mm-per-px.\n"
            "Monocular photos carry no absolute scale."
        )

    z, r = mask_to_profile_mm(rows, left, right, mm_per_px)
    r = fix_bad_rows(r, rel=0.6)

    a, b, rms_fr = fit_frustum(z, r)
    spl, rms_sp = fit_spline(z, r)

    zz = np.linspace(z.min(), z.max(), 2000)
    rr_spl = spl(zz)
    rr_fr = a * zz + b

    H_meas = float(z.max() - z.min())

    max_meas = 2.0 * float(np.percentile(r, 95))
    rim_meas = band_diameter(z, r, band=0.05, where="top")
    base_meas = band_diameter(z, r, band=0.05, where="bottom")

    V_spl = volume_of_revolution(zz, rr_spl)
    V_fr = volume_of_revolution(zz, rr_fr)

    density = None
    if args.capacity is not None and args.mass is not None:
        material_ml = V_spl - args.capacity
        if material_ml > 0:
            density = float(args.mass / material_ml)

    checks = []

    def add(name, value, ref, tol_pct, unit, higher_is_worse=True):
        if ref is None or value is None:
            checks.append({"name": name, "value": value, "ref": ref,
                           "err_pct": None, "tol_pct": tol_pct, "unit": unit,
                           "status": "not checked"})
            return
        e = pct_err(value, ref)
        ok = abs(e) <= tol_pct
        checks.append({"name": name, "value": round(value, 2), "ref": ref,
                       "err_pct": round(e, 2), "tol_pct": tol_pct, "unit": unit,
                       "status": "PASS" if ok else "FAIL"})

    add("height", H_meas, args.height, 3.0, "mm")
    add("max_diameter", max_meas, args.rim, 4.0, "mm")
    add("base_diameter", base_meas, args.base, 6.0, "mm")

    if args.capacity is not None:
        material_ml = V_spl - args.capacity
        checks.append({
            "name": "envelope_gt_capacity",
            "value": round(material_ml, 2),
            "ref": None, "err_pct": None, "tol_pct": None, "unit": "ml",
            "status": "PASS" if material_ml > 0 else
                      "FAIL: exterior volume < capacity, scale is wrong",
        })

    if density is not None:
        ok = 2.0 <= density <= 2.7
        status = "PASS" if ok else ("FAIL" if density < 0.5 or density > 4.0 else "SUSPECT")
        checks.append({"name": "density", "value": round(density, 3), "ref": None,
                       "err_pct": None, "tol_pct": None, "unit": "g/cm3",
                       "status": status,
                       "note": "ceramic/glass ~2.4-2.6, plastic ~0.9-1.2"})
    else:
        if args.capacity is not None and args.mass is not None and (V_spl - args.capacity) <= 0:
            note = ("material volume <= 0: the exterior volume came out smaller "
                    "than the capacity. Almost always a wrong absolute scale, "
                    "not a wrong fit.")
        else:
            note = "need --capacity and --mass"
        checks.append({"name": "density", "value": None, "ref": None,
                       "err_pct": None, "tol_pct": None, "unit": "g/cm3",
                       "status": note})

    imwrite_u(out_dir / f"{args.tag}_mask.png", mask)

    overlay = img.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
    cv2.drawMarker(overlay, (int(left.mean()), int((rows.min() + rows.max()) / 2)),
                   (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
    imwrite_u(out_dir / f"{args.tag}_overlay.png", overlay)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(5, 7))
        ax.plot(r, z, ".", ms=2, color="#888", label="silhouette")
        ax.plot(rr_spl, zz, "-", lw=2, color="#1f77b4", label="spline fit")
        ax.plot(rr_fr, zz, "--", lw=1.5, color="#ff7f0e", label="frustum fit")
        ax.set_xlabel("radius r (mm)")
        ax.set_ylabel("height z (mm)")
        ax.set_title(f"V_spline={V_spl:.1f} ml   V_frustum={V_fr:.1f} ml")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.set_aspect("equal")
        fig.tight_layout()
        fig.savefig(out_dir / f"{args.tag}_profile.png", dpi=140)
        plt.close(fig)
    except Exception as exc:
        print(f"[warn] profile plot skipped: {exc}")

    report = {
        "image": str(img_path),
        "scale": {"mm_per_px": mm_per_px, "source": scale_src, **scale_diag},
        "geometry": {
            "height_mm": round(H_meas, 2),
            "max_diameter_mm": round(max_meas, 2),
            "lid_diameter_mm": round(rim_meas, 2),
            "base_diameter_mm": round(base_meas, 2),
            "frustum_slope": round(a, 5),
            "frustum_rms_mm": round(rms_fr, 3),
            "spline_rms_mm": round(rms_sp, 3),
        },
        "volume": {
            "exterior_spline_ml": round(V_spl, 2),
            "exterior_frustum_ml": round(V_fr, 2),
            "capacity_ml": args.capacity,
            "material_ml": None if args.capacity is None else round(V_spl - args.capacity, 2),
            "mass_g": args.mass,
            "density_g_cm3": None if density is None else round(density, 3),
        },
        "checks": checks,
        "verdict": "PASS" if any(c["status"] == "PASS" for c in checks) and
                             not any(c["status"] == "FAIL" for c in checks) else
                   ("FAIL" if any(c["status"] == "FAIL" for c in checks) else "INCOMPLETE"),
    }
    (out_dir / f"{args.tag}_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\ninterpreter : {sys.executable}")
    print(f"image       : {img_path}")
    print(f"scale       : {mm_per_px:.5f} mm/px  ({scale_src})")
    print(f"height      : {H_meas:8.2f} mm")
    print(f"rim dia     : {rim_meas:8.2f} mm")
    print(f"base dia    : {base_meas:8.2f} mm")
    print(f"lid dia     : {rim_meas:8.2f} mm   (top band, NOT the body)")
    print(f"V spline    : {V_spl:8.2f} ml")
    print(f"V frustum   : {V_fr:8.2f} ml")
    if args.capacity is not None:
        print(f"material    : {V_spl - args.capacity:8.2f} ml")
    if density is not None:
        print(f"density     : {density:8.3f} g/cm3   <- THE number")
    print()
    print(f"{'check':22s} {'value':>10s} {'ref':>10s} {'err%':>8s}  status")
    print("-" * 66)
    for c in checks:
        v = "-" if c["value"] is None else f"{c['value']:.2f}"
        rf = "-" if c["ref"] is None else f"{c['ref']:.2f}"
        ep = "-" if c["err_pct"] is None else f"{c['err_pct']:+.2f}"
        print(f"{c['name']:22s} {v:>10s} {rf:>10s} {ep:>8s}  {c['status']}")
    print("-" * 66)
    print(f"VERDICT: {report['verdict']}")
    print(f"artifacts: {out_dir}/{args.tag}_{{report.json,mask.png,overlay.png,profile.png}}")
    return 0 if report["verdict"] != "FAIL" else 1

if __name__ == "__main__":
    raise SystemExit(main())
