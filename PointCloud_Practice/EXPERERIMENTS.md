##  Experiment Log: Impact of Data Distribution on Training Stability

###  Motivation
As a proactive experiment, I modified the synthetic dataset to understand how data distribution affects model performance. 
Initially, the two classes were centered at `(0, 0, 0)` and `(5, 5, 5)`, resulting in a smooth loss curve and 100% accuracy. 

In this experiment, I changed the second class center from `(5, 5, 5)` to `(0.1, 0.1, 0.1)`, while keeping the Gaussian noise scale (`0.5`) unchanged. The training epochs were increased to 2500.

###  Observation
As shown in the loss curve, the training became highly unstable. 
- **Spikes**: Two massive loss spikes appeared around Epoch 1000 and Epoch 2000 (Loss jumped from ~0 to ~7 and ~5.5 respectively).
- **Convergence**: The model eventually stabilized, but the test set accuracy dropped from 1.0000 to **0.9200**.

###  Analysis: Why did this happen?
1. **Spatial Overlap (The Noise vs. Distance Problem)**: The distance between the two class centers is `0.1`, but the standard deviation of the noise is `0.5`. This means the two classes heavily overlap in 3D space. The model is essentially trying to find a boundary between two mixed clouds of points.
2. **Unstable Gradient (The Spikes)**: Because of the heavy overlap, the model struggles to find a stable decision boundary. When the model temporarily finds a "lucky" set of weights that fits the current batch perfectly, the next batch (which looks completely different due to the noise) severely punishes the model, causing a gradient explosion (the huge spikes).
3. **Accuracy Ceiling**: 92% accuracy is actually a very reasonable result. Given the overlapping distribution, a perfect 100% separation is theoretically impossible. The model successfully learned the weak statistical patterns.

###  Conclusion
This experiment perfectly demonstrates a core rule of machine learning: **"Data and feature distribution determine the upper limit of the model."** It also highlights the importance of monitoring loss curves to detect training instability.
