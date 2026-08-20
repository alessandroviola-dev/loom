# LOOM Roadmap

## Phase 0 — Foundation — COMPLETE
- [x] Mission / handoff discipline
- [x] Private repository `Ilcoach/loom`

## Phase 1 — Baseline — COMPLETE
- [x] Canonical Ollama/MLX 4B baseline
- [x] Coding Baseline 001

## Phase 2 — Benchmark Framework — ACTIVE
- [x] Coding Benchmark 01 v1.0.1
- [ ] Reasoning benchmark later

## Phase 3 — Local Agent Investigation — CHARACTERIZED
- [x] Pi Agentic Coding Benchmark 001

## Phase 4 — llama.cpp Frontier — CHARACTERIZED
- [x] 4B Q4 efficiency control
- [x] 8B Q4/Q3/Q2 memory/quality boundaries

## Phase 5 — Direct MLX 8B Frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified artifacts

## Phase 6 — Amplify — QUEUED BEHIND STRETCH
- [x] Amplifier 001–003 resource boundary characterized
- [x] Amplifier 004 compact-feedback plan/runner frozen
- [ ] Run Amplifier 004 after current Stretch architectural sequence

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Frozen subject: Qwen3-8B 3-bit/group64, 36 layers, Apple M1 / 8 GB.
Frozen runtime: mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
Usability promotion target: ~20 token/s.

### Stretch 001–013 — COMPLETE PASS
- [x] Layer-addressable I/O and bounded materialization/eviction
- [x] Exact streamed block/body/full-logit parity
- [x] Persistent ordinary KV
- [x] Exact autoregressive feedback
- [x] Materialization/process-read attribution
- [x] H8 persistent transformer hotset
- [x] M4 oracle target verification

### Stretch 014–017 — EXACT BLOCK FRONTIER CHARACTERIZED
- [x] M8 valid numerical-parity FAIL
- [x] Attribute M8 divergence to shape-dependent quantized-linear MLP execution
- [x] Map q/k/v/o exact through M=9; gate/up/down exact through M=5
- [x] Confirm M=5 exact end-to-end over 15 oracle tokens
- [x] Freeze M=5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] Balanced `M4 -> M5 -> M5 -> M4`
- [x] M4 pooled `1.6983236855 token/s`
- [x] M5 pooled `1.8646802766 token/s`
- [x] M5/M4 `1.09795340695x` (~+9.80%)
- [x] Freeze M=5 as preferred exact block
- [x] Close block-size scaling for frozen MLX 0.31.2

### Stretch 019 — COMPLETE PASS
- [x] `M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`
- [x] H8 pooled `1.6634679103 token/s`
- [x] H16 pooled `2.6094542092 token/s`
- [x] H16/H8 `1.56868322678x` (~+56.87%)
- [x] Confirm transformer residency/materialization as primary active speed axis
- [x] Freeze result

### Stretch 020 — COMPLETE PASS
- [x] `M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`
- [x] H16 pooled `1.8043852697 token/s`
- [x] H24 pooled `2.4333574371 token/s`
- [x] H24/H16 `1.34857975065x` (~+34.86%)
- [x] H24/H16 median materialization `0.160439630864x`
- [x] H24/H16 median forward `0.777126124736x`
- [x] Freeze result

### Stretch 021 — COMPLETE PASS
- [x] `M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Balanced `H24 -> H32 -> H32 -> H24`
- [x] H24 pooled `2.7358720706 token/s`
- [x] H32 pooled `3.0490014165 token/s`
- [x] H32/H24 `1.11445321190x` (~+11.45%)
- [x] H32/H24 median materialization `0.342275431401x`
- [x] H32/H24 median forward `0.964972714945x`
- [x] H32 hotset `2,701,672,448 B`
- [x] H32 hybrid raw-weight budget `2,973,941,760 B`
- [x] Observe diminishing transformer-residency returns
- [x] Freeze `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-result.md`

### Stretch 022 — COMPLETE PASS / TRANSFORMER RESIDENCY CEILING
- [x] Valid run `20260820-145851`
- [x] `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Balanced `H32 -> H36 -> H36 -> H32`
- [x] H32 pooled `2.7636911417 token/s`
- [x] H36 pooled `3.0539262294 token/s`
- [x] H36/H32 `1.10501719360x` (~+10.50%)
- [x] H36/H32 median transformer materialization `0.037393043672x`
- [x] H36/H32 median transformer forward `0.924682100759x`
- [x] H36/H32 full-pass process reads/block `0.087645726747x`
- [x] H36 transformer hotset `3,039,381,504 B`
- [x] H36 hybrid raw-weight budget `3,311,650,816 B`
- [x] H36 min observed free `25%`; peak swap `2040.5 MB`
- [x] Freeze M5+H36 as best demonstrated transformer-resident profile
- [x] Close transformer-hotset scaling permanently; no H33–H35 rescue search
- [x] Freeze `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-result.md`

Controlled transformer-residency gain curve:
- H8 -> H16: ~+56.87%
- H16 -> H24: ~+34.86%
- H24 -> H32: ~+11.45%
- H32 -> H36: ~+10.50%.

### Stretch 023 — H36 shared-stage persistence — CURRENT / READY
- [x] Keep exact block size M=5 frozen
- [x] Keep all 36 transformer layers persistent
- [x] Scientific factor = embedding + final RMSNorm + LM head streamed-per-pass -> persistent-once only
- [x] Shared payload = `544,546,816 B`
- [x] Full persistent raw model payload = `3,583,928,320 B`
- [x] Preserve model/runtime/quantization/KV/parity/I-O/safety policy
- [x] Preserve no-cache-purge policy
- [x] Control H36 blob `9111dde483206a774a9fe5426522dab6e77cecca`
- [x] Add full-persistent helper `scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
- [x] Freeze helper blob `8c263e7be15441581e481e6f41cbd16f87d4df4b`
- [x] Add balanced runner `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py`
- [x] Freeze balanced runner blob `b8d69c218ee251662fc54a809ca6bf13a4a4e4da`
- [x] Preregister `research/stretch/m5-h36-shared-stage-persistence-023-plan.md`
- [x] Balanced order `STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`
- [x] Measure shared materialization/forward separately from transformer metrics
- [x] Exclude one-time treatment setup from steady-state target rate but report it separately
- [x] Estimate target-block break-even for the one-time shared setup
- [x] Any constituent/provenance failure => `SHARED_STAGE_COMPARISON_INCOMPLETE`, no winner/no automatic retry
- [ ] Run Stretch 023
- [ ] Freeze result
- [ ] Close raw-weight residency axis regardless of outcome

### Stretch 024+ — next independent axis after raw-weight residency
- [ ] Select next factor from Stretch 023 residual evidence
- [ ] If residency is saturated, prioritize compute/kernel/runtime or a separately controlled prefetch experiment where relevant
- [ ] Consider newer MLX only as a separately preregistered environment change
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after target-side architecture is sufficiently characterized
- [ ] Measure actual acceptance rate and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity and KV quantization separately
- [ ] Do not promote an interactive profile until speed approaches frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
