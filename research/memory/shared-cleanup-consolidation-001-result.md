# SHARED-CLEANUP-CONSOLIDATION 001 — Result

Date: 2026-08-22
Classification: `SHARED_CLEANUP_CONSOLIDATION_001_COMPLETE`
Interpretation: `SHARED_CLEANUP_COST_MATERIAL`

Raw evidence: `results-local/memory/shared-cleanup-consolidation-001/20260822-172422/`

Both arms used exact S1 residency: layers 0..34 persistent, layer 35 streamed, embedding/final norm/LM head persistent, 3,499,501,056 B persistent raw weights and 84,427,264 logical streamed B/token.

CONTROL retained post-embedding, layer-35, post-norm and post-head cleanup. TREATMENT changed only shared-stage cleanup cadence: post-embedding and post-norm cleanup were omitted/deferred while layer-35 cleanup and final post-head cleanup remained unchanged. Explicit `mx.eval` topology was identical.

Exact parity PASS for both arms, all four constituents and all three prompts. No resource aborts.

CONTROL pooled: 5.643 tok/s, 177.226 ms/token, E2E 5.047 tok/s, TTFT 1.336 s, peak MLX 3,537,250,032 B, min free 16%, peak swap 2179.44 MB.

TREATMENT pooled: 7.065 tok/s, 141.548 ms/token, E2E 6.206 tok/s, TTFT 1.228 s, peak MLX 3,537,250,032 B, min free 18%, peak swap 1918.62 MB.

Causal effect: generation +25.206%, E2E +22.960%, wall/token -35.678 ms (-20.131%), TTFT -8.080%, peak MLX delta 0 B. The removed wall is ~58.22% of the prior descriptive ~61.284 ms fixed stream-activation term; this comparison is contextual only.

Conclusion: shared-stage cleanup cadence is causally a material component of S1 fixed streaming-activation overhead. The result does not attribute saved time to any specific internal subsystem. Physical SSD traffic remains unproven.

Next: isolate one explicit shared-stage `mx.eval` boundary while preserving successful cleanup consolidation, exact S1 residency and model math.
