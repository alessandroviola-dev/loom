# LOOM DFlash B7 Wavefront Verifier 001 — Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`

## Result

The B7 target verifier now preserves canonical single-position (`q_len=1`) attention/KV semantics while executing layer-by-layer across seven candidate positions and reusing each unique routed expert across the positions assigned to it.

Correctness gate:
- all layer hidden states bitwise exact vs sequential teacher-forced reference;
- router IDs and weights bitwise exact;
- KV bitwise exact;
- final logits bitwise exact;
- token decisions bitwise exact;
- first divergence: none.

External-expert union:
- 1,205 unique `(layer, expert)` instances across B7;
- 172.14 unique expert instances per verified position;
- 431,519,451 B useful external expert bytes per verified position.

Timing:
- sequential B7: 10.8152 s;
- wavefront B7: 6.5430 s;
- speedup: 1.653x.

Memory / ownership:
- peak MLX: 985,002,536 B;
- peak RSS: 1,003,978,752 B;
- swap delta: 0 MiB;
- memory pressure: PASS;
- routed-expert ownership: PASS, zero leak.

Raw evidence:
`results-local/research/dflash-b7-wavefront-verifier-001/20260824T111511Z/`

Local script:
`scripts/loom_30b_moe_dflash_b7_wavefront_verifier_001.py`

## Interpretation

This closes the second target-side prerequisite for DFlash. The earlier B7 failure was caused by numerically different batched-attention execution, not expert union/coalescing. The wavefront schedule preserves the canonical sequential attention/KV arithmetic while retaining material expert-I/O amortization.

The learned DFlash drafter has still not been ported or executed. Therefore DFlash integration remains conditional on a minimal exact-target drafter implementation/parity checkpoint before any speculative-generation performance claim.
