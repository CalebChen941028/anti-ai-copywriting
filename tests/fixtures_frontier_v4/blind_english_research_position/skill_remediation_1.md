# Treat the KV Cache as the System, Not the Workload

At 128k tokens the KV cache stops being a data structure. It becomes the machine. On an 8×H100 node — 640 GB of HBM3 — long-context traffic pushes the cache past 70% of total capacity, and every decoded token re-reads the whole thing. Arithmetic intensity collapses toward one FLOP per byte moved.

Call the memory wall what it is: an accounting failure. We optimized the quantity this workload no longer spends, then filed the one it does spend under implementation detail.

Three levers exist. Speculative decoding, KV quantization, cluster-level sharding. The field evaluates each in isolation, as though they were orthogonal. They are not. Each moves the operating point of the other two. This paper argues for a joint treatment, and for three changes in how results get reported.

## Claim 1. Speculation buys latency, not capacity.

A well-matched draft model cuts end-to-end token latency 2.4× and leaves the output distribution bitwise unchanged. Rejection sampling against the target's residual distribution makes the result exact, not approximate. That is the cleanest win on the board, because it costs nothing in quality.

Read the number carefully. Speculation converts a bandwidth-bound decode into a compute-denser verification step: γ draft tokens checked in one pass over the context, so the cache is read once per γ tokens rather than once per token. Acceptance rate α bounds the gain. The gain saturates as γ grows past the point where α^γ kills the tail.

None of that touches the resident footprint. The cache still occupies 448 GB. A node starved for capacity before speculation is starved after it. Publish (α, γ, bytes per accepted token) beside the latency figure, or 2.4× is uninterpretable.

## Claim 2. FP8 for keys. INT4 only with evidence.

Quantization goes at footprint directly. FP8 halves it against BF16; INT4 quarters it. The precision cost is asymmetric across the two tensors.

Keys enter softmax through q·k, and softmax exponentiates perturbation: a relative error in a key component becomes a multiplicative shift in attention weight. At 128k keys, the tail of that weight distribution is exactly where retrieval lives. Values get averaged under those weights, so their errors partly cancel.

FP8 (E4M3, per-tensor scaling) is close to lossless for keys in published evaluations. INT4 survives on values with per-channel scaling and outlier isolation. On keys it degrades needle-in-haystack and multi-hop retrieval well before perplexity moves — and perplexity is the wrong instrument at this length, since it averages across positions and hides exactly the tail long context exposes. Our position: FP8 as the default for both tensors, INT4 admitted for values only, gated on per-layer retrieval validation at the deployed context length.

The levers couple. Cheaper bytes per token lower the cost of each verification pass, which pushes the optimal γ upward; a longer γ raises acceptance pressure on the draft model. Tune them in sequence — quantize, then re-tune speculation — and you land on a worse point than tuning them together.

## Claim 3. The cluster is the memory hierarchy. Design it like one.

Tensor parallelism gives each GPU a shard of the KV heads, and attention over a long context forces an all-to-all exchange every layer. Once the cache spills past HBM, the bottleneck stops being HBM bandwidth (~3.35 TB/s per H100) and becomes NVLink (~900 GB/s bidirectional), then InfiniBand. A 4× drop, then two orders of magnitude. No amount of quantization recovers that.

So stop treating KV as a monolithic resident array. Tier it: hot blocks resident in HBM, warm blocks on NVLink peers, cold prefix blocks on NVMe with rehydration. Prefix caching across requests that share a system prompt is the highest-yield instance — a per-request cost becomes a one-time cost, and it composes cleanly with both other levers. Disaggregated prefill and decode carries the same idea across the fabric, at the price of making interconnect topology a first-class scheduling constraint instead of a deployment afterthought.

## What we ask of the field.

Report bytes per accepted token, not tokens per second alone. Validate quantization at the context length you deploy, on retrieval tasks, not at 4k on perplexity. Co-design draft length, cache precision, and shard topology as one search space, and state the α your latency number depends on.

The 2.4× is real. It is also a latency result cited as though it were a capacity result, and those are different walls. Long-context inference will be governed by the second one until we stop reporting the first as though it settles the question.