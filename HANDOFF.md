# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — two coordinated tracks on Apple M1 / 8 GB: **Amplify** (small model, better system capability) and **Stretch** (SSD/RAM memory hierarchy and out-of-core execution).

Current checkpoint: `STRETCH_005_EIGHT_LAYER_STREAMED_FORWARD_SCALING_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models/results.
- Record disk around large model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- No aggregate quality score from partial runs.
- Change one experimental factor at a time for causal tests.
- Do not weaken guardrails post-hoc.
- No automatic context/budget rescue ladders.
- No new large-model acquisition until existing artifacts are exhausted.

Verified GGUF, Direct MLX 3-bit and Direct MLX 4-bit artifacts remain retained.
Current Stretch disk level is ~36.3 GiB free; no new model download is planned.

# Frozen references

## Canonical Ollama/MLX 4B

`qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`): artifact 40.71, delivery-adjusted 30.00, delivery 3/6, recovered semantic diagnostic 82.86, weighted prompt 186.46 tok/s, generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`): delivery-adjusted 77.15, strict 60.00, delivery 6/6, protocol 4/6, no hidden-test feedback, ~612 s.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4: pp512 230.85 tok/s, tg128 22.33 tok/s, minimum free memory 22%.

This is an alternate capability/efficiency profile, not a runtime-only control against Qwen3.5/MLX.

## Direct MLX 8B 3-bit reference

`mlx-community/Qwen3-8B-3bit`:
- smoke PASS
- standalone T01 PASS
- full six-task coding benchmark COMPLETE
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6.

Technically stable but not promoted on quality.

# Track A — Amplify

Goal: improve end-to-end capability of a small model through validation/repair/tools/planner/verifier/retrieval and later specialization.

## Amplifier 001–003

- Amplifier 001 warm-resident validator + max-one-repair: `PARTIAL_RESOURCE_FAIL` during T02 repair.
- Amplifier 002 call isolation works, but T02 repair still reaches 4% free from recovered 68%.
- Amplifier 003 repair context reduced 4096 -> 3072 only; repair still reaches 4% free from recovered 70%.
- Do not infer a memory leak or specific KV/allocator root cause.
- Do not automatically descend to context 2048.

## Repair prompt anatomy

T02 initial 1638 B; repair 4573 B; ratio 2.792x. Validation feedback 2762 B (~60.4%). Record: `research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`.

## Amplifier 004 — READY / QUEUED

Plan: `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
Runner: `scripts/capability_amplifier_004_compact_feedback.py`
Runner blob: `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`

Single change vs 003: variable repair-feedback detail capped at 768 UTF-8 bytes. Initial context 4096, repair context 3072, task/candidate, validation, one repair, selection, isolation, scorer and guardrails stay fixed.

If 004 resource-fails, stop prompt-level rescue on this Ollama/MLX profile.

Amplify 004 remains queued while the current Stretch scaling sequence is producing new positive evidence.

# Track B — Stretch / Memory Hierarchy

Goal: use SSD + RAM as an explicit model-memory hierarchy. Dense layer streaming still uses all transformer layers sequentially while only a bounded subset is resident. Layer skipping/early exit is a separate later problem.

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen config/environment:
- qwen3
- hidden size 4096
- 36 transformer layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group size 64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

## Stretch 001 — COMPLETE PASS

Result: `research/stretch/layer-streaming-feasibility-001-result.md`
Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`:
- 36/36 layer IDs exact
- 907 tensors
- total tensor payload 3,583,928,320 B (~3.338 GiB)
- non-layer/shared 544,546,816 B (~519.32 MiB)
- every transformer layer exactly 84,427,264 B (~80.52 MiB), 25 tensors
- layer 18 exact selective I/O 84,427,264 B in 0.069784 s, 1153.794 MiB/s
- system 68% free / 850.5 MB swap -> 69% / 850.5 MB.

Interpretation: exact per-layer storage access works. Do not infer future token throughput from the one-shot I/O rate.

## Stretch 002 — COMPLETE PASS

Result: `research/stretch/single-layer-mlx-materialization-002-result.md`
Runner blob: `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`:
- layer 18 provenance 25 tensors / 84,427,264 B
- pre-eval active delta 0 B
- post-eval active delta exactly 84,427,264 B
- post-clear active/cache delta 0/0 B
- eval wall 0.039611 s
- min free 67%; peak swap 850.5 MB.

Interpretation: one layer can remain lazy, materialize independently and be fully reclaimed without full-model construction.

## Stretch 003 — COMPLETE PASS

Result: `research/stretch/two-layer-bounded-residency-003-result.md`
Runner blob: `5882b01c37616f668705713f46e5c30aa40c268a`
Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`:
- same MLX child process
- layer 18: 0 -> 84,427,264 -> 0 B; cache 0 B
- layer 19: 0 -> 84,427,264 -> 0 B; cache 0 B
- min free 67%; peak swap 826.5 MB; disk unchanged.

Interpretation: repeated raw-weight residency remains bounded across consecutive materialize/evict cycles.

## Stretch 004 — COMPLETE PASS

Plan: `research/stretch/two-layer-streamed-micro-forward-parity-004-plan.md`
Runner: `scripts/stretch_two_layer_streamed_micro_forward_parity_004.py`
Runner blob: `426423c9d9b7bd7bd1c6a3620197ad5212c678e6`
Result: `research/stretch/two-layer-streamed-micro-forward-parity-004-result.md`

Run `20260819-162454` — `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

For the first time Stretch 004 executed real official Qwen3 transformer-block computation.

Resident control, layers 18+19 simultaneously:
- materialized raw-weight delta: **168,854,528 B** exactly = 2 layer payloads.

Streamed path:
- layer 18: pre-eval delta -65,540 B; materialized 84,361,724 B; post-clear delta -65,540 B; cache 0 B
- layer 19: pre-eval delta 0 B; materialized 84,427,264 B; post-clear delta 0 B; cache 0 B
- both cycles pass frozen per-layer +/-1 MiB materialization and +/-4 MiB post-clear gates.

Numerical resident-vs-streamed parity:
- pass true
- max absolute difference **0.0**
- mean absolute difference **0.0**
- threshold `0.00043500000000000006`.

System:
- host gate 66/65/65% free; swap 826.5 MB
- minimum runtime free memory 63%
- peak swap 826.5 MB
- peak child RSS 178.281 MB
- disk 36.296 -> 36.296 GiB.

Canonical interpretation:
> For the frozen two-block Qwen3 micro-forward, actual transformer computation produces the same output under resident and one-layer-at-a-time streamed weight residency. Raw layer-weight residency is approximately halved relative to the two-layer resident control.

This still excludes embeddings, final norm, LM head, tokenizer, KV cache, autoregressive generation and the other 34 transformer blocks.

## Stretch 005 — Eight-Layer Streamed Forward Scaling — READY

Plan: `research/stretch/eight-layer-streamed-forward-scaling-005-plan.md`
Runner: `scripts/stretch_eight_layer_streamed_forward_scaling_005.py`
Runner blob: `8bbfff727a0131c48d4ba71edc8de485182b7fbe`

Single changed factor vs Stretch 004:
- chain depth 2 -> 8 transformer blocks.

Frozen layers:
`[14, 15, 16, 17, 18, 19, 20, 21]`.

Everything else remains frozen:
- same deterministic batch1/seq4/hidden4096 activation
- same official Qwen3 TransformerBlock
- same quantization/load semantics
- same attention mask
- same resident-vs-streamed comparison
- same per-layer materialization/eviction gates
- same numerical parity formula
- no tokenizer/embedding/final norm/LM head/KV/token generation
- same host/runtime guardrails.

Resident expected raw-weight delta:
`8 * 84,427,264 = 675,418,112 B` with +/-8 MiB gate.

Per streamed layer:
- pre-eval active delta <=32 MiB
- materialized delta 84,427,264 B +/-1 MiB
- post-clear active delta within +/-4 MiB
- post-clear cache <=4 MiB.

Primary scaling metrics:
- resident materialized delta
- max one-layer streamed materialized delta
- resident/streamed raw-weight residency ratio
- per-cycle residual active/cache
- resident vs streamed wall times
- numerical parity
- system free/swap.

Primary PASS:
`EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`.

A PASS would show the same real transformer computation scaling to 8 consecutive blocks while streamed raw-weight residency remains near one block at a time. It would still not be end-to-end LLM inference.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_eight_layer_streamed_forward_scaling_005.py
python3 scripts/stretch_eight_layer_streamed_forward_scaling_005.py
```

No download is expected.

If py_compile/provenance/runtime fails, classify it as harness/runtime compatibility until diagnosed; do not reinterpret it as evidence against layer streaming.

# If Stretch 005 passes

Preregister a full 36-transformer-block body parity experiment with the same tiny deterministic activation before adding shared embeddings/final norm/KV/token generation. Preserve resident numerical control and explicit raw-weight residency accounting.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
