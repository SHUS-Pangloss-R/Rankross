# 线性代数补丁：从投影到特征分解

配套 PRIMER.md 的 §3.5、§6.3。**目标**：让 $u^TCu$ 和特征分解变成你能手算的东西。

---

## §1 向量、内积、投影

### 1.1 内积的定义

两个列向量 $u, x \in \mathbb{R}^3$：

$$u^Tx = u_1x_1 + u_2x_2 + u_3x_3$$

结果是一个**数**，不是向量。

### 1.2 内积的两个含义

**含义一：投影长度 × 长度。**

$$u^Tx = \|u\|\,\|x\|\cos\theta$$

**含义二：如果 $\|u\|=1$，则 $u^Tx$ 就是 $x$ 在 $u$ 方向上的坐标。**

举个例子，$u = (1,0,0)^T$（x 轴方向），$x=(3,5,2)^T$：

$$u^Tx = 1\cdot3 + 0\cdot5 + 0\cdot2 = 3$$

就是 $x$ 的横坐标。所以「投影」这件事，**就是一次内积**。

### 1.3 平方长度用内积写

$$\|x\|^2 = x^Tx$$

这个后面要用。

---

## §2 方差 = 二次型（完整推导）

### 2.1 先定义清楚

有 $n$ 个点 $x_1, \dots, x_n \in \mathbb{R}^3$。

**质心**（每个点都相同权重）：

$$\bar x = \frac{1}{n}\sum_{i=1}^{n} x_i$$

**去中心**：

$$x_i' = x_i - \bar x$$

去中心后有个关键性质：

$$\frac{1}{n}\sum_i x_i' = \frac{1}{n}\sum_i x_i - \bar x = 0$$

**平均值变成零。** 这一步的作用是让「平方和」直接等于「方差」，不用再减均值。

下面都假设已经去过中心，所以写 $x_i$ 就代表 $x_i'$。

### 2.2 问题：把点投影到一个方向上，这些投影值有多分散

取一个**单位**向量 $u$（$\|u\| = 1$）。

每个点投影到 $u$ 上，得到一个标量：

$$t_i = u^Tx_i$$

这 $n$ 个标量的方差：

$$\text{Var}(t) = \frac{1}{n}\sum_{i=1}^{n}(t_i - \bar t)^2$$

因为 $\bar t = \frac1n\sum u^Tx_i = u^T(\frac1n\sum x_i) = u^T\cdot 0 = 0$，所以

$$\text{Var}(t) = \frac{1}{n}\sum_i t_i^2$$

### 2.3 把平方拆开

$$t_i^2 = (u^Tx_i)^2 = (u^Tx_i)(u^Tx_i)$$

注意 $u^Tx_i$ 是一个数，数的转置等于它自己：

$$u^Tx_i = (u^Tx_i)^T = x_i^Tu$$

代入：

$$t_i^2 = (u^Tx_i)(x_i^Tu)$$

标量乘法的结合律允许我们重新加括号：

$$(u^Tx_i)(x_i^Tu) = u^T\big(x_ix_i^T\big)u$$

**注意这里发生了什么**：$x_ix_i^T$ 不是数，是 $3\times3$ 矩阵（外积）。$u^T M u$ 里，$u^T$ 是 $1\times3$，$M$ 是 $3\times3$，$u$ 是 $3\times1$，乘出来是 $1\times1$ 的数。

### 2.4 求和

$$\sum_i t_i^2 = \sum_i u^T(x_ix_i^T)u = u^T\left(\sum_i x_ix_i^T\right)u$$

第二步利用了 $u$ 与求和号无关，可以提到外面。

### 2.5 定义协方差矩阵

$$C = \frac{1}{n}\sum_{i=1}^{n} x_i x_i^T$$

它是 $3\times3$ 矩阵。于是

$$\text{Var}(t) = \frac{1}{n}\sum_i t_i^2 = u^T C u$$

$$\boxed{\text{点云在方向 } u \text{ 上的方差} = u^TCu}$$

**这个式子是整个讲义里最重要的一条。** 记住它的读法：

> 给它一个方向，它告诉你「点在这个方向上散得多开」。

### 2.6 手算一遍 C

取 4 个二维点（二维好算）：

$$x_1 = (2,0),\quad x_2=(-2,0),\quad x_3=(0,1),\quad x_4=(0,-1)$$

质心：$\frac14[(2,0)+(-2,0)+(0,1)+(0,-1)] = (0,0)$。**已经居中**。

外积（对二维）：

$$x_1x_1^T = \begin{bmatrix}2\\0\end{bmatrix}[2\ \ 0] = \begin{bmatrix}4&0\\0&0\end{bmatrix}$$

$$x_2x_2^T = \begin{bmatrix}-2\\0\end{bmatrix}[-2\ \ 0] = \begin{bmatrix}4&0\\0&0\end{bmatrix}$$

$$x_3x_3^T = \begin{bmatrix}0\\1\end{bmatrix}[0\ \ 1] = \begin{bmatrix}0&0\\0&1\end{bmatrix}$$

$$x_4x_4^T = \begin{bmatrix}0\\-1\end{bmatrix}[0\ \ -1] = \begin{bmatrix}0&0\\0&1\end{bmatrix}$$

求和：

$$\begin{bmatrix}4&0\\0&0\end{bmatrix}+\begin{bmatrix}4&0\\0&0\end{bmatrix}+\begin{bmatrix}0&0\\0&1\end{bmatrix}+\begin{bmatrix}0&0\\0&1\end{bmatrix} = \begin{bmatrix}8&0\\0&2\end{bmatrix}$$

除以 $n=4$：

$$C = \begin{bmatrix}2&0\\0&0.5\end{bmatrix}$$

### 2.7 用 $u^TCu$ 验证

**沿 x 轴**，$u=(1,0)$：

$$u^TCu = \begin{bmatrix}1&0\end{bmatrix}\begin{bmatrix}2&0\\0&0.5\end{bmatrix}\begin{bmatrix}1\\0\end{bmatrix} = \begin{bmatrix}1&0\end{bmatrix}\begin{bmatrix}2\\0\end{bmatrix} = 2$$

**直接算投影方差**：$t_i = x_{i,1}$，即 $2,-2,0,0$。平方和 $=4+4+0+0=8$，除以 4 得 **2**。✓

**沿 y 轴**，$u=(0,1)$：

$$u^TCu = 0.5$$

直接算：$t_i = 0,0,1,-1$，平方和 $=0+0+1+1=2$，除以 4 得 **0.5**。✓

**沿 45° 方向**，$u=(\tfrac{1}{\sqrt2},\tfrac{1}{\sqrt2})$：

$$u^TCu = \frac12(2) + \frac12(0.5) = 1.25$$

直接算投影：$t_i = \frac{x_{i,1}+x_{i,2}}{\sqrt2}$，得 $\sqrt2, -\sqrt2, \frac{1}{\sqrt2}, -\frac{1}{\sqrt2}$。平方和 $=2+2+0.5+0.5=5$，除以 4 得 **1.25**。✓

**三次全对。** $u^TCu$ 确实就是「该方向的方差」。

---

## §3 特征值与特征向量

### 3.1 定义

对一个方阵 $A$，如果存在非零向量 $v$ 和数 $\lambda$ 满足

$$Av = \lambda v$$

则 $v$ 是 $A$ 的**特征向量**，$\lambda$ 是对应的**特征值**。

### 3.2 几何意义

$Av = \lambda v$ 的意思是：**把矩阵 $A$ 作用在 $v$ 上，结果仍然沿着 $v$ 的方向，只是长度乘了 $\lambda$。**

绝大多数向量被 $A$ 作用后会**转向**。只有特征向量不转向。

**为什么叫「特征」**：它们刻画了这个线性变换的「骨架方向」——哪些方向被拉伸，拉伸多少，其余方向都是这些的混合。

### 3.3 手算 $2\times2$ 的特征值

对

$$C = \begin{bmatrix}2&0\\0&0.5\end{bmatrix}$$

解 $\det(C - \lambda I) = 0$：

$$\det\begin{bmatrix}2-\lambda & 0\\0& 0.5-\lambda\end{bmatrix} = (2-\lambda)(0.5-\lambda) = 0$$

$$\lambda_1 = 2,\qquad \lambda_2 = 0.5$$

**求特征向量**，代回 $(C-\lambda I)v = 0$。

$\lambda_1=2$：

$$\begin{bmatrix}0&0\\0&-1.5\end{bmatrix}\begin{bmatrix}v_1\\v_2\end{bmatrix} = \begin{bmatrix}0\\0\end{bmatrix} \Rightarrow v_2 = 0$$

取 $v_1 = (1,0)^T$。

$\lambda_2=0.5$：

$$\begin{bmatrix}1.5&0\\0&0\end{bmatrix}\begin{bmatrix}v_1\\v_2\end{bmatrix}=0 \Rightarrow v_1 = 0$$

取 $v_2=(0,1)^T$。

### 3.4 特征向量方向上的方差

把 $u = v_1$ 代入 $u^TCu$：

$$v_1^TCv_1 = v_1^T(\lambda_1 v_1) = \lambda_1\underbrace{v_1^Tv_1}_{=1} = \lambda_1 = 2$$

**特征值就是该方向的方差。** 上面已经用「直接投影」独立验证过是 2。两条路对上了。

### 3.5 转一下数据，特征值不变

把上面 4 个点整体旋转 45°。旋转矩阵

$$R = \frac{1}{\sqrt2}\begin{bmatrix}1&-1\\1&1\end{bmatrix}$$

新点集 $y_i = Rx_i$。新的协方差：

$$C' = \frac1n\sum (Rx_i)(Rx_i)^T = \frac1n\sum R x_ix_i^T R^T = R\,C\,R^T$$

算出来：

$$C' = \begin{bmatrix}1.25&0.75\\0.75&1.25\end{bmatrix}$$

它的特征值仍然是 $2$ 和 $0.5$（解 $\det(C'-\lambda I)=0$ 得到），特征向量变成 $(1,1)^T/\sqrt2$ 和 $(1,-1)^T/\sqrt2$。

**结论**：数据转了，协方差矩阵变了，**但特征值没变，特征向量跟着数据一起转。**

这说明特征值和特征向量描述的是**数据本身的形状**（拉得多长、朝哪儿），不依赖于你用什么坐标系去看它。

### 3.6 谱定理

**对称矩阵一定可以写成**

$$C = V\Lambda V^T$$

其中 $V$ 的列是**互相正交的单位**特征向量，$\Lambda$ 是对角矩阵（特征值）。

协方差矩阵 $C = \frac1n\sum x_ix_i^T$ 一定是对称的（因为 $(x_ix_i^T)^T = x_ix_i^T$），所以这个定理一定适用。

**这是 PCA 能做的根本原因**：正交的坐标轴存在，你才能「换一套坐标系」而不损失信息。

---

## §4 为什么最小特征向量是法向

### 4.1 几何图像

点云的协方差 $C$ 把一个**单位球**映射成一个**椭球**：

$$\{Cu \mid \|u\|=1\}$$

这个椭球的三个**半轴长**是 $\sqrt{\lambda_1}, \sqrt{\lambda_2}, \sqrt{\lambda_3}$，方向就是三个特征向量。

- 主轴方向 $v_1$：拉得最长（方差最大）
- 次轴 $v_2$
- 最短轴 $v_3$：拉得最短（方差最小）

### 4.2 局部平面意味着什么

一个曲面上某点附近的邻域，近似是一块**薄片**：

- 在薄片内任意方向：点散得开 → 方差大
- **垂直于薄片**：点几乎不动 → 方差**极小**

所以「方差最小的方向」= 「垂直于表面的方向」= **法向**。

### 4.3 严格证明：最小方差方向 = 最小特征向量

问题：

$$\min_{u}\ u^TCu \quad \text{s.t.}\quad \|u\|=1$$

约束写成 $u^Tu = 1$。拉格朗日函数：

$$\mathcal{L}(u,\lambda) = u^TCu - \lambda(u^Tu - 1)$$

对 $u$ 求偏导（利用 $\frac{\partial}{\partial u}(u^TAu) = 2Au$ 当 $A$ 对称）：

$$\frac{\partial \mathcal{L}}{\partial u} = 2Cu - 2\lambda u = 0$$

$$\Rightarrow\ Cu = \lambda u$$

**这一步就是全部秘密**：一阶条件把优化问题变成了特征值问题。

代回目标函数：

$$u^TCu = u^T(\lambda u) = \lambda$$

所以目标值就是特征值，而所有候选 $u$ 只能是特征向量，因此

$$\min = \lambda_{\min}, \qquad \max = \lambda_{\max}$$

**证毕。**

### 4.4 三个特征值的实用含义

按 $\lambda_1 \ge \lambda_2 \ge \lambda_3$ 排序：

| 量 | 含义 |
| :--- | :--- |
| $\lambda_3$ | 邻域的「厚度」 |
| $\lambda_2$ | 薄片内的短轴 |
| $\lambda_1$ | 薄片内的长轴 |

派生的常用特征：

$$\text{平面度} = \frac{\lambda_2 - \lambda_3}{\lambda_1}$$

平面度接近 1 说明这个邻域真的很平，法向可信；接近 0 说明是边缘或噪点，法向不可信。

$$\text{表面变化度} = \frac{\lambda_3}{\lambda_1+\lambda_2+\lambda_3}$$

这个量小 → 平坦；大 → 曲率高。

**T7 里你应该把这两个量算出来，用它筛掉不可靠的法向。**

---

## §5 代码与公式的对应

```python
# 1. 取邻域
idx = kdtree.query(x, k=30)[1]          # 最近 30 个点的下标
P = points[idx]                          # (30, 3)

# 2. 去中心      <-- PRIMER §2.1
c = P.mean(axis=0)                       # 质心 (3,)
Q = P - c                                # 每行是一个 x_i'

# 3. 协方差      <-- PRIMER §2.5
C = Q.T @ Q / len(Q)                     # (3,3)  注意是 Q.T @ Q，不是 Q @ Q.T

# 4. 特征分解    <-- PRIMER §3.6
w, V = np.linalg.eigh(C)                 # eigh 返回值是【升序】，V 的列是特征向量

# 5. 法向 = 最小特征值对应的方向
normal = V[:, 0]                         # eigh 升序，所以第 0 列就是最小的
```

### 五个必须注意的坑

**坑 1：`Q.T @ Q` 不是 `Q @ Q.T`**

$Q$ 是 $(30,3)$。

- `Q.T @ Q` → $(3,3)$ ✓ 这是 $\sum_i x_ix_i^T$
- `Q @ Q.T` → $(30,30)$ ✗ 这是每个点两两内积，完全不是协方差

**这是最容易写反的一处。** 检查方法：协方差的形状必须等于**特征维度的平方**，不是点数的平方。

**坑 2：`np.linalg.eigh` 返回的是升序**

`eigh` → 升序（ascending），所以 `V[:, 0]` 是**最小**特征值的方向 = 法向。

`eig` → 不保证顺序，而且对对称矩阵不用它。

**坑 3：忘了去中心**

不去中心，$\frac1n\sum x_ix_i^T$ 是**二阶矩**，不是协方差。当点云离原点很远时，这个矩阵被「位置」主导，而不是被「形状」主导。表现是：法向看起来随机。

**坑 4：除以 $n$ 还是 $n-1$**

- 除以 $n$：总体协方差，和 $u^TCu$ 的推导一致
- 除以 $n-1$：无偏估计

**在我们的用途里，两者只差一个常数，特征向量完全一样**，特征值差个因子。为了一致性，统一除 $n$。

**坑 5：特征向量的符号任意**

$v$ 和 $-v$ 都是解。所以算出来的法向**一半朝里、一半朝外**。

这不是 bug，是数学性质。修法见 PRIMER §6.4。

---

## §6 自检题

1. 写出 $\text{Var}(u^Tx) = u^TCu$ 的完整推导，不许跳步。
2. 用 4 个点 $(3,0), (-3,0), (0,2), (0,-2)$ 手算 $C$、特征值、特征向量。
3. 上题中，沿 $(1,1)/\sqrt2$ 方向的方差是多少？用 $u^TCu$ 算一遍，再直接投影算一遍，对得上吗？
4. 证明：任何对称矩阵的特征值都是实数。（提示：$Cv=\lambda v$，两边左乘 $v^T$）
5. 为什么法向取**最小**而不是最大特征向量？如果把「最小」和「最大」搞反，会得到什么方向？
6. 一个点云的邻域 $\lambda_1=1.0,\ \lambda_2=0.9,\ \lambda_3=0.85$。这个点的法向可信吗？为什么？

---

## §7 参考

- 3Blue1Brown《Essence of Linear Algebra》第 9–12 集（内积、叉积、特征向量），第 14 集（SVD）
- 任意线性代数教材的「对称矩阵与二次型」一章
