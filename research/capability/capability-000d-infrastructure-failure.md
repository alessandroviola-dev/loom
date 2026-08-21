# CAPABILITY 000D — infrastructure failure

Date: 2026-08-21
Status: PRESERVED HARNESS FAILURE / NO SCIENCE

The first integrated Pi-loop attempt with `prefill_step_size=512` failed before model prefill or any tool execution because server instrumentation failed in the server thread.

Observed state:
- classification: `CAPABILITY_000D_INFRASTRUCTURE_FAILURE`
- input request length: 1518 tokens
- generated tokens: 0
- tool sequence: none
- `answer.txt`: absent
- `numbers.txt`: byte-identical
- minimum free memory: 17%
- peak swap: 2288.25 MB
- peak MLX: 3417.901 MB, corresponding to loaded weights only
- provider identity remained localhost `loom-mlx-local` -> canonical Qwen3-8B-3bit; no fallback observed
- Pi automatically retried the failed request, but no retry reached model execution.

Interpretation:

This run contains no evidence against `prefill_step_size=512`. The treatment was never exercised. It is a harness/instrumentation defect and does not consume the CAPABILITY 000D scientific attempt.

Next action: repair only the failing instrumentation/server path and rerun the same frozen 000D task as `CAPABILITY 000D Fix1`, with no scientific-factor changes.

Local evidence:
`results-local/capability/capability-000d/20260821-151637/`
