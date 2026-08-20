# Stretch 037 — Fix2 resource-fresh ABBA result

Date: 2026-08-20
Status: **`M1_QMV_FAST_TUNING_PASS` — valid balanced ABBA; S1_R8 promoted for the frozen M1 path.**

## Provenance and non-reuse

This is the separately authorized `STRETCH_037_FIX2_RESOURCE_FRESH_ATTEMPT`,
not a retry of Fix1. Its committed, remote-verified source identity is:

```text
HARNESS_REVISION = "STRETCH_037_FIX2_RESOURCE_FRESH_ATTEMPT"
commit = 7291df6c6c34971647cbca1786f78a87ea278046
```

Fix2 preserves both prior runners unchanged and uses only fresh evidence:

- standalone preflight:
  `results-local/stretch/m1-qmv-fast-tuning-037-fix2/preflight/20260820-215510/preflight-summary.json`;
- fresh full ABBA root:
  `results-local/stretch/m1-qmv-fast-tuning-037-fix2/20260820-215547/`.

No prior Fix1 run directory, constituent, or artifact was reused. No cache
purge, artificial allocation, automatic process kill, runtime change, weight
conversion, quantization change, or gate change occurred.

## Gates before science

The passive pre-creation host sample passed naturally: system-wide free memory
`63%`, swap `634.44 MB` (required `>=60%`, `<=5600 MB`).

Fix1→Fix2 normalized harness diff passed. It permits only the Fix2 harness
revision/provenance declaration and Fix2 output paths. The scientific rendered
source diff also passed: only built-in MLX qmv implementation versus custom
S1_R8 injection. `py_compile` passed under the literal, non-dereferenced
canonical launcher:

```text
results-local/mlx/venv-mlx-lm-0.31.3/bin/python
```

CONTROL and TREATMENT no-model dispatch both passed with
`model_loaded=false` and `target_compute_executed=false`. Runtime provenance
was mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`.

Fresh real-weight CONTROL/S1_R8 parity passed for BF16, 3-bit affine,
group_size=64, M=5 in every required class:

| K → N | Shape equal | Exact equality | max abs diff | mean abs diff |
|---|---:|---:|---:|---:|
| 4096 → 4096 | true | true | 0 | 0 |
| 4096 → 1024 | true | true | 0 | 0 |
| 4096 → 12288 | true | true | 0 | 0 |
| 12288 → 4096 | true | true | 0 | 0 |

The mandatory fresh in-harness preflight at
`.../20260820-215547/preflight/preflight-summary.json` repeated all those
checks before any constituent.

## Frozen factor and ABBA

CONTROL remained built-in MLX 0.31.2
`affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0`. TREATMENT remained the
M1-specific process-local custom S1_R8 `qmv_fast`; this is not a geometry-only
comparison. Qwen3-8B 3-bit affine/group64 BF16, M5, H36, full raw-weight
persistence, single final cleanup, BF16 KV, oracle, numerical/resource gates,
and ABBA sequencing remained frozen.

Fresh order completed exactly:

| Constituent | Launch samples (free %, swap MB) | Accepted oracle tokens | Classification |
|---|---|---:|---|
| CONTROL | 64/634.44, 64/634.44, 64/634.44 | 10 | PASS |
| S1_R8 | 69/1328.12, 70/1328.12, 71/1320.12 | 10 | PASS |
| S1_R8 | 72/1555.75, 73/1555.75, 73/1555.75 | 10 | PASS |
| CONTROL | 72/1539.75, 72/1539.75, 72/1539.75 | 10 | PASS |

Every child passed `SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS`: full raw-weight
persistence was exactly `3,583,928,320 B`; prompt and all ten generated-token
logit checks had max/mean absolute difference `0`; top-1 was equal; the exact
oracle sequence was accepted; and `generated_sequence_equal=true`. Thus all
four constituents completed two exact M5 blocks and 40 accepted tokens were
pooled.

## Measured result

Primary metric is pooled accepted oracle tokens / total target-block wall.

| Metric | CONTROL | S1_R8 |
|---|---:|---:|
| Constituents / accepted tokens | 2 / 20 | 2 / 20 |
| Target-block wall | 1.457160 s | 1.333095 s |
| Pooled tok/s | 13.725329 | 15.002682 |
| Wall / accepted token | 0.072858 s | 0.066655 s |
| Median block wall | 0.363852 s | 0.331027 s |
| Final cleanup / token | 0.009497 s | 0.009115 s |
| Minimum free memory | 20% | 25% |
| Peak swap | 1584.31 MB | 1571.75 MB |
| Peak MLX memory | 3,632,130,592 B | 3,632,130,080 B |

`S1_R8 / CONTROL = 1.093065`, a **+9.306539%** improvement. The prior
14.3307 tok/s CONTROL is historical only and was not used; the fresh ABBA
CONTROL is the comparator.

The child telemetry does not expose a nonzero `peak_active_memory_bytes` for
this full-model path (the harness aggregate therefore records `0`); peak MLX
memory above is the observable resident/stream peak. The no-model startup
preflight observed active/peak MLX memory `53,559,296 / 54,099,980 B`.

S1_R8 prepared four specializations. Factory/JIT was outside target timing:
`0.000331 / 0.040906 s` then `0.000141 / 0.038941 s` for the two treatment
constituents; startup totals were `0.056652 s` and `0.054307 s` respectively.
Observable recompilation during target timing was `0` for both.

## Decision

Classification: **`M1_QMV_FAST_TUNING_PASS`**. The raw harness classification
is `M1_QMV_FAST_TUNING_BALANCED_COMPARISON_PASS` with `VALID_ABBA` scientific
result. Since S1_R8 is faster and every correctness/resource gate passed,
promote the M1-specific process-local S1_R8 custom qmv implementation as the
new canonical compute path for this frozen M1 Qwen3-8B 3-bit/group64 BF16 M5
H36 configuration. Retain built-in MLX outside that explicitly supported
configuration.

Result evidence: `results-local/stretch/m1-qmv-fast-tuning-037-fix2/20260820-215547/summary.json`.
