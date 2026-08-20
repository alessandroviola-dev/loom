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

### Stretch 001–017 — COMPLETE / EXACT BLOCK FRONTIER
- [x] Layer-addressable I/O and bounded materialization/eviction
- [x] Exact streamed block/body/full-logit parity
- [x] Persistent ordinary BF16 KV
- [x] Exact autoregressive feedback
- [x] Materialization/process-I/O attribution
- [x] Persistent transformer hotset mechanism
- [x] M8 valid numerical-parity FAIL
- [x] Attribute M8 divergence to shape-dependent quantized-linear MLP path
- [x] Map q/k/v/o exact through M=9; gate/up/down exact through M=5
- [x] Confirm M5 exact end-to-end over 15 oracle tokens
- [x] Freeze M5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] M4 pooled `1.6983236855 token/s`
- [x] M5 pooled `1.8646802766 token/s`
- [x] M5/M4 ~+9.80%
- [x] Freeze M5 as preferred exact block
- [x] Close block-size scaling for frozen runtime

### Stretch 019–022 — TRANSFORMER RESIDENCY — COMPLETE
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
- [x] Apply harness-only Fix1
- [x] Valid run `20260820-153308`
- [x] `M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- [x] STREAMED pooled `2.2094465476 token/s`
- [x] PERSISTENT pooled `3.5325973363 token/s`
- [x] PERSISTENT/STREAMED ~+59.89%
- [x] Median target block wall ~36.83% lower
- [x] Shared rematerialization/process-read pressure effectively removed
- [x] Full persistent raw model `3,583,928,320 B`
- [x] Mean shared setup `0.3723145 s`
- [x] Estimated break-even `0.4392464321` target blocks
- [x] PERSISTENT min observed free `23%`; peak swap `2487.69 MB`
- [x] Freeze `M5 + H36 + full raw-weight persistence` as best demonstrated target architecture
- [x] Close raw-weight residency axis
- [x] Freeze `research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — FULL-PERSISTENT COMPUTE/KERNEL ATTRIBUTION — CURRENT / FIX2 READY
- [x] Keep M5 frozen
- [x] Keep H36 frozen
- [x] Keep all raw model weights persistent
- [x] Keep MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1 frozen
- [x] Qwen3 block anatomy frozen: input norm -> attention -> residual -> post norm -> MLP -> residual
- [x] MLP anatomy frozen: gate + up -> SwiGLU -> down
- [x] CONTROL = canonical Stretch 023 full-persistent helper blob `120ad7be2f275559898bf636ca8e8fe039a56c60`
- [x] PROFILED = target-block-only explicit `mx.eval` component boundaries
- [x] Prompt remains unprofiled
- [x] Measure norm, attention, residual1, post norm, gate, up, SwiGLU, down, residual2
- [x] Measure persistent-layer build/reuse and cleanup wall
- [x] Preserve inherited shared-stage forward/materialization telemetry
- [x] Balanced order `CONTROL -> PROFILED -> PROFILED -> CONTROL`
- [x] Treat PROFILED/CONTROL speed only as instrumentation perturbation
- [x] Require inherited child PASS in both variants
- [x] Any failure => `COMPUTE_ATTRIBUTION_INCOMPLETE`; no automatic retry/rescue
- [x] Preregister original plan `research/stretch/full-persistent-compute-kernel-attribution-024-plan.md`
- [x] Preserve run `20260820-155313` as harness/telemetry defect / no scientific result
- [x] Confirm exact defect: parent aggregation `NameError: name 'args' is not defined`
- [x] Freeze defect record `research/stretch/full-persistent-compute-kernel-attribution-024-harness-defect-20260820-155313.md`
- [x] Fix2 changes only three parent layer-geometry references to `len(HOTSET_LAYER_IDS)`
- [x] Canonical PROFILED Fix2 blob `83f9e12dfa30445810ca4d39150dbcd151ad3e66`
- [x] Canonical balanced runner Fix2 blob `de464c4fe5dca90c2fe110337f12e3f6424ea937`
- [x] Preregister Fix2 `research/stretch/full-persistent-compute-kernel-attribution-024-harness-fix2.md`
- [ ] Run a completely new Fix2 ABBA
- [ ] Freeze attribution result
- [ ] Select next independent optimization axis from measured bottleneck

### Stretch 025+ — CONDITIONAL NEXT AXIS
- [ ] If MLP dominates, test quantized-linear/MLP kernel or runtime factor separately
- [ ] If attention dominates, test attention/SDPA factor separately
- [ ] If cleanup/framework residual dominates, test GC/cache-clear restructuring separately
- [ ] If shared forward remains material, isolate embedding/head compute separately
- [ ] Consider newer MLX only as separately preregistered environment comparison
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 evidence with newer runtime results
- [ ] Select a real drafter only after target architecture/bottleneck is sufficiently characterized
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
