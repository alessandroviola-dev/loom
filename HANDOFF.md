# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_011_MATERIALIZATION_IO_ATTRIBUTION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No automatic rescue ladders or hidden retries.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute whole-run telemetry to a sub-phase without phase-scoped evidence.
- Long child runs must use file-backed state/final/stdout/stderr or otherwise drain pipes.
- Do not equate repeated safetensors materialization time with physical SSD throughput; macOS page cache may satisfy reads.
- Do not purge macOS caches casually to manufacture a cold-cache state.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Stretch disk is ~36.27 GiB free; no download is planned.

## Frozen capability references

Canonical Ollama/MLX 4B `qwen3.5:4b-mlx`, context 4096:
- Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6, generation 16.01 tok/s
- Pi Agentic Coding 001: delivery-adjusted 77.15, strict 60.00, delivery 6/6, ~612 s.

llama.cpp 4B Q4 efficiency reference:
- pp512 230.85 tok/s
- tg128 22.33 tok/s.

Direct MLX Qwen3-8B 3-bit coding reference:
- COMPLETE
- min free 14%
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6
- technically stable but not promoted on quality.

## Track A — Amplify

Amplifier 001–003 characterized a resource boundary in the canonical 4B repair workflow. Do not claim a leak or specific KV/allocator cause.

Amplifier 004 remains preregistered/queued:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- one change: repair-feedback variable detail capped at 768 UTF-8 bytes.

Stretch remains primary while architectural evidence continues to improve.

# Track B — Stretch / Memory Hierarchy

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Environment/config:
- Qwen3, hidden 4096, 36 layers, vocab 151936
- 32 attention heads, 8 KV heads, head dim 128
- RMSNorm eps 1e-6
- `tie_word_embeddings=false`
- 3-bit/group64
- mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.

Weight layout:
- complete tensor payload 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Frozen Stretch results

### 001 — COMPLETE PASS
`LAYER_ADDRESSABLE_IO_PASS`: all 36 transformer layers exactly addressable and selectively readable.

### 002 — COMPLETE PASS
`SINGLE_LAYER_MLX_EVICTION_PASS`: one layer materializes 0 -> 84,427,264 -> 0 B active.

### 003 — COMPLETE PASS
`TWO_LAYER_BOUNDED_RESIDENCY_PASS`: repeated one-layer cycles remain bounded in one MLX process.

### 004 — COMPLETE PASS
`TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`: first real Qwen3 block compute; exact resident/streamed activation parity.

### 005 — COMPLETE PASS
`EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`: resident/streamed layer-weight ratio 7.999223710482908x; exact parity.

### 006 — COMPLETE PASS
Valid run `20260819-164605`, `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`:
- resident transformer body observed 3,039,315,964 B
- max streamed layer 84,427,264 B
- ratio 35.99922371048291x
- all 36 layer cycles reclaim layer weights
- max/mean activation diff 0.0 / 0.0.

Earlier transform launch is harness-only/no scientific result.

### 007A — COMPLETE PASS
Run `20260819-165247`, `SHARED_COMPONENT_ANATOMY_PASS`:
- embedding 272,269,312 B
- final norm 8,192 B
- LM head 272,269,312 B
- other 0
- embedding/head untied.

### 007B — COMPLETE PASS
Run `20260819-170334`, `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`:
- official resident model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x
- full logits `[1,4,151936]` max/mean diff 0.0 / 0.0
- top-1 equality true.

### 008 — COMPLETE PASS
Scientific runner/blob:
- `scripts/stretch_one_token_kv_autoregressive_parity_008.py`
- `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`.

Harness pipefix/blob:
- `scripts/stretch_one_token_kv_autoregressive_parity_008_pipefix.py`
- `8b2ce5902d3ed45c9120273fab415fe67a026d4a`.

First launch stalled on an undrained verbose stdout pipe; harness-only/no scientific result.

Valid run `20260819-173553`, `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`:
- prompt and feedback logits exact parity
- generated token `1` equal
- persistent 36-layer KV offsets 4 -> 5
- total KV 37,748,736 B
- resident model 3,583,928,320 B vs max streamed raw-weight stage 272,269,312 B.

Result:
`research/stretch/one-token-kv-autoregressive-parity-008-result.md`.

### 009 — COMPLETE PASS
Runner/blob:
- `scripts/stretch_four_token_kv_autoregressive_parity_009.py`
- `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Valid run `20260819-183143`, `FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`:
- prompt + all 4 feedback steps max/mean logit diff 0.0 / 0.0
- generated sequence resident/streamed `[1,374,264,4647]`
- KV offsets 4 -> 5 -> 6 -> 7 -> 8
- KV stays 37,748,736 B
- resident model 3,583,928,320 B
- max streamed stage 272,269,312 B
- ratio 13.16317396798652x
- mean 36-layer materialization 0.188658 s/token
- mean 36-layer forward 0.192317 s/token
- stream-token bucket min free 64%.

Result:
`research/stretch/four-token-kv-autoregressive-parity-009-result.md`.

### 010 — COMPLETE PASS

Plan:
`research/stretch/sixteen-token-autoregressive-stability-010-plan.md`

Runner/blob:
- `scripts/stretch_sixteen_token_autoregressive_stability_010.py`
- `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Valid run `20260819-183844`:
`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`.

Scientific change vs 009: continuation depth 4 -> 16 only.

Correctness/stability:
- prompt parity max/mean 0.0 / 0.0
- all 16 feedback steps max/mean 0.0 / 0.0
- top-1 equality at every step
- resident and streamed generated sequence identical:
  `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- final resident/streamed KV offsets all 20
- final KV bytes 37,748,736 / 37,748,736 B.

Weight residency unchanged:
- resident full model 3,583,928,320 B
- max streamed stage 272,269,312 B
- ratio 13.16317396798652x.

Unoptimized timing:
- 36-layer materialization walls:
  `[0.212377,0.190494,0.18926,0.187676,0.464371,1.359481,0.519632,1.396424,1.413411,1.425179,1.425537,1.442005,1.412515,1.404428,1.41408,1.397497]`
- mean layer materialization 0.990898 s/token
- mean layer forward **0.192486 s/token**, approximately stable across the run
- full pass walls `[1.863135,1.838579,1.849972,1.833425,2.366761,3.336781,2.38608,3.34347,3.425303,3.465824,3.485435,3.454962,3.358077,3.369774,3.487604,3.358349]`
- mean full pass 2.888971 s/token
- median full pass 3.350773 s/token
- logical streamed throughput 0.346144 token/s.

Resource:
- whole-run min free 24%, peak swap 1563.31 MB, peak child RSS 764.844 MB
- stream prompt min free 70%
- stream tokens min free 66%, peak RSS 354.938 MB
- disk 36.272 -> 36.270 GiB.

Important new finding:
- tokens 1–4 materialize all 36 layer weights in ~0.19–0.21 s
- token 5/7 are transitional
- token 6 and tokens 8–16 are ~1.36–1.44 s
- transformer forward remains ~0.19 s/token.

Canonical interpretation:
> Sixteen-token persistent-KV autoregressive correctness is established with exact resident parity. The current runtime also shows a late-run materialization slowdown while compute remains stable. Timing alone does not establish whether the cause is physical storage/page-cache behavior or MLX/allocator/materialization lifecycle.

Result:
`research/stretch/sixteen-token-autoregressive-stability-010-result.md`.

## Stretch 011 — Materialization I/O Attribution — READY

Plan:
`research/stretch/materialization-io-attribution-011-plan.md`

Runner:
`scripts/stretch_materialization_io_attribution_011.py`

Runner blob:
`16125f7eb0b2fb662591e194de0498513a563a6d`.

Frozen upstream:
- Stretch 009 blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- Stretch 010 transform blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Scientific workload: exact Stretch 010 16-token workload, **unchanged**.

New instrumentation only:
- Darwin `/usr/lib/libproc.dylib`
- `proc_pid_rusage(..., RUSAGE_INFO_V2)`
- cumulative process `ri_diskio_bytesread`, `ri_diskio_byteswritten`, `ri_pageins`, resident size and physical footprint
- snapshots around each layer `build_block()` and `mx.eval(block.parameters())`
- equivalent shared-stage/pass-level snapshots
- early tokens 1–4 vs late tokens 8–16 descriptive I/O means
- diagnostic correlation between materialization wall and disk-read/page-in deltas.

No OS cache purge, tokenizer, sampling, prefetch, KV quantization or other scientific change.

Primary PASS:
`MATERIALIZATION_IO_ATTRIBUTION_PASS`.

Interpretation boundary:
`ri_diskio_bytesread` is per-process Darwin disk-I/O accounting, not automatically an exact count of model-file SSD bytes. A timing/I/O correlation is diagnostic evidence, not causal proof by itself.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_materialization_io_attribution_011.py
python3 scripts/stretch_materialization_io_attribution_011.py
```

No download is expected.

If 011 attributes the slow regime to actual disk/page-in activity, characterize storage/page-cache policy next. If disk/page-in counters remain flat while materialization slows, investigate MLX/allocator/materialization lifecycle. Tokenizer/text integration remains queued until this performance boundary is characterized.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.