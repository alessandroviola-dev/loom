# LOOM — DFlash Block B7 Parity Diagnosis 001

Date: 2026-08-24
Classification: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001_FAIL_GATE`

Local evidence: `results-local/research/dflash-block-b7-parity-diag-001/20260824T110012Z/`

## Result

Controlled variants:
- A: sequential teacher-forced B7 reference;
- B: causal B7 block without union-coalesced MoE;
- C: current B7 union-coalesced path.

The first A/B and A/C divergence occurs immediately at layer 0, position 0, `post_attention_hidden`:
- max abs error: `1.4901161e-08`;
- mean abs error: `2.6425653e-09`.

At that boundary the KV K/V states are still bitwise exact.

Parity:
- A/B: FAIL;
- A/C: FAIL;
- B/C: PASS across all 336 layer/position/stage comparisons.

Therefore union-coalesced MoE is not the source of the B7 divergence. The root cause is the multi-position/block attention batching path. The tiny first-layer floating-point difference cascades through the 48-layer target; final A/B logits differ by max `0.021434784`, mean `0.001928339`.

Memory/ownership remained safe:
- swap delta: `0 MiB`;
- active growth: `0 B`;
- no routed-expert ownership or logical live-expert leak.

No repair was performed. DFlash integration remains blocked.

## Interpretation

This failure does not invalidate block expert-union amortization. B and C are bitwise identical, so the expert coalescing path preserves the block arithmetic it receives. The unresolved issue is specifically the batched attention execution at B7.

A direct tolerance relaxation is not promoted. The next experiment should avoid the numerically different B7 batched-attention kernel while preserving the expert-union advantage: process attention with canonical single-position (`q_len=1`) semantics inside each layer, then reuse each unique routed expert once across the block positions for that layer. This layer-wise wavefront ordering is the next correctness-preserving candidate.

Gate: `MULTI_POSITION_TARGET_VERIFICATION_FAIL`.
