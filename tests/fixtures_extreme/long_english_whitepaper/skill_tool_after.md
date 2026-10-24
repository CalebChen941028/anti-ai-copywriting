# Bandwidth, Not FLOPs: A Position on Long-Context LLM Inference

A 70B model at 128K context holds roughly 40 GB of KV cache per sequence in FP16 — about 320 KB per generated token. Its weights occupy 140 GB. Batch 128 sequences and the weights amortize to roughly 1 GB per sequence per decode step; the cache still demands 40. Long-context inference is a bandwidth problem, and most of the field's optimizations still target the wrong resource.

## The gap is structural

Per-generation HBM bandwidth has grown about 1.6–2×, while dense FP16 throughput has grown closer to 3×. The roofline ridge point on a current accelerator sits near 200–300 FLOP/byte. Decode at batch size B has an arithmetic intensity of roughly B FLOP/byte once the KV term is ignored — two orders of magnitude below the ridge at B = 1. Large batches close that gap only while context stays short. Long context reopens it: KV traffic scales with batch × context length, weight traffic with batch alone. Push batch size up far enough and the cache, not the weights, becomes the quantity you are amortizing.

Prefill is a different animal. Quadratic attention over a long prompt is genuinely compute-bound and rewards every FLOP-efficiency trick. Decode does not. Conflating the two phases produces kernels and schedulers that help the wrong half of the serving loop.

## Compression trades are real and under-reported

Four families dominate, and each pays in a currency its papers rarely price.

Eviction keeps attention sinks and heavy hitters, drops the rest. The savings are large and cheap to obtain, but eviction is irreversible: a token discarded at step 200 is gone at step 2,000, and the error compounds autoregressively. Needle-in-haystack scores conceal this, because retrieving one planted sentence is not the same workload as multi-document reasoning across a 100K-token corpus.

Quantization is more forgiving than its reputation. Keys carry channel-wise outliers and need per-channel scaling; values tolerate per-token quantization. Four bits is close to lossless on most benchmarks, two bits is not — and the dequantization cost must be fused into the attention kernel, or the bandwidth savings evaporate into extra instructions.

Architectural approaches — latent caches, cross-layer sharing, aggressive GQA — cut bytes per token by an order of magnitude and are the only family that changes the asymptotics. They also require pretraining, which is why they lose to post-hoc tricks in short papers.

Offloading does not reduce bytes; it relocates them. PCIe delivers roughly 64 GB/s against multi-terabyte HBM. Per-token migration is viable only when the prefetch predictor is right almost every time.

## Speculation competes for the same resource

Speculative decoding works because decode is memory-bound: verifying γ draft tokens plus one costs a single pass over the weights. Expected accepted tokens per step is (1 − α^(γ+1))/(1 − α), and realized speedup divides that by the draft overhead. The arithmetic is unforgiving. Low acceptance rates and long draft chains both collapse the return.

Long context breaks the usual accounting. The draft model needs its own cache or must share the target's, and verification runs attention over the full KV for γ + 1 query positions. Draft trees improve acceptance and multiply the cache footprint. Most important, compression and speculation are substitutes. Every byte saved per token by a 4-bit cache or a latent representation is headroom speculation can no longer exploit. Raising batch size has the same effect, for the same reason: all three push the workload toward the ridge point, and whichever gets there first wins.

## What we should do instead

Report end-to-end throughput and latency at fixed task quality on contexts of 64K tokens or more, with dependencies that span the window. Compression ratios, acceptance rates, and FLOP utilization are intermediate quantities; publishing them as headline results invites optimizations that do not survive contact with a serving stack.

Disaggregate prefill and decode onto separate pools. The two phases have opposite bottlenecks, and co-locating them forces one to run at the other's efficiency.

Treat bytes moved per accepted token as the objective function. Architecture-level reduction, KV-aware scheduling, and speculation should be co-tuned against that single number rather than evaluated in isolation, where each looks better than it is.

The memory wall will not be climbed by making arithmetic faster. It will be climbed by moving fewer bytes, and by spending the bandwidth we have on tokens the model actually keeps.

---

质检门禁已通过，本轮仅做句读层面的微调，无被拦截项需要剔除；所有数字（40 GB / 320 KB / 140 GB / 128 / 1.6–2× / 3× / 200–300 FLOP/byte / 64 GB/s / γ + 1）与原文严格一致，未增删事实。