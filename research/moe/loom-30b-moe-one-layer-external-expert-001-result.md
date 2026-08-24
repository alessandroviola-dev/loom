# LOOM 30B MoE — One-Layer External Expert 001 Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`
Run ID: `20260824T070045Z`

## Result

A real Qwen3-30B-A3B MLX decoder layer executed bitwise-identically to a canonical control while routed experts remained external and only one selected packed expert was live at a time.

Canonical runtime components recovered from `mlx_lm.models.qwen3_moe` and `switch_layers`: `Attention`, `Qwen3MoeSparseMoeBlock`, `Qwen3MoeDecoderLayer`, `SwitchGLU`, `QuantizedSwitchLinear`, `gather_qmm`.

## Correctness

Deterministic float16 inputs:
- T1: `[1,1,2048]`
- T4: `[1,4,2048]`
- T8: `[1,8,2048]`

T1 router top-k IDs: `[118, 56, 65, 84, 98, 97, 119, 36]`.

Parity:
- router IDs: exact;
- router weights: bitwise exact, zero error;
- all eight selected expert outputs: bitwise exact;
- complete MoE output: bitwise exact;
- complete decoder-layer output: bitwise exact;
- strongest passing tolerance: `atol=0`, `rtol=0`.

External expert bytes read for T1: `20,054,016 B` = 8 × `2,506,752 B`.

## Residency

Canonical control expert bank resident: `320,864,256 B`.

Serial external-expert maximum logical expert bytes resident: `2,506,752 B`.

Logical expert residency reduction: `99.21875%`.

Measured peaks:
- CONTROL MLX: `331,495,092 B`; RSS `644,284,416 B`;
- SERIAL_EXPERT MLX: `12,938,408 B`; RSS `130,367,488 B`.

Ownership/release audit: PASS. Weak references for every external expert parameter array were dead after release before the next expert load.

## Timing

Warm packed pread P50/P90/P95: `2.009 / 2.180 / 2.229 ms`.

MLX construction P50: `0.615 ms`.
Byte decode/view P50: `9.213 ms`.
Eight-expert compute P50: `2.995 ms`.
Complete external MoE P50: `15.455 ms`.
Full treatment layer P50: `16.282 ms`.

Device-verified physical-I/O + compute descriptive one-layer lower bound: `14.103 ms`; linear 48-layer descriptive extrapolation: `0.677 s`. This is not a full-model token-rate prediction.

## Early routing overlap observation

Synthetic T4: 30 unique experts / 32 selections.
Synthetic T8: 51 unique experts / 64 selections.

This is only a structural observation from synthetic activations and is not promoted as DFlash or real-generation routing evidence.

## Decision

- first multi-layer external-expert prototype: `CONDITIONAL`;
- full 14.344 GiB expert-bank repack justified now: `NO`;
- DFlash/block-routing branch remains justified: `YES`.

Strongest supported conclusion: one real Qwen3-30B-A3B MLX layer can preserve canonical attention, router, quantized expert math, aggregation and residual semantics while keeping only one routed expert live at a time. External-expert execution is therefore computationally viable on the reference architecture; the remaining central problem is whole-model traffic and amortization, not per-expert correctness or residency.

Raw evidence: `results-local/moe/one-layer-external-expert-001/20260824T070045Z/`.
