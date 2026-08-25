# LOOM DFlash Full-Logit Reference Parity 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`
Classification: `FULL_LOGIT_REFERENCE_PARITY_PASS`
Gate: `PASS`

## Purpose

Determine whether the remaining DFlash mismatch is caused by a material numerical divergence in the MLX drafter port or is already present when the authoritative publisher/reference drafter consumes the same frozen inputs.

## Population

Deterministic stratified subset: best and worst corrected target-rank state from each frozen trajectory P1/P2/P3.

| Stratum | State | Correct target rank | Max abs | Mean abs | RMSE | Rel-L2 | Cosine |
|---|---|---:|---:|---:|---:|---:|---:|
| P1 best | `P1_t32:6` | 3 | 0.007463 | 0.001219 | 0.001528 | 0.000652 | 0.999999808 |
| P1 worst | `P1_t16:4` | 2890 | 0.004254 | 0.000790 | 0.000994 | 0.000412 | 0.999999915 |
| P2 best | `P2_t16:3` | 3 | 0.003529 | 0.000666 | 0.000834 | 0.000382 | 0.999999932 |
| P2 worst | `P2_t01:4` | 3510 | 0.008128 | 0.001637 | 0.002045 | 0.001059 | 0.999999487 |
| P3 best | `P3_t01:2` | 2 | 0.007325 | 0.001438 | 0.001788 | 0.000923 | 0.999999619 |
| P3 worst | `P3_t01:4` | 1645 | 0.009598 | 0.002038 | 0.002529 | 0.001375 | 0.999999164 |

## Parity gates

- Input/tap/position/mask hashes identical for all 6 states.
- Full 32,000-dimensional drafter-logit vectors compared before target-token decode.
- Draft-row argmax exact parity: `6/6`.
- Top-5 ordered parity: `6/6`.
- Top-10 ordered parity: `6/6`.
- Top-50 row sets identical: `6/6`; only minor ordering swaps inside the tolerated numerical delta.
- Corrected `row + d2t[row]` target-token decode parity: `6/6`.
- Established numerical gates passed for every state: max absolute error <= `0.025`, mean absolute error <= `0.004`.

Full float32 vectors are not bitwise identical. The earliest non-bitwise differences begin at fusion, but they remain small and do not materially alter the output distribution or selected proposal rows on the tested states.

## Scientific interpretation

The MLX DFlash port is exonerated as the remaining practical explanation on this stratified subset. Both near-target and very-poor-rank examples reproduce the authoritative reference distribution to extremely high cosine similarity and identical decision-level argmax/top-k behavior.

Therefore the residual frozen mismatch must be investigated upstream of the drafter implementation itself: verifier/hidden-state provenance, target revision, exact tap extraction/interface semantics, or genuine candidate/training-distribution behavior.

This result does not prove that every possible state is numerically identical, but it strongly rejects a material MLX-port divergence as the mechanism producing the observed `0/63` corrected top-1 compatibility.

## External provenance observation

The published model card names `Qwen/Qwen3-30B-A3B` as verifier/base model and uses target layers `1 12 23 34 45` for vLLM data generation/training, but the documented commands do not pin a verifier revision. The exact historical verifier/tap runtime provenance therefore remains a live upstream-interface question.

## Next checkpoint

`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

Static audit first. Recover the strongest possible historical verifier revision/runtime provenance and prove whether the local frozen tap contract matches publisher training semantics before any further model execution.

Evidence:
`results-local/research/dflash-full-logit-reference-parity-001/20260825T102523Z/`
