# Stretch 037 — preflight harness Fix2 resource-fresh attempt

Date: 2026-08-20
Status: **`STRETCH_037_FIX2_RESOURCE_FRESH_ATTEMPT` — authorized, pre-science.**

## Separate identity and scope

Fix2 is a new, separately authorized source revision after Fix1's resource
launch-gate stop. It is **not a retry of Fix1**. It has no reusable run
directory, constituent, or artifact. Its source identity is:

```text
HARNESS_REVISION = "STRETCH_037_FIX2_RESOURCE_FRESH_ATTEMPT"
```

| Runner | Path |
|---|---|
| preserved original | `scripts/stretch_m1_qmv_fast_comparison_037.py` |
| preserved Fix1 | `scripts/stretch_m1_qmv_fast_comparison_037_fix1.py` |
| new Fix2 | `scripts/stretch_m1_qmv_fast_comparison_037_fix2.py` |

Fix2 writes only to fresh `results-local/stretch/m1-qmv-fast-tuning-037-fix2/`
paths. Its built-in normalized comparison against Fix1 removes the new
revision declaration and substitutes its Fix2 output path with the Fix1 output
path; exact equality is required. Thus permitted differences are only the
Fix2 revision/provenance identity and necessary output paths.

## Frozen scientific factor

- **CONTROL:** built-in MLX 0.31.2
  `affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0`.
- **TREATMENT:** M1-specific process-local custom S1_R8 `qmv_fast`.
- Qwen3-8B, 3-bit affine, group_size=64, BF16, M5, H36, full raw-weight
  persistence, a single final cleanup, and BF16 KV remain unchanged.
- ABBA remains `CONTROL -> S1_R8 -> S1_R8 -> CONTROL`; every fresh constituent
  requires two M5 blocks and ten accepted exact oracle tokens.

This factor is not "geometry alone." No kernel, source kernel, oracle, ABBA,
weights, quantization, runtime, venv, numerical gate, resource gate, cleanup,
or sequencing changes are permitted.

## Mandatory gates

Before any model work, Fix2 requires render/compile, literal canonical launcher
`results-local/mlx/venv-mlx-lm-0.31.3/bin/python` without dereference, runtime
provenance, CONTROL/TREATMENT no-model markers, normalized source checks, and
fresh real-weight BF16 bits=3/group_size=64/M5 parity for 4096→4096,
4096→1024, 4096→12288, and 12288→4096. Every comparison must be shape-equal,
bit-exact, and have zero maximum and mean absolute difference.

Immediately before each fresh constituent, launch only at system-wide free
memory >=60% and swap <=5600 MB. Runtime abort remains free memory <5% or swap
>5600 MB. No cache purge, forced memory release, automatic process kill, or
host-state manipulation is allowed. A launch-gate failure ends this Fix2
attempt as `M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE`, scientific result NONE,
with no retry.

## Required evidence and decision

The source revision must be committed and remote-verified before the fresh
in-harness preflight and ABBA. The evidence summary records `HARNESS_REVISION`,
normalized Fix1→Fix2 status, provenance, preflight, parity, constituent
resource samples, correctness, timing, cleanup, MLX memory, specializations,
and observable recompilation count.

Only a fully exact and resource-valid ABBA can compare pooled accepted-oracle
tokens / total target-block wall. Promote S1_R8 only if it is faster; otherwise
retain built-in MLX (including materially flat results, for lower complexity).
