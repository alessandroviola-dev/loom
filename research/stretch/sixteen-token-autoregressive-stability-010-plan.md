# Stretch 010 — Sixteen-Token Autoregressive Stability — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Does the exact resident-vs-phase-streamed autoregressive parity established by Stretch 009 remain stable across a longer deterministic continuation, while persistent ordinary BF16 KV state and raw-weight residency remain bounded?

## Single scientific change

Relative to valid Stretch 009:

**generated/feedback continuation depth: 4 -> 16 tokens**.

No other scientific factor changes.

Instrumentation is extended to expose the already-measured full streamed pass wall per token; this is measurement only, not a model/runtime policy change.

## Frozen provenance

Source runner:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`

Required source blob:
`3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Upstream frozen provenance remains:
- Stretch 008 scientific source `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`
- Stretch 008 pipefix `8b2ce5902d3ed45c9120273fab415fe67a026d4a`
- Stretch 002 helper `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Frozen model/environment:
- Qwen3-8B 3-bit/group64
- Apple M1 / 8 GB
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- 36 transformer layers
- 8 KV heads / head dim 128
- untied embedding and LM head.

## Preserved execution policy

Prompt token IDs:
`[[1, 42, 2048, 151935]]`.

Generation:
- deterministic argmax
- no tokenizer
- no sampling
- no KV quantization
- no prefetch/double buffering
- no model download.

Resident control:
- official fully resident Qwen3
- official `make_prompt_cache`.

Streamed path:
- embedding phase-streamed
- each of 36 transformer blocks materialized one at a time
- one persistent ordinary BF16 `KVCache` per layer
- final RMSNorm
- LM head phase-streamed.

Harness transport remains file-backed:
- progress `child-state.json`
- final payload `child-final.json`
- stdout/stderr file handles
- no undrained verbose captured pipe.

## KV expectations

Prompt length: 4.

After 16 feedback passes, final offset must be:
**20**.

Required offset sequence:
- prompt: 4
- token 1: 5
- ...
- token 16: 20.

All offsets remain below the first ordinary `KVCache` capacity boundary at 256 positions.

Expected allocated cache payload therefore remains approximately/exactly the established first-block allocation:
**37,748,736 B total across 36 layers**.

Any >1 MiB growth relative to prompt allocation before offset 20 is a failure under the frozen gate.

## Numerical/token gates

PASS requires:
1. prompt-with-KV full-logit parity;
2. first argmax token equality;
3. full-logit numerical parity at all 16 feedback steps;
4. top-1 equality at all 16 feedback steps;
5. identical 16-token resident and streamed generated sequence;
6. all 36 cache offsets equal the expected position after each step;
7. resident and streamed cache allocations remain within the frozen size gate;
8. all existing streamed embedding/layer/norm/head materialization gates pass on prompt and every token pass;
9. existing host/runtime safety guardrails remain satisfied.

Numerical threshold remains the Stretch 009 rule:
`1e-5 + 1e-5 * resident_max_abs` per comparison.

## Timing instrumentation

For each of 16 streamed feedback passes record:
- total 36-layer parameter-materialization wall;
- total 36-layer transformer-forward wall;
- complete phase-streamed token-pass wall (`embedding -> 36 layers -> norm -> LM head`, including existing GC/bookkeeping inside the pass).

Summaries:
- mean/median layer-materialization seconds/token;
- mean/median layer-forward seconds/token;
- mean/median full-pass seconds/token;
- logical streamed tokens/second = `1 / mean_full_pass_seconds`.

Interpretation boundary:
The logical tok/s is runtime wall time under the current host/cache state. It is **not physical SSD throughput** and must not be converted into an SSD bytes/token claim because macOS page cache may satisfy repeated safetensors reads.

## Resource interpretation

System-wide free memory and swap remain decisive for safety.
Process RSS and phase-scoped polling are diagnostic.

Whole-run extrema include the resident control; streamed phase buckets must be used when discussing streamed host pressure.

## Classifications

Primary PASS:
`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`.

Existing failure classes from Stretch 009 remain semantically applicable, including:
- `PREFLIGHT_FAIL`
- `HOST_STATE_NOT_READY`
- `PARTIAL_RESOURCE_FAIL`
- `TELEMETRY_FAIL`
- `RUNTIME_FAIL`
- `RESIDENT_CONTROL_SIZE_MISMATCH`
- `KV_CACHE_STATE_FAIL`
- `KV_CACHE_GROWTH_UNEXPECTED`
- `STREAMED_WEIGHT_STAGE_FAIL`
- `PROMPT_KV_NUMERICAL_PARITY_FAIL`
- `GENERATED_TOKEN_MISMATCH`
- `MULTI_TOKEN_KV_NUMERICAL_PARITY_FAIL`
- `MULTI_TOKEN_TOP1_MISMATCH`
- `GENERATED_SEQUENCE_MISMATCH`.

A failure must be attributed to the relevant gate; harness defects are not model/runtime failures.

## Decision after PASS

A PASS will establish medium-short deterministic stability at 16 generated tokens and a first stable logical end-to-end per-token timing estimate.

Then choose the next single factor based on the result:
- likely tokenizer/text integration if stability is clean;
- cache-capacity boundary as a separate later experiment;
- prefetch/double buffering only after the unoptimized runtime is frozen.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_sixteen_token_autoregressive_stability_010.py
python3 scripts/stretch_sixteen_token_autoregressive_stability_010.py
```

No download is expected.