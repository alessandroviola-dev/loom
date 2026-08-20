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

## Phase 7 — Stretch / Memory Hierarchy & Target Architecture — ACTIVE

Frozen subject: Qwen3-8B 3-bit/group64, 36 layers, Apple M1 / 8 GB.
Frozen runtime: mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
Usability promotion target: ~20 token/s.

### Stretch 001–017 — EXACTNESS / ARCHITECTURE FRONTIER — COMPLETE
- [x] Layer-addressable I/O and bounded materialization/eviction
- [x] Exact streamed body/full-logit parity
- [x] Persistent ordinary KV
- [x] Materialization/process-read attribution
- [x] Persistent transformer hotset mechanism
- [x] Oracle target verification
- [x] Attribute M-dependent divergence to quantized-linear MLP execution
- [x] Map q/k/v/o exact through M=9; gate/up/down exact through M=5
- [x] Confirm M=5 exact end-to-end over 15 oracle tokens
- [x] Freeze M=5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] M5/M4 controlled target-rate ratio `1.09795340695x` (~+9.80%)
- [x] Freeze M5 as preferred exact block
- [x] Close block-size scaling under frozen runtime

### Stretch 019–022 — TRANSFORMER RESIDENCY CURVE — COMPLETE
- [x] H8 -> H16 ~+56.87%
- [x] H16 -> H24 ~+34.86%
- [x] H24 -> H32 ~+11.45%
- [x] H32 -> H36 ~+10.50%
- [x] Stretch 022 `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Freeze H36 transformer hotset `3,039,381,504 B`
- [x] Close transformer residency permanently; H36 is physical ceiling
- [x] No H33–H35 rescue search

### Stretch 023 — FULL RAW-WEIGHT PERSISTENCE — COMPLETE PASS
- [x] Preregister H36 shared-streamed vs shared-persistent ABBA
- [x] Preserve initial `20260820-151540` as harness defect / no scientific result
- [x] Apply harness-only fix1 before rerun
- [x] Valid scientific run `20260820-153308`
- [x] `M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- [x] Balanced `STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`
- [x] STREAMED pooled `2.2094465476 token/s`
- [x] PERSISTENT pooled `3.5325973363 token/s`
- [x] PERSISTENT/STREAMED `1.59886073736x` (~+59.89%)
- [x] Median target block wall ~36.83% lower
- [x] Shared rematerialization/process-read pressure effectively removed
- [x] Full persistent raw model payload `3,583,928,320 B`
- [x] Mean shared setup `0.3723145 s`
- [x] Estimated break-even `0.4392464321` target blocks
- [x] PERSISTENT min observed free `23%`; peak swap `2487.69 MB`
- [x] Freeze `M5 + H36 + full raw-weight persistence` as best demonstrated target architecture
- [x] Close raw-weight residency axis
- [x] Freeze `research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — FULL-PERSISTENT COMPUTE/KERNEL ATTRIBUTION — CURRENT / READY
- [x] Keep M5 frozen
- [x] Keep H36 frozen
- [x] Keep all raw model weights persistent
- [x] Keep MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1 frozen
- [x] Verify Qwen3 v0.31.3 block anatomy: input norm -> attention -> residual -> post norm -> MLP -> residual
- [x] Verify MLP anatomy: gate + up -> SwiGLU -> down
- [x] CONTROL = canonical Stretch 023 full-persistent helper
- [x] PROFILED = target-block-only explicit `mx.eval` component boundaries
- [x] Prompt remains unprofiled
- [x] Measure input norm, attention, residual1, post norm, gate, up, SwiGLU, down, residual2
- [x] Measure persistent layer build/reuse and cleanup wall
- [x] Preserve inherited shared-stage forward/materialization telemetry
- [x] Balanced order `CONTROL -> PROFILED -> PROFILED -> CONTROL`
- [x] Treat PROFILED/CONTROL speed only as instrumentation perturbation, never optimization evidence
- [x] Require exact inherited child PASS in both variants
- [x] Any failure => `COMPUTE_ATTRIBUTION_INCOMPLETE`; no auto retry/rescue
- [x] Preregister `research/stretch/full-persistent-compute-kernel-attribution-024-plan.md`
- [x] Canonical PROFILED entrypoint blob `845b10da26a70455cd40f483cea5d313f9ac12dd`
- [x] Canonical runner blob `f298d32f39cbed6410a1d395a735fce819f354f3`
- [ ] Run Stretch 024
- [ ] Freeze attribution result
- [ ] Select next independent optimization axis from measured bottleneck

### Stretch 025+ — CONDITIONAL NEXT AXIS
- [ ] If MLP dominates, test quantized-linear/MLP kernel or runtime factor separately
- [ ] If attention dominates, test attention/SDPA factor separately
- [ ] If per-layer cleanup/framework residual dominates, test GC/cache-clear restructuring separately
- [ ] If shared forward remains material, isolate embedding/head compute separately
- [ ] Consider newer MLX only as a separately preregistered environment comparison
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after target-side architecture/bottleneck is sufficiently characterized
- [ ] Measure real acceptance and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity/quantization separately
- [ ] Do not promote interactive profile until speed approaches frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed/profiled evidence
- [ ] Publish findings when ready
