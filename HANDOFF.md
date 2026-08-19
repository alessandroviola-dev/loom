# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — two coordinated tracks on Apple M1 / 8 GB: **Amplify** (small model, better system capability) and **Stretch** (SSD/RAM memory hierarchy and out-of-core execution).

Current checkpoint: `STRETCH_004_TWO_LAYER_STREAMED_FORWARD_PARITY_READY`

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
Latest observed free disk around current Stretch work: ~36.299 GiB.

# Frozen references

## Canonical Ollama/MLX 4B

`qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71
- delivery-adjusted 30.00
- delivery 3/6
- recovered semantic diagnostic 82.86
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- delivery-adjusted 77.15
- strict 60.00
- delivery 6/6
- protocol 4/6
- no hidden-test feedback
- ~612 s.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4:
- pp512 230.85 tok/s
- tg128 22.33 tok/s
- minimum free memory 22%.

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

Warm-resident validator + max-one-repair. Run `20260819-142640`: T01 6/6; T02 initial 3/7; repair hits 4% free. `PARTIAL_RESOURCE_FAIL`. No leak claim.

## Amplifier 002

Call-isolated. Run `20260819-144256`: T02 repair starts from 68% free after confirmed unload, then 68 -> 63 -> 23 -> 16 -> 4%. `PARTIAL_RESOURCE_FAIL`. Isolation works but is insufficient.

## Amplifier 003

Repair context 4096 -> 3072 only. Run `20260819-150342`: repair starts 70% free / 2069.12 MB swap, then 70 -> 65 -> 31 -> 7 -> 6 -> 4%. `PARTIAL_RESOURCE_FAIL`; peak swap 2318.12 MB. Initial calls themselves reach 6% free. Do not descend automatically to 2048.

## Prompt anatomy

T02 initial 1638 B; repair 4573 B; ratio 2.792x. Validation feedback 2762 B (~60.4%). Record: `research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`.

## Amplifier 004 — READY / QUEUED

Plan: `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
Runner: `scripts/capability_amplifier_004_compact_feedback.py`
Runner blob: `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`

Single change vs 003: variable repair-feedback detail capped at 768 UTF-8 bytes. Initial context 4096, repair context 3072, task/candidate, validation, one repair, selection, isolation, scorer and guardrails stay fixed.

If 004 still resource-fails, stop prompt-level rescue on this Ollama/MLX profile.

# Track B — Stretch / Memory Hierarchy

Goal: use SSD + RAM as an explicit model-memory hierarchy. Dense layer streaming still uses all layers sequentially while only a bounded subset is resident. Layer skipping/early exit is a separate later problem.

## Stretch 001 — COMPLETE PASS

Plan: `research/stretch/layer-streaming-feasibility-001-plan.md`
Runner: `scripts/stretch_layer_streaming_feasibility_001.py`
Runner blob: `890444928abd6cc24e7194317c92b36b50fd994b`
Result: `research/stretch/layer-streaming-feasibility-001-result.md`

Valid run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`:
- 36/36 layer IDs exact
- 907 tensors
- total tensor payload 3,583,928,320 B (~3.338 GiB)
- non-layer/shared 544,546,816 B (~519.32 MiB)
- every layer exactly 84,427,264 B (~80.52 MiB), 25 tensors
- layer 18 exact selective I/O: 84,427,264 B in 0.069784 s, 1153.794 MiB/s
- system 68% free / 850.5 MB swap -> 69% / 850.5 MB.

Interpretation: exact per-layer storage access is feasible. Do not infer future token throughput from the one-shot I/O rate.

## Stretch 002 — COMPLETE PASS

Plan: `research/stretch/single-layer-mlx-materialization-002-plan.md`
Runner: `scripts/stretch_single_layer_mlx_materialization_002.py`
Runner blob: `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
Result: `research/stretch/single-layer-mlx-materialization-002-result.md`

Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`:
- layer 18: 25 tensors / 84,427,264 B
- pre-eval active delta 0 B
- post-eval active delta exactly 84,427,264 B
- post-clear active/cache delta 0/0 B
- eval wall 0.039611 s
- min free 67%; peak swap 850.5 MB.

Interpretation: one layer can remain lazy, materialize independently and be fully reclaimed without full-model construction.

## Stretch 003 — COMPLETE PASS

Plan: `research/stretch/two-layer-bounded-residency-003-plan.md`
Runner: `scripts/stretch_two_layer_bounded_residency_003.py`
Runner blob: `5882b01c37616f668705713f46e5c30aa40c268a`
Result: `research/stretch/two-layer-bounded-residency-003-result.md`

Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`:
- same MLX child process
- source provenance PASS against Stretch 002 blob `e7bd6b...`
- host gate 67/67/67% free; swap 826.5 MB
- layer 18: pre 0 B -> post 84,427,264 B -> clear 0 B / cache 0 B; eval 0.039539 s
- layer 19: pre 0 B -> post 84,427,264 B -> clear 0 B / cache 0 B; eval 0.041369 s
- minimum free 67%
- peak swap 826.5 MB
- peak child RSS 40.469 MB
- disk unchanged 36.299 GiB.

Canonical interpretation:
> Raw layer-weight residency remains bounded across repeated consecutive materialize/evict cycles in the same MLX process. This closes the raw-weight prerequisite stage and authorizes a real transformer-block forward test.

## Stretch 004 — Two-Layer Streamed Micro-Forward Parity — READY

Plan: `research/stretch/two-layer-streamed-micro-forward-parity-004-plan.md`
Runner: `scripts/stretch_two_layer_streamed_micro_forward_parity_004.py`
Runner blob: `426423c9d9b7bd7bd1c6a3620197ad5212c678e6`

Purpose:
- introduce actual Qwen3 transformer-block computation for the first time;
- compare exact resident layers 18+19 against streamed layer18 -> evict -> layer19 -> evict;
- use installed `mlx_lm.models.qwen3.TransformerBlock`, not a manual reimplementation;
- use exact local 3-bit/group64 quantized weights;
- deterministic synthetic activation: batch1, seq4, hidden4096;
- official attention-mask helper;
- no tokenizer, embeddings, full model, KV cache or token generation.

Frozen gates:
- model config: qwen3 / hidden4096 / 36 layers / 32 heads / 8 KV heads / head_dim128 / 3-bit group64
- resident two-layer materialized delta near 168,854,528 B (+/-2 MiB)
- streamed pre-eval delta <=32 MiB per layer
- streamed materialized delta near 84,427,264 B (+/-1 MiB) per layer
- post-clear active delta within +/-4 MiB and cache <=4 MiB
- numerical parity: max abs diff <= `1e-5 + 1e-5 * resident_max_abs`
- host gate 3x >=60% free; runtime free<5% / swap>5600 MB abort.

Primary PASS:
`TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

A PASS still does not prove end-to-end token generation. It would prove that real Qwen3 transformer computation can preserve output while reducing simultaneous layer-weight residency over a two-layer chain.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_two_layer_streamed_micro_forward_parity_004.py
python3 scripts/stretch_two_layer_streamed_micro_forward_parity_004.py
```

No download is expected.

If py_compile/provenance/runtime fails, classify as harness/runtime compatibility until diagnosed; do not reinterpret it as evidence against layer streaming.

# Open questions

1. Does exact Qwen3 two-layer streamed forward match the resident control numerically?
2. Does materialized weight residency fall from ~2 layers resident to ~1 layer at a time while activations remain bounded?
3. If Stretch 004 passes, how many consecutive layers can be streamed with numerical parity before adding embeddings/shared norm/KV?
4. When should queued Amplifier 004 resume relative to Stretch progression?

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
