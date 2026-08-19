# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; coordinated tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_007B_PHASE_STREAMED_FULL_LOGIT_PARITY_READY`

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

Every transformer layer: 25 tensors / 84,427,264 B (~80.52 MiB).

## Stretch 001 — COMPLETE PASS

Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`.

- 36/36 layer IDs exact
- 907 tensors
- total tensor payload 3,583,928,320 B
- shared/non-layer payload 544,546,816 B
- each transformer layer 84,427,264 B
- layer 18 selective I/O exact: 84,427,264 B in 0.069784 s at 1153.794 MiB/s.

Interpretation: exact per-layer storage addressing works. Do not infer token throughput from the one-shot I/O rate.

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

- resident two-layer materialized delta 168,854,528 B
- streamed near one 84.4 MB layer at a time
- max/mean parity difference 0.0 / 0.0
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

Plan: `research/stretch/full-36-layer-streamed-body-parity-006-plan.md`
Corrected wrapper: `scripts/stretch_full_36_layer_streamed_body_parity_006.py`
Corrected wrapper blob: `ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`
Frozen source: Stretch 005 blob `8bbfff727a0131c48d4ba71edc8de485182b7fbe`.
Result: `research/stretch/full-36-layer-streamed-body-parity-006-result.md`

The first attempted launch stopped inside the transform wrapper and is separately classified as harness-only/no scientific result in `research/stretch/full-36-layer-streamed-body-parity-006-harness-note.md`.

Valid run `20260819-164605` — `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`.

Resident transformer body:
- exact body payload 3,039,381,504 B
- observed materialized delta 3,039,315,964 B.

Streamed body:
- all layers 0..35 pre-eval delta 0 B
- every layer materializes exactly 84,427,264 B
- every layer post-clear active/cache returns 0/0 B
- resident/streamed raw-weight ratio 35.99922371048291x.

Parity:
- max abs diff 0.0
- mean abs diff 0.0.

Timing, micro-forward batch1/seq4:
- streamed parameter materialization 1.207812 s
- streamed transformer forward 0.440137 s.

Whole-run system telemetry:
- min free 22%
- peak swap 1325.69 MB
- peak child RSS 381.844 MB
- disk 36.297 -> 36.293 GiB.

Do not attribute whole-run min-free/peak-swap specifically to the streamed phase because the resident 36-layer control is included.

Canonical interpretation:
> The complete 36-block Qwen3 transformer body executes with one-layer-at-a-time streamed raw-weight residency and exact resident final-activation parity. Raw transformer-layer residency is ~2.831 GiB resident versus ~80.52 MiB at a time streamed.

## Stretch 007A — COMPLETE PASS

Plan: `research/stretch/shared-component-anatomy-007a-plan.md`
Runner: `scripts/stretch_shared_component_anatomy_007a.py`
Runner blob: `7e147476119766a5cf29b697120291b1b96b9bb9`
Result: `research/stretch/shared-component-anatomy-007a-result.md`

Run `20260819-165247` — `SHARED_COMPONENT_ANATOMY_PASS`.

Read-only; no MLX/model launch/materialization/network.

Observed local config:
- vocab size 151936
- `tie_word_embeddings=false`
- RMSNorm epsilon 1e-6
- quantization 3-bit/group64.

Exact tensor accounting:
- all tensors 907
- transformer-layer bytes 3,039,381,504 B
- non-layer bytes 544,546,816 B
- total 3,583,928,320 B.

Non-layer decomposition:
- embedding: 3 tensors / **272,269,312 B**
  - `model.embed_tokens.weight` U32 `[151936,384]` 233,373,696 B
  - `model.embed_tokens.scales` BF16 `[151936,64]` 19,447,808 B
  - `model.embed_tokens.biases` BF16 `[151936,64]` 19,447,808 B
- final RMSNorm: 1 tensor / **8,192 B**
  - `model.norm.weight` BF16 `[4096]`
- LM head: 3 tensors / **272,269,312 B**
  - `lm_head.weight` U32 `[151936,384]` 233,373,696 B
  - `lm_head.scales` BF16 `[151936,64]` 19,447,808 B
  - `lm_head.biases` BF16 `[151936,64]` 19,447,808 B
- other: 0 tensors / 0 B.

Canonical interpretation:
> Embedding and LM head are separate quantized ~272.27 MB payloads used at opposite ends of the forward path. They can therefore be tested as phase-streamed components instead of remaining simultaneously resident.

Official mlx-lm v0.31.3 Qwen3 semantics verified: `Embedding -> 36 TransformerBlock -> final RMSNorm -> lm_head` when `tie_word_embeddings=false`; official loader quantizes modules when matching `.scales` tensors are present.

## Stretch 007B — Phase-Streamed Full-Logit Parity — READY

Plan: `research/stretch/phase-streamed-full-logit-parity-007b-plan.md`
Runner: `scripts/stretch_phase_streamed_full_logit_parity_007b.py`
Runner blob: `b08c9b44ae062ee259ab6641575e44c4d7d753e6`

Research question:
Can token-ID-to-final-logit execution match an official fully resident Qwen3 control while raw weights are phase-streamed as:

`embedding -> evict -> layer0..35 one at a time -> final norm -> LM head`?

Frozen token IDs:
`[[1, 42, 2048, 151935]]`.

No tokenizer, KV cache or autoregressive generation yet.

Resident control:
- official `mlx_lm.utils.load_model(model_dir, lazy=False, strict=True)`
- expected model tensor payload 3,583,928,320 B
- broad accounting gate +/-64 MiB
- execute same token IDs to full logits.

Phase-streamed path:
1. embedding payload 272,269,312 B, materialize -> lookup -> evict;
2. all 36 transformer blocks, exact Stretch per-layer gates;
3. final norm payload 8,192 B;
4. separate LM head payload 272,269,312 B, materialize -> logits -> evict.

Expected logits shape:
`[1,4,151936]`.

Parity:
- full logits compared in float32
- threshold `1e-5 + 1e-5 * resident_max_abs`
- top-1 token IDs per position also recorded.

Primary PASS:
`PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`.

Structural expectation if PASS:
- resident complete model ~3.34 GiB raw tensor payload simultaneously;
- largest streamed raw-weight stage ~272.27 MB (embedding or LM head), with transformer stages ~84.43 MB;
- exact/near-exact full-logit parity.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_phase_streamed_full_logit_parity_007b.py
python3 scripts/stretch_phase_streamed_full_logit_parity_007b.py
```

No download is expected.

If 007B passes, the next stage is the first KV/autoregressive experiment: a tiny frozen prompt and exactly one generated token before any longer generation loop.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
