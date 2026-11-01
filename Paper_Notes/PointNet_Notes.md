# PointNet Paper Reading Notes
**Date**: 2026-10-11
**Progress**: Completed (19/19) - Full paper read, with the math proof understood
**Paper**: PointNet: Deep Learning on Point Sets for 3D Classification and Segmentation

---

##  Core Idea of PointNet
The fundamental challenge of processing 3D point clouds is their **unordered nature (permutation invariance)**. 
The key idea to solve this is: 
- 1.sort input into a canonical order(hard to do so in higher dimensions)
- 2.treat the input as a sequence to train an RNN, but augment the training data by all kinds of permutations(The fact is :Order does matter,and it’s hard to scale to thousands of input elements,which is common)
- 3.approximate a general function defined on a point set by applying a symmetric function on transformed elements in the set(what the paper do)
> *"Apply a symmetric function on transformed elements in the set."*

### 📐 Key Equation
$$f(\{x_1, \dots, x_n\}) \approx g (h(x_1), \dots, h(x_n))$$

###  My Understanding (Mapping to Code)
- **$h$ (MLP)**: A shared Multi-Layer Perceptron that operates independently on each point. It maps each point from 3D coordinates to high-dimensional features (e.g., 3 -> 64 -> 128 -> 1024). *(This is `self.mlp` in my code).*
- **$g$ (Symmetric Function + Max Pooling)**: A function that takes the unordered set of features and aggregates them. The paper uses Max Pooling to ensure the output does not depend on the order of the points. *(This is `torch.max(features, dim=1)` in my code).*
- **Conclusion**: Regardless of how we shuffle the input points, the extracted global feature remains the same. 

##  Key Takeaways
- RNNs are not suitable for unordered sets because they process sequences, and it's hard to scale to thousands of points.
- PointNet treats the input as a set, not a sequence
- The network learns a set of functions $h$ to capture different properties (edges, corners, etc.) of the geometric shapes.

---

##  Theorem 1: Why $g \circ h$ is the right form

The paper does not just propose this form, it argues it is **universal**. Any continuous set function $f$ on a compact domain can be approximated arbitrarily well by $\gamma \circ \text{MAX}$ with a large enough $K$ (pooling dimension):

$$f(\{x_1,\dots,x_n\}) \approx \gamma \circ \text{MAX} \circ h$$

The paper defers the full proof to the supplementary. My paraphrase of the two moves (check it against the supplement, I am reconstructing from the argument sketch):

1. **Squeeze from above**: Sort the points so $x_1 \le x_2 \le \dots \le x_n$. Build the vector $u = (\max_i h(x_i)_1, \dots, \max_i h(x_i)_K)$. Every point can be recovered from $u$ as long as $K$ is large enough, so the map from the sorted point set to $u$ is **injective**. Then a continuous $\tau$ exists with $\tau(u) = f(S)$.
2. **Squeeze from below**: For an open-ball neighbourhood of $S$, the sum over the balls stays a valid symmetric form because $\alpha(\cdot)\beta(\cdot)$ is itself symmetric. This connects the max form back to the original set function.

The result: $K$ is the **pooling dimension** (1024 in the paper), and the bound is tight in the sense that $K = |S|$ is enough for exact reconstruction.

**What I took from it**: max is not chosen for convenience, it is chosen because it preserves the *set* while throwing away the *order*. Sum and mean would also be permutation-invariant, but they average away the extreme points, which are exactly the shape-critical ones (corners, edges).

##  Theorem 2: Why max gives a "critical point set" for free

$$\text{MAX}: \quad \text{the output is determined by } C_S = \{x_i \mid h(x_i) = u, \ u = \max_j h(x_j)\}$$

with $|C_S| \le K$. The theorem has **two parts**, and the second one is the part I had wrong when I first wrote this note:

- **(a) A stability corridor**: $\forall S$, there exist sets $\mathcal{C}_S, \mathcal{N}_S \subseteq \mathcal{X}$ with $\mathcal{C}_S \subseteq \mathcal{N}_S$ such that $f(T) = f(S)$ whenever $\mathcal{C}_S \subseteq T \subseteq \mathcal{N}_S$. That is: the output is unchanged if the critical points survive, **and** unchanged as long as extra points stay inside an upper bound $\mathcal{N}_S$. So PointNet is robust to *added* noise points, not only to removed ones. The paper says this explicitly in the introduction ("corruption through point insertion (outliers) or deletion (missing data)").
- **(b) A hard cap**: $|\mathcal{C}_S| \le K$. The prediction is *totally determined* by a finite subset of at most $K$ points. This is the "bottleneck dimension".

Two consequences that matter for practice:

- **Robustness to input perturbation**: the effective input is a small **skeleton** (the paper's Figure 5 shows these are the boundary / silhouette points). Insertion and deletion are both buffered, up to $\mathcal{N}_S$ and $\mathcal{C}_S$ respectively.
- **An upper bound on "how many points matter"**: at most $K$ points can ever be responsible for the global feature. With $K = 1024$ that is a generous budget, but it is a real limit and it is why PointNet degrades on large scenes.

This also answers a question I had while writing the MiniPointNet code: **why does a 3-layer MLP with no local neighbourhood still work?** It is because $\gamma$ is applied to the *global* max vector, and the max vector already aggregates information from all $K$ critical point directions. The model is not looking at local patches; it is looking at the global skeleton.

##  Theorem 3: T-Net and the orthogonality constraint

The paper adds an input transform $T$ (the "T-Net") to make the network invariant to a rigid transformation. Two of them actually:

- **Input T-Net**: a mini-PointNet (point-independent feature extraction + max pooling + fc) predicting a $3\times3$ affine matrix, applied directly to the input coordinates. It canonicalizes the input before the main network sees it.
- **Feature T-Net**: a $64\times64$ matrix predicting a transform in feature space, with the **regularization term** $L_{reg} = \|I - AA^T\|_F^2$ added to the softmax loss, where $A$ is the feature alignment matrix.

The orthogonality constraint is the important part. A transformation matrix in feature space has far higher dimension than the $3\times3$ spatial one, which "greatly increases the difficulty of optimization", so the paper constrains it toward orthogonal: an orthogonal map loses no information, and the paper reports that this makes optimization more stable and improves performance.

**This is the answer to the open question in my previous notes.** My overfitting experiment showed the model has no spatial invariance (fails the 90-degree rotation test). T-Net is exactly the mechanism the paper uses to fix that. I had been trying to fix it with coordinate normalization, which is the wrong tool.

##  Training details worth remembering

- **Loss**: multi-class cross entropy is default; the classification head is a small MLP on the global feature.
- **Optimizer**: Adam, initial lr = $10^{-3}$ (**not** $10^{-2}$ like my MiniPointNet, which may be part of why mine was spiky).
- **Batch size**: 32.
- **Batch norm**: applied after every layer with ReLU. Decay rate starts at 0.5 and is increased to 0.99; the $\gamma$ init is 1 and $b$ init is 0.
- **Dropout**: keep ratio 0.7 on the last mlp of the classification net.
- **Data augmentation that matters**: random **rotation about the up axis (yaw only)**, jitter each point with Gaussian noise, random uniform **scale**. Yaw-only is deliberate, not lazy: ModelNet models share a consistent up direction, so full SO(3) augmentation would teach the net that "upside down" is normal and wash out the top/bottom distinction. For my cup this matters directly.

> *Note: some of these are in the supplementary rather than the main paper; I should re-check exact values against the supplement before quoting them as final.*

##  Key Takeaways (completed)

- The permutation invariance is a **property of the aggregation operator, not something learned**. $\gamma \circ \text{MAX} \circ h$ is invariant **for every $h$**. So any "test" that just shuffles points and checks the output did not change will pass even with an untrained network. That is a unit test, not a learning test.
- Max pooling gives a **critical point set** $C_S$ with $|C_S| \le K$: the model is robust to non-critical points and its output depends on at most $K$ points.
- The T-Net **learns** invariance to rigid transforms, but the pooling itself is **structurally** invariant to ordering. Those are two different kinds of invariance and they should be tested differently.
- Permutation invariance $\ne$ **shape** invariance. A model can be perfectly permutation-invariant and still fail on a rotated object, because rotation changes the coordinates, not the order. **My own rotation failure was this case.**

## ❣ Questions for Further Study (resolved)

- ~~What exactly is the "T-Net" mentioned in Figure 2?~~ → Answered: input/feature transform network with an $I - AA^T$ orthogonality regularizer, solving the exact failure I found in my overfitting experiment.
- ~~How does the max pooling layer handle gradients during backpropagation?~~ → Answered: max is piecewise linear and picks **one** point per feature dimension, so the gradient flows back only through the argmax point. The gradient is a sparse mask. This is why max pooling is cheap to backprop and why the critical point set is also the gradient path.
- **New question**: Theorem 2 bounds robustness by $\mathcal{N}_S$, but the bound is *data-dependent*, not a fixed tolerance. What actually sets $\mathcal{N}_S$ for a trained net, and how quickly does it collapse under adversarial (rather than random) point insertion? The theorem covers random corruption; it does not promise adversarial robustness, and the difference matters for a real scene.

##  Final Verdict

PointNet is a **global** representation: it compresses a point set to one vector, then classifies. It handles ordering with a hard theoretical guarantee and rigid transforms with a learned assist. Its limitation is equally clean: **it has no local neighbourhood**, so it cannot capture fine-grained structure (this is why PointNet++ exists). 

For my own work the lesson is: I had two problems and one of them was not a training problem at all. My rotation failure was a **representation** problem. T-Net is the principled fix, and the augmentation ablation (train with / without rotation, test with / without) is the only honest way to measure whether it worked.
