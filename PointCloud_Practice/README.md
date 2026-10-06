# 1.MiniPointNet: 3D Point Cloud Classification (Synthetic Data)

##  Overview
This project is a hands-on implementation of a **Mini-PointNet** architecture built from scratch using PyTorch. It serves as an introductory step into 3D Deep Learning. Instead of using complex, memory-heavy datasets, we generated synthetic 3D point cloud data to focus entirely on understanding the core neural network architecture.

##  Key Concepts Covered
- **3D Point Cloud Data Structure**: Handling point sets with shape `[Batch, N, 3]`, where `N` is the number of points (1024) and `3` represents the `(x, y, z)` coordinates.
- **Permutation Invariance**: Understanding that a point cloud is an unordered set. We handle this by applying a symmetric function (Max Pooling) over the point dimension.
- **Mini-PointNet Architecture**:
  - **Per-point MLP**: Shared weights across all points to extract local features (`3 -> 64 -> 128 -> 256`).
  - **Global Feature Extraction**: Using `torch.max(features, dim=1)` to aggregate point features into a single global feature vector per sample.
  - **Classification Head**: A fully connected network (`256 -> 128 -> 2`) to output class logits.
- **PyTorch Training Loop**: Standardized implementation of Forward Propagation, Loss Calculation, Backpropagation, and Optimizer Step.
- **GPU Acceleration**: Full model and data transfer to CUDA device.

##  Dataset
Since 3D datasets are large, we generated a synthetic dataset of 1000 samples to validate the architecture:
- **Class 0 (Airplane)**: 1024 random points clustered near the origin `(0, 0, 0)`.
- **Class 1 (Chair)**: 1024 random points clustered near `(5, 5, 5)`.

##  Results
The model converges extremely quickly and achieves **1.0000 (100%) accuracy** on the test set. This validates that the Mini-PointNet successfully learned to distinguish the spatial distribution of the two synthetic classes.

##  Environment & Dependencies
- Python 3.11
- PyTorch (Nightly build for CUDA support)
- Scikit-learn (for train/test split)
- Matplotlib (for loss curve visualization)

##  File Descriptions
- `MiniPointNet_Classification.ipynb`: Complete Jupyter Notebook covering synthetic data generation, network definition, training loop, and evaluation.

- ##  2.Geometric Processing & Visualization Basics

###  Overview
Before diving into deep neural networks, it's crucial to understand how to manipulate raw 3D data. This notebook covers fundamental point cloud processing techniques using Open3D.

###  Key Concepts Covered
- **Statistical Outlier Removal**: Removed noisy, floating points using `remove_statistical_outlier` to clean the point cloud surface.
- **Voxel Downsampling**: Reduced the number of points using `voxel_down_sample` (voxel_size=0.05) while preserving the overall shape of the object, which is essential for efficient GPU memory usage.
- **Height-based Colorization**: Instead of a uniform color, we extracted Z-coordinates, normalized them (0.0 to 1.0), and applied a color map (`plt.cm.plasma`) to create a beautiful height-based pseudo-color effect.
- **Visualization Customization**: Configured a customized visualization window with a dark background and adjusted point size for better aesthetics.

###  Results
The raw point cloud (potentially hundreds of thousands of points) was cleaned and downsampled to a few thousand points. The final visualization shows a smooth, noise-free point cloud colored by elevation, making it much easier to inspect the geometry visually.

###  File Descriptions
- `PointCloud_Geometry_Processing.ipynb`: Code for statistical outlier removal, voxel downsampling, and height-based coloring.
