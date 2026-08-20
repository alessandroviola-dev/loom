# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_016_QUANTIZED_LINEAR_M_BOUNDARY_MAPPING_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Promotion target

Interactive usability target: approximately **20 token/s**.

This is a profile-promotion target, not a scientific PASS threshold for intermediate experiments.

Canonical decision:
`research/usability-speed-target-v1.md`.

## Safety / research constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- Launch-state gate where preregistered: >=60% free memory and swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails or parity thresholds post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No automatic rescue ladders or hidden retries.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute whole-run host telemetry to a sub-phase without phase-scoped evidence.
- Long child runs use file-backed state/final/stdout/stderr or drained pipes.
- Do not equate logical safetensors materialization time or Darwin process disk-I/O accounting with forensic model-file SSD throughput.
- Do not purge macOS caches casually to manufacture a cold-cache state.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Latest valid Stretch run ended with ~36.715 GiB free. No download is planned for Stretch 016.

## Frozen capability references

Canonical Ollama/MLX 4B `qwen3.5:4b-mlx`, context 4096:
- Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6, generation 16.01 tok/s
- Pi Agentic Coding 001: delivery-adjusted 77.15, strict 60.00, delivery 6/6, ~612 s.

llama.cpp 4B Q4 efficiency reference:
- pp512 230.85 tok/s
- tg128 22.33 tok/s.

Direct MLX Qwen3-8B 3-bit coding reference:
- technically stable full session
- min free 14%
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6
- not promoted on quality.

## Track A — Amplify

Amplifier 001–003 characterized a resource boundary in the canonical 4B repair workflow. Do not claim leak/KV/allocator root cause.

Amplifier 004 remains preregistered/queued:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- single change: repair-feedback variable detail capped at 768 UTF-8 bytes.

Stretch remains primary while the architectural speed/memory frontier is improving.

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

## Frozen Stretch history

### 001–005 — COMPLETE PASS

- 001 `LAYER_ADDRESSABLE_IO_PASS`: all 36 layers exactly addressable/selectively readable.
- 002 `SINGLE_LAYER_MLX_EVICTION_PASS`: one layer materializes 0 -> 84,427,264 -> 0 B active.
- 003 `TWO_LAYER_BOUNDED_RESIDENCY_PASS`: repeated one-layer cycles remain bounded.
- 004 `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`: real Qwen3 block compute with exact resident/streamed activation parity.
- 005 `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`: exact parity; resident/streamed layer-weight ratio ~8x.

### 006 — COMPLETE PASS

`FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`, valid run `20260819-164605`:
- body 3,039,315,964 B resident vs max streamed layer 84,427,264 B
- ratio 35.99922371048291x
- exact full-body parity.

### 007A / 007B — COMPLETE PASS

007A `SHARED_COMPONENT_ANATOMY_PASS`:
- embedding 272,269,312 B
- norm 8,192 B
- LM head 272,269,312 B
- untied embedding/head.

007B `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`, run `20260819-170334`:
- resident full model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x
- full logits exact.

### 008 — COMPLETE PASS

`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`, run `20260819-173553`:
- first persistent-KV autoregressive streamed proof
- exact prompt/post-token logits
- KV offsets 4 -> 5
- KV total 37,748,736 B.

### 009 — COMPLETE PASS

`FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`, run `20260819-183143`:
- exact resident/streamed sequence `[1,374,264,4647]`
- exact logits all feedback steps
- KV offsets 4 -> 8
- mean layer materialization 0.188658 s/token
- mean layer forward 0.192317 s/token.

### 010 — COMPLETE PASS

`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact prompt + 16 feedback logits
- identical frozen 16-token sequence
- final KV offset 20, 37,748,736 B
- mean full pass 2.888971 s/token
- logical throughput 0.346144 token/s
- materialization transition ~0.19 s early -> ~1.4 s late while forward stays ~0.19 s.

Result:
`research/stretch/sixteen-token-autoregressive-stability-010-result.md`.

### 011 — COMPLETE PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- correctness/KV gates exact
- late transformer materialization process reads ~3,039,395,840 B/token
- late full-pass process reads ~3.584 GB/token
- materialization-time/disk-read Pearson 0.9995866107996246
- mean forward 0.191414 s/token
- logical throughput 0.312407 token/s.

Canonical interpretation: pure one-layer dense autoregressive streaming reaches approximately one target-weight traversal per generated token under Darwin process-I/O accounting. This is diagnostic evidence, not forensic per-file tracing.

Result:
`research/stretch/materialization-io-attribution-011-result.md`.

### 012 — COMPLETE PASS

Valid run `20260819-192349`:
`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`.

Single change vs 011:
- layers 0..7 retained persistently across prompt + 16 tokens.

Key result:
- exact prompt + all 16 feedback logits
- hotset 675,418,112 B
- hybrid simultaneous raw-weight budget 947,687,424 B
- resident/hybrid ratio 3.7817620338074676x
- mean full pass 2.092360 s/token
- logical throughput **0.477929 token/s**
- improvement vs 011 ~52.98%
- late full-pass process reads ~899,052,885 B/token
- stream-token min free 59%.

Result:
`research/stretch/eight-layer-persistent-hotset-012-result.md`.

Decision: residency helps but remains far below the ~20 token/s target; test traversal amortization.

### 013 — COMPLETE PASS

Plan:
`research/stretch/four-token-oracle-block-verification-013-plan.md`

Runner/blob:
- `scripts/stretch_four_token_oracle_block_verification_013.py`
- `deeb0339294162f38cd4522d2890b6a0c728f96e`.

Valid run `20260819-193702`:
`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`.

Single scientific change vs 012:
- 16 one-token target traversals -> 4 causal traversals of 4 known-correct oracle tokens each.

Correctness/performance:
- all 16 position logits exact vs resident sequential control
- top-1 equality all 16 positions
- all oracle tokens accepted
- streamed KV offsets 4 -> 8 -> 12 -> 16 -> 20
- target-block total wall 8.484694 s
- oracle target-verification throughput **1.8857486198 token/s**
- ratio vs Stretch 012 **3.9456668664x**.

Boundary:
- no real drafter
- zero draft/rejection/rollback cost
- metric is an oracle target-side upper bound, not deployable speculative throughput.

Result:
`research/stretch/four-token-oracle-block-verification-013-result.md`.

### 014 — COMPLETE VALID FAIL

Plan:
`research/stretch/eight-token-oracle-block-verification-014-plan.md`

Runner/blob:
- `scripts/stretch_eight_token_oracle_block_verification_014.py`
- `6d7afd43969e752a7cce39ae474d7054ccc7edd8`.

Earlier launch-only attempt:
- `HOST_STATE_NOT_READY` at 52% free memory
- no scientific result.

Valid scientific run `20260820-122922`:
`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`.

Key observations:
- host gate PASS at 63% / 64% / 65% free
- prompt parity exact
- first target position already diverges: max abs `0.34375`
- all 16 position numerical gates fail
- top-1 equality remains true through steps 1–15 and fails at step 16
- final resident/streamed KV offsets both 20
- final KV bytes both 37,748,736 B
- stream-block min free 56%
- failure is scientific/numerical, not resource-related.

Result:
`research/stretch/eight-token-oracle-block-verification-014-result.md`.

Decision: freeze failure; do not relax parity; do not advance directly to block size 16.

### 015 — COMPLETE ATTRIBUTION PASS

Plan:
`research/stretch/eight-token-divergence-attribution-015-plan.md`

Runner/blob:
- `scripts/stretch_eight_token_divergence_attribution_015.py`
- `933c366220625e845e788b2ab1521ae78d9e7d15`.

Valid run `20260820-124515`:
`QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`.

Launch/provenance:
- source/version/config/layer-0 provenance PASS
- host samples 71% / 71% / 72% free
- launch swap 1232.62 MB.

Direct QuantizedLinear M4/M8:
- q_proj exact
- k_proj exact
- v_proj exact
- o_proj exact
- gate_proj **diverges**, max abs `0.001220703125`
- up_proj **diverges**, max abs `0.0009765625`
- down_proj **diverges**, max abs `1.75`.

Layer-0 causal trace:
- exact through input norm, q/k/v, q/k norm, RoPE, SDPA, o_proj, attention residual and post-attention layernorm
- first M4/M8 divergence: **gate_proj**
- gate_proj trace max abs `0.0078125`
- up_proj trace max abs `0.00439453125`
- SwiGLU max abs `0.005859375`
- down_proj max abs `0.03125`
- final block output max abs `0.0625`
- first M1/M4 traced divergence: none.

Resource:
- peak MLX memory 272,389,176 B
- disk after 36.715 GiB free.

Canonical interpretation:
> **The Stretch 014 eight-token parity failure is attributable to shape-dependent quantized-linear execution in the frozen MLX 0.31.2 / Qwen3-8B 3-bit path. At layer 0, M=4 remains numerically identical while M=8 first diverges at gate_proj and propagates through the MLP.**

Upstream context:
- MLX 0.31.x documents `quantized_matmul` dispatch dependent on `M` and different reduction trees.
- This is consistent with the observation but does not by itself identify the exact internal kernel used by this M1/3-bit run.
- Later `qmv_wide` work targets small-M speculative verification, but affine quantization is gated to newer GPU generations; do not assume an MLX upgrade fixes the M1 path without a separate controlled experiment.

Result:
`research/stretch/eight-token-divergence-attribution-015-result.md`.

Decision: map the exact M transition under the frozen environment before changing runtime/kernel policy.

## Stretch 016 — QuantizedLinear M-Boundary Mapping — READY

Plan:
`research/stretch/quantized-linear-m-boundary-mapping-016-plan.md`

Runner:
`scripts/stretch_quantized_linear_m_boundary_mapping_016.py`

Frozen runner blob:
`a5c3f4acd6a4150d2db7477f3f20d01a00b4f759`.

Question:
> At what exact `M` in 1..16 does each actual frozen layer-0 quantized projection stop reproducing the `M=1` first-row result?

Frozen:
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- Qwen3-8B 3-bit/group64 artifact
- actual layer-0 quantized weights
- no runtime upgrade
- no strict-mode patch
- no threshold relaxation
- no download.

Sweep:
- `M=1..16`
- q_proj / k_proj / v_proj / o_proj / gate_proj / up_proj / down_proj
- first input row bit-identical across all M
- down-projection probe independent of gate/up so its boundary is not confounded.

Primary classification:
`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`.

# Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_quantized_linear_m_boundary_mapping_016.py
python3 scripts/stretch_quantized_linear_m_boundary_mapping_016.py
```

No download is expected.

After the run, freeze the exact M boundary before deciding between preserving the exact block-size frontier and introducing a separately preregistered runtime/kernel experiment.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.
