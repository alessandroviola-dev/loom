# Stretch 037 — preflight harness Fix1

Date: 2026-08-20
Status: **`STRETCH_037_PREFLIGHT_HARNESS_FIX1_READY` — pre-science only.**

## Scope and source identity

This is a distinct preflight-harness revision authorized after the preserved
`20260820-212659` harness failure. It is **not** a retry and has no reusable
scientific constituent.

| Runner | Path | Git blob |
|---|---|---|
| preserved defective source | `scripts/stretch_m1_qmv_fast_comparison_037.py` | `5dd2e0bcc652d7197a06e4230d6519ced7ea73df` |
| distinct Fix1 source | `scripts/stretch_m1_qmv_fast_comparison_037_fix1.py` | `3ae67ab6af37f420eaf5098f6c20448c0f0f8d96` |

The original runner is unchanged and remains defect evidence.

## Frozen root cause and exact normalized harness diff

The original full-run branch created `root`, then called
`render_preflight(repo, root / "preflight")`. `render_preflight` writes
`control-final.py` immediately, but the child `preflight/` directory did not
exist.

Fix1 changes only the evidence-directory setup:

```diff
 root=repo/"results-local/stretch/m1-qmv-fast-tuning-037"/...; root.mkdir(parents=True)
-try: preflight=render_preflight(repo,root/"preflight"); ...
+preflight_dir=root/"preflight"; preflight_dir.mkdir(parents=True,exist_ok=False)
+try: preflight=render_preflight(repo,preflight_dir); ...
```

`exist_ok=False` makes a collision in a purportedly fresh run fail rather than
reuse evidence. There are no changes to CONTROL, TREATMENT, kernel, oracle,
M5, H36, cleanup, runtime, thresholds, ABBA order, resource gates or numerical
gates. No telemetry or error-handling behavior changed.

## Preserved pre-fix reproduction

A fresh invocation of the original runner on 2026-08-20 created
`results-local/stretch/m1-qmv-fast-tuning-037/20260820-213943/summary.json`
and stopped before model launch or target computation:

```text
classification: M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE
scientific_result: NONE
failure_reason: preflight: FileNotFoundError: .../20260820-213943/preflight/control-final.py
```

This is the same missing-child-directory defect as the original preserved
failure. The original source was not modified.

## Fresh Fix1 preflight evidence

Fresh Fix1 preflight:

`results-local/stretch/m1-qmv-fast-tuning-037/preflight/20260820-213948/preflight-summary.json`

It passed all launch prerequisites without loading a resident model or running
target compute:

- fresh root and `preflight/` evidence directory: PASS;
- CONTROL and TREATMENT render/compile: PASS;
- normalized source factor diff: PASS;
- literal canonical launcher and child `sys.prefix`: PASS;
- CONTROL and TREATMENT child markers: `model_loaded=false`,
  `target_compute_executed=false`;
- pinned runtime provenance: mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`,
  transformers `5.12.1`: PASS.

The mandatory real-weight startup kernel sanity in that same preflight also
passed for BF16 affine 3-bit/group64 M5 inputs. CONTROL built-in qmv_fast and
custom S1_R8 have shape equality and strict bit equality for all required
classes; every `max_abs_diff` and `mean_abs_diff` is `0`:

| K -> N |
|---|
| 4096 -> 4096 |
| 4096 -> 1024 |
| 4096 -> 12288 |
| 12288 -> 4096 |

It instantiated four S1_R8 specializations. JIT/startup is outside ABBA target
timing.

## Preregistration remains frozen

CONTROL remains built-in MLX `0.31.2` affine qmv_fast. TREATMENT remains the
M1-specific process-local custom `S1_R8` qmv_fast implementation. The factor
is not geometry alone. The only permitted ABBA after a fresh in-harness launch
preflight is `CONTROL -> S1_R8 -> S1_R8 -> CONTROL`, with two M5 blocks and ten
accepted oracle tokens per constituent.

## Next action

Commit and remote-verify this Fix1 revision before beginning any full-model
work. After that verification, create one wholly fresh run directory, rerun the
mandatory in-harness preflight there, and run the ABBA only if it passes.
