# CAPABILITY 000D Fix2 — Resource abort result

Date: 2026-08-21
Status: COMPLETE / SCIENTIFIC RESOURCE RESULT
Classification: `CAPABILITY_000D_FIX2_RESOURCE_ABORT`

## Purpose

Test whether the canonical Qwen3-8B 3-bit system can complete the frozen multi-turn Pi `numbers.txt` tool task at context 4096 with the sole runtime treatment `prefill_step_size=512`.

## Harness status

Fix2 repaired the remaining instrumentation lifecycle defect. The direct preflight completed through the canonical local model, returned `OK.`, and produced a finalized turn record. Exact `OK` punctuation was diagnostic only and no longer gated infrastructure admission.

Fix1 root cause was that `Generator.completion_usage_response` was not an `mlx_lm.server.APIHandler` lifecycle hook for the non-stream path. Fix2 moved completion finalization to the actual handler lifecycle and made telemetry fail-open.

Telemetry errors during the scientific run: 0.

## Scientific result

The model completed the first real Pi turn and emitted/executed `read numbers.txt`.

Turn 1:
- input: 1521 tokens
- M segments: `512,512,425,68,3`
- prefill: 23.091 s
- generated: 35 tokens
- generation: 11.690 tok/s
- KV logical/capacity: 1555 / 1792
- peak MLX: 4075.12 MB
- minimum free memory: 6%
- peak swap: 2284.25 MB
- action: `read numbers.txt`

The second model request then began with 1576 input tokens. Its first 512-token prefill segment started, but the hard resource gate fired at 4% free memory before completion.

Turn 2 incomplete:
- input: 1576 tokens
- first 512 segment started
- peak MLX observed: 4146.45 MB
- minimum free memory: 4%
- swap: 2193.69 MB at abort
- no second tool action completed

`answer.txt` was not created. `numbers.txt` remained byte-identical, SHA-256 `5c6f702ac103f5832a4285cd4c4d10f8f508a13d1ba3dd796f4faaee1ec7c68c`.

Provider identity remained `loom-mlx-local -> localhost -> canonical Qwen3-8B-3bit`; no fallback was observed.

Local evidence:
`results-local/capability/capability-000d-fix2/20260821-155539/`

## Interpretation

This is the first valid integrated multi-turn scientific result for step 512.

`prefill_step_size=512` is sufficient for the first ~1521-token Pi request and genuine tool execution, but it does not provide enough headroom for the immediately following ~1576-token request under the observed host/runtime state.

The failure does not yet establish that 1576 tokens intrinsically exceed the 8 GB envelope. The second request contained only 55 more input tokens than the first, while observed peak MLX increased by ~71.33 MB. A separate experiment is required to distinguish prompt-length pressure from inter-request allocator/cache/reference retention.

Do not promote 512 as a sustainable multi-turn Pi default yet.

## Next question

Run a fresh-vs-sequential second-turn attribution using the exact captured request bodies:

1. second request alone from a fresh model/server state;
2. first request followed by second request in the same server process with no cleanup treatment;
3. compare idle MLX active/cache/system state between them.

No model, prompt, tool, context, KV format or chunk-size change should be made in that attribution experiment.