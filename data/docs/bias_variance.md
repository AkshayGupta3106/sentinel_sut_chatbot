# Bias-Variance Tradeoff

Bias is the error introduced by approximating a real-world problem with a simplified model. High-bias models make strong assumptions about the data and tend to underfit, meaning they perform poorly on both training and test sets. Linear regression on a highly non-linear dataset is a classic example of high bias.

Variance is the error introduced by a model's sensitivity to small fluctuations in the training set. High-variance models fit the training data very closely, including its noise, and tend to overfit. Deep decision trees with no depth limit are a classic example of high variance.

The total expected error of a model decomposes as: Error = Bias^2 + Variance + Irreducible Error. As model complexity increases, bias typically decreases while variance increases. The goal is to find the sweet spot that minimizes total error, not to minimize bias or variance individually.

Practical techniques to manage the tradeoff include regularization (L1/L2) to reduce variance, ensembling (bagging reduces variance, boosting reduces bias), cross-validation to detect over/underfitting, and adjusting model capacity (more/fewer parameters, deeper/shallower trees).

A common interview follow-up: "How do you diagnose whether a model is high bias or high variance?" Answer: plot training vs validation error curves (learning curves). High bias shows both errors converging to a high value. High variance shows a large gap between low training error and high validation error.
