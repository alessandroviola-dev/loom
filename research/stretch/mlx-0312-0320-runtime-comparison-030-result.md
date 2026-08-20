# Stretch 030 — MLX 0.31.2 vs 0.32.0 Runtime Comparison — Result

Date: 2026-08-20
Status: COMPLETE — SCIENTIFIC PASS / TREATMENT NOT PROMOTED

## Classification

`MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`

Valid run:
`results-local/stretch/mlx-0312-0320-runtime-comparison-030-fix3/20260820-175251`

Summary:
`results-local/stretch/mlx-0312-0320-runtime-comparison-030-fix3/20260820-175251/summary.json`

## Scientific question

Does changing only the coherent macOS MLX runtime package pair from `mlx + mlx-metal 0.31.2` to `mlx + mlx-metal 0.32.0` preserve frozen M5 correctness and improve target-verification throughput on the Apple M1 / 8 GB reference system?

## Frozen architecture

Both variants used the same runtime-portable derivative of the frozen Stretch 027 workload:

- Qwen3-8B 3-bit/group64
- M5
- H36
- full raw-weight persistence
- one final cleanup/pass
- BF16 KV
- mlx-lm 0.31.3
- transformers 5.12.1
- numpy 2.5.2
- safetensors 0.8.0
- Python 3.13.0
- identical oracle/numerical/top-1/acceptance/resource gates
- no deliberate cache purge

Scientific factor only:

- CONTROL: `mlx==0.31.2`, `mlx-metal==0.31.2`
- TREATMENT: `mlx==0.32.0`, `mlx-metal==0.32.0`

Balanced order:

`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`

The Fix3 harness explicitly verified the real inner child runtime for every constituent.

## Preserved pre-run defects

Three pre-science harness/setup defects occurred before the valid run and are retained as audit evidence:

1. original setup used shell Python instead of the canonical LOOM MLX venv;
2. runner Fix1 required a nonexistent failure-class string;
3. runner Fix2 dereferenced venv `bin/python` symlinks with `Path.resolve()`, losing venv package context.

None launched a valid scientific ABBA constituent and none contributes measurements to this result.

## Valid balanced result

| Metric | MLX 0.31.2 | MLX 0.32.0 |
|---|---:|---:|
| Pooled target-verification tok/s | 13.074823729584752 | 12.341753014370326 |
| Median target block wall | 0.3795345 s | 0.405476 s |
| Mean final cleanup wall | 0.05542983333333333 s | 0.06362483333333334 s |
| Minimum observed free memory | 17% | 22% |
| Peak observed swap | 2801.88 MB | 2809.25 MB |

Ratios:

- MLX0320 / MLX0312 target rate: `0.9439326502310171x`
- treatment throughput change: approximately `-5.61%`
- MLX0320 / MLX0312 median block-wall ratio: `1.068350835036077x`
- treatment median block wall: approximately `+6.84%`

Observed higher pooled target rate: **MLX0312**.

## Interpretation

MLX 0.32.0 is admissible under the frozen M5 correctness gates: the full ABBA completed and all inherited exactness/resource requirements passed.

However, the isolated runtime upgrade is slower on the M1 reference system. The balanced causal evidence is the within-run target-rate ratio `0.9439326502x`; cross-experiment absolute rates are not used as causal evidence.

The treatment had more observed free memory but nearly identical peak swap, so the negative throughput result is not a memory-capacity failure.

The final-cleanup wall is also larger under 0.32.0, but this secondary metric is not treated as a complete causal decomposition of the runtime regression.

## Decision

- Do **not** promote MLX 0.32.0.
- Retain coherent `mlx + mlx-metal 0.31.2` as the preferred runtime for the current target-side architecture.
- Do not remap the M boundary under 0.32.0 because the prerequisite condition `exact + faster` was not met.
- Preserve the validated 0.32.0 treatment venv for audit/reproduction; do not overwrite the canonical venv.
- Return to a compute/geometry factor under MLX 0.31.2.

## Next factor

Stretch 031 will re-evaluate target oracle block geometry on the *current* optimized execution schedule. The old M4/M5 comparison predates full persistence and the cleanup reductions, so it does not establish that M5 remains the throughput optimum after Stretch 023–027.

The first controlled comparison is M2 vs M5 with the same 10-token oracle prefix in both variants, keeping all other architecture/runtime/resource policies frozen.
