# Learning Path

My trajectory so far, and where it is going. Kept here so that progress is
visible rather than implied.

Target: 3D vision, specifically point cloud registration.

---

## 1. Where I started

| Date | Work | What it actually taught me |
| :--- | :--- | :--- |
| 2026-10-02 | Titanic (Seaborn), Logistic Regression vs Random Forest | End-to-end pipeline, feature engineering |
| 2026-10-03 | Titanic (Kaggle original), GridSearchCV + Voting | Hyper-parameter search, ensembling |
| 2026-10-04 | PyTorch GPU linear regression | Forward / backward, `.to(device)` |
| 2026-10-05 | MiniPointNet, symmetric function | First network written from scratch |
| 2026-10-07 | Real meshes, 3 classes, 100% accuracy | **First time I distrusted my own number** |
| 2026-10-08 | ModelNet10, 90% | Offline caching, augmentation, scheduler, early stopping |
| 2026-10-11 | PointNet paper | How to read a paper |

## 2. The three shifts

**从会调库到会写网络.**
Titanic was calling sklearn. MiniPointNet was assembling modules and writing the
training loop myself.

**从会跑通到会怀疑.**
On 2026-10-07 I scored 100% and labelled it "Severely Overfitted" myself. That
labelling is the turning point of this repository. The easy thing to write there
was "100% accuracy, works well".

**从用别人的数据到造自己的真值.**
Cup_Practice is the first 3D project where I know the right answer in advance.
Three measurements agreeing to 1.2% carry more information than 100% accuracy on
three meshes.

## 3. Where I am now (2026-11-01)

| Item | Result | Evidence |
| :--- | :--- | :--- |
| PointNet paper, Theorem 1-3 | completed | `Paper_Notes/PointNet_Notes.md` |
| Cup Day 1: silhouette = profile, ruler ground truth | height -0.19%, dia +0.25% | `Cup_Practice/DAY1_LOG.md` |
| Cup Day 2: surface of revolution, watertight | mesh volume vs analytic -0.06% | `Cup_Practice/Day2_revolve.ipynb` |
| Cup Day 3: tilt ablation | mIoU drop 62.3% (no aug) vs 0.5% (aug) | `Cup_Practice/DAY3_LOG.md` |
| T0: PCA variance identity | own implementation | `Cup_Practice/T0_normal_estimation.ipynb` |
| T0b: normal estimation on a plane | 0.04 deg at sigma=0.05, 0.24 deg at sigma=0.5 | same |
| T1: mask extraction | max row width 162 px vs 163 expected | `Cup_Practice/T1_mask.ipynb` |

## 4. Where I am going

Each task has a numeric acceptance criterion, so "done" is not a judgement call.

### Stage A - finish the reconstruction (this week)

- [x] **T1** mask extraction, max row width 162 px (expected 163)
- [x] **T2** scale anchoring: scale 0.36915, max diameter 59.06 mm
- [x] **T2b** quantified the 9%: it is an equipment limit, not a bug. The base
  cut that made the diameter match the ruler was tuned against that same ruler,
  so it was circular. Reported a bound instead of a number. See `DAY2_LOG.md`.
- [~] **T3** contact-shadow cut: **not pursued.** The shadow is as wide as the
  cup, so there is no edge to detect; every rule I tried was fitting noise.
- [ ] **T4** spline fit and volume integration, with the scale carried as a
  parameter and the 9% propagated into the volume
- [ ] **T5** revolve into a mesh: watertight, volume within 0.5% of the integral
- [ ] **T6** hand-written IoU / mIoU: reproduce 0.375 from 0.319 / 0.588 / 0.219

### Stage B - from segmentation to registration (winter break)

- [ ] **T7** normals and FPFH descriptors: (N, 33) shape, outward-consistent normals
- [ ] **T8** coarse registration: FPFH + RANSAC + Kabsch, rotation error under 1 deg
  on a known synthetic rotation
- [ ] **T9** ICP refinement: table of initial angle to final error, 0 / 10 / 30 / 90 / 180 deg
- [ ] **T10** quantify the symmetry ambiguity: at which initial angles does ICP land
  on the wrong symmetric solution?

### Stage C - read and reproduce (spring)

- [ ] Read GeoTransformer and RoReg, write notes in the same format as the PointNet notes
- [ ] Reproduce one module of one of them on my own data
- [ ] Write down honestly which step I failed and why

## 5. Why this path

The lab I want to join works on point cloud registration. Registration needs
three things I am building in order:

1. **Geometry** - rotations, SVD, Kabsch. Covered in `Cup_Practice/PRIMER.md` section 4-5.
2. **Point cloud handling** - normals, descriptors, neighbourhoods. Task T7.
3. **Honest evaluation** - ground truth, ablation, error in physical units.
   This is what Cup_Practice is for.

The order matters. Reading a registration paper before I can compute a rotation
matrix from correspondences means memorising rather than understanding.

## 6. How to read this file

- A box is checked only when the acceptance number is met on my own data.
- When something fails, the failure goes into a `DAY*_LOG.md`, not into silence.
- Dates are real; if a stage takes three months, the dates will say so.
