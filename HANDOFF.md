# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; coordinated tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_007A_SHARED_COMPONENT_ANATOMY_READY`

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
- Change one experimental factor at a time for causal tests.
- No automatic context/budget rescue ladders.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute aggregate host telemetry to a sub-phase unless phase-scoped telemetry exists.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Current Stretch disk level is ~36.29 GiB free; no download is planned.

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

Frozen config/environment:
- qwen3
- hidden size 4096
- 36 transformer layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Every transformer layer: 25 tensors / 84,427,264 B (~80.52 MiB).
Known shared/non-layer tensor payload from Stretch 001: 544,546,816 B (~519.32 MiB), exact physical decomposition not yet frozen.

## Stretch 001 — COMPLETE PASS

Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`.

- 36/36 layer IDs exact
- 907 tensors
- total tensor payload 3,583,928,320 B
- shared/non-layer payload 544,546,816 B
- each transformer layer 84,427,264 B
- layer 18 selective I/O exact: 84,427,264 B in 0.069784 s at 1153.794 MiB/s.

Interpretation: exact per-layer storage addressing works. Do not infer future token throughput from the one-shot I/O rate.

## Stretch 002 — COMPLETE PASS

Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`.

Layer 18:
- pre-eval active delta 0 B
- post-eval active delta exactly 84,427,264 B
- post-clear active/cache 0/0 B
- min free 67%; peak swap 850.5 MB.

Interpretation: one layer can remain lazy, materialize independently and be reclaimed.

## Stretch 003 — COMPLETE PASS

Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`.

Same MLX process:
- layer 18: 0 -> 84,427,264 -> 0 B; cache 0 B
- layer 19: 0 -> 84,427,264 -> 0 B; cache 0 B
- min free 67%; peak swap 826.5 MB.

Interpretation: repeated one-layer residency remains bounded.

## Stretch 004 — COMPLETE PASS

Run `20260819-162454` — `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

First real transformer-compute experiment using official Qwen3 `TransformerBlock`.

Resident layers 18+19:
- materialized delta 168,854,528 B = two exact layer payloads.

Streamed:
- ~84.4 MB one layer at a time
- post-clear within frozen tolerance; cache 0 B.

Parity:
- max abs diff 0.0
- mean abs diff 0.0.

System:
- min free 63%
- peak swap 826.5 MB.

Canonical interpretation: same two-block computation/output with approximately half simultaneous raw layer-weight residency.

Result: `research/stretch/two-layer-streamed-micro-forward-parity-004-result.md`.

## Stretch 005 — COMPLETE PASS

Run `20260819-163413` — `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`.

Layers `[14,15,16,17,18,19,20,21]`.

Resident:
- observed materialized delta 675,352,572 B.

Streamed:
- max one-layer materialized delta 84,427,264 B
- no cumulative active/cache growth
- resident/streamed ratio 7.999223710482908x.

Parity:
- max/mean absolute difference 0.0 / 0.0.

Timing:
- streamed parameter materialization 0.042391 s
- streamed forward 0.067679 s.

System:
- min free 63%
- peak swap 810.5 MB
- disk unchanged.

Result: `research/stretch/eight-layer-streamed-forward-scaling-005-result.md`.

## Stretch 006 — COMPLETE PASS

Plan: `research/stretch/full-36-layer-streamed-body-parity-006-plan.md`
Corrected wrapper: `scripts/stretch_full_36_layer_streamed_body_parity_006.py`
Corrected wrapper blob: `ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`
Frozen source: exact Stretch 005 blob `8bbfff727a0131c48d4ba71edc8de485182b7fbe`.
Result: `research/stretch/full-36-layer-streamed-body-parity-006-result.md`

The first attempted launch stopped inside the transform wrapper and is separately classified as harness-only/no scientific result in `research/stretch/full-36-layer-streamed-body-parity-006-harness-note.md`.

Valid run `20260819-164605` — `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`.

Preflight:
- corrected transform PASS
- exact layers 0..35
- all 36 layer provenance checks PASS
- host gate 66/66/66% free, swap 802.5 MB.

Resident full transformer body:
- exact 36-layer payload 3,039,381,504 B
- observed materialized delta **3,039,315,964 B**
- difference -65,540 B, inside frozen tolerance.

Streamed full transformer body:
- all layers 0..35 independently show pre-eval delta 0 B
- all materialize exactly **84,427,264 B**
- all post-clear active deltas return to **0 B**
- all post-clear caches return to **0 B**
- max one-layer materialized delta **84,427,264 B**
- resident/streamed raw-weight ratio **35.99922371048291x**.

Numerical parity:
- pass true
- max abs diff **0.0**
- mean abs diff **0.0**
- threshold 0.011210000000000001.

Timing, frozen micro-forward batch1/seq4:
- streamed total parameter materialization wall **1.207812 s**
- streamed total transformer forward wall **0.440137 s**.

Whole-run system telemetry:
- minimum free memory **22%**
- peak swap **1325.69 MB**
- peak child RSS **381.844 MB**
- disk **36.297 -> 36.293 GiB**.

Important interpretation boundary: whole-run minimum free/peak swap include the 36-layer resident control and must not be attributed specifically to the streamed phase.

Canonical interpretation:
> The complete 36-block Qwen3 transformer body executes with one-layer-at-a-time streamed raw-weight residency and produces the exact same final activation as a control holding all 36 block weights simultaneously. Raw layer-weight materialization is ~2.831 GiB resident versus ~80.52 MiB at a time streamed, an observed ~36x ratio.

This establishes full-body dense layer streaming on the reference machine, but it is still not end-to-end LLM inference. Token embeddings, final RMSNorm, output projection/LM head, tokenizer, KV cache and autoregressive generation remain excluded.

## Stretch 007A — Shared Component Anatomy — READY

Plan: `research/stretch/shared-component-anatomy-007a-plan.md`
Runner: `scripts/stretch_shared_component_anatomy_007a.py`
Runner blob: `7e147476119766a5cf29b697120291b1b96b9bb9`

Purpose: map the exact 544,546,816-byte non-layer payload before adding shared components to inference.

Read-only method:
- exact Stretch 001 header-catalog helper blob `890444928abd6cc24e7194317c92b36b50fd994b`
- no MLX import/model launch/tensor materialization/network
- read local config fields including `vocab_size`, `tie_word_embeddings`, `rms_norm_eps`, quantization
- catalog every non-layer tensor with name/dtype/shape/bytes
- deterministic groups: embedding, final_norm, lm_head, other
- require total non-layer bytes exactly 544,546,816 B.

Primary PASS:
`SHARED_COMPONENT_ANATOMY_PASS`.

A PASS will authorize `Stretch 007B`: real token embedding -> all 36 streamed transformer blocks -> final RMSNorm -> output projection according to the observed local layout -> final-logit parity against resident control, still without KV/autoregressive generation.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_shared_component_anatomy_007a.py
python3 scripts/stretch_shared_component_anatomy_007a.py
```

No model launch or download is expected.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
