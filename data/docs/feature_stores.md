# Feature Stores

A feature store is a centralized system for storing, managing, and serving machine learning features consistently across training and inference. It solves a problem that plagues most ML teams once they have more than a couple of models in production: the same feature (e.g. "user's 7-day purchase count") gets computed slightly differently in the training pipeline versus the serving pipeline, causing silent accuracy degradation.

A feature store typically has two storage layers. The offline store (often a data warehouse or data lake, e.g. BigQuery, Snowflake, or Parquet on S3) holds large volumes of historical feature values used for training and batch scoring, optimized for throughput over latency. The online store (often Redis, DynamoDB, or a key-value store) holds the latest feature values for low-latency lookups during real-time inference, optimized for latency over throughput.

The core value proposition is consistency: the same feature transformation logic is defined once and used to populate both stores, eliminating training-serving skew caused by duplicated, drifting feature code between a data science notebook and a production service.

Feature stores also enable feature reuse and discovery across teams. Without one, it's common for five different teams to independently compute "average order value in the last 30 days" with five subtly different definitions, none of which agree during an incident post-mortem. A feature store with a shared registry (feature name, owner, freshness SLA, data type) turns features into a discoverable, governed asset instead of scattered pipeline code.

Point-in-time correctness is a critical, easy-to-get-wrong feature store capability: when constructing a training set, features must be retrieved as they existed at the time of each historical label, not their current values. Getting this wrong leaks future information into training data (label leakage) and produces a model that looks great offline and fails in production. Popular open-source and managed options include Feast, Tecton, and Databricks Feature Store.

A common interview question: "How would you detect that a feature store is causing training-serving skew?" Answer: log the feature values actually used at serving time alongside each prediction, then periodically compare their distribution to the same features computed offline for the same entities at the same timestamps. A systematic divergence points to a skew bug, not model degradation.
