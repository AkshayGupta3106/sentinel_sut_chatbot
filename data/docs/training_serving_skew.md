# Training-Serving Skew

Training-serving skew is the gap between a model's performance during offline evaluation and its actual performance in production, caused by differences between how data is processed at training time versus at serving time. It is one of the most common and most silent failure modes in deployed ML systems, because the model doesn't crash — it just quietly gets worse.

The most frequent cause is duplicated feature logic: a data scientist writes feature transformations in a Python notebook using pandas for training, while a separate engineering team reimplements the same logic in Java or Go for the low-latency serving path. Any subtle difference (rounding, timezone handling, null-value defaults, a slightly different lookback window) creates skew that offline metrics never catch, since offline evaluation uses the training-side implementation by definition.

A second common cause is temporal skew: training data reflects the world as it was weeks or months ago, while serving requests reflect the world right now. If the underlying data distribution has shifted (new product categories, seasonal behavior, a UI redesign changing click patterns), the model faces inputs it never effectively saw in a representative way during training, even though no bug exists in either pipeline.

A third cause is sampling skew: training data is often filtered or resampled (e.g., balancing classes, removing outliers, deduplication) in ways that don't match the raw, messy distribution of real-time production traffic. A model trained on a carefully cleaned dataset can behave unpredictably on the noisy inputs it actually receives in production.

The standard mitigation is to unify the feature computation path — using a feature store (see feature_stores.md) or a shared feature transformation library invoked identically by both the training pipeline and the serving service, ideally in the same language and same code path, not reimplemented twice.

A common interview question: "Your model's offline AUC is 0.91 but online conversion metrics didn't move at all. How do you debug this?" Answer: first rule out a serving bug entirely unrelated to skew (is the model even receiving the traffic, is the endpoint healthy). Then compare the feature vectors logged at serving time against what the offline pipeline would have computed for the same raw inputs — a mismatch here is the classic skew signature, and it should be checked before assuming the online audience is simply different from the offline evaluation set.
