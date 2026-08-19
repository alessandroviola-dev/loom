# Stretch 009 — Four-Token KV Autoregressive Parity — Result

Date: 2026-08-19
Valid run: `20260819-183143`
Classification: **FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS**

## Provenance

Runner:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`

Frozen runner blob:
`3e0780850bb65f9dccf07946f89597fa2e4d17e1`

Upstream frozen provenance:
- Stretch 008 scientific source `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`
- Stretch 008 pipefix `8b2ce5902d3ed45c9120273fab415fe67a026d4a`
- Stretch 002 helper `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Environment:
- Apple M1 / 8 GB reference host
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Qwen3-8B 3-bit/group64
- 36 transformer layers
- ordinary BF16 `KVCache`.

## Frozen policy

Prompt token IDs:
`[[1, 42, 2048, 151935]]`

Generation:
- deterministic argmax
- exactly four generated/feedback tokens
- persistent per-layer ordinary `KVCache`
- no tokenizer
- no sampling
- no KV quantization
- no prefetch/double buffering.

Resident control remains the official fully resident Qwen3 plus `make_prompt_cache`.

Streamed path remains embedding -> 36 transformer blocks one at a time -> final norm -> LM head, with 36 persistent KV caches.

## Numerical/token parity

Prompt parity:
- pass true
- max absolute difference **0.0**
- mean absolute difference **0.0**
- first-token equality true.

All four feedback steps pass exact full-logit parity:
- step 1 max/mean diff **0.0 / 0.0**
- step 2 max/mean diff **0.0 / 0.0**
- step 3 max/mean diff **0.0 / 0.0**
- step 4 max/mean diff **0.0 / 0.0**
- top-1 equality true at every step.

Generated sequence:
- resident: **`[1, 374, 264, 4647]`**
- streamed: **`[1, 374, 264, 4647]`**
- sequence equality: true.

## Persistent KV state

Expected offsets:
`4 -> 5 -> 6 -> 7 -> 8`.

Final resident cache offsets: all **8**.
Final streamed cache offsets: all **8**.

Final cache allocation:
- resident **37,748,736 B**
- streamed **37,748,736 B**.

No additional KV capacity block was required because offset 8 remains below the default 256-position allocation boundary.

## Weight residency

Official resident full-model materialized delta:
**3,583,928,320 B**.

Maximum streamed raw-weight stage delta:
**272,269,312 B**.

Resident / max-streamed-stage ratio:
**13.16317396798652x**.

Persistent KV bytes are accounted separately from the raw-weight-stage ratio.

## Per-token transformer timing

For the four streamed feedback tokens, total wall accumulated across the 36 transformer layers only:

Layer materialization:
- 0.188703 s
- 0.188927 s
- 0.188051 s
- 0.188951 s
- mean **0.188658 s/token**.

Layer forward:
- 0.188268 s
- 0.194739 s
- 0.193971 s
- 0.192290 s
- mean **0.192317 s/token**.

Combined mean transformer-only materialization + forward:
**0.380975 s/token**.

This is not end-to-end token latency or physical SSD time. It excludes embedding/head/norm, Python/bookkeeping/GC and other pass overhead, and repeated weight access may be served partly or wholly from macOS page cache. Do not convert this number directly into a claimed production tok/s figure.

## Host/resource telemetry

Launch gate:
- 67% free / 595.62 MB swap
- 67% free / 595.62 MB swap
- 68% free / 595.62 MB swap.

Whole run:
- minimum free memory **21%**
- peak swap **1401.94 MB**
- peak child RSS **641.656 MB**
- disk **36.281 -> 36.281 GiB**.

Phase-scoped diagnostic buckets:
- resident: min free **21%**, peak swap **1401.94 MB**, peak RSS **354.328 MB**
- stream prompt: min free **64%**, peak swap **1321.94 MB**, peak RSS **348.453 MB**
- stream tokens: min free **64%**, peak swap **1305.94 MB**, peak RSS **251.5 MB**.

Whole-run extrema include the resident control. Phase buckets are diagnostic because polling can miss short peaks.

## Canonical interpretation

Stretch 009 establishes a short multi-token autoregressive sequence with persistent KV state and exact resident-vs-streamed parity at every generated step.

The architecture remains stable across four repeated token passes while maximum raw-weight-stage residency remains ~272.27 MB rather than the complete 3.584 GB model tensor payload.

This is stronger than the one-token proof but is still not a usable-generation benchmark. It does not yet establish tokenizer/text behavior, long-run stability, the 256-position KV allocation transition, physical storage bytes/token, or optimized end-to-end throughput.

## Decision

Proceed to a longer deterministic continuation before adding tokenizer or optimization. Change only continuation depth from 4 to 16 generated/feedback tokens. Preserve the same prompt, argmax policy, ordinary BF16 KVCache, resident control, phase-streamed weight policy and guardrails. Record full-pass wall per streamed token in addition to the already collected transformer-only timing.