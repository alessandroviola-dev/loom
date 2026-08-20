# Stretch 031 — SINGLE_PASS M2 vs M5 Geometry Comparison — Preregistration

Date: 2026-08-20
Status: READY — NOT YET RUN

## Background

Stretch 030 completed a valid coherent MLX 0.31.2 vs 0.32.0 ABBA and found MLX 0.32.0 exact but slower (`0.9439326502x` target-rate ratio). MLX 0.31.2 therefore remains the preferred runtime.

The current target-side architecture is:

- Qwen3-8B 3-bit/group64
- MLX 0.31.2 + mlx-metal 0.31.2
- mlx-lm 0.31.3
- M5 oracle target blocks
- H36 persistent transformer residency
- full raw-weight persistence
- one final cleanup/pass
- ordinary BF16 KV.

Stretch 018 previously found M5 faster than M4 by ~9.8%, but that experiment occurred before full weight persistence and before the large cleanup-schedule improvements in Stretch 023–027. It therefore does not establish that M5 remains the throughput optimum on the current execution schedule.

Upstream MLX performance reports also show nonlinear small-M quantized-matmul cost around the speculative-verification range, motivating a direct M2 check. This upstream observation is motivation only; it is not evidence about the M1 result.

Reference:
`https://github.com/ml-explore/mlx/issues/3553`

## Scientific question

On the frozen current MLX 0.31.2 SINGLE_PASS architecture, is verifying the same oracle continuation as M2 blocks faster per accepted token than M5 blocks?

## Single scientific factor

Target oracle block size only:

- CONTROL: `M=5`
- TREATMENT: `M=2`

Everything else is frozen.

## Common continuation depth

A direct comparison must avoid different KV depth/continuation lengths.

Both variants therefore verify the same first **10 frozen oracle tokens**:

`[1,374,264,4647,1483,304,279,1809,315,5994]`

Geometry:

- M5 CONTROL: `2 x 5 = 10` target tokens
- M2 TREATMENT: `5 x 2 = 10` target tokens

The resident reference also generates exactly 10 tokens in both variants.

The M5 helper's change from the historical 15-token Stretch 027 continuation to 10 tokens is a common diagnostic-depth normalization, not the scientific factor. Both sides use the same 10-token depth.

## Frozen factors

No changes to:

- model or safetensors
- 3-bit/group64 quantization
- MLX 0.31.2 / mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- H36
- full raw-weight persistence
- single final cleanup/pass
- BF16 KV
- prompt
- oracle token values
- parity thresholds
- top-1/acceptance policy
- resource gates
- I/O policy
- deliberate cache policy (`NONE`).

## Harness construction

Both variants reconstruct frozen Stretch 027 from blob:

`6636456df5a773ac6062fdad66b7dc96abe8bd81`

The Stretch 031 geometry callback is intentionally applied only **after** the inherited Stretch 017/H36 wrapper has verified its frozen M5 reconstruction. This avoids weakening historical source-provenance checks.

### M5 control

`scripts/stretch_single_pass_m5_ten_token_control_031.py`

Frozen blob:
`5f047b9e5f42bed959ced59e9329a8c8d7e3fc25`

Expected constituent classification:
`SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS`

Expected:
- block size 5
- block count 2
- accepted oracle tokens 10.

### M2 treatment

`scripts/stretch_single_pass_m2_ten_token_variant_031.py`

Frozen blob:
`6005ff3a285760457d3255bc6505f2987c1fa4e8`

Expected constituent classification:
`SINGLE_PASS_M2_TEN_TOKEN_GEOMETRY_PASS`

Expected:
- block size 2
- block count 5
- accepted oracle tokens 10.

## Balanced comparison

Runner:

`scripts/stretch_single_pass_m2_m5_geometry_comparison_031.py`

Frozen blob:
`bc3b21ff504c65d0852aad68a566cba924888d90`

Balanced order:

`M5 -> M2 -> M2 -> M5`

No constituent measurements from historical experiments are reused.

No automatic retry.

No deliberate cache purge.

## Primary metric

Pooled target-verification accepted tokens per second:

`accepted oracle tokens / total target-block wall seconds`

Primary causal comparison:

`M2 pooled target rate / M5 pooled target rate`

Because both sides accept the same number of tokens at the same continuation depth, this directly measures the block-geometry cost relevant to oracle verification.

## Secondary metrics

- wall seconds per accepted token
- median block wall
- final-cleanup seconds per accepted token
- minimum observed system free memory
- peak observed swap.

Median block wall is descriptive only because an M2 block and an M5 block contain different token counts. The per-token metric and pooled target rate are the decision metrics.

## Correctness/resource gates

Each constituent must independently satisfy inherited gates plus Stretch 031 provenance:

- expected constituent classification
- H36 layers 0..35
- persistent raw weights near 3,583,928,320 B
- exact expected block size
- exactly 10 accepted oracle tokens
- expected number of target blocks
- one final cleanup per target pass and no transformer-body cleanup marker
- inherited prompt/KV/numerical/top-1/oracle acceptance gates
- inherited memory/swap safety policy.

If the first M2 constituent reaches the frozen scientific gates and fails numerical/top-1/oracle acceptance, classify:

`M2_SINGLE_PASS_GEOMETRY_EXACTNESS_FAIL`

This is a valid scientific FAIL. Stop immediately; no rescue or retry.

Harness/resource/provenance failures classify:

`SINGLE_PASS_M2_M5_GEOMETRY_COMPARISON_INCOMPLETE`

and are not scientific performance evidence.

A complete exact ABBA classifies:

`SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS`

## Decision policy

No post-hoc effect threshold is invented.

If M2 has the higher pooled target rate and remains exact/resource-safe:

- freeze the M2 win;
- do not immediately call M2 globally optimal;
- separately preregister M2 vs M3 at a common continuation depth to map the local optimum.

If M5 has the higher pooled target rate:

- retain M5 as preferred current block size;
- treat the M2 small-M hypothesis as negative on this M1 workload;
- move to the next independent compute factor rather than rescue M2.

If rates are effectively indistinguishable within the observed balanced data:

- retain M5 because it verifies more tokens per traversal and already has the stronger historical exactness evidence;
- record the flat result without post-hoc reruns.

## Run command

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_single_pass_m5_ten_token_control_031.py
python3 -m py_compile scripts/stretch_single_pass_m2_ten_token_variant_031.py
python3 -m py_compile scripts/stretch_single_pass_m2_m5_geometry_comparison_031.py
python3 scripts/stretch_single_pass_m2_m5_geometry_comparison_031.py
```

If the runner stops, preserve the run and inspect it before any rerun.
