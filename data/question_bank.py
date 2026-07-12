"""
Question bank: ~100 questions spanning basic -> advanced difficulty
across all 15 knowledge-base topics. Each question is tagged with its
expected source doc, so running the whole bank doubles as a large-
scale retrieval quality check (not just a 10-question golden set).

Used by ask_question_bank.py to generate realistic traffic volume for
the observability platform to actually have something to observe.
"""

QUESTION_BANK = [
    # --- bias_variance.md ---
    {"question": "What is the bias-variance tradeoff?", "topic": "bias_variance", "difficulty": "basic"},
    {"question": "What does high bias mean in a machine learning model?", "topic": "bias_variance", "difficulty": "basic"},
    {"question": "What is an example of a high-bias model?", "topic": "bias_variance", "difficulty": "basic"},
    {"question": "How does model complexity affect bias and variance?", "topic": "bias_variance", "difficulty": "intermediate"},
    {"question": "What regularization techniques help manage the bias-variance tradeoff?", "topic": "bias_variance", "difficulty": "intermediate"},
    {"question": "How do you diagnose whether a model suffers from high bias or high variance using learning curves?", "topic": "bias_variance", "difficulty": "advanced"},
    {"question": "How does bagging reduce variance while boosting reduces bias?", "topic": "bias_variance", "difficulty": "advanced"},

    # --- gradient_descent.md ---
    {"question": "What is stochastic gradient descent?", "topic": "gradient_descent", "difficulty": "basic"},
    {"question": "What is the difference between batch and mini-batch gradient descent?", "topic": "gradient_descent", "difficulty": "basic"},
    {"question": "Why is mini-batch gradient descent the most commonly used variant in deep learning?", "topic": "gradient_descent", "difficulty": "basic"},
    {"question": "How does momentum help gradient descent converge faster?", "topic": "gradient_descent", "difficulty": "intermediate"},
    {"question": "What makes Adam different from plain SGD?", "topic": "gradient_descent", "difficulty": "intermediate"},
    {"question": "Why might Adam generalize worse than SGD with momentum on some tasks?", "topic": "gradient_descent", "difficulty": "advanced"},
    {"question": "How do adaptive optimizers like RMSprop adjust the learning rate per parameter?", "topic": "gradient_descent", "difficulty": "advanced"},

    # --- classification_metrics.md ---
    {"question": "What is precision in classification?", "topic": "classification_metrics", "difficulty": "basic"},
    {"question": "What is recall in classification?", "topic": "classification_metrics", "difficulty": "basic"},
    {"question": "What is the F1 score?", "topic": "classification_metrics", "difficulty": "basic"},
    {"question": "Why is accuracy a bad metric for imbalanced datasets?", "topic": "classification_metrics", "difficulty": "intermediate"},
    {"question": "What is the difference between ROC-AUC and PR-AUC?", "topic": "classification_metrics", "difficulty": "intermediate"},
    {"question": "When should you prefer PR-AUC over ROC-AUC?", "topic": "classification_metrics", "difficulty": "advanced"},
    {"question": "How would you choose between optimizing for precision versus recall in a fraud detection system?", "topic": "classification_metrics", "difficulty": "advanced"},

    # --- regularization.md ---
    {"question": "What is L2 regularization?", "topic": "regularization", "difficulty": "basic"},
    {"question": "What is L1 regularization?", "topic": "regularization", "difficulty": "basic"},
    {"question": "What problem does regularization solve?", "topic": "regularization", "difficulty": "basic"},
    {"question": "Why does L1 regularization produce sparse solutions but L2 doesn't?", "topic": "regularization", "difficulty": "intermediate"},
    {"question": "What is Elastic Net regularization?", "topic": "regularization", "difficulty": "intermediate"},
    {"question": "How does dropout act as a regularizer in neural networks?", "topic": "regularization", "difficulty": "advanced"},
    {"question": "When would you prefer Elastic Net over pure Lasso regularization?", "topic": "regularization", "difficulty": "advanced"},

    # --- transformer_attention.md ---
    {"question": "What is self-attention in transformers?", "topic": "transformer_attention", "difficulty": "basic"},
    {"question": "What are Query, Key, and Value vectors in attention?", "topic": "transformer_attention", "difficulty": "basic"},
    {"question": "Why is scaling used in scaled dot-product attention?", "topic": "transformer_attention", "difficulty": "basic"},
    {"question": "What is multi-head attention and why is it useful?", "topic": "transformer_attention", "difficulty": "intermediate"},
    {"question": "Why do transformers need positional encoding?", "topic": "transformer_attention", "difficulty": "intermediate"},
    {"question": "What is the time complexity of self-attention with respect to sequence length?", "topic": "transformer_attention", "difficulty": "advanced"},
    {"question": "How does causal masking enable autoregressive generation in decoder-only models?", "topic": "transformer_attention", "difficulty": "advanced"},

    # --- feature_stores.md ---
    {"question": "What is a feature store?", "topic": "feature_stores", "difficulty": "basic"},
    {"question": "What is the difference between an online store and an offline store in a feature store?", "topic": "feature_stores", "difficulty": "basic"},
    {"question": "Name two popular feature store tools.", "topic": "feature_stores", "difficulty": "basic"},
    {"question": "How do feature stores prevent training-serving skew?", "topic": "feature_stores", "difficulty": "intermediate"},
    {"question": "What is point-in-time correctness in a feature store?", "topic": "feature_stores", "difficulty": "intermediate"},
    {"question": "How would you detect that a feature store is causing training-serving skew?", "topic": "feature_stores", "difficulty": "advanced"},
    {"question": "What is label leakage and how does point-in-time correctness prevent it?", "topic": "feature_stores", "difficulty": "advanced"},

    # --- training_serving_skew.md ---
    {"question": "What is training-serving skew?", "topic": "training_serving_skew", "difficulty": "basic"},
    {"question": "What causes training-serving skew?", "topic": "training_serving_skew", "difficulty": "basic"},
    {"question": "How does temporal skew differ from sampling skew?", "topic": "training_serving_skew", "difficulty": "intermediate"},
    {"question": "What is the standard mitigation for training-serving skew?", "topic": "training_serving_skew", "difficulty": "intermediate"},
    {"question": "Your model's offline AUC is high but online conversion metrics didn't move. How do you debug this?", "topic": "training_serving_skew", "difficulty": "advanced"},
    {"question": "Why doesn't offline evaluation catch feature computation bugs caused by duplicated pipeline logic?", "topic": "training_serving_skew", "difficulty": "advanced"},

    # --- data_drift_monitoring.md ---
    {"question": "What is data drift?", "topic": "data_drift_monitoring", "difficulty": "basic"},
    {"question": "What statistical test is commonly used to detect drift in categorical features?", "topic": "data_drift_monitoring", "difficulty": "basic"},
    {"question": "What is the difference between covariate shift and concept drift?", "topic": "data_drift_monitoring", "difficulty": "intermediate"},
    {"question": "What is Population Stability Index (PSI) used for?", "topic": "data_drift_monitoring", "difficulty": "intermediate"},
    {"question": "What PSI value typically indicates significant drift?", "topic": "data_drift_monitoring", "difficulty": "intermediate"},
    {"question": "How do you monitor model quality when ground truth labels are delayed by 30 days?", "topic": "data_drift_monitoring", "difficulty": "advanced"},
    {"question": "What are the four layers a production monitoring dashboard typically tracks?", "topic": "data_drift_monitoring", "difficulty": "advanced"},

    # --- batch_vs_online_prediction.md ---
    {"question": "What is the difference between batch and online prediction?", "topic": "batch_vs_online_prediction", "difficulty": "basic"},
    {"question": "When is batch prediction the right choice?", "topic": "batch_vs_online_prediction", "difficulty": "basic"},
    {"question": "When is online prediction required instead of batch?", "topic": "batch_vs_online_prediction", "difficulty": "intermediate"},
    {"question": "What is a hybrid batch-online prediction pattern?", "topic": "batch_vs_online_prediction", "difficulty": "intermediate"},
    {"question": "Design a product recommendation system for an e-commerce homepage: would you use batch or online prediction?", "topic": "batch_vs_online_prediction", "difficulty": "advanced"},
    {"question": "What is the staleness risk tradeoff in batch prediction?", "topic": "batch_vs_online_prediction", "difficulty": "advanced"},

    # --- ab_testing_deployment.md ---
    {"question": "What is a canary deployment?", "topic": "ab_testing_deployment", "difficulty": "basic"},
    {"question": "What is shadow deployment?", "topic": "ab_testing_deployment", "difficulty": "basic"},
    {"question": "What are feature flags used for in ML deployment?", "topic": "ab_testing_deployment", "difficulty": "basic"},
    {"question": "How does canary deployment differ from shadow deployment?", "topic": "ab_testing_deployment", "difficulty": "intermediate"},
    {"question": "What is the multiple comparisons problem in A/B testing?", "topic": "ab_testing_deployment", "difficulty": "intermediate"},
    {"question": "Your canary at 5% traffic shows a 2% CTR improvement but it's not statistically significant yet. What do you do?", "topic": "ab_testing_deployment", "difficulty": "advanced"},
    {"question": "Why do network effects violate the independence assumption in A/B testing?", "topic": "ab_testing_deployment", "difficulty": "advanced"},

    # --- model_compression.md ---
    {"question": "What is quantization in the context of model compression?", "topic": "model_compression", "difficulty": "basic"},
    {"question": "What is pruning?", "topic": "model_compression", "difficulty": "basic"},
    {"question": "What is the difference between structured and unstructured pruning?", "topic": "model_compression", "difficulty": "intermediate"},
    {"question": "What is knowledge distillation?", "topic": "model_compression", "difficulty": "intermediate"},
    {"question": "How does low-rank factorization relate to LoRA fine-tuning?", "topic": "model_compression", "difficulty": "advanced"},
    {"question": "You need to deploy a model on a mobile device with a strict 50MB size limit and 100ms latency budget. Walk through your approach.", "topic": "model_compression", "difficulty": "advanced"},

    # --- continual_learning.md ---
    {"question": "What is continual learning?", "topic": "continual_learning", "difficulty": "basic"},
    {"question": "What is catastrophic forgetting?", "topic": "continual_learning", "difficulty": "basic"},
    {"question": "What is rehearsal as a mitigation for catastrophic forgetting?", "topic": "continual_learning", "difficulty": "intermediate"},
    {"question": "What is Elastic Weight Consolidation?", "topic": "continual_learning", "difficulty": "intermediate"},
    {"question": "Why not retrain your model every time new labeled data arrives instead of on a fixed schedule?", "topic": "continual_learning", "difficulty": "advanced"},
    {"question": "How does online evaluation differ for a continually updating model?", "topic": "continual_learning", "difficulty": "advanced"},

    # --- data_engineering_fundamentals.md ---
    {"question": "What is the difference between ETL and ELT?", "topic": "data_engineering_fundamentals", "difficulty": "basic"},
    {"question": "What is the difference between structured, semi-structured, and unstructured data?", "topic": "data_engineering_fundamentals", "difficulty": "basic"},
    {"question": "When would you use stream processing instead of batch processing?", "topic": "data_engineering_fundamentals", "difficulty": "intermediate"},
    {"question": "What does data validation and schema enforcement protect against?", "topic": "data_engineering_fundamentals", "difficulty": "intermediate"},
    {"question": "Your daily data ingestion job succeeded but the model's offline metrics tanked. What do you check first?", "topic": "data_engineering_fundamentals", "difficulty": "advanced"},
    {"question": "Why is ELT more flexible than ETL for modern cloud data warehouses?", "topic": "data_engineering_fundamentals", "difficulty": "advanced"},

    # --- embeddings_vector_search.md ---
    {"question": "What is an embedding?", "topic": "embeddings_vector_search", "difficulty": "basic"},
    {"question": "What distance metric is commonly used to measure embedding similarity?", "topic": "embeddings_vector_search", "difficulty": "basic"},
    {"question": "What is Approximate Nearest Neighbor (ANN) search?", "topic": "embeddings_vector_search", "difficulty": "basic"},
    {"question": "What is HNSW and why is it commonly used in vector databases?", "topic": "embeddings_vector_search", "difficulty": "intermediate"},
    {"question": "What is hybrid search in retrieval-augmented generation?", "topic": "embeddings_vector_search", "difficulty": "intermediate"},
    {"question": "Your RAG system's retrieval quality dropped after switching to a cheaper embedding model. How do you confirm this is the cause?", "topic": "embeddings_vector_search", "difficulty": "advanced"},
    {"question": "What are the tradeoffs of different chunking strategies in RAG?", "topic": "embeddings_vector_search", "difficulty": "advanced"},

    # --- mlops_ci_cd.md ---
    {"question": "What is MLOps?", "topic": "mlops_ci_cd", "difficulty": "basic"},
    {"question": "How does ML CI/CD differ from traditional software CI/CD?", "topic": "mlops_ci_cd", "difficulty": "basic"},
    {"question": "What is model versioning and why is Git alone insufficient for it?", "topic": "mlops_ci_cd", "difficulty": "intermediate"},
    {"question": "What makes ML reproducibility harder than traditional software reproducibility?", "topic": "mlops_ci_cd", "difficulty": "intermediate"},
    {"question": "How is testing a machine learning system fundamentally different from testing traditional software?", "topic": "mlops_ci_cd", "difficulty": "advanced"},
    {"question": "Why should automated rollback triggers watch business metrics rather than just infrastructure health checks?", "topic": "mlops_ci_cd", "difficulty": "advanced"},
]

TOPIC_TO_SOURCE_FILE = {
    "bias_variance": "bias_variance.md",
    "gradient_descent": "gradient_descent.md",
    "classification_metrics": "classification_metrics.md",
    "regularization": "regularization.md",
    "transformer_attention": "transformer_attention.md",
    "feature_stores": "feature_stores.md",
    "training_serving_skew": "training_serving_skew.md",
    "data_drift_monitoring": "data_drift_monitoring.md",
    "batch_vs_online_prediction": "batch_vs_online_prediction.md",
    "ab_testing_deployment": "ab_testing_deployment.md",
    "model_compression": "model_compression.md",
    "continual_learning": "continual_learning.md",
    "data_engineering_fundamentals": "data_engineering_fundamentals.md",
    "embeddings_vector_search": "embeddings_vector_search.md",
    "mlops_ci_cd": "mlops_ci_cd.md",
}
