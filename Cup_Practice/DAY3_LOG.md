# Day 3 Log: Pose Robustness, and a Test That Could Actually Fail

##  Motivation

Day 2 produced a watertight mesh and a labelled point cloud
(`cup_points.npz`, 50 000 points, labels base / wall / lid, 10.1 / 66.5 / 23.3%).
The labels are exact, because they were computed from the parametric model rather
than painted.

Before training I had to decide what this dataset can measure. It **cannot**
measure generalisation to new shapes: there is one cup, and every sample is the
same 50 000 points resampled, so a random split is not a distribution shift at
all. It **can** measure robustness to a pose change, because that is a genuine
shift in the input distribution.

So the experiment asks one question: does the network use shape, or does it use
absolute coordinates?

##  The first version of this experiment was wrong

The first ablation rotated the cup about its **vertical axis (yaw)** and tested at
30 degrees. The model trained without augmentation scored:

| train | test 0 deg | test 30 deg yaw | drop |
| :--- | ---: | ---: | ---: |
| no rotation | 0.9958 | 0.9946 | 0.1% |

That looks like a robust model. It is not. **The labels are height bands, and a
yaw rotation leaves every point's height unchanged**, so the input-output relation
is identical and the test has nothing to fail at. The 0.1% was the experiment
measuring nothing.

The rule I took from this: a test is only worth running if I can say in advance
what a failure would look like. I could not.

##  Corrected design: tilt instead of yaw

A tilt about a horizontal axis is what actually mixes $z$ into $x$ and $y$.

**A useful trap:** the *z range* barely changes when a tall thin cup is tilted
(108.6 mm upright vs 109.9 mm at 30 degrees), because the cup trades height for
width. Looking at the range would have suggested nothing happened. What changes is
which point sits at which height.

So the diagnostic is a **z-only baseline**: label every point by absolute height,
with thresholds set upright.

| pose | z range (mm) | z-only baseline accuracy |
| :--- | :--- | ---: |
| 0 deg | -108.58 .. 104.01 | 1.000 |
| 30 deg tilt | -109.90 .. 103.77 | 0.835 |

That 0.835 is the ceiling of "coordinates only". It is also the reason the four
cells below can show a difference at all.

##  Setup

- **Data**: 50 000 points, `N = 1024` per sample, 1200 samples, drawn without
  replacement. Each sample centred on its own centroid, so translation invariance
  is free and cannot contaminate the rotation test.
- **Model**: per-point MLP (3 -> 64 -> 128 -> 1024), global max pooling,
  concatenate the global feature back onto every point, then a 512 -> 256 -> 3
  head. Adam, lr 1e-3, 15 epochs, batch 16, jitter sigma 0.01.
- **Pose**: tilt about a horizontal axis. Training either upright only, or with a
  random tilt in +/-30 degrees at a random azimuth. Evaluation at exactly 0 and 30
  degrees.

##  Results

mIoU:

| train / test | 0 deg (seen) | 30 deg (unseen) | drop |
| :--- | ---: | ---: | ---: |
| upright only | 0.9946 | **0.3751** | **+62.3%** |
| tilt aug +/-30 | 0.9792 | 0.9747 | +0.5% |

Per-class IoU:

| train / test | base | wall | lid |
| :--- | ---: | ---: | ---: |
| upright only @0d | 0.993 | 0.997 | 0.994 |
| upright only @30d | 0.319 | 0.588 | 0.219 |
| tilt aug @0d | 0.993 | 0.985 | 0.960 |
| tilt aug @30d | 0.987 | 0.982 | 0.955 |

Unit tests, on an **untrained** network:

```
permutation invariance, max|delta| : 0.000e+00   PASS
batch coupling,        max|delta| : 2.956e-05   PASS  (1e-4: GPU kernels reorder reductions)
output shape (4,512,3)             : (4, 512, 3) PASS
```

##  Analysis

**1. The coordinate dependence is real and severe.** Without augmentation the
unseen tilt destroys the model: mIoU 0.9946 -> 0.3751, accuracy 0.63. This is the
same failure I hit on the three built-in meshes, now with a control.

**2. The failure is not simply "predict the majority class".** Always predicting
wall would give accuracy 0.665 (the wall share) but mIoU only 0.222. The collapsed
model scores accuracy 0.629 with mIoU 0.375, so it partially tracks the shape and
still gets a third of it wrong. It is degraded, not degenerate.

**3. Thin bands fail first.** Under tilt the base (10 mm) and lid (32 mm) IoU drop
to 0.319 and 0.219, while the wall holds at 0.588. A thin band has the smallest
margin: the same absolute z error that is harmless inside a 170 mm band moves most
of a 10 mm band's points across the boundary. Predicted, then observed.

**4. Augmentation nearly closes the gap** (0.5% drop). The residual cost is on the
lid (0.960 -> 0.955), again the thin band.

**5. The permutation test proves nothing about learning.** `max|delta| = 0.000e+00`
on a freshly initialised network, because
$\gamma \circ \text{MAX} \circ h$ is invariant for any $h$. It is a unit test on
the pooling axis, and it belongs in a different box from the table above.

**6. The collapsed number is not reproducible to two digits.** Three runs gave
0.2512, 0.3730 and 0.3751. CUDA convolution is not bit-deterministic even with a
fixed seed. The conclusion (it collapses) is robust; the value should be reported
as roughly 0.25-0.38, not as 0.375.

##  Conclusion

**Rotation robustness here is learned, not structural.** The architecture
guarantees invariance to *ordering*; it guarantees nothing about *pose*. Those two
were conflated in my earlier notes and are now separated by measurement.

Two things I believe now that I did not before this project:

- **The experiment needs a failure mode before it is run.** The yaw version
  produced 0.9946 and felt like a success. It was a null experiment, and nothing
  in the output said so.
- **A difference of one number is not a result.** Every real finding here came
  from a *pair* of numbers that should have agreed or should have differed, never
  from a single score.

##  Open issues

- **Augmentation versus T-Net is unmeasured on my machine.** The notebook has the
  cell; my own runs gave T-Net 0.9824 -> 0.5616 (a 42.8% drop), i.e. learning the
  invariance recovers roughly half of what augmentation recovers. One run is not
  evidence; needs three seeds.
- **One shape, so this says nothing about generalisation.** To make that claim I
  need several cups, which is the parametric generator, not another photo.
- **The collapsed-cell variance (0.25-0.38) needs explaining** before any number
  from it is quoted.
