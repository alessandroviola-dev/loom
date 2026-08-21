# CAPABILITY 000K — Allocator-cache boundary reclamation

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

After the proven 000I request-local `prompt_cache` detach, does explicitly releasing MLX allocator cache at a completed-request boundary restore system-free headroom enough to make sequential R2 safe, without changing model semantics?

## Frozen subject

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- exact captured R1/R2 from CAPABILITY 000H
- same tokenizer/chat template/tool schemas/server path

## Control and treatment

CONTROL: apply only the proven 000I stale completed-response `prompt_cache` detach after R1, then execute R2.

TREATMENT: apply that same targeted detach after R1, then call only the documented MLX allocator-cache clearing operation (`mx.clear_cache()` or exact installed equivalent), then execute R2.

This is a single new factor: allocator-cache release after the already-proven targeted detach.

## Measurements

At loaded idle, post-R1 pre-detach, post-detach, post-cache-clear, immediately before R2 and R2 peak record:

- MLX active/cache/peak
- system free % and swap
- server RSS
- boundary latency of detach and cache clear separately
- R1 response/tool-call equivalence
- R2 completion/tool behavior

No `gc.collect()`, process restart, model reload, context/KV/model/prompt/tool/prefill changes or host-memory manipulation.

## Decision

PASS requires material cache reduction, improved system-free headroom, R2 completion above the hard 5% floor, unchanged semantics, and acceptable boundary latency.

Classifications:

- `CAPABILITY_000K_ALLOCATOR_CACHE_RECLAMATION_PASS`
- `CAPABILITY_000K_ALLOCATOR_CACHE_RECLAMATION_NO_GO`
- `CAPABILITY_000K_INFRASTRUCTURE_INCOMPLETE`

Do not run CAPABILITY 001 automatically.