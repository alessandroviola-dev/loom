# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_012_EIGHT_LAYER_PERSISTENT_HOTSET_READY`

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
- Do not equate logical safetensors materialization time or Darwin process disk-I/O accounting with forensic model-file SSD throughput.
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
- prompt + 4 feedback steps exact logits
- sequence `[1,374,264,4647]` identical
- KV 4 -> 8, stable 37,748,736 B
- mean 36-layer materialization 0.188658 s/token
- mean 36-layer forward 0.192317 s/token
- stream-token bucket min free 64%.

Result:
`research/stretch/four-token-kv-autoregressive-parity-009-result.md`.

### 010 — COMPLETE PASS
Runner/blob:
- `scripts/stretch_sixteen_token_autoregressive_stability_010.py`
- `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Valid run `20260819-183844`, `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`:
- exact prompt + 16 feedback logits
- resident/streamed sequence identical `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- final KV offset 20; 37,748,736 B
- resident full model 3,583,928,320 B
- max streamed stage 272,269,312 B
- ratio 13.16317396798652x
- mean transformer forward 0.192486 s/token
- mean full pass 2.888971 s/token
- median full pass 3.350773 s/token
- logical streamed throughput 0.346144 token/s
- materialization regime changes from ~0.19 s early to ~1.4 s late while forward stays ~0.19 s.

Result:
`research/stretch/sixteen-token-autoregressive-stability-010-result.md`.

### 011 — COMPLETE PASS

Plan:
`research/stretch/materialization-io-attribution-011-plan.md`

Runner/blob:
- `scripts/stretch_materialization_io_attribution_011.py`
- `16125f7eb0b2fb662591e194de0498513a563a6d`.

Valid run `20260819-185036`:
`MATERIALIZATION_IO_ATTRIBUTION_PASS`.

Correctness/state:
- exact prompt + all 16 feedback logits
- same 16-token generated sequence as 010
- final KV offsets all 20
- KV 37,748,736 B
- resident model 3,583,928,320 B
- max streamed stage 272,269,312 B
- ratio 13.16317396798652x.

Timing reproduced:
- materialization token 1: 0.215334 s
- token 2: 0.397099 s
- token 3 onward ~1.39–1.41 s
- mean materialization 1.261344 s/token
- mean transformer forward 0.191414 s/token
- mean full pass 3.200954 s/token
- median full pass 3.351453 s/token
- logical streamed throughput 0.312407 token/s.

Darwin process disk-I/O attribution:
- materialization disk reads/token:
  `[48513024,389873664,3023896576,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840,3039395840]`
- late steady-state transformer materialization ~3,039,395,840 B/token, very near frozen transformer payload 3,039,381,504 B
- late full-pass disk-read accounting ~3.584 GB/token, very near complete tensor payload 3,583,928,320 B
- build/select reads negligible compared with materialization
- materialization page-ins all zero
- materialization-time vs disk-read Pearson **0.9995866107996246**.

Early 1–4 vs late 8–16:
- mean materialization wall 0.85343275 -> 1.3990707778 s
- mean materialization disk reads 1,625,419,776 -> 3,039,395,840 B
- mean full-pass disk reads 1,959,089,152 -> 3,584,055,068 B.

Resource:
- whole-run min free 22%
- peak swap 1606.94 MB
- stream-token bucket min free 65%
- disk 36.267 -> 36.269 GiB.

Canonical interpretation:
> Pure one-layer-at-a-time dense autoregressive streaming reaches a steady state where Darwin process disk-I/O accounting is approximately one transformer-body traversal during layer materialization and approximately one full-model payload during the complete pass per generated token. The near-payload deltas and ~0.9996 timing correlation strongly support I/O as the dominant late materialization cost, but `ri_diskio_bytesread` is not a forensic per-file SSD trace.

Result:
`research/stretch/materialization-io-attribution-011-result.md`.

## Stretch 012 — Eight-Layer Persistent Hotset — READY

Plan:
`research/stretch/eight-layer-persistent-hotset-012-plan.md`

Runner:
`scripts/stretch_eight_layer_persistent_hotset_012.py`

Runner blob:
`8e10660af778655a279f30e7d59785163bc204e3`.

Frozen reconstruction:
- Stretch 009 source blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- Stretch 010 transform blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`
- Stretch 011 instrumentation blob `16125f7eb0b2fb662591e194de0498513a563a6d`.

Single scientific change:
- transformer layers **0..7** are materialized once and retained across streamed prompt + all 16 token passes.

Unchanged:
- layers 8..35 remain one-at-a-time streamed/evicted
- embedding/final norm/LM head remain streamed
- same prompt, 16-token argmax loop, resident control, BF16 KVCache, parity/cache gates, I/O instrumentation and resource guardrails
- no tokenizer/sampling/KV quantization/prefetch/cache purge/download.

Expected hotset payload:
**675,418,112 B**.

Expected worst simultaneous raw-weight budget:
- hotset + embedding/head max new stage
- 675,418,112 + 272,269,312 = **947,687,424 B** (~903.79 MiB).

Expected late transformer process-read accounting if retention works:
~3,039,395,840 - 675,418,112 ≈ **2,363,977,728 B/token**.

Expected late full-pass process reads may move from ~3.584 GB toward ~2.909 GB/token. These are diagnostic expectations, not PASS thresholds.

Primary PASS:
`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_eight_layer_persistent_hotset_012.py
python3 scripts/stretch_eight_layer_persistent_hotset_012.py
```

No download is expected.

If 012 validates the expected reduction in repeated process reads without losing correctness/resource safety, build a small retained-layer frontier in separate preregistered experiments before choosing a practical profile. Tokenizer/text integration remains queued until the first RAM-for-I/O optimization point is characterized.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.