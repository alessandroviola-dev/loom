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
- [x] Shared setup mean `0.3723145 s`; break-even `0.4392464321` target blocks
- [x] Freeze M5 + H36 + full raw-weight persistence
- [x] Close raw-weight residency

### Stretch 024 — COMPUTE/FRAMEWORK ATTRIBUTION — COMPLETE PASS
- [x] Preserve Fix1 telemetry defect `20260820-155313`
- [x] Valid Fix2 `20260820-160140`
- [x] `FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`
- [x] Transformer compute `0.8081826820 s/block`
- [x] Attention path `0.2207656117 s/block`
- [x] MLP path `0.5874170703 s/block`
- [x] MLP/attention `2.6608178049x`
- [x] Per-layer cleanup sum `0.9268928333 s/block`
- [x] Identify cleanup/framework as largest measured category
- [x] Freeze result

### Stretch 025 — BATCHED TRANSFORMER CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-161317`
- [x] `FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`
- [x] BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- [x] Median block wall ~70.34% lower
- [x] Replace 36 per-layer cleanup calls with one cleanup/body
- [x] Freeze result

### Stretch 026 — SHARED-STAGE BATCHED CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-162951`
- [x] `FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`
- [x] SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%)
- [x] Median block wall ~11.19% lower
- [x] Consolidate embedding/norm/head cleanup to one post-head cleanup
- [x] Freeze result

### Stretch 027 — SINGLE END-OF-PASS CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-163715`
- [x] `FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`
- [x] SHARED_BATCHED pooled `11.7148420019 token/s`
- [x] SINGLE_PASS pooled `12.7306853225 token/s`
- [x] SINGLE_PASS/SHARED_BATCHED `1.0867142144x` (~+8.67%)
- [x] Median block wall `0.4188015 -> 0.396305 s` (~5.37% lower)
- [x] SINGLE_PASS final cleanup `0.0558401667 s/block`
- [x] SINGLE_PASS min free `23%`; peak swap `2562.94 MB`
- [x] Freeze one final cleanup/pass as preferred schedule
- [x] Explicitly do not promote zero-cleanup
- [x] Close cleanup-frequency consolidation axis
- [x] Freeze `research/stretch/full-persistent-single-pass-cleanup-comparison-027-result.md`

### Stretch 028 — SINGLE_PASS COMPUTE RE-ATTRIBUTION — CURRENT / READY
- [x] Keep M5 frozen
- [x] Keep H36 frozen
- [x] Keep full raw-weight persistence frozen
- [x] Keep one final cleanup/pass frozen
- [x] Keep MLX 0.31.2 / model / KV / parity / resource policy frozen
- [x] CONTROL = canonical Stretch 027 helper blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`
- [x] PROFILED = target-block-only explicit `mx.eval` component boundaries
- [x] Prompt remains unprofiled
- [x] Measure norm, attention, residual1, post norm, gate, up, SwiGLU, down, residual2
- [x] Preserve final cleanup and shared-stage telemetry
- [x] Balanced order `CONTROL -> PROFILED -> PROFILED -> CONTROL`
- [x] Treat PROFILED/CONTROL speed only as instrumentation perturbation
- [x] PROFILED helper `scripts/stretch_single_pass_compute_reattribution_028_profiled.py`
- [x] PROFILED blob `0858e39a46bf09fe7750691b6dcd95b6753e5c70`
- [x] Runner `scripts/stretch_single_pass_compute_reattribution_comparison_028.py`
- [x] Runner blob `65d1c93967ed786623a3899e0f510ad9ef8de1e2`
- [x] Preregister `research/stretch/single-pass-compute-reattribution-028-plan.md`
- [x] No automatic retry/rescue
- [ ] Run Stretch 028
- [ ] Freeze re-attribution result
- [ ] Select first compute/kernel optimization from new ranking

### Stretch 029+ — COMPUTE/KERNEL OPTIMIZATION
- [ ] If MLP dominates re-attribution, choose one quantized-linear/MLP factor
- [ ] If attention dominates, choose one attention/SDPA factor
- [ ] If residual/framework wall remains material, isolate it first
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
