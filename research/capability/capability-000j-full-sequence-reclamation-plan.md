# CAPABILITY 000J — Full-sequence targeted reclamation validation

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Does the exact CAPABILITY 000I request-local treatment keep the full captured R1-R6 sequence safe when applied after every completed response, without changing model semantics or using global cleanup?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- prefill_step_size 512
- enable_thinking=false
- same tokenizer/chat template/tool schemas
- exact R1-R6 bodies captured in CAPABILITY 000H

## Sole treatment

After each completed HTTP response, detach only the stale completed `GenerationBatch.Response.prompt_cache` identified in CAPABILITY 000I.

Forbidden: `mx.clear_cache()`, `gc.collect()`, allocator/global queue reset, process restart between requests, prompt/model/context/KV/tool/prefill-step changes.

## Design

Use two fresh comparable processes:

1. CONTROL: exact R1->R6 sequentially, natural server behavior, no treatment.
2. TREATMENT: exact R1->R6 sequentially, apply the 000I targeted detach after every completed response before the next request.

Host admission before each process: free >=60%, swap <=5600 MB. No inference preflight in the scientific process.

## Per-turn measurements

For every request record:

- input tokens and actual M segments
- response completion / resource abort
- prefill and generation wall
- KV logical/capacity
- MLX active/cache immediately before request
- MLX peak
- MLX active/cache immediately after response, before detach
- treatment-only active/cache immediately after detach
- system minimum free and peak swap
- response bytes/text, tool-call structure/arguments and finish reason

Also record the stale response prompt-cache bytes detached after each completed treatment turn.

## Resource policy

Hard abort after admitted execution begins if free <5% or swap >5600 MB. No rescue.

## Success

Treatment is promotable to integrated Pi validation only if:

- it reaches strictly farther than control, ideally all R1-R6;
- every completed treated response matches the corresponding canonical/fresh behavior at the available semantic/tool-call level;
- no global cleanup is used;
- active-memory boundary state remains materially lower than control where comparable;
- no new lifecycle/harness failure appears.

## Classifications

- `CAPABILITY_000J_FULL_SEQUENCE_RECLAMATION_PASS`
- `CAPABILITY_000J_RECLAMATION_PARTIAL_GO`
- `CAPABILITY_000J_RECLAMATION_NO_GO`
- `CAPABILITY_000J_INFRASTRUCTURE_INCOMPLETE`

A full PASS means all six treatment requests complete safely. Partial GO means treatment materially extends the safe sequence but still hits the resource floor later. No-GO means no material extension/safety benefit.

## Next-step rule

Do not run integrated Pi or CAPABILITY 001 inside 000J. ChatGPT reviews the full-sequence result first.