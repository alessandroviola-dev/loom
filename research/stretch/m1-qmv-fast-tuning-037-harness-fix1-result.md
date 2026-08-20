# Stretch 037 — preflight harness Fix1 result

Date: 2026-08-20
Status: **`M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE` — scientific result NONE.**

## Fix1 provenance

Fix1 is a distinct source identity, not a retry of the preserved original
runner. Commit `f9d80966eb40a03430b6dfb7ff1a73bf1c800d90` was remote-verified
before this launch. It preserves
`scripts/stretch_m1_qmv_fast_comparison_037.py` (blob
`5dd2e0bcc652d7197a06e4230d6519ced7ea73df`) and uses distinct
`scripts/stretch_m1_qmv_fast_comparison_037_fix1.py` (blob
`3ae67ab6af37f420eaf5098f6c20448c0f0f8d96`). The only harness change is
fresh `preflight/` evidence-directory creation with `exist_ok=False` before
rendering.

## Fresh in-harness preflight: PASS

Fresh root:

`results-local/stretch/m1-qmv-fast-tuning-037/20260820-214110/`

Its mandatory in-harness preflight passed before any constituent. Evidence:

`results-local/stretch/m1-qmv-fast-tuning-037/20260820-214110/preflight/preflight-summary.json`

It passed source render/compile, normalized factor-only source diff, literal
canonical launcher/runtime provenance, CONTROL and S1_R8 no-model markers, and
the four real-weight BF16 affine 3-bit/group64 shape classes. Every real-weight
comparison was shape-equal and bit-exact with `max_abs_diff=0` and
`mean_abs_diff=0`; S1_R8 instantiated four specializations. JIT startup was
outside target timing.

## Stop: resource launch gate before CONTROL computation

The fresh first CONTROL constituent did not pass its inherited host launch
gate. Its first host sample was:

```text
free memory: 59%     (required >=60%)
swap:        634.44 MB (required <=5600 MB)
classification: HOST_STATE_NOT_READY
```

The parent therefore stopped immediately and classified the outer run as
`M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE`. Evidence:

- outer summary: `results-local/stretch/m1-qmv-fast-tuning-037/20260820-214110/summary.json`
- CONTROL child summary:
  `results-local/stretch/m5-ten-token-single-pass-control-031-fix3/20260820-214112/summary.json`
- CONTROL stdout:
  `results-local/stretch/m1-qmv-fast-tuning-037/20260820-214110/attempt-1-control-stdout.txt`

This is a resource/preflight stop, not a numerical/top-1/oracle failure and
not a performance result. No target block ran, no oracle token was accepted,
no cleanup/timing/wall-per-token metric exists, and neither S1_R8 constituent
nor the final CONTROL constituent launched. No prior constituent or run
artifact is reusable.

## Frozen interpretation and next action

The scientific factor remains built-in MLX 0.31.2 affine qmv_fast versus the
M1-specific custom S1_R8 qmv_fast implementation, not geometry alone. ABBA
remains `CONTROL -> S1_R8 -> S1_R8 -> CONTROL`, with two M5 blocks and ten
accepted oracle tokens per constituent.

Per the frozen no-retry rule, this Fix1 launch is complete as an INCOMPLETE
resource result. Do not rerun it, change thresholds, alter the factor, or reuse
any constituent. Any future run requires separate explicit authorization for a
new revision/attempt with a new source identity and wholly fresh preflight/run
directory.
