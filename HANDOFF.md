# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM now runs two coordinated tracks on the Apple M1 / 8 GB reference system: **Amplify** (small model, better system capability) and **Stretch** (memory hierarchy / out-of-core execution).

Current checkpoint: `STRETCH_003_TWO_LAYER_BOUNDED_RESIDENCY_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset/replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around large runtime/model work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- No aggregate quality score from partial runs.
- Change one experimental factor at a time for causal tests.
- Do not weaken guardrails post-hoc.
- No automatic context/budget rescue ladders.
- No new large-model acquisition until existing artifacts are exhausted.

Verified GGUF, Direct MLX 3-bit and Direct MLX 4-bit artifacts remain retained.

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

## Amplifier 001

Warm-resident validator + max-one-repair. Run `20260819-142640`: T01 6/6; T02 initial 3/7; repair hits 4% free. `PARTIAL_RESOURCE_FAIL`. Warm residency lacks headroom; no leak claim.

## Amplifier 002

Call-isolated. Run `20260819-144256`: T02 repair starts from 68% free after confirmed unload, then 68 -> 63 -> 23 -> 16 -> 4%. `PARTIAL_RESOURCE_FAIL`. Isolation works but is insufficient.

## Amplifier 003

Repair context only reduced 4096 -> 3072. Run `20260819-150342`: repair starts 70% free / 2069.12 MB swap, then 70 -> 65 -> 31 -> 7 -> 6 -> 4%. `PARTIAL_RESOURCE_FAIL`; peak swap 2318.12 MB. Initial calls themselves reach only 6% free. Do not descend automatically to 2048.

## Prompt anatomy

T02 initial 1638 B; repair 4573 B; ratio 2.792x. Validation feedback alone 2762 B (~60.4%). Record: `research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`.

## Amplifier 004 — READY / QUEUED

Plan: `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
Runner: `scripts/capability_amplifier_004_compact_feedback.py`
Runner blob: `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`

Single change vs 003: variable repair-feedback detail capped at 768 UTF-8 bytes. Initial context 4096, repair context 3072, task/candidate, validation, one repair, selection, isolation, scorer and guardrails stay fixed.

If 004 still resource-fails, stop prompt-level rescue on this Ollama/MLX profile.

# Track B — Stretch / Memory Hierarchy

Goal: use SSD + RAM as an explicit model-memory hierarchy. Dense layer streaming means all layers are still used sequentially while only a bounded subset is resident. Layer skipping/early exit is a separate later problem.

## Stretch 001 — LAYER_ADDRESSABLE_IO_PASS

Plan: `research/stretch/layer-streaming-feasibility-001-plan.md`
Runner: `scripts/stretch_layer_streaming_feasibility_001.py`
Runner blob: `890444928abd6cc24e7194317c92b36b50fd994b`
Canonical result: `research/stretch/layer-streaming-feasibility-001-result.md`

Valid run `20260819-154335`:
- classification `LAYER_ADDRESSABLE_IO_PASS`
- 36/36 layer IDs exact, no missing/unexpected
- 907 tensors
- total tensor payload 3,583,928,320 B (~3.338 GiB)
- non-layer/shared 544,546,816 B (~519.32 MiB)
- every transformer layer exactly 84,427,264 B (~80.52 MiB), 25 tensors
- layer 18 selective I/O: exact 84,427,264 B read in 0.069784 s, 1153.794 MiB/s
- system state 68% free / 850.5 MB swap -> 69% / 850.5 MB
- disk unchanged.

Interpretation: the artifact is cleanly layer-addressable and exact one-layer byte-range I/O works without full-model materialization. Do not infer future token throughput from the one-shot I/O measurement.

## Stretch 002 — SINGLE_LAYER_MLX_EVICTION_PASS

Plan: `research/stretch/single-layer-mlx-materialization-002-plan.md`
Runner: `scripts/stretch_single_layer_mlx_materialization_002.py`
Runner blob: `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
Canonical result: `research/stretch/single-layer-mlx-materialization-002-result.md`

Run `20260819-155641`:
- classification `SINGLE_LAYER_MLX_EVICTION_PASS`
- version lock PASS: mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- layer 18 provenance PASS: 25 tensors / 84,427,264 B
- host gate: 70%, 68%, 67% free; swap 850.5 MB
- pre-eval MLX active delta: **0 B**
- post-eval MLX active delta: **84,427,264 B** exactly
- post-clear MLX active delta: **0 B**
- post-clear MLX cache delta: **0 B**
- `mx.eval` wall: 0.039611 s
- minimum observed free memory: 67%
- peak observed swap: 850.5 MB
- peak child RSS: 40.25 MB
- disk 36.319 -> 36.319 GiB.

Canonical interpretation:
> One raw transformer layer can remain lazy before evaluation, materialize independently to exactly its tensor payload, and be reclaimed back to baseline active/cache memory without constructing the Qwen model.

This is a prerequisite only. No transformer forward computation, shared embeddings/norm, activations, residual stream, KV cache or generation was included.

## Stretch 003 — Two-Layer Repeated Bounded Residency — READY

Plan: `research/stretch/two-layer-bounded-residency-003-plan.md`
Runner: `scripts/stretch_two_layer_bounded_residency_003.py`
Runner blob: `5882b01c37616f668705713f46e5c30aa40c268a`

Frozen provenance:
- Stretch 002 source blob must equal `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

Probe:
- layer 18 then layer 19
- same MLX child process
- each layer must be 25 tensors / 84,427,264 B
- no Qwen model construction, tokenizer, KV cache or generation.

Per cycle:
1. `mx.load()` safetensors;
2. retain only selected layer lazy arrays and delete full tensor dictionary;
3. require pre-eval active delta <=32 MiB;
4. `mx.eval()` selected layer;
5. require materialized active delta within +/-1 MiB of 84,427,264 B;
6. delete references + GC + `mx.clear_cache()`;
7. require post-clear active/cache deltas <=1 MiB.

Primary PASS: `TWO_LAYER_BOUNDED_RESIDENCY_PASS` only if both cycles satisfy all gates in the same process.

A PASS would establish repeated bounded raw-weight residency, but still not actual streamed transformer inference.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_two_layer_bounded_residency_003.py
python3 scripts/stretch_two_layer_bounded_residency_003.py
```

No download and no full-model construction are expected.

If py_compile/provenance/runtime preflight fails, classify it as harness/runtime compatibility only, not evidence against layer streaming.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
