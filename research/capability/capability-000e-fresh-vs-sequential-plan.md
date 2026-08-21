# CAPABILITY 000E — Fresh vs sequential turn attribution

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Why did CAPABILITY 000D Fix2 abort on the second Pi request at 1576 input tokens?

Two hypotheses must be distinguished before changing the runtime:

1. `INTRINSIC_REQUEST_SIZE_LIMIT`: the exact 1576-token request is unsafe even when executed as the first request after a fresh model load.
2. `INTER_REQUEST_ACCUMULATION`: the 1576-token request is safe when fresh, but becomes unsafe after the preceding 1521-token request because memory/cache/references persist across requests.

## Frozen subject

- canonical Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- enable_thinking=false
- `prefill_step_size=512`
- same tokenizer/chat template/provider bridge
- exact request bodies captured in CAPABILITY 000D Fix2

Do not change prompt, tools, model, KV precision, context or chunk size.

## Evidence inputs

Use the exact captured first and second scientific request JSON bodies from:

`results-local/capability/capability-000d-fix2/20260821-155539/requests/`

Verify their canonical token counts before testing:

- request 1: 1521 input tokens
- request 2: 1576 input tokens

If exact bodies/token counts cannot be recovered, stop as infrastructure incomplete.

## Two scientific paths

### Path FRESH_R2

Fresh process/model/server state. Load canonical model once, then execute exact request 2 as the first real request.

No preceding request, no cleanup treatment.

### Path SEQUENTIAL_R1_R2

Separate fresh process/model/server state. Execute exact request 1, allow the HTTP response lifecycle to finish normally, then execute exact request 2 immediately in the same process.

No `gc.collect`, `mx.clear_cache`, model reload, prompt mutation or other cleanup treatment between requests.

## Measurements

At minimum sample:

- system free memory and swap
- process RSS
- MLX active memory
- MLX cache memory
- MLX peak memory
- request input tokens
- actual prefill segments
- KV logical/capacity length
- request completion/abort
- post-request idle active/cache/RSS

For sequential path record checkpoints:

- model loaded idle
- immediately before R1
- R1 peak
- immediately after R1 completion
- 1 s / 3 s / 5 s idle after R1, with no cleanup
- immediately before R2
- R2 peak/abort

Do not retain MLX tensors in telemetry structures. Observers must be fail-open and store numeric scalars only.

## Reference lifetime audit

Inspect source/runtime state for residual references after R1:

- request-scoped KV cache
- generator objects
- prompt-processing batches
- logits/hidden states
- response/event buffers
- instrumentation closures
- MLX allocator cache

Do not alter lifetime behavior in this experiment. Report evidence only.

## Hard resource gate

Abort a path if:

- free memory <5%, or
- swap >5600 MB.

A resource abort after actual inference is valid evidence.

## Classification logic

If FRESH_R2 itself crosses the resource gate:

`CAPABILITY_000E_INTRINSIC_REQUEST_SIZE_LIMIT`

provided the path is otherwise valid.

If FRESH_R2 completes but SEQUENTIAL R2 crosses the gate:

`CAPABILITY_000E_INTER_REQUEST_ACCUMULATION`

If both complete safely:

`CAPABILITY_000E_NO_REPRODUCTION`

If instrumentation or exact-request recovery fails:

`CAPABILITY_000E_INFRASTRUCTURE_INCOMPLETE`

## No treatment yet

Do not test:

- step 256/384/etc.
- `mx.clear_cache()`
- `gc.collect()`
- prefix/KV caching
- prompt compression
- tool removal
- KV quantization
- different model representation

Those become separate treatments only after attribution.

## Output

Persist under:

`results-local/capability/capability-000e/<run-id>/`

Return:

- classification
- exact request token counts
- FRESH_R2 result
- SEQUENTIAL R1/R2 result
- checkpoint table for active/cache/RSS/free/swap
- whether R1 residual active/cache remains above loaded-idle baseline
- supported residual-reference findings
- evidence directory
- files created/modified

No Git/HANDOFF/ROADMAP changes from Pi.