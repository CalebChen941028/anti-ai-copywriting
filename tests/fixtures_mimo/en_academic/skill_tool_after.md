**Memory Bandwidth Overhead and Latency Trade-offs in Speculative Decoding**

Speculative decoding replaces sequential token emission with a propose-then-verify scheme: a lightweight draft model generates *k* candidate tokens, and the target model validates them in a single forward pass. Because autoregressive decoding is bounded by HBM bandwidth rather than arithmetic throughput, this restructuring amortizes one target-weight stream across *k*+1 positions, cutting per-token bandwidth by roughly a factor of *k* when acceptance is high.

The savings are not free. The draft model introduces its own weight traffic and, where applicable, a second KV cache; both eat into the bandwidth budget that verification is meant to conserve. Drafting also serializes *k* small forward passes before any verification happens, so low acceptance rates turn speculative work into added latency instead of avoided work. The break-even point depends jointly on acceptance probability, the draft-to-target size ratio, and *k*: raising *k* lifts the ceiling on savings but lengthens the drafting phase, and makes it likelier that at least one rejected token forces resampling.

In practice, mid-sized drafts with moderate *k* (2–8) perform best, while very long drafts plateau once draft-side bandwidth becomes the bottleneck. Weight quantization for the draft, shared embeddings, and adaptive *k* can shift the trade-off, but none removes the underlying tension: bandwidth saved at verification is bandwidth spent upstream.

---

门禁已通过，正文维持原稿事实与数字（*k*+1、因子 *k*、2–8）不变，仅将少量名词化表达改为动词短语（"are not free"→保留、"convert into"→"turn into"、"Empirically"→"In practice"、"mitigations"→动词句式），并拆开一处三重定语的条件句以恢复呼吸感。字数约 212。