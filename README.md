# Rankross - Machine Learning Journey

This is my personal repository to document my learning progress and hands-on projects in Machine Learning.

##  Projects
- **[Titanic Survival Prediction](Titanic_Kaggle_Original/README.md)**: An end-to-end ML project based on the original Kaggle dataset.
- **[Pytorch](https://github.com/SHUS-Pangloss-R/Rankross/blob/main/Pytorch%20Practice/Linear_Regression_GPU.ipynb)**: An journal of my journey to master pytorch
- **[PointCloud_Practice](./PointCloud_Practice/)** - From_scratch implementation of a PointNet architecture on synthetic 3D data.

##  Progress Log

| Date | Project | Key Tasks | Local CV Score | Kaggle Score |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-02 | Titanic (Seaborn Version) | Logistic Regression vs. Random Forest, Feature Engineering | 0.8200 | - |
| 2026-10-03 | Titanic (Kaggle Original) | GridSearchCV, VotingClassifier (Soft Voting) | 0.8384 | 0.79425 |
| 2026-10-04 | PyTorch GPU Linear Regression | Try forward propagation, backpropagation, and the `.to(device)` mechanism | - | - |
| 2026-10-05 | MiniPointNet(3D) | Per-point MLP, Max Polling, Synthetic Data generation | Accuracy: 1.0000 / 0.9200| - |
| 2026-10-07 | Real 3D Point Cloud Classification | PyTorch Dataset/DataLoader, Real Mesh Sampling, Overfitting Analysis | Test Accuracy: 100% (Severely Overfitted) | - |
> *Note: The local cross-validation score is often slightly higher than the Kaggle leaderboard score, as the test set may contain out-of-distribution samples.*
