# Transformer Self-Attention

Self-attention lets each token in a sequence attend to every other token, weighting their contributions when building that token's new representation. This solves the long-range dependency problem that plagued RNNs, since attention operates in constant path length between any two positions regardless of distance.

Each token is projected into three vectors: Query (Q), Key (K), and Value (V), via learned linear transformations. Attention scores are computed as the dot product of a token's Query with every other token's Key, scaled by the square root of the key dimension (to prevent extremely large dot products from pushing softmax into saturated regions), then passed through softmax to get attention weights. The output is the weighted sum of Value vectors using those weights.

Multi-Head Attention runs several attention operations in parallel, each with its own learned Q/K/V projections, allowing the model to jointly attend to information from different representation subspaces (e.g., one head might capture syntactic relationships, another might capture coreference). The outputs of all heads are concatenated and linearly projected back to the model dimension.

Positional Encoding is added to token embeddings before attention because self-attention itself is permutation-invariant and has no inherent sense of token order. Original Transformers used fixed sinusoidal encodings; many modern models use learned or relative positional encodings (e.g., RoPE - Rotary Position Embeddings) instead.

Causal (masked) self-attention, used in decoder-only models like GPT, prevents a token from attending to future tokens by masking out upper-triangular attention scores before softmax, which is what enables autoregressive generation.

A common interview question: "What is the time complexity of self-attention with respect to sequence length, and why is that a problem?" Answer: O(n^2) with respect to sequence length n, because every token attends to every other token. This makes very long sequences expensive, which is why techniques like sparse attention, sliding window attention, and linear attention approximations exist.
