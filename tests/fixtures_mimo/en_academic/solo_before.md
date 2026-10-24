# Memory Bandwidth Overhead and Latency Trade-offs in Speculative Decoding for Large Language Models

**Abstract**

Speculative decoding accelerates autoregressive generation by employing a lightweight draft model to propose multiple tokens simultaneously, which a larger target model then verifies in parallel. While this paradigm reduces the number of sequential forward passes, it introduces a critical tension between memory bandwidth consumption and end-to-end latency.

The primary overhead stems from frequent weight loading during draft verification. Although parallel verification amortizes latency across multiple tokens, each pass requires streaming the target model's parameters from device memory to compute units. When the draft model's acceptance rate is low, wasted computation inflates effective memory bandwidth costs without proportional throughput gains. Conversely, high acceptance rates amortize bandwidth overhead, yielding net latency reductions. The trade-off is further modulated by target model size: larger models benefit more from verification batching but also impose steeper bandwidth demands per pass.

Empirically, optimal deployment requires balancing draft length and model capacity against available memory bandwidth. Techniques such as adaptive early exit and cache-aware token reordering can mitigate bandwidth pressure while preserving acceptance rates. Future work should formalize the interaction between bandwidth saturation and speculative savings, particularly for heterogeneous hardware where memory hierarchies differ.

**Keywords:** speculative decoding, memory bandwidth, latency, large language models, autoregressive generation