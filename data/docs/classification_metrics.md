# Classification Evaluation Metrics

Precision is the fraction of predicted positives that are actually positive: TP / (TP + FP). It answers "when the model says positive, how often is it right?" Precision matters most when false positives are costly, such as spam detection where flagging a legitimate email is expensive.

Recall (Sensitivity) is the fraction of actual positives correctly identified: TP / (TP + FN). It answers "of all the real positives, how many did the model catch?" Recall matters most when false negatives are costly, such as cancer screening where missing a real case is dangerous.

F1 Score is the harmonic mean of precision and recall: 2 * (Precision * Recall) / (Precision + Recall). It is preferred over a simple average because it penalizes extreme imbalance between precision and recall more heavily, and it is the standard metric for imbalanced classification tasks.

ROC-AUC measures the model's ability to rank positive examples above negative examples across all classification thresholds, plotting True Positive Rate against False Positive Rate. It is threshold-independent, which makes it useful for comparing models, but it can be misleadingly optimistic on highly imbalanced datasets.

PR-AUC (Precision-Recall AUC) is generally preferred over ROC-AUC when the positive class is rare, since it focuses on the minority class performance directly rather than being diluted by a large number of true negatives.

A common interview question: "Your dataset is 99% negative class. Why is accuracy a bad metric here?" Answer: a model that always predicts "negative" achieves 99% accuracy while being useless. Precision, recall, F1, or PR-AUC give a much more honest picture of performance on the minority class.
