# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; two tracks: **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_006_TRANSFORM_FIX_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset/replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails post-hoc.
- Change one experimental factor at a time.
- No automatic context/budget rescue ladders.
- No new large-model acquisition while existing artifacts suffice.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Current Stretch disk level is ~36.29 GiB free; no download is planned.

# Frozen capability references

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

Qwen3-4B Q4: pp512 230.85 tok/s, tg128 22.33 tok/s, min free 22%.

## Direct MLX 8B 3-bit reference

`mlx-community/Qwen3-8B-3bit` full coding benchmark:
- COMPLETE
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6.

Technically stable but not promoted on quality.

# Track A — Amplify

Amplifier 001–003 showed the canonical Ollama/MLX 4B repair path is resource-bound:
- 001 warm-resident repair: free 4%
- 002 call-isolated repair: starts 68% free, reaches 4%
- 003 repair context 3072: starts 70% free, reaches 4%.

Do not claim leak or specific allocator/KV cause. Do not automatically descend to context 2048.

T02 repair anatomy:
- initial 1638 B
- repair 4573 B
- validation feedback 2762 B (~60.4%).

Amplifier 004 — Compact Feedback remains preregistered/queued:
- plan `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- runner `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- single change: variable repair-feedback detail capped at 768 UTF-8 bytes.

Stretch remains primary while the current sequence continues to produce positive architectural evidence.

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
Shared/non-layer tensor payload: 544,546,816 B (~519.32 MiB).

## Stretch 001 — COMPLETE PASS

Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`.

- exact layer IDs 0..35
- total tensor payload 3,583,928,320 B
- one-layer selective I/O exact
- layer 18 read 84,427,264 B in 0.069784 s
- 1153.794 MiB/s one-shot selective read.

Interpretation: exact per-layer storage addressing works. Do not infer future token throughput from the one-shot I/O rate.

## Stretch 002 — COMPLETE PASS

Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`.

Layer 18:
- pre-eval active delta 0 B
- post-eval active delta exactly 84,427,264 B
- post-clear active/cache 0/0 B
- min free 67%; peak swap 850.5 MB.

Interpretation: one layer can stay lazy, materialize independently and be reclaimed.

## Stretch 003 — COMPLETE PASS

Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`.

Same MLX process:
- layer 18: 0 -> 84,427,264 -> 0 B; cache 0
- layer 19: 0 -> 84,427,264 -> 0 B; cache 0
- min free 67%; peak swap 826.5 MB.

Interpretation: repeated one-layer residency remains bounded.

## Stretch 004 — COMPLETE PASS

Run `20260819-162454` — `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

First real transformer-compute experiment using official Qwen3 `TransformerBlock`.

Resident layers 18+19:
- materialized delta exactly 168,854,528 B.

Streamed:
- layer 18 ~84.36 MB then eviction
- layer 19 84,427,264 B then eviction
- caches 0 B after cycles.

Parity:
- max abs diff 0.0
- mean abs diff 0.0.

System:
- min free 63%
- peak swap 826.5 MB.

Canonical interpretation: same two-block computation/output with approximately half simultaneous raw layer-weight residency.

Result: `research/stretch/two-layer-streamed-micro-forward-parity-004-result.md`.

## Stretch 005 — COMPLETE PASS

Plan: `research/stretch/eight-layer-streamed-forward-scaling-005-plan.md`
Runner: `scripts/stretch_eight_layer_streamed_forward_scaling_005.py`
Runner blob: `8bbfff727a0131c48d4ba71edc8de485182b7fbe`
Result: `research/stretch/eight-layer-streamed-forward-scaling-005-result.md`

Run `20260819-163413` — `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`.

Frozen layers `[14,15,16,17,18,19,20,21]`.

Resident control:
- expected exact payload 675,418,112 B
- observed materialized delta **675,352,572 B**.

Streamed:
- max one-layer materialized delta **84,427,264 B**
- layer 14: small -65,540 B bookkeeping delta, within frozen tolerance
- layers 15–21: pre 0 / materialized 84,427,264 / post-clear 0 / cache 0
- no cumulative active/cache growth.

Scaling:
- resident/streamed raw-weight ratio **7.999223710482908x**
- stream total parameter materialization wall 0.042391 s
- stream total forward wall 0.067679 s.

Parity:
- max abs diff **0.0**
- mean abs diff **0.0**
- threshold 0.0008300000000000001.

System:
- host gate 65/63/63% free
- minimum runtime free 63%
- peak swap 810.5 MB
- peak child RSS 169.469 MB
- disk 36.294 -> 36.294 GiB.

Canonical interpretation:
> Increasing real transformer depth from 2 to 8 makes resident raw layer-weight materialization grow ~8x while streamed materialization remains near one layer at a time, with exact final numerical parity and no observed accumulation.

This is still a micro-forward, not end-to-end LLM inference.

## Stretch 006 — Full 36-Layer Streamed Body Parity — READY AFTER HARNESS FIX

Plan:
`research/stretch/full-36-layer-streamed-body-parity-006-plan.md`

Runner:
`scripts/stretch_full_36_layer_streamed_body_parity_006.py`

Corrected runner blob:
`ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`

Frozen source:
- exact Stretch 005 blob `8bbfff727a0131c48d4ba71edc8de485182b7fbe`.

Single scientific factor:
- chain depth 8 -> all **36 layers, 0..35**.

Preserved:
- same synthetic batch1/seq4/hidden4096 input
- same official Qwen3 TransformerBlock
- same 3-bit/group64 loading/quantization
- same resident-vs-streamed sequence
- same per-layer streamed gates
- same parity formula
- same host/runtime safety
- no tokenizer/embedding/final norm/LM head/KV/token generation.

Resident exact transformer-body payload:
`36 * 84,427,264 = 3,039,381,504 B` (~2.831 GiB).

Resident tolerance:
+/-36 MiB, preserving Stretch 005's +/-1 MiB-per-layer scale.

Each streamed cycle remains:
- pre-eval delta <=32 MiB
- materialized delta 84,427,264 B +/-1 MiB
- post-clear active within +/-4 MiB
- post-clear cache <=4 MiB.

Primary PASS:
`FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`.

### First launch — HARNESS TRANSFORM FAIL / NO SCIENTIFIC RESULT

The first launch stopped after Stretch 005 source provenance PASS and before execution of the transformed benchmark:
- failure: `transform invariant failed for experiment labels: expected 2 occurrence(s), found 1`
- no MLX child process or layer computation was launched
- no resource, parity or model conclusion is permitted.

Record:
`research/stretch/full-36-layer-streamed-body-parity-006-harness-note.md`

Demonstrated defect:
- one global textual label replacement used a brittle combined occurrence invariant.

Fix:
- split console experiment label and summary experiment label into separate exact one-occurrence invariants.

Scientific design/gates remain unchanged.

Expected structural signal if scaling continues:
- resident raw-weight residency ~36 layer payloads
- streamed raw-weight residency ~1 layer payload
- ratio near 36x
- final resident/streamed activation parity.

A PASS would cover the complete transformer body but still exclude shared embeddings/final norm/LM head, tokenizer, KV cache and autoregressive generation.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_full_36_layer_streamed_body_parity_006.py
python3 scripts/stretch_full_36_layer_streamed_body_parity_006.py
```

No download is expected.

If Stretch 006 passes, the next architectural stage is shared-model components + final-logit parity before KV/autoregressive generation.

# Continuation rule

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
