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
Promotion target: ~20 token/s.

### Stretch 001–017 — COMPLETE / EXACT BLOCK FRONTIER
- [x] Layer-addressable I/O and bounded materialization
- [x] Exact streamed/full-logit parity
- [x] Persistent BF16 KV
- [x] Materialization/process-I/O attribution
- [x] Persistent transformer hotsets
- [x] M8 valid numerical-parity FAIL
- [x] Quantized-linear shape dependence mapped
- [x] q/k/v/o exact through M9; gate/up/down exact through M5
- [x] M5 exact end-to-end over 15 oracle tokens
- [x] Freeze M5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] M5 ~+9.80% vs M4
- [x] Freeze M5 as preferred exact block
- [x] Close block-size scaling

### Stretch 019–022 — TRANSFORMER RESIDENCY — COMPLETE
- [x] H8 -> H16 ~+56.87%
- [x] H16 -> H24 ~+34.86%
- [x] H24 -> H32 ~+11.45%
- [x] H32 -> H36 ~+10.50%
- [x] Freeze H36 physical transformer-residency ceiling
- [x] Close transformer residency

### Stretch 023 — FULL RAW-WEIGHT PERSISTENCE — COMPLETE PASS
- [x] Preserve initial harness defect `20260820-151540`
- [x] Valid Fix1 `20260820-153308`
- [x] `M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- [x] PERSISTENT/STREAMED ~+59.89%
- [x] Full persistent raw model `3,583,928,320 B`
- [x] Freeze M5 + H36 + full raw-weight persistence
- [x] Close raw-weight residency

### Stretch 024 — COMPUTE/FRAMEWORK ATTRIBUTION — COMPLETE PASS
- [x] Preserve Fix1 telemetry defect `20260820-155313`
- [x] Valid Fix2 `20260820-160140`
- [x] `FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`
- [x] MLP/attention `2.6608178049x`
- [x] Old per-layer cleanup sum `0.9268928333 s/block`
- [x] Identify cleanup/framework as largest old-schedule category
- [x] Freeze result

### Stretch 025 — BATCHED TRANSFORMER CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-161317`
- [x] `FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`
- [x] BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- [x] Replace 36 per-layer cleanups with one post-body cleanup
- [x] Freeze result

### Stretch 026 — SHARED-STAGE BATCHED CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-162951`
- [x] `FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`
- [x] SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%)
- [x] Consolidate embedding/norm/head cleanup to one post-head cleanup
- [x] Freeze result

### Stretch 027 — SINGLE END-OF-PASS CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-163715`
- [x] `FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`
- [x] SINGLE_PASS/SHARED_BATCHED `1.0867142144x` (~+8.67%)
- [x] SINGLE_PASS pooled `12.7306853225 token/s`
- [x] Median block `0.396305 s`
- [x] Freeze one final cleanup/pass
- [x] Do not promote zero-cleanup
- [x] Close cleanup-frequency axis
- [x] Freeze result

### Stretch 028 — SINGLE_PASS COMPUTE RE-ATTRIBUTION — COMPLETE PASS
- [x] Valid ABBA `20260820-164802`
- [x] `SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`
- [x] CONTROL pooled `12.7076859473 token/s`
- [x] PROFILED/CONTROL instrumentation ratio `0.6851113869x`
- [x] Transformer compute `0.4496960012 s/block`
- [x] Attention path `0.1231006118 s/block`
- [x] MLP path `0.3265953895 s/block`
- [x] MLP/attention `2.6530769000x`
- [x] up_proj `0.0993149300 s/block`
- [x] attention `0.0985796947 s/block`
- [x] gate_proj `0.0965807990 s/block`
- [x] down_proj `0.0942869299 s/block`
- [x] Final cleanup `0.0617505 s/block`
- [x] Shared forward `0.0280353333 s/block`
- [x] Accounted share ~93.95%
- [x] Freeze `research/stretch/single-pass-compute-reattribution-028-result.md`
- [x] Select quantized MLP projection path as first compute optimization axis

### Stretch 029 — GATE+UP QUANTIZED FUSION — CURRENT / READY
- [x] Keep M5 frozen
- [x] Keep H36 frozen
- [x] Keep full raw-weight persistence frozen
- [x] Keep one final cleanup/pass frozen
- [x] Keep MLX 0.31.2 / model / KV / resource policy frozen
- [x] CONTROL = Stretch 027 SINGLE_PASS blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`
- [x] Scientific factor = gate_proj + up_proj two quantized matmuls -> one fused quantized matmul
- [x] Concatenate packed quantized weight/scales/affine biases once by output row during setup
- [x] No per-forward weight concatenation
- [x] Remove original gate/up module references after fused materialization
- [x] Keep SwiGLU and down_proj unchanged
- [x] Treat frozen numerical/top1/acceptance mismatch as valid scientific fusion FAIL
- [x] No rescue ordering / partial fusion / threshold relaxation / automatic retry
- [x] Balanced order `CONTROL -> FUSED -> FUSED -> CONTROL`
- [x] FUSED helper `scripts/stretch_gate_up_quantized_fusion_029.py`
- [x] FUSED blob `c37ff6313106807c1e2e5070b7fb8f19e97abea6`
- [x] Runner `scripts/stretch_gate_up_quantized_fusion_comparison_029.py`
- [x] Runner blob `8d89665b5d3061891a53f1734e19331aa1a4fb34`
- [x] Preregister `research/stretch/gate-up-quantized-fusion-029-plan.md`
- [ ] Run Stretch 029
- [ ] Freeze PASS or valid scientific fusion FAIL
- [ ] Select next independent compute factor

### Stretch 030+ — CONDITIONAL COMPUTE/RUNTIME AXIS
- [ ] If gate+up fusion is exact and faster, promote it and remeasure residual compute
- [ ] If fusion fails exactness, preserve FAIL and choose a different compute factor
- [ ] If fusion is exact but flat/slower, close this implementation path
- [ ] Consider attention/SDPA separately
- [ ] Consider newer MLX only as separately preregistered environment comparison
- [ ] Never overwrite frozen MLX 0.31.2 evidence with newer runtime results
- [ ] Select a real drafter only after target-side architecture is sufficiently optimized
- [ ] Measure real acceptance and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity/quantization separately
- [ ] Do not promote interactive profile until speed approaches ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed/profiled evidence
- [ ] Publish findings when ready
