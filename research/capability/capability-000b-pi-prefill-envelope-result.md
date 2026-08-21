# CAPABILITY 000B — Pi prefill envelope — result

Date: 2026-08-21
Status: COMPLETE
Classification: `CAPABILITY_000B_EXACT_REPLAY_COMPLETE`

## Exact request

The first real Pi request for the canonical Qwen3-8B 3-bit bridge contains **1504 input tokens**:

- system / agent instructions: 608
- user task: 65
- tool schemas: 814
- other protocol/template tokens: 17

Context headroom at the frozen 4096-token window is 2592 tokens. Therefore the immediate failure is not exhaustion of the context limit itself.

## Prefill behavior

The current MLX path performs segmented/chunked prefill with observed M shapes `[1,1430]`, `[1,70]`, `[1,3]` and `prefill_step_size=2048`.

Full-position logical logits graphs are constructed, but prefill logits are discarded and are not materialized. Actual materialized logits are last-token only, shape `[1,1,151936]`. Full-sequence logits are therefore not supported as the memory-cliff cause.

KV uses ordinary BF16 `BatchKVCache` and allocates in 256-token blocks. For the 1504-token request the allocated capacity is 1536 tokens, with K/V shape `[1,8,1536,128]` per layer across 36 layers.

## Memory evidence

Exact direct replay of the Pi request completed without Pi-process overhead but reached only **6% minimum free memory**, one percentage point above the inherited 5% abort floor.

Observed exact-replay metrics:

- input tokens: 1504
- prefill wall: 20.61 s
- minimum free memory: 6%
- peak swap: 1675.0 MB
- peak MLX memory: 4180.1 MB

Dominant allocations:

- resident model weights: ~3417.9 MiB
- persistent first KV capacity increment: ~216 MiB
- transient first M=1430 prefill peak above post-prefill active: ~546 MiB

Theoretical BF16 KV for the actual 1504-token sequence is 211.5 MiB. Theoretical full-sequence logits would be 435.9 MiB BF16 or 871.7 MiB FP32, but those logits are not materially instantiated by the observed path.

## Attribution

- weights: `PROVEN`
- KV: `PROVEN`
- full-sequence logits: `NOT_SUPPORTED`
- qmm / prefill temporaries: `STRONGLY_SUPPORTED`
- attention temporaries: `NOT_SUPPORTED`
- Pi process as the cliff cause: `NOT_SUPPORTED`
- long agent/tool prompt as a driver of large-prefill M: `STRONGLY_SUPPORTED`
- unidentified share of ~546 MiB transient: `PLAUSIBLE`

## Decision

Do not change model, quantization, KV precision, context size or tool semantics yet.

The first justified treatment is to reduce the peak M of the unchanged exact Pi prefill by using smaller prefill chunks. This directly targets the strongly-supported transient allocation while preserving the exact 1504-token prompt, all four Pi tools, Qwen3-8B 3-bit weights, BF16 KV and the 4096 context window.

Next experiment: `CAPABILITY 000C — bounded prefill-chunk frontier`.

Local raw evidence:
`results-local/capability/capability-000b/20260821-143705/`
