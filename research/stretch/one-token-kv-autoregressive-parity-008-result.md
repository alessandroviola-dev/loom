# Stretch 008 — One-Token KV Autoregressive Parity — Result

Date: 2026-08-19
Valid run: `20260819-173553`
Classification: **ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS**

## Provenance

Scientific runner:
`scripts/stretch_one_token_kv_autoregressive_parity_008.py`

Frozen scientific runner blob:
`03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`

Harness-only pipe fix:
`scripts/stretch_one_token_kv_autoregressive_parity_008_pipefix.py`

Pipefix blob:
`8b2ce5902d3ed45c9120273fab415fe67a026d4a`

The earlier launch stalled after `stream_token_layer_17_complete` because per-state JSON was emitted into a captured stdout pipe that the parent did not drain during execution. That launch is separately recorded in `research/stretch/one-token-kv-autoregressive-parity-008-harness-note.md` and has **no scientific result**. The valid rerun changed only harness stdout behavior: per-state `child-state.json` writes and the final completion payload were preserved; model, cache, prompt, parity gates, weight policy and safety guardrails were unchanged.

Frozen upstream provenance:
- Stretch 007B source blob `b08c9b44ae062ee259ab6641575e44c4d7d753e6`
- Stretch 002 helper blob `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Environment:
- Apple M1 / 8 GB
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Qwen3-8B 3-bit/group64
- 36 transformer layers
- 8 KV heads / head dim 128
- `tie_word_embeddings=false`.

## Frozen autoregressive policy

Prompt token IDs:
`[[1, 42, 2048, 151935]]`

Generation:
- deterministic argmax
- exactly one generated token
- same persistent per-layer `KVCache` state reused for the feedback pass
- no tokenizer
- no sampling
- no multi-token loop
- no cache quantization.

Resident control:
- official fully resident Qwen3
- official `make_prompt_cache`.

Streamed path:
- embedding phase-streamed
- each transformer layer materialized one at a time
- 36 persistent `KVCache` objects remain resident
- final RMSNorm phase
- LM head phase-streamed.

## PASS results

### Prompt-with-KV parity

- pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- threshold: `0.00018125000000000001`
- resident/streamed generated token equality: true
- generated token: **`[[1]]`**.

### Persistent KV state after prompt

Resident:
- total cache bytes: **37,748,736 B**
- all 36 layer offsets: **4**.

Streamed:
- total cache bytes: **37,748,736 B**
- all 36 layer offsets: **4**.

The default ordinary BF16 `KVCache` allocation is 1,048,576 B per layer because capacity is allocated in 256-position blocks.

### Feedback of generated token

The generated token `[[1]]` was fed back through the same resident and streamed cache states.

Post-token parity:
- pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- threshold: `0.00023750000000000003`
- post-token top-1 equality: true.

Persistent KV state after feedback:

Resident:
- total cache bytes: **37,748,736 B**
- all offsets: **5**.

Streamed:
- total cache bytes: **37,748,736 B**
- all offsets: **5**.

The cache did not allocate another capacity block between offsets 4 and 5.

## Weight residency

Official resident full-model materialized delta:
**3,583,928,320 B**.

Maximum streamed raw-weight stage delta:
**272,269,312 B**.

Resident / maximum streamed raw-weight-stage ratio:
**13.16317396798652x**.

The persistent KV cache is accounted separately from the raw-weight-stage ratio.

## Host/resource telemetry

Launch gate:
- 72% free / 1223.88 MB swap
- 72% free / 1223.88 MB swap
- 74% free / 1223.88 MB swap.

Whole valid run:
- minimum free memory: **26%**
- peak swap: **1583.75 MB**
- peak child RSS: **878.5 MB**
- disk: **36.294 -> 36.290 GiB**.

Diagnostic phase buckets captured by polling:
- `stream_prompt`: min free **64%**, peak swap **1479.75 MB**, peak child RSS **347.578 MB**, 7 samples
- `stream_token`: min free **69%**, peak swap **1471.75 MB**, peak child RSS **166.531 MB**, 3 samples.

The phase buckets are diagnostic only because polling can miss short phases. Whole-run minima/maxima include the resident control and must not be attributed specifically to streamed execution.

## Canonical interpretation

Stretch 008 is the first LOOM result to establish **actual autoregressive cache reuse** for the streamed Qwen3-8B path.

The resident and phase-streamed executions:
- produce identical prompt logits;
- choose the same deterministic next token;
- maintain the same 36 persistent KV cache states;
- advance all cache offsets from 4 to 5;
- produce identical logits after feeding the generated token back through the persisted cache.

Meanwhile the raw model weights remain phase-streamed, with maximum simultaneous raw-weight materialization ~272.27 MB rather than the complete 3.584 GB tensor payload.

This is a one-token deterministic autoregressive proof, not yet a usable generation benchmark. It does not establish long-run stability, text-tokenizer behavior, sampling correctness, physical SSD bandwidth per token or acceptable tokens/second.

## Decision

Proceed to Stretch 009: extend the same frozen resident-vs-streamed architecture to a short deterministic multi-token argmax loop, preserving persistent ordinary KVCache state and checking numerical/token parity at every generated step. Use phase/file-based child telemetry to avoid captured-pipe stalls and record per-token materialization/forward time before any prefetch or cache optimization.