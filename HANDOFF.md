# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; coordinated tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_008_ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Research / safety constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails post-hoc.
- Change one experimental factor at a time where causal attribution matters.
- No automatic context/budget rescue ladders.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute aggregate host telemetry to a sub-phase unless phase-scoped telemetry exists.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Current Stretch disk level is ~36.28 GiB free; no download is planned.

# Frozen capability references

## Canonical Ollama/MLX 4B

`qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`): artifact 40.71, delivery-adjusted 30.00, delivery 3/6, recovered semantic diagnostic 82.86, weighted prompt 186.46 tok/s, generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`): delivery-adjusted 77.15, strict 60.00, delivery 6/6, protocol 4/6, no hidden-test feedback, ~612 s.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4: pp512 230.85 tok/s, tg128 22.33 tok/s, minimum free 22%.

## Direct MLX 8B 3-bit reference

`mlx-community/Qwen3-8B-3bit` full coding benchmark:
- COMPLETE
- minimum free 14%
- peak swap 1683.38 MB
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6.

Technically stable but not promoted on quality.

# Track A — Amplify

Amplifier 001–003 showed the canonical Ollama/MLX 4B repair path is resource-bound:
- 001 warm-resident repair reaches 4% free;
- 002 call-isolated repair starts from recovered 68% free and still reaches 4%;
- 003 repair context 3072 starts from recovered 70% free and still reaches 4%.

Do not claim a leak or specific KV/allocator root cause. Do not automatically descend to context 2048.

T02 prompt anatomy:
- initial 1638 B
- repair 4573 B
- repair/initial 2.792x
- validation feedback 2762 B (~60.4%).

Amplifier 004 — Compact Feedback remains preregistered and queued:
- plan `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- runner `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- single change: variable repair-feedback detail capped at 768 UTF-8 bytes.

Stretch remains primary while the current architectural sequence continues to produce positive evidence.

# Track B — Stretch / Memory Hierarchy

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen environment/config:
- qwen3
- hidden size 4096
- 36 transformer layers
- vocab size 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- RMSNorm epsilon 1e-6
- `tie_word_embeddings=false`
- quantization 3-bit / group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Weight layout:
- total tensor payload 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Stretch 001 — COMPLETE PASS

Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`.

- 36/36 layer IDs exact
- total tensor payload 3,583,928,320 B
- one-layer selective I/O exact
- layer 18 read 84,427,264 B in 0.069784 s at 1153.794 MiB/s.

Interpretation: exact per-layer storage addressing works. Do not infer token throughput from one-shot I/O rate.

## Stretch 002 — COMPLETE PASS

Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`.

Layer 18:
- pre-eval active delta 0 B
- post-eval active delta 84,427,264 B
- post-clear active/cache 0/0 B
- min free 67%; peak swap 850.5 MB.

## Stretch 003 — COMPLETE PASS

Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`.

Same MLX process:
- layer 18: 0 -> 84,427,264 -> 0 B; cache 0 B
- layer 19: 0 -> 84,427,264 -> 0 B; cache 0 B
- min free 67%; peak swap 826.5 MB.

## Stretch 004 — COMPLETE PASS

Run `20260819-162454` — `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

- official Qwen3 TransformerBlock computation
- resident two-layer materialized delta 168,854,528 B
- streamed near one 84.4 MB layer at a time
- numerical parity max/mean difference 0.0 / 0.0
- min free 63%; peak swap 826.5 MB.

Result: `research/stretch/two-layer-streamed-micro-forward-parity-004-result.md`.

## Stretch 005 — COMPLETE PASS

Run `20260819-163413` — `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`.

- layers `[14..21]`
- resident materialized delta 675,352,572 B
- max streamed one-layer delta 84,427,264 B
- resident/streamed ratio 7.999223710482908x
- numerical parity max/mean diff 0.0 / 0.0
- no cumulative active/cache growth
- streamed parameter materialization 0.042391 s
- streamed forward 0.067679 s
- min free 63%; peak swap 810.5 MB.

Result: `research/stretch/eight-layer-streamed-forward-scaling-005-result.md`.

## Stretch 006 — COMPLETE PASS

Valid run `20260819-164605` — `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`.

The first launch was a transform-harness failure before MLX execution and is separately recorded in `research/stretch/full-36-layer-streamed-body-parity-006-harness-note.md`.

Valid run:
- resident transformer body observed 3,039,315,964 B
- max streamed one-layer 84,427,264 B
- resident/streamed ratio 35.99922371048291x
- all layers 0..35: pre-eval 0 B, materialize 84,427,264 B, post-clear active/cache 0/0 B
- full-body activation parity max/mean diff 0.0 / 0.0
- streamed parameter materialization 1.207812 s
- streamed transformer forward 0.440137 s.

Whole-run telemetry:
- min free 22%
- peak swap 1325.69 MB
- peak child RSS 381.844 MB
- disk 36.297 -> 36.293 GiB.

Whole-run telemetry includes the resident 36-layer control; do not attribute it specifically to streamed execution.

Result: `research/stretch/full-36-layer-streamed-body-parity-006-result.md`.

Canonical interpretation: the entire 36-block transformer body executes with one-layer-at-a-time raw-weight residency and exact resident parity.

## Stretch 007A — COMPLETE PASS

Run `20260819-165247` — `SHARED_COMPONENT_ANATOMY_PASS`.

Read-only physical layout recovery:
- `tie_word_embeddings=false`
- embedding: 3 tensors / 272,269,312 B
- final RMSNorm: 1 tensor / 8,192 B
- LM head: 3 tensors / 272,269,312 B
- other: 0.

Embedding and LM head are distinct quantized payloads used at opposite ends of the forward path and can be phase-streamed separately.

Result: `research/stretch/shared-component-anatomy-007a-result.md`.

## Stretch 007B — COMPLETE PASS

Plan: `research/stretch/phase-streamed-full-logit-parity-007b-plan.md`
Runner: `scripts/stretch_phase_streamed_full_logit_parity_007b.py`
Runner blob: `b08c9b44ae062ee259ab6641575e44c4d7d753e6`
Result: `research/stretch/phase-streamed-full-logit-parity-007b-result.md`

Run `20260819-170334` — `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`.

Frozen token IDs:
`[[1,42,2048,151935]]`.

Resident official control:
- `mlx_lm.utils.load_model(..., lazy=False, strict=True)`
- full-model materialized delta exactly **3,583,928,320 B**.

Phase-streamed path:
- embedding materialized **272,269,312 B** -> evict
- max transformer-layer materialized **84,427,264 B**
- final RMSNorm selected/materialized **8,192 / 8,192 B**
- LM head materialized **272,269,312 B** -> evict
- max streamed weight-stage delta **272,269,312 B**
- resident/max-streamed-stage ratio **13.16317396798652x**.

Full-logit parity `[1,4,151936]`:
- max absolute difference **0.0**
- mean absolute difference **0.0**
- threshold 0.00018125000000000001
- top-1 equality true
- resident top1 `[[921,78,84,1]]`
- streamed top1 `[[921,78,84,1]]`.

Whole-run telemetry:
- host gate 69/69/70% free, swap 1125.62 MB
- minimum free **25%**
- peak swap **1586.0 MB**
- peak child RSS **1007.547 MB**
- disk **36.276 -> 36.276 GiB**.

Again, whole-run telemetry includes the official resident control.

Canonical interpretation:
> Complete token-ID-to-final-logit Qwen3 execution is operational with embedding/head phase streaming plus one-layer-at-a-time transformer streaming, with exact logits versus the official fully resident control and a ~13.16x raw-weight-stage residency ratio.

This is full-forward parity but not yet autoregressive cache reuse.

## Stretch 008 — One-Token KV Autoregressive Parity — READY

Plan:
`research/stretch/one-token-kv-autoregressive-parity-008-plan.md`

Runner:
`scripts/stretch_one_token_kv_autoregressive_parity_008.py`

Runner blob:
`03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`

Frozen provenance:
- Stretch 007B blob `b08c9b44ae062ee259ab6641575e44c4d7d753e6`
- Stretch 002 helper blob `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Official mlx-lm v0.31.3 KV semantics verified:
- Qwen3 has no custom `make_cache`;
- `make_prompt_cache` uses one default `KVCache()` per layer;
- KVCache step capacity is 256 positions;
- Qwen3 applies RoPE using `cache.offset` before `update_and_fetch`;
- official attention mask is built once from cache[0] before the layer loop.

Frozen prompt remains:
`[[1,42,2048,151935]]`.

Generation policy:
- deterministic argmax only
- exactly one generated token
- then feed that token back through the model using the same persisted cache.

Resident path:
1. official fully resident model;
2. official `make_prompt_cache`;
3. prompt prefill -> cache offsets 4;
4. select one argmax token;
5. feed token back through same cache -> offsets 5.

Streamed path:
- 36 persistent `KVCache()` objects remain resident;
- raw weights continue phase-streamed: embedding -> each layer -> norm -> LM head;
- prompt prefill fills layer caches to offset 4;
- resident-selected token is the common numerical feedback input;
- same caches reused for feedback and advance to offset 5.

Expected ordinary BF16 KV allocation:
- ~1,048,576 B per layer due 256-position allocation step
- ~37,748,736 B total for 36 layers after prompt
- no additional allocation block expected at offset 5.

Primary gates:
- cache count/offset/byte gates resident and streamed
- full prompt-with-cache logit parity
- identical resident/streamed generated token
- full post-token logit parity after actual cache reuse
- existing streamed weight-stage materialization gates
- same host/runtime guardrails.

Primary PASS:
`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

Phase-scoped host telemetry is recorded diagnostically where polling catches phases; absence of a phase sample is not a scientific failure.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_one_token_kv_autoregressive_parity_008.py
python3 scripts/stretch_one_token_kv_autoregressive_parity_008.py
```

No download is expected.

If Stretch 008 passes, next extend the same deterministic autoregressive loop to a short multi-token argmax sequence before optimization/prefetch.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
