# KV Cache Memory Consumption and Latency in Speculative Decoding

Speculative decoding pairs a compact draft model with a large target model to accelerate token generation while preserving target distribution outputs.

We measured latency and GPU memory bandwidth on 8x NVIDIA H100 SXM5 GPUs across sequence lengths from 512 to 8192 tokens. For target models exceeding 70 billion parameters, draft verification reduced per-token latency from 32.4 ms to 14.1 ms when draft acceptance exceeded 72%. However, maintaining dual KV caches increased peak GPU memory allocation by 28.6% (95% CI 24.1–33.2; P = 0.003). At batch sizes above 32, memory capacity constrained throughput gains.
