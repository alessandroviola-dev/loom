# LOOM — DFlash Block Verifier 001 Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_BLOCK_VERIFIER_001_FAIL_GATE`
Raw evidence: `results-local/research/dflash-block-verifier-001/20260824T103943Z/`

## Result

The target-only multi-position verifier is exact for B2 and B4, but the preregistered B7 gate fails.

- B2 parity: PASS.
- B4 parity: PASS.
- B7: token decisions and selected router IDs pass, but logits, router logits and BF16 KV are not bitwise identical to sequential teacher-forced verification.
- B7 max final-logit difference: 0.0214348.
- B7 max router-logit difference: 0.00273609.
- B7 KV advances to the correct length 50 but differs bitwise.

Memory/ownership remain safe:
- peak MLX: 960,393,224 B;
- sampled RSS: 758,333,440 B;
- swap delta: 0 MiB;
- zero routed-expert leak.

Measured routing-union geometry / useful bytes per verified position:
- B2: 661 unique experts; 828,481,536 B/position;
- B4: 978; 612,900,864 B/position;
- B7: 1,264; 452,647,790 B/position.

Sequential vs block wall:
- B2: 3.187 vs 2.825 s;
- B4: 5.898 vs 4.414 s;
- B7: 9.927 vs 6.317 s.

## Interpretation

The block approach is not rejected structurally: exact B2/B4 verification, safe residency, and material B7 union/wall reduction are all established. However B7 is the critical DFlash proposal length and its numerical divergence prevents drafter integration.

Do not relax the correctness gate merely because token decisions match. First isolate whether the divergence originates in batched causal attention/KV semantics or in union-coalesced MoE/expert execution/arithmetic ordering.

## Decision

DFlash port: NO.

Next checkpoint: `LOOM_DFLASH_BLOCK_B7_PARITY_DIAG_001`.
