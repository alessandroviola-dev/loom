# Stretch 029 — Gate+Up Quantized Fusion — RESULT

Date: 2026-08-20
Status: **COMPLETE — EXACT BUT SLOWER**

## Valid run

Run directory:
`results-local/stretch/gate-up-quantized-fusion-comparison-029-fix1/20260820-171714`

Classification:
`GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`

Balanced order:
`CONTROL -> FUSED -> FUSED -> CONTROL`

No measurement from the earlier harness-defect sequence `20260820-170503` was reused.

## Frozen sources

CONTROL:
- `scripts/stretch_full_persistent_single_pass_cleanup_027.py`
- blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`

FUSED Fix1 helper:
- `scripts/stretch_gate_up_quantized_fusion_029_fix1.py`
- blob `93d985a526f4433b10fec39fbaf5807059807821`

Fix1 balanced runner:
- `scripts/stretch_gate_up_quantized_fusion_comparison_029_fix1.py`
- blob `3e8c32292763c10d2acea234152d0ff835fe985d`

Original scientific fusion transform remained frozen in:
- `scripts/stretch_gate_up_quantized_fusion_029.py`
- blob `c37ff6313106807c1e2e5070b7fb8f19e97abea6`.

## Scientific factor

CONTROL uses separate quantized `gate_proj(x)` and `up_proj(x)` calls.

FUSED:
- concatenates packed gate/up quantized weight, scales and affine biases once during setup;
- removes the original steady-state gate/up module references after fused materialization;
- performs one `mx.quantized_matmul` for gate+up;
- splits the result into gate/up halves;
- leaves SwiGLU and `down_proj` unchanged.

Everything else remained frozen:
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2;
- mlx-lm 0.31.3;
- transformers 5.12.1;
- M=5;
- H36;
- full raw-weight persistence;
- one final cleanup/pass;
- ordinary BF16 KV;
- frozen oracle/numerical/top1/acceptance gates;
- resource and I/O policy;
- no deliberate cache purge.

## Primary result

CONTROL pooled target-verification rate:
`13.228627278575932 token/s`

FUSED pooled target-verification rate:
`12.352399124132555 token/s`

FUSED / CONTROL:
`0.933762730176664x`

Therefore FUSED is approximately **6.62% slower** than CONTROL in the balanced experiment.

## Block wall

CONTROL median block wall:
`0.374359 s`

FUSED median block wall:
`0.406644 s`

FUSED / CONTROL median block-wall ratio:
`1.0862407475177571x`

Therefore FUSED median target block wall is approximately **8.62% higher**.

## Cleanup / resources

Mean final cleanup wall:
- CONTROL `0.05385683333333333 s`
- FUSED `0.06512233333333334 s`.

Minimum observed free memory:
- CONTROL `19%`
- FUSED `22%`.

Peak observed swap:
- CONTROL `2575.56 MB`
- FUSED `2614.5 MB`.

Resource gates remained satisfied.

## Exactness result

FUSED completed both treatment constituents and the full balanced ABBA under the inherited frozen correctness gates.

Therefore gate+up fusion is **numerically admissible at M5 under MLX 0.31.2**. The experiment is not a parity failure.

## Interpretation

The fused representation is exact, but slower under MLX 0.31.2. The larger fused output geometry does not improve target verification cost enough to beat two separate quantized projections on this hardware/runtime.

The higher FUSED final-cleanup wall is secondary telemetry and must not be treated as the sole causal explanation. The decisive causal evidence is the balanced target-rate and target-wall comparison.

## Decision

- Do **not** promote gate+up fusion.
- Close this exact fusion implementation under MLX 0.31.2.
- Do not try rescue ordering, partial fusion, threshold relaxation, or post-hoc fusion variants.
- Restore canonical Stretch 027 SINGLE_PASS as the preferred target architecture.
- Next independent factor: isolated MLX runtime comparison, keeping model, mlx-lm, Transformers, source workload, M5/H36/full persistence/single cleanup/KV/gates frozen.

The frozen MLX 0.31.2 evidence remains canonical historical evidence even if a newer runtime later wins.
