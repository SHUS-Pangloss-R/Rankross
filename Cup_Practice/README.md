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

**Verdict: PASS.** Three independent readings agree within 1.2%, and the spline
and frustum volumes agree within 0.3%, which is what a nearly straight-walled
thermos should do. See [DAY1_LOG.md](DAY1_LOG.md).

##  Environment & Dependencies

- Python 3.11
- OpenCV (calibration, thresholding, contours)
- NumPy, SciPy (profile fit, integration)
- matplotlib (silhouette and profile plots)
- Open3D (only to turn the fitted profile into a point cloud / mesh for the PointNet track)

##  File Descriptions

- `cup_00_measure.py`: ruler and water-jug ground truth into `ground_truth.json`.
- `cup_01_calibrate.py`: checkerboard intrinsics + distortion, saved to `camera.json`.
- `cup_02_silhouette.py`: background subtraction, width-per-scanline extraction.
- `cup_03_profile_fit.py`: fit $r(z)$, integrate volume, run the density sanity check.
- `cup_04_revolve.py`: profile -> point cloud -> `.pt` cache for the segmentation track.

##  What this project is really testing

Not "can I segment a cup". The cup is nearly rotationally symmetric, so a model that memorises absolute coordinates scores well on it and then fails on the same cup tilted 20 degrees, which is the same failure I hit with the three built-in meshes.

The honest evaluation is therefore two-fold:

1. **Reconstruction accuracy**: does the photo pipeline reproduce the ruler and the water jug? Reported in mm and ml, cross-checked by density.
2. **Learned invariance**: does the model still segment the cup after a rotation the training set never saw? Reported as an accuracy drop, with and without augmentation.

##  工具说明

Day 1-3 的流水线代码与 AI 协作完成，每一条结论均由本人在自己拍的数据上复现验证（见各 LOG 与 report）。T0、T1 为本人独立实现。
