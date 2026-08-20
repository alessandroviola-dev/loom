# LOOM Stretch 029 — Harness Defect — 20260820-170503

Status: **HARNESS DEFECT — NO SCIENTIFIC RESULT**

Run directory:
`results-local/stretch/gate-up-quantized-fusion-comparison-029/20260820-170503`

Outer classification:
`GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`

## What happened

Frozen order:
`CONTROL -> FUSED -> FUSED -> CONTROL`

Attempt 1 CONTROL completed all inherited gates:
- classification `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- M=5
- H36
- 15 accepted oracle tokens
- full persistent raw-weight bytes `3,583,928,320`
- min free memory `13%`
- peak swap `2504.25 MB`.

Attempt 2 FUSED terminated in approximately `0.304 s` before producing a child `summary.json`.

Exact traceback:

```text
RuntimeError: Stretch 029 wrapper invariant failed; missing ['single_quantized_matmul_gate_up']
```

## Root cause

The FUSED helper constructs an intermediate transformed Stretch-013 wrapper and injects the runtime callback:

```python
source = __stretch029_apply_gate_up_fusion(source)
```

The actual fused-runtime text, including the provenance string:

```text
single_quantized_matmul_gate_up
```

is created only later, when that callback executes inside the wrapper after the final runtime source has been assembled.

The original preflight incorrectly searched the **intermediate wrapper source** for `single_quantized_matmul_gate_up` before executing the callback. That condition is impossible by construction, so the helper aborted before model/treatment execution.

This is the same class of source-transform phase-order error previously seen in Stretch 023: validating post-callback runtime content at pre-callback wrapper time.

## Scientific interpretation

None.

The FUSED treatment did not launch and did not reach MLX quantized execution, parity gates, or resource gates. Therefore this run does **not** demonstrate:
- fused numerical parity failure;
- fused performance failure;
- MLX kernel incompatibility;
- memory/swap failure;
- model failure.

No Stretch 029 scientific attempt was consumed by attempt 2.

Attempt 1 CONTROL is audit-only and must not be reused in a repaired comparison.

## Harness-only repair

The repair may change only the wrapper preflight invariant:
- preserve the check that `__stretch029_apply_gate_up_fusion(source)` is present exactly in the wrapper;
- remove the invalid requirement that the post-callback string `single_quantized_matmul_gate_up` already exist in the wrapper before callback execution.

The actual `add_gate_up_fusion()` transform remains frozen and unchanged.

Everything scientific remains frozen:
- CONTROL Stretch 027 blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`;
- M=5;
- H36;
- full raw-weight persistence;
- one final cleanup/pass;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- ordinary BF16 KV;
- exact numerical/top1/acceptance gates;
- I/O/resource gates;
- scientific fusion transform;
- order `CONTROL -> FUSED -> FUSED -> CONTROL`;
- no deliberate cache purge;
- no automatic retry/rescue.

A repaired run must start a completely new ABBA sequence. No measurements from `20260820-170503` may be reused.
