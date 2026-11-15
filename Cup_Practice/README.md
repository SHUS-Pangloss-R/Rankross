# Cup_Practice: From Photos to a Point Cloud

##  Why this project exists

Every previous project used a dataset someone else built: Kaggle's Titanic CSV, Open3D's built-in Bunny, ModelNet10's 4000 CAD models. Cup_Practice is different: the object is **my own cup**, and I measure it with a ruler before any code runs. That gives me something the earlier projects never had, a **ground truth**.

With a ground truth I can finally answer the question my overfitting analysis could only pose: does my pipeline reproduce reality, or does it just look convincing?

##  Constraint: photos only

No CAD file, no LiDAR. This is **Case D** in the triage table and it changes the approach fundamentally. Three consequences:

1. **Monocular photos carry no absolute scale.** A reconstruction from photos alone is correct up to a single unknown factor. Without a metric reference in the frame, "the cup is 8 units tall" is meaningless. Fixing this is Step 4, not an afterthought.
2. **Photogrammetry (COLMAP/MVS) is the wrong primary tool for a glazed cup.** Dense MVS needs texture to match. A white ceramic or transparent glass cup has almost none, and its specular highlights are *moving* features that actively corrupt matching. It will produce a sparse, noisy cloud with a hole where the highlight is.
3. **Silhouettes do not need texture at all.** This is the pivot: for a body of revolution, the silhouette under a view perpendicular to the axis *is* the profile curve, exactly. One calibrated photo plus a scale reference determines the shape up to the orthographic assumption.

##  The key idea: silhouette + revolution prior

For a surface of revolution $r(z)$ about the $z$ axis, project onto the $xz$ plane along $y$:

$$(r(z)\cos\theta,\ r(z)\sin\theta,\ z) \longmapsto (r(z)\cos\theta,\ z)$$

As $\theta$ sweeps $[0, 2\pi)$ for fixed $z$, the image coordinate spans exactly $[-r(z), r(z)]$. So the projected **region** is $\{(x,z): |x| \le r(z)\}$, and the **silhouette boundary is the profile curve itself**.

That is an exact result under orthographic projection. A phone at $\approx 1$ m from a $\approx 10$ cm cup is close enough to orthographic that the residual is small and *measurable* (see the perspective check in STEPS.md).

Consequence: **one good silhouette determines a symmetric cup's shape.** Rotation about the axis does not change the silhouette at all, so a turntable adds nothing for a pure revolution. Its real jobs are (a) detecting that the cup is *not* a pure revolution (a handle), and (b) covering the non-symmetric part. This inverts the usual advice: shoot many angles to *test* symmetry, not to *build* shape.

##  Volume from the profile, and why that is the best validation

If $r(z)$ is known, the exterior volume is exactly

$$V = \pi \int_0^H r(z)^2 \, dz$$

and the **capacity** (interior) volume is measured by filling the cup with water and pouring it into a measuring jug. Then:

- $V_{ext} - V_{int}$ = material volume
- mass / material volume = **density**

If the derived density lands near 2.4-2.6 g/cm3 the cup is ceramic/glass; near 0.9-1.2 it is plastic. **A physically plausible density means the profile, the scale, and the water measurement are all simultaneously correct.** That is a far stronger check than "the picture looks right", and it is the one number that catches a unit or scale error.

##  Key Concepts Covered

- **Absolute scale from a metric reference**: A4 paper (210 x 297 mm, exact), a coin, or a printed checkerboard. Monocular scale is unobservable otherwise.
- **Camera intrinsics and distortion**: OpenCV checkerboard calibration, focus and exposure locked, no digital zoom.
- **Silhouette segmentation**: matte background, diffuse light, shadow suppression, background subtraction.
- **Surface-of-revolution fitting**: parameterise $r(z)$ (spline or frustum), fit to silhouette width per scanline, integrate for volume.
- **Symmetry test as a decision gate**: identical silhouettes across yaw means pure revolution; differences localise the handle.
- **Perspective vs orthographic**: quantify the residual rather than assume it away.
- **Learned vs structural invariance**: the same distinction from the PointNet notes, now with a real object.

##  Results

Day 1 closed the loop on a straight-walled thermos. Scale is anchored on the
ruler height, and the two diameters are the independent check.

| Check | Ground truth (ruler) | Photo-derived | Error |
| :--- | ---: | ---: | ---: |
| Height | 213 mm | 212.59 mm | -0.19% |
| Max body diameter | 65 mm | 65.16 mm | +0.25% |
| Base diameter | 62 mm | 61.29 mm | -1.14% |
| Exterior volume (spline) | 626.54 ml | 626.54 ml | - |
| Exterior volume (frustum) | - | 624.52 ml | -0.32% vs spline |
| Capacity | not measured (no jug) | - | - |
| Material density | cannot be derived without capacity | - | - |

**Verdict: PASS, with a correction.** Three readings agreed within 1.2% and the
spline and frustum volumes within 0.3%. See [DAY1_LOG.md](DAY1_LOG.md).

**Correction from Day 2.** Those numbers came from a pipeline in which the base
cut was tuned until the diameter matched the ruler, which makes the check
circular. Measured without that tuning, the diameter is **59.06 mm, 9% short**,
and a single hand-held photo cannot separate "scale is wrong" from "base position
is wrong". The honest statement is a bound, not a number. See
[DAY2_LOG.md](DAY2_LOG.md).

##  Four bugs that did not crash

> The complete chronological list is in **[../MISTAKES.md](../MISTAKES.md)**. The four below are the ones that happened inside this project.

Every serious bug in this project produced a **wrong number instead of an error**.

| Bug | What it looked like | How it was caught |
| :--- | :--- | :--- |
| Opening the mask with a 9x9 kernel | body width 163 -> 153 px | diameter 4.4% short against the ruler |
| A4 sheet matched as a campus card | every length 10% short | two independent scale estimates disagreed |
| `width = [r-1+1 ...]` instead of `r-l+1` | "width" was actually the right edge coordinate | the number stopped being a width |
| `pcd2.points` never assigned the transformed array | registration error 61.7 deg on a cloud that had never moved | the two clouds' centroids should have differed by `t_gt` and did not |

The last one is why T8 had to be rebuilt. `P2` held the transformed points, `pcd2`
still held the original, and every downstream number was computed against a target
that had never moved. **Nothing raised an exception.**

What the four have in common: none fails loudly, and each was found by comparing
two numbers that should have agreed -- never by looking at a picture.

After the fix the registration numbers changed completely: coarse registration
gave 23.07 deg against the ground truth with a 1.39 mm translation error, and ICP
brought the translation to 0.028 mm while the rotation stayed near 23 deg. That
remaining angle is not an error -- see below.

##  What the registration actually shows

The object is a surface of revolution, so rotation about its own axis is not
observable. A 23 deg discrepancy with a 0.03 mm translation error is the signature
of that, not of a failed algorithm.

| Quantity | Value | Identifiable? |
| :--- | ---: | :--- |
| Translation error after ICP | 0.028 mm | yes |
| Inlier ratio | 99.59% | yes |
| RMSE | 0.91 mm | yes |
| Rotation about the cup's own axis | ~23 deg | **no** |

ICP convergence, from an initial error of delta about the horizontal axis:

| delta | final rotation error | inlier ratio | verdict |
| ---: | ---: | ---: | :--- |
| 0 deg | 0.57 deg | 100.00% | converged |
| 10 deg | 8.39 deg | 100.00% | converged |
| 30 deg | 41.72 deg | 30.19% | failed |
| 90 deg | 153.97 deg | 8.40% | failed |
| 180 deg | 180.00 deg | 0.00% | failed |

**The basin of convergence is somewhere between 10 and 30 degrees.**

##  Environment & Dependencies

- Python 3.11
- OpenCV (calibration, thresholding, contours)
- NumPy, SciPy (profile fit, integration)
- matplotlib (silhouette and profile plots)
- Open3D (only to turn the fitted profile into a point cloud / mesh for the PointNet track)

##  File Descriptions

- `cup_day1.py`: the Day-1 pipeline. Mask from background difference, per-row
  edges, contact-shadow cut, spline fit, volume, and the pass/fail report.
- `Day2_revolve.ipynb`: profile -> watertight mesh -> labelled point cloud.
- `Day3_segment.ipynb`: segmentation head, tilt ablation, permutation and
  batch-coupling tests.
- `T0_normal_estimation.ipynb`: own implementation, plane normals by PCA.
- `T1_mask.ipynb`: own implementation, silhouette extraction.
- `PRIMER.md`, `PRIMER_线代.md`: the theory notes this project is built on.
- `DAY1_LOG.md`, `DAY2_LOG.md`, `DAY3_LOG.md`: what worked, what failed, and why.
- `shots/`: the two photos (cup present, cup absent).

##  What this project is really testing

Not "can I segment a cup". The cup is nearly rotationally symmetric, so a model that memorises absolute coordinates scores well on it and then fails on the same cup tilted 20 degrees, which is the same failure I hit with the three built-in meshes.

The honest evaluation is therefore two-fold:

1. **Reconstruction accuracy**: does the photo pipeline reproduce the ruler and the water jug? Reported in mm and ml, cross-checked by density.
2. **Learned invariance**: does the model still segment the cup after a rotation the training set never saw? Reported as an accuracy drop, with and without augmentation.
