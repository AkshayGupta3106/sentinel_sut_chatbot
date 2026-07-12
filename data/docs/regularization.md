# Regularization: L1 vs L2

Regularization adds a penalty term to the loss function to discourage overly complex models and reduce overfitting by constraining the magnitude of the model's weights.

L2 Regularization (Ridge) adds the sum of squared weights (lambda * sum(w_i^2)) to the loss. It shrinks all weights toward zero smoothly but rarely makes them exactly zero. It works well when most features are expected to contribute at least a little to the prediction, and it has a closed-form solution in linear regression.

L1 Regularization (Lasso) adds the sum of absolute weights (lambda * sum(|w_i|)) to the loss. Because of the geometry of the L1 penalty (a diamond-shaped constraint region versus L2's circular region), it tends to push many weights to exactly zero, effectively performing automatic feature selection. This makes L1 useful when you suspect many features are irrelevant.

Elastic Net combines both L1 and L2 penalties, giving a tunable balance between Lasso's sparsity and Ridge's smooth shrinkage. It is particularly useful when features are correlated, since pure L1 tends to arbitrarily pick one correlated feature and zero out the others.

Dropout, used in neural networks, is a different but related regularization technique: during training, it randomly zeroes out a fraction of neurons in each forward pass, forcing the network to not rely too heavily on any single neuron and effectively training an ensemble of subnetworks.

A common interview question: "Why does L1 produce sparse solutions but L2 doesn't?" Answer: the L1 penalty's constraint region has corners at the axes, so the loss contours are more likely to intersect the constraint region exactly at a corner (where some weights are zero). The L2 constraint region is smooth (a circle/sphere), so the optimal intersection point rarely lands exactly on an axis.
