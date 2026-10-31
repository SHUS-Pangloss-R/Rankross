# Rankross - Machine Learning Journey

This is my personal repository to document my learning progress and hands-on projects in Machine Learning.

##  Projects
- **[Titanic Survival Prediction](Titanic_Kaggle_Original/README.md)**: An end-to-end ML project based on the original Kaggle dataset.
- **[Pytorch](https://github.com/SHUS-Pangloss-R/Rankross/blob/main/Pytorch%20Practice/Linear_Regression_GPU.ipynb)**: An journal of my journey to master pytorch
- **[PointCloud_Practice](./PointCloud_Practice/)** - From_scratch implementation of a PointNet architecture on synthetic 3D data.
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
> *Note: The local cross-validation score is often slightly higher than the Kaggle leaderboard score, as the test set may contain out-of-distribution samples.*
> Open Threads
Things I flagged and have not closed yet. Keeping them visible is the point.

The 92% accuracy ceiling in EXPERERIMENTS.md is not established. The two classes are centred 0.173 apart with noise sigma 0.5, which is an SNR around 0.35. A closed-form Bayes bound on that setup is close to chance for a single point, so 92% is more likely an artefact of evaluating on the training distribution with a lucky seed than evidence of a real ceiling. Re-run it on a held-out split with 5 seeds and report mean +/- std before repeating the claim.
Permutation invariance can never be "learned". gamma o MAX o h is invariant for every h, including an untrained one. Any test that shuffles points and checks the output did not change is a unit test on the aggregation axis, not a learning test. The two things that are learned are shape invariance (rotation, via T-Net + augmentation) and the critical point set.
T-Net is the fix for my rotation failure. My overfitting experiment showed the network fails on a 90-degree rotation. That is a representation problem, not a training problem. The augmentation ablation (train-rot/rot x test-rot/rot) is the honest way to measure whether the fix worked.
Max pooling buffers insertion and deletion, but only up to a learned bound. Theorem 2(a) gives a corridor: 
f
(
T
)
=
f
(
S
)
f(T)=f(S) whenever 
C
S
⊆
T
⊆
N
S
C 
S
​
 ⊆T⊆N 
S
​
 , so extra points are tolerated as long as they stay inside 
N
S
N 
S
​
 . The bound is data-dependent, not a fixed tolerance, and it says nothing about adversarial insertion. That gap is the natural next question for a real scene.
What changed after finishing the PointNet paper
I started this repository writing down what the model does. After the paper I am trying to write down what the model guarantees, and what it does not.

Three things I now believe that I did not before:

Invariance is structural or learned, never both. Ordering is structural (MAX), rigid transforms are learned (T-Net). Confusing the two is what made my earlier rotation "test" feel like a result when it was a unit test.
Robustness has a bound. Theorem 2 says at most K points carry the global feature. That is a real limit, and it is the honest reason PointNet degrades on large scenes rather than "it needs more layers".
A ground truth changes what a good result means. The three built-in meshes gave me 100% accuracy and zero information. Measuring my own cup with a caliper gives me a number in mm to be wrong about.
