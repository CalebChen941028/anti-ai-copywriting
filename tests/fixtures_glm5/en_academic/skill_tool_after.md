**Memory Bandwidth and Latency Trade-offs in Speculative Decoding**

Speculative decoding attacks a core bottleneck of autoregressive LLM inference: every decoding step reads the full parameter set from HBM to emit one token. A lightweight draft model proposes *k* tokens; the target model then scores all of them in a single forward pass. One weight load now serves multiple tokens, which raises arithmetic intensity without changing the output distribution—rejected positions are resampled from the adjusted softmax, so the scheme stays lossless.

Everything hinges on the acceptance rate. Accepted drafts cut latency almost linearly in the number of tokens verified, because bandwidth, not FLOPs, dominates each step. Rejections do the opposite: they waste the draft model's serial decode steps and stretch the verification pass. Net speedup is expected accepted tokens per cycle divided by total cycle time; with poor acceptance—and a draft that is slow relative to the target—the ratio drops below one. KV-cache traffic makes matters worse: verification attends over *k* positions, and speculative states must be kept, then rolled back on rejection.

The optimal draft length therefore varies by task. Low-entropy, near-greedy generation tolerates long proposals; open-ended sampling calls for short ones. Newer designs fold drafting into the target itself—early-exit layers, self-drafting heads—trading extra parameters to remove the separate draft model's bandwidth cost and memory footprint.

*(~213 words)*