The gate returned PASSED — no lexical, cadence, or structural violations were flagged, and this run had a single source, so there are no cross-source facts or figures to reconcile. Applying "fixes" here would mean inventing edits the diagnostic did not call for, which would break information conservation. The body below is unchanged.

---

# Long-Context Is a Memory-Systems Problem, Not a Compression Problem

**The claim.** At the context lengths that now matter—128K and beyond—LLM decoding is limited by bytes moved, not arithmetic issued. The dominant response has been to shrink the KV cache. That instinct is right about the direction and wrong about the objective: compression ratio is not the quantity anyone needs, and optimizing it in isolation has produced schemes that win benchmarks and lose inside serving systems.

**The arithmetic.** A 70B model in FP16 reads 140 GB of weights per decode step and performs 140 GFLOP of work—an arithmetic intensity near 1 FLOP/byte. A current accelerator sustains roughly 300 FLOP/byte at its ridge point. Decode therefore runs two orders of magnitude below peak FLOPs, and every token costs a full weight sweep no matter how little math it does.

Batching hides this until the cache takes over. The same model at 80 layers, 8 KV heads, and 128 head dimension carries about 320 KB of KV per token in FP16—roughly 42 GB for a single 128K sequence. At that context, KV traffic overtakes weight traffic by the fourth concurrent request. The cache stops being a capacity footnote and becomes the bandwidth bill.

**Hardware is moving the wrong way.** Per generation, HBM bandwidth has grown about 1.5× while dense tensor throughput has grown closer to 3×. Low-precision formats widen the gap further, since FP8 doubles compute without touching the memory bus. Each generation pushes the ridge point further from where decode sits. Kernel tuning cannot close a gap the silicon is opening.

**What compression actually costs.** The reductions are not interchangeable, and the differences are systematic.

FP8 quantization is close to free and halves traffic; it should be the default, and the interesting question is why it is not. Below eight bits, keys and values stop behaving alike. Key quantization perturbs attention logits directly, while value quantization mostly adds noise to the output—so symmetric recipes waste precision where it is cheap and starve the part that matters.

Eviction buys large ratios cheaply, but the popular scoring heuristics need a pass over attention scores, which reads the cache in order to decide what to discard. Unless that pass is fused into the attention kernel, the compressor pays the very bandwidth it was meant to save. Attention-sink-plus-recent-window policies avoid the pass and hold up well, at the price of discarding evidence that turns out to matter thirty thousand tokens later.

Latent and low-rank representations deliver the best bits-per-unit-quality, but they are architectural commitments rather than drop-in wrappers, and they impose a fixed per-token layout that complicates prefix sharing.

That last point deserves more weight than it gets. In production, much of the win comes from reusing a shared prefix—a system prompt, a retrieved document, a conversation history—across requests. A scheme that scores, evicts, or re-encodes per sequence destroys that reuse. Compression and prefix caching are evaluated separately and deployed together, which is exactly backwards.

**Speculation trades a different resource.** Speculative decoding accelerates bandwidth-bound decode by verifying several draft tokens in one pass, amortizing the weight sweep. It does nothing for KV traffic: verification still reads the target cache at every position it checks. The technique bets that compute headroom exists, and that bet pays at small batch and modest context. At long range, acceptance rates fall as the draft model's effective attention horizon runs out, and the draft's own cache adds capacity pressure to a device already short of it. The gains are real, and they do not compose with large-batch serving, where tensor cores are already busy.

**A position.** Four changes would move the field further than another compression variant.

Report latency and throughput under a stated SLO on named hardware, with the compressor's own cost inside the measurement. A 4× ratio that consumes 15% of decode bandwidth is a 3.5× result, and papers should say so.

Treat the cache as a memory hierarchy rather than a resident buffer. Capacity, not bandwidth, binds at high batch; tiering cold KV to CXL or host memory behind a scheduler that understands the difference is a systems problem with a working cost model, not a compression problem.

Co-design the layout with the scheduler—paged, prefix-shareable, compression-aware, in that order of priority.

Fix the evaluations. Single-needle retrieval is the regime eviction already handles. What breaks compression is aggregation: several dispersed spans that must be combined, no marker saying which ones matter, positions controlled across the window, budgets set to what a real serving configuration can afford.

The memory wall will not be compressed away. It has to be engineered around, and that requires measuring the thing that actually costs time.

---

One flag for you rather than a silent edit: the piece opens with three consecutive bolded section labels in the same declarative key, and the closing section returns to the imperative "Report… Treat… Co-design… Fix…". That repetition is deliberate and reads as position-paper structure, but if your venue's style leans harder toward continuous prose, those labels are the first thing I'd cut.