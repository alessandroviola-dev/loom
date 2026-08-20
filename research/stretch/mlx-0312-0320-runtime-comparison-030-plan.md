# Stretch 030 — MLX 0.31.2 vs 0.32.0 Runtime Comparison — PREREGISTRATION

Date: 2026-08-20
Status: **READY AFTER ISOLATED ENVIRONMENT SETUP**

## Scientific question

On the canonical Stretch 027 target architecture, does changing **only MLX runtime 0.31.2 -> 0.32.0** preserve the frozen M5 correctness gates and improve target-verification cost on the Apple M1 / 8 GB reference system?

## Why this factor is next

Stretch 028 re-attribution showed true transformer compute is now the dominant optimization target:
- transformer compute `0.44969600122810033 s/block`;
- attention path `0.1231006117692838 s/block`;
- MLP path `0.3265953894588165 s/block`;
- MLP/attention `2.653076899982628x`;
- up/attention/gate/down are individually all near `0.095–0.099 s/block`.

Stretch 029 tested one manual gate+up quantized fusion. The valid balanced run `20260820-171714` was exact but slower:
- CONTROL `13.228627278575932 token/s`;
- FUSED `12.352399124132555 token/s`;
- FUSED/CONTROL `0.933762730176664x` (~6.62% slower).

Therefore the exact gate+up fusion implementation is closed under MLX 0.31.2.

The next independent factor is the runtime itself.

## External runtime evidence frozen before the experiment

Official MLX release metadata observed 2026-08-20:
- MLX `v0.32.0` was released 2026-07-07;
- its official release notes include `Generate qmm implementations with cmake` and `[Metal][Performance]: Add split-K for quantized matmul (small M)`.

Official release source:
`https://github.com/ml-explore/mlx/releases/tag/v0.32.0`

Official PyPI metadata for `mlx-lm==0.31.3` on Darwin requires:
`mlx>=0.31.2`.

Therefore keeping `mlx-lm==0.31.3` while testing `mlx==0.32.0` is package-compatible.

PyPI metadata source:
`https://pypi.org/pypi/mlx-lm/0.31.3/json`

These external facts motivate the test only. The local balanced experiment decides promotion.

## Frozen canonical workload

Exact same source in CONTROL and TREATMENT:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`

Frozen blob:
`6636456df5a773ac6062fdad66b7dc96abe8bd81`

Frozen architecture/workload:
- Qwen3-8B 3-bit/group64;
- M=5;
- H36;
- full raw-weight persistence;
- one final cleanup/pass;
- ordinary BF16 KV;
- same prompt and frozen oracle sequence;
- same numerical/top1/acceptance gates;
- same resource and I/O policy;
- no deliberate cache purge.

## CONTROL environment

Canonical current Python environment:
- `mlx==0.31.2`;
- `mlx-lm==0.31.3`;
- `transformers==5.12.1`.

The balanced runner refuses to start if those versions are not observed.

## MLX0320 treatment environment

Treatment venv:
`.venvs/stretch030-mlx0320`

Setup utility:
`scripts/stretch_mlx_0320_env_setup_030.py`

Frozen setup blob:
`fde39967be02cba81ea14bb043c9fdacd24db861`

Setup policy:
1. create venv from the canonical interpreter with `--system-site-packages`;
2. overlay **only** `mlx==0.32.0` with `pip --no-deps`;
3. do not modify the canonical environment;
4. require identical Python, mlx-lm, Transformers, NumPy and safetensors versions between environments;
5. write a local environment provenance marker.

Environment setup is **not** a scientific constituent and is completed before the balanced run.

No pip installation occurs inside the scientific runner.

## Scientific factor

Exactly one intended package difference:

`mlx 0.31.2 -> mlx 0.32.0`

The exact same Stretch 027 source is executed by both interpreters.

No source-level optimization is added to MLX0320.

## Balanced order

`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`

No automatic retry.

No measurement from previous experiments is pooled into this comparison.

## Correctness rule

MLX0320 must pass the same inherited M5 gates as the canonical runtime.

A first treatment failure in any frozen numerical/top1/oracle acceptance/sequence gate is a valid scientific result:

`MLX_0320_RUNTIME_EXACTNESS_FAIL`

Stop immediately. Do not relax thresholds, modify the oracle, change M, or try a rescue package combination.

## Complete balanced success

If all four constituents pass correctness/resource/provenance gates:

`MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`

Primary metric:
- pooled target-verification token/s;
- `MLX0320 / MLX0312` ratio.

Secondary:
- median/mean target block wall;
- final cleanup wall;
- minimum free memory;
- peak swap.

## Incomplete classification

Harness, environment-provenance, resource, missing-summary, or other non-scientific execution failure:

`MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE`

Do not automatically rerun.

## Frozen runner

`scripts/stretch_mlx_0312_0320_runtime_comparison_030.py`

Blob:
`0d0a27549067cef61a1dca7d3bf8f0e1f954d98b`

## Interpretation policy

### MLX0320 exact + faster
Promote MLX 0.32.0 as the preferred runtime for a new runtime branch of evidence. Do not rewrite MLX 0.31.2 history.

Then separately preregister a new M-boundary mapping under 0.32.0, because the old M5 ceiling was established under 0.31.2.

### MLX0320 exact + flat/slower
Retain MLX 0.31.2 as canonical runtime and close 0.32.0 as a speed upgrade for this workload. Move to a different compute factor.

### MLX0320 exactness fail
Preserve the scientific FAIL. MLX 0.32.0 is not admissible for this frozen M5 profile without a separately designed future investigation.

## Exact execution sequence

First provision and validate the isolated treatment environment:

```bash
python3 -m py_compile scripts/stretch_mlx_0320_env_setup_030.py
python3 scripts/stretch_mlx_0320_env_setup_030.py
```

Only if setup prints `Environment setup: PASS`, run:

```bash
python3 -m py_compile scripts/stretch_mlx_0312_0320_runtime_comparison_030.py
python3 scripts/stretch_mlx_0312_0320_runtime_comparison_030.py
```

Do not run the canonical workload manually between balanced constituents.
