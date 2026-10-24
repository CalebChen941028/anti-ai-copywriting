# Beyond the Memory Wall: A Co-Design Agenda for Long-Context LLM Inference

**Position paper**

Long-context LLM inference is no longer a compute-only problem. It is a memory-system problem. Systems that treat the KV cache as an unbounded per-request artifact and rely on speculative decoding as a universal latency fix will hit diminishing returns. The path forward is co-designed memory management, accuracy-aware KV compression, and adaptive speculation under explicit bandwidth budgets.

## Memory bandwidth versus compute scaling

Autoregressive decode exposes the imbalance between compute and memory scaling. Each generated token requires reading model weights and the KV cache, while tensor cores can execute far more arithmetic than HBM can feed. At small batch sizes, decode arithmetic intensity is low; at long context lengths, KV-cache reads dominate weight reads. Prefill remains comparatively compute-bound and parallel, but decode is serial, latency-sensitive, and bandwidth-limited. Capacity and bandwidth are distinct constraints: capacity limits context length and batch size, while bandwidth limits token latency and sustained throughput.

Paged attention and KV paging address fragmentation and capacity, not the underlying byte traffic. Offloading KV blocks to host memory or remote storage converts an HBM bottleneck into an interconnect bottleneck and adds tail latency. Larger batches improve arithmetic intensity but increase KV-cache capacity pressure and can violate latency SLOs. The correct systems abstraction is a bandwidth budget per decode step, with scheduling decisions based on KV bytes, attention sparsity, and batch composition rather than nominal FLOPs alone.

## KV-cache compression trade-offs

KV compression is necessary, but no single policy is universally safe. Quantization reduces both capacity and bandwidth; 4-bit KV caches can be robust with group-wise scales and outlier handling, yet long-tail attention channels and retrieval-sensitive tasks remain vulnerable. Low-rank and latent KV representations reduce bytes when the KV subspace is genuinely low-dimensional, but they can degrade multi-hop reasoning and exact recall. Eviction and sparsity exploit attention locality, but fixed eviction policies can discard tokens that later become relevant. Recomputation trades bandwidth for compute and latency, which is unattractive when decode is already latency-bound.

Compression must be accuracy-aware and workload-specific. A practical design uses hybrid storage: high-fidelity paged KV for recent or high-attention tokens, quantized or low-rank representations for older history, and retrieval or summarization for archival context. Each tier needs an explicit error budget and fallback path. Evaluation must move beyond perplexity to long-context tasks such as needle-in-a-haystack, multi-document reasoning, and exact citation, with tail-latency and bandwidth-counter measurements.

## Speculative decoding trade-offs

Speculative decoding reduces the number of sequential target-model passes by drafting multiple tokens and verifying them in parallel. Its benefit depends on acceptance rate, draft cost, verification overhead, and batch regime. In low-batch, latency-critical decode, speculation can improve time per token. In high-batch throughput-oriented serving, the target GPU may already be saturated; extra draft computation and KV traffic can reduce goodput. At long contexts, the draft model must also attend to the same history, and duplicated or poorly shared KV caches can erase the bandwidth savings.

Speculation should therefore be adaptive. The serving system should monitor acceptance rate, draft length, batch size, context length, and memory-bandwidth utilization, then enable or disable speculation per request class. Tree speculation can raise acceptance but increases verification compute. Shared compressed KV between draft and target models is essential for long-context efficiency.

## Recommendations

Treat HBM bandwidth as a first-class SLO and schedule decode by KV-byte traffic. Expose the KV cache as a multi-tier object with paging, quantization, eviction, and retrieval backed by per-workload accuracy contracts. Make speculation a controlled policy rather than a default. Disaggregate prefill and decode where it reduces interference, and route contexts to avoid recomputation. Benchmark long-context accuracy, bandwidth counters, and tail latency alongside tokens per second. The memory wall will not be solved by one compression trick; it requires co-design across models, caches, schedulers, and hardware.