# Rankross - Machine Learning Journey

This is my personal repository to document my learning progress and hands-on projects in Machine Learning.

##  Projects
- **[Learning Path](./ROADMAP.md)**: The trajectory so far and the next tasks, with acceptance numbers.
- **[Titanic Survival Prediction](Titanic_Kaggle_Original/README.md)**: An end-to-end ML project based on the original Kaggle dataset.
- **[Pytorch](https://github.com/SHUS-Pangloss-R/Rankross/blob/main/Pytorch%20Practice/Linear_Regression_GPU.ipynb)**: An journal of my journey to master pytorch
- **[PointCloud_Practice](./PointCloud_Practice/)** - From_scratch implementation of a PointNet architecture on synthetic 3D data.
- **[Cup_Practice](./Cup_Practice/)** - Modelling my own thermos from phone photos, with a ruler as ground truth: silhouette + revolution prior, then a pose-robustness ablation.
- **[Paper Reading Notes](./Paper_Notes/)** - My deep learning paper notes and summaries (Current: PointNet-  COMPLETED).

##  Progress Log

| Date | Project | Key Tasks | Local CV Score | Kaggle Score |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-02 | Titanic (Seaborn Version) | Logistic Regression vs. Random Forest, Feature Engineering | 0.8200 | - |
| 2026-10-03 | Titanic (Kaggle Original) | GridSearchCV, VotingClassifier (Soft Voting) | 0.8384 | 0.79425 |
| 2026-10-04 | PyTorch GPU Linear Regression | Try forward propagation, backpropagation, and the `.to(device)` mechanism | - | - |
| 2026-10-05 | MiniPointNet(3D) | Per-point MLP, Max Polling, Synthetic Data generation | Accuracy: 1.0000 / 0.9200| - |
| 2026-10-07 | Real 3D Point Cloud Classification | PyTorch Dataset/DataLoader, Real Mesh Sampling, Overfitting Analysis | Test Accuracy: 100% (Severely Overfitted) | - |
| 2026-10-08 | ModelNet10 Point Cloud Classification | Offline Caching, Data Augmentation, LR Scheduler, Gradient Clipping, Early Stopping | Test Acc: 90.00% | - |
| 2026-10-11 | PointNet Paper Reading | Unordered Point Sets, Permutation Invariance, Symmetric Functions (MLP + Max Pooling) | - | - |  
| 2026-10-31 | PointNet Paper Reading (completed) | Theorem 1 (universality of MAX), Theorem 2 (critical point set + stability corridor), Theorem 3 (T-Net, orthogonality regularizer), training details | - | - |
| 2026-10-31 | Cup_Practice (Day 1) | Photo ground truth, silhouette = profile, height-anchored scale, contact-shadow cut | height -0.19%, max dia +0.25%, base -1.14% | - |
| 2026-10-31 | Cup_Practice (Day 2) | Spline profile, surface of revolution, watertight mesh, labelled point cloud | mesh volume vs analytic: -0.06% | - |
| 2026-10-31 | Cup_Practice (Day 3) | Tilt ablation, z-only baseline, permutation / batch-coupling unit tests | mIoU drop 62.3% (no aug) vs 0.5% (aug) | - |
| 2026-10-31 | Cup_Practice (T0/T1) | Own implementation of the PCA variance identity and of mask extraction | max row width 162 px vs 163 expected | - |

> *Note: The local cross-validation score is often slightly higher than the Kaggle leaderboard score, as the test set may contain out-of-distribution samples.*

##  Open Threads

Things I flagged and have not closed yet. Keeping them visible is the point.

- **The 92% accuracy ceiling in `EXPERERIMENTS.md` is not established.** The two classes are centred 0.173 apart with noise sigma 0.5 -- an SNR around 0.35. A closed-form Bayes bound on that setup is close to chance for a single point, so 92% is more likely an artefact of evaluating on the training distribution with a lucky seed than evidence of a real ceiling. Re-run on a held-out split with 5 seeds and report mean +/- std before repeating the claim.
- **Permutation invariance can never be "learned".** `gamma o MAX o h` is invariant for every `h`, including an untrained one. A test that shuffles points and checks the output did not change is a unit test on the aggregation axis, not a learning test. The invariance to *ordering* is structural; the invariance to *pose* is what gets learned.
- **My first pose experiment was a null test.** I rotated about the vertical axis, which leaves height-band labels unchanged, so the unaugmented model "survived" at 0.9946. A test is only worth running if I can say in advance what its failure looks like. Tilt about a horizontal axis is the version that can fail, and it does (0.375).
- **T-Net is a direction, not yet a number.** One run gave mIoU 0.9824 -> 0.5616 without augmentation (a 42.8% drop) against 0.5% with augmentation. That suggests learning the invariance recovers roughly half of what augmenting for it recovers. One run is not evidence; needs three seeds.
- **The collapsed mIoU is not reproducible to two digits.** Three runs gave 0.2512 / 0.3730 / 0.3751 on the same seed; CUDA convolution is not bit-deterministic. Quote a range, or three seeds, or do not quote it.
- **Max pooling buffers insertion and deletion, but only up to a learned bound.** Theorem 2(a) gives a corridor: $f(T) = f(S)$ whenever $\mathcal{C}_S \subseteq T \subseteq \mathcal{N}_S$, so extra points are tolerated as long as they stay inside $\mathcal{N}_S$. The bound is data-dependent, not a fixed tolerance, and it says nothing about *adversarial* insertion.
- **A mask is not the object.** In `T1_mask.ipynb` the Otsu threshold came out at 62 while the cup's printed pattern dips to diff 52, so the mask splits into pieces and the largest-component rule trims ~10 px off some rows. The widest row survives, which is why the diameter still matches the ruler, but this is a real limit of a single global threshold.

##  What changed after finishing the PointNet paper

I started this repository writing down what the model does. After the paper I am trying to write down what the model *guarantees*, and what it does not.

Three things I now believe that I did not before:

1. **Invariance is structural or learned, never both.** Ordering is structural (`MAX`); rigid transforms are learned (T-Net) or bought with augmentation. Confusing the two is what made my earlier rotation "test" feel like a result when it was a unit test.
2. **Robustness has a bound.** Theorem 2 says at most `K` points carry the global feature. That is a real limit, and it is the honest reason PointNet degrades on large scenes rather than "it needs more layers".
3. **A ground truth changes what a good result means.** The three built-in meshes gave me 100% accuracy and zero information. Measuring my own thermos with a ruler gives me three numbers that agree to 1.2%, and a pose test that collapses on purpose.
