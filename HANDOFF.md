# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM now runs two coordinated tracks on the Apple M1 / 8 GB reference system: **Amplify** (small model, better system capability) and **Stretch** (memory hierarchy / out-of-core execution).

Current checkpoint: `STRETCH_002_SINGLE_LAYER_MLX_READY`

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

Warm-resident validator + max-one-repair.
Run `20260819-142640`: T01 6/6; T02 initial 3/7; repair hits 4% free. `PARTIAL_RESOURCE_FAIL`. Warm residency lacks headroom; no leak claim.

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

First launch `20260819-153944`: `MODEL_NOT_FOUND` because default locator searched HF cache. No weight inspection; harness locator issue only. Correct verified model path: `results-local/mlx/models/Qwen3-8B-3bit`.

Valid run `20260819-154335` using explicit path:
- classification `LAYER_ADDRESSABLE_IO_PASS`
- `num_hidden_layers`: 36
- safetensors shards: 1
- tensors: 907
- total tensor payload: 3,583,928,320 B (~3.338 GiB)
- discovered layer IDs: exact 0..35
- missing/unexpected: none
- non-layer/shared payload: 544,546,816 B (~519.32 MiB)
- every layer: exactly 84,427,264 B (~80.52 MiB)
- transformer-layer payload total: 3,039,381,504 B (~2.831 GiB)

Selective I/O probe, layer 18:
- 25 tensors
- expected/read bytes: 84,427,264 / 84,427,264
- wall 0.069784 s
- effective throughput 1153.794 MiB/s
- SHA256 `2185c6f5cf1528ad8c0789426491e88ba6acc9ca36d11992a95742d4bd5f452d`
- system state 68% free / 850.5 MB swap -> 69% / 850.5 MB
- disk unchanged 36.310 GiB.

Canonical interpretation:
> The 8B 3-bit artifact is cleanly layer-addressable and exact one-layer byte-range I/O works without reading/materializing the full model. This proves a prerequisite only, not end-to-end streamed inference.

Do not infer future token throughput directly from the one-shot 1153.794 MiB/s result; OS page cache, repeated reads and compute overlap can change effective behavior.

## Stretch 002 — Single-Layer MLX Materialization + Eviction — READY

Plan: `research/stretch/single-layer-mlx-materialization-002-plan.md`
Runner: `scripts/stretch_single_layer_mlx_materialization_002.py`
Runner blob: `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`

Probe layer: 18; expected 25 tensors / 84,427,264 B.

Method:
- use frozen Direct MLX venv (mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1)
- no Qwen model construction, tokenizer, KV cache or token generation
- `mx.load(model.safetensors)` then retain only layer-18 arrays
- drop all other array references before evaluation
- measure MLX active/cache/peak before eval
- if pre-eval active delta >32 MiB, classify `EAGER_FULL_FILE_LOAD_SUSPECTED`
- `mx.eval()` selected layer only
- measure MLX/system memory
- delete layer refs + `gc.collect()` + `mx.clear_cache()`
- eviction pass requires final active/cache within +1 MiB of baseline
- 3 launch samples >=60% free; runtime free<5% / swap>5600 guardrails.

Possible primary classifications:
- `SINGLE_LAYER_MLX_EVICTION_PASS`
- `SINGLE_LAYER_MLX_MATERIALIZATION_PASS_EVICTION_INCONCLUSIVE`
- `EAGER_FULL_FILE_LOAD_SUSPECTED`
- safety/harness classifications as defined in plan.

If eviction passes, next experiment should prove **repeated bounded residency across two sequential layers** before attempting a full streamed transformer forward.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_single_layer_mlx_materialization_002.py
python3 scripts/stretch_single_layer_mlx_materialization_002.py
```

No download and no full-model construction are expected.

If `py_compile` or a child API preflight fails, treat it as harness/runtime compatibility only; do not reinterpret it as evidence against layer streaming.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
