"""
Golden evaluation set: hand-curated (query -> expected source doc)
pairs against the real knowledge base in data/docs/. This is the
regression baseline every future retrieval change gets checked against.
"""

GOLDEN_EVAL_SET = [
    {"query": "What is the bias-variance tradeoff?", "expected_source": "bias_variance.md"},
    {"query": "How do you diagnose high variance using learning curves?", "expected_source": "bias_variance.md"},
    {"query": "What is the difference between L1 and L2 regularization?", "expected_source": "regularization.md"},
    {"query": "Why does dropout help prevent overfitting?", "expected_source": "regularization.md"},
    {"query": "What is the time complexity of self-attention?", "expected_source": "transformer_attention.md"},
    {"query": "Why do transformers need positional encoding?", "expected_source": "transformer_attention.md"},
    {"query": "Why can Adam generalize worse than SGD with momentum?", "expected_source": "gradient_descent.md"},
    {"query": "What is the difference between batch and mini-batch gradient descent?", "expected_source": "gradient_descent.md"},
    {"query": "Why is accuracy a bad metric for imbalanced datasets?", "expected_source": "classification_metrics.md"},
    {"query": "When should you prefer PR-AUC over ROC-AUC?", "expected_source": "classification_metrics.md"},
]
