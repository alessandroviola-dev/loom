# CAPABILITY 000I — Targeted request-local reclamation result

Date: 2026-08-21
Classification: `CAPABILITY_000I_TARGETED_RECLAMATION_PASS`

## Finding

The retained request-boundary MLX state has a precise request-local owner.

`mlx_lm.server.ResponseGenerator._generate` keeps the finished local `gen_responses` object alive while the generation thread returns to its idle loop. The finished `GenerationBatch.Response` retains its `prompt_cache` list, which in turn retains the completed request's 36 KVCache objects.

Relevant source paths recovered locally:

- `mlx_lm/server.py`, `ResponseGenerator._generate`, approximately lines 882-912; finished response handled without clearing/rebinding `gen_responses` before the idle loop around 847-864.
- `mlx_lm/generate.py`, `GenerationBatch.next/filter`, approximately lines 1383-1462; batch-owned caches are released, but the stale response-local cache remains reachable.

This is a completed-request lifecycle retention bug/state, not a need to shrink the model or prompt.

## Object evidence

After R1 HTTP completion:

- `GenerationBatch.Response`: alive through `_generate` frame local `gen_responses`; owns ~218.39 MiB KV plus ~0.29 MiB logits metadata.
- 36 `KVCache` objects: alive through `Response.prompt_cache`; ~218.39 MiB.
- `PromptProcessingBatch`: alive structurally through `BatchGenerator._prompt_batch`, but owns 0 retained MLX bytes in this accounting.
- `GenerationBatch`: alive structurally through `BatchGenerator._generation_batch`, owns 0 retained MLX bytes in this accounting.
- `CompletionRequest` / stream iterators: dead by post-response checkpoint.

Metadata-accounted request-local retained state: ~218.68 MiB versus the previously observed +468.30 MiB post-R1 active delta.

## Targeted treatment

After R1 is fully complete, detach only the stale completed `GenerationBatch.Response.prompt_cache`.

No `mx.clear_cache()`, no `gc.collect()`, no allocator reset, no process restart, no queue-wide cleanup, no model/context/KV/prompt/tool/prefill-step change.

## Control vs treatment

Control:

- loaded idle active/cache: 3417.90 / 0.00 MiB
- post-R1 active/cache: 3886.20 / 234.07 MiB
- post-R1 active residual: +468.30 MiB
- R2 peak: 4194.45 MiB
- R2 minimum free: 5%
- R2: PASS

Treatment:

- pre-release active/cache: 3886.20 / 234.07 MiB
- post-release active/cache: 3634.20 / 486.07 MiB
- active recovered: 252.00 MiB
- R2 peak: 4095.95 MiB
- R2 minimum free: 5%
- R2: PASS

Derived:

- active recovered: 252.00 MiB / 53.81% of the observed +468.30 MiB residual
- R2 peak reduction: 98.50 MiB
- free-headroom gain in this run: 0 percentage points

The active-memory reduction is real, while allocator cache increases by roughly the same 252 MiB. Therefore sustained multi-turn behavior must be tested before promoting this as an integrated bridge fix.

## Semantic safety

R1 control and treatment responses were identical at the byte/tool level: identical 1601-byte response, empty text, identical tool call and identical `read(numbers.txt, offset=0, limit=2000)` arguments.

R2 control/treatment first tool call was also identical (`bash/awk`). Token-ID equality was not available because logprobs were disabled.

## Evidence

Local evidence:
`results-local/capability/capability-000i/20260821-170809/`

Local-only scripts created:

- `scripts/capability_000i_request_local_reclamation.py`
- `scripts/capability_000i_targeted_reclamation_phase_b.py`

These implementation scripts remain local until explicitly synchronized.

## Interpretation

CAPABILITY 000I establishes a precise request-local lifecycle cause and demonstrates a targeted release that materially lowers active MLX memory and R2 peak without changing model semantics or using global cleanup.

Because the released active memory becomes allocator cache and system free headroom did not improve in this two-turn run, the next experiment must validate this exact treatment across the full captured R1-R6 sequence before any integrated Pi promotion.