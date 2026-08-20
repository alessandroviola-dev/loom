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
- [x] Exact streamed parity
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
- [x] Close block-size scaling for frozen runtime

### Stretch 019–022 — TRANSFORMER RESIDENCY — COMPLETE
- [x] H8 -> H16 ~+56.87%
- [x] H16 -> H24 ~+34.86%
- [x] H24 -> H32 ~+11.45%
- [x] H32 -> H36 ~+10.50%
- [x] Freeze H36 physical transformer-residency ceiling
- [x] Close transformer residency permanently

### Stretch 023 — FULL RAW-WEIGHT PERSISTENCE — COMPLETE PASS
- [x] Preserve initial harness defect `20260820-151540`
- [x] Valid Fix1 run `20260820-153308`
- [x] `M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- [x] PERSISTENT/STREAMED ~+59.89%
- [x] Full persistent raw model `3,583,928,320 B`
- [x] Shared setup mean `0.3723145 s`; break-even `0.4392464321` target blocks
- [x] Freeze `M5 + H36 + full raw-weight persistence` as best target architecture
- [x] Close raw-weight residency
- [x] Freeze result file

### Stretch 024 — COMPUTE/FRAMEWORK ATTRIBUTION — COMPLETE PASS
- [x] Preserve Fix1 telemetry defect `20260820-155313` / no scientific result
- [x] Apply parent-geometry Fix2 only
- [x] Valid Fix2 ABBA `20260820-160140`
- [x] `FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`
- [x] Transformer compute `0.8081826820 s/block`
- [x] Attention path `0.2207656117 s/block`
- [x] MLP path `0.5874170703 s/block`
- [x] MLP/attention `2.6608178049x`
- [x] Per-layer cleanup sum `0.9268928333 s/block`
- [x] Shared forward `0.0552578333 s/block`
- [x] Residual unattributed `0.0995254846 s/block`
- [x] Accounted share ~94.74%
- [x] Identify cleanup/framework path as largest measured remaining category
- [x] Freeze `research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

### Stretch 025 — BATCHED TRANSFORMER CLEANUP — COMPLETE PASS
- [x] Valid ABBA run `20260820-161317`
- [x] `FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`
- [x] CONTROL pooled `2.7615996621 token/s`
- [x] BATCHED pooled `10.6674479980 token/s`
- [x] BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- [x] CONTROL median block `1.5667445 s`
- [x] BATCHED median block `0.464723 s` (~70.34% lower)
- [x] BATCHED mean one-per-body cleanup `0.060996 s`
- [x] BATCHED min free `23%`; peak swap `2535.12 MB`
- [x] Freeze `M5 + H36 + full persistence + one transformer cleanup/body` as preferred execution schedule
- [x] Freeze `research/stretch/full-persistent-batched-cleanup-comparison-025-result.md`

### Stretch 026 — SHARED-STAGE BATCHED CLEANUP — CURRENT / READY
- [x] Keep M5 frozen
- [x] Keep H36 frozen
- [x] Keep full raw-weight persistence frozen
- [x] Keep Stretch 025 one-per-transformer-body cleanup frozen in both variants
- [x] Scientific factor = shared-stage cleanup schedule only
- [x] BATCHED baseline blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`
- [x] SHARED_BATCHED treatment removes individual embedding/norm/head cleanup and performs one post-head cleanup
- [x] SHARED_BATCHED helper `scripts/stretch_full_persistent_shared_batched_cleanup_026.py`
- [x] SHARED_BATCHED blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`
- [x] Balanced runner `scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py`
- [x] Runner blob `e958bde5d8a239ffa5fd192922e0693854d478e0`
- [x] Balanced order `BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`
- [x] Preregister `research/stretch/full-persistent-shared-batched-cleanup-comparison-026-plan.md`
- [x] No automatic retry / no cache purge / no partial shared-stage cleanup rescue
- [ ] Run Stretch 026
- [ ] Freeze result
- [ ] Select next factor from controlled evidence

### Stretch 027+ — CONDITIONAL NEXT AXIS
- [ ] If SHARED_BATCHED wins materially, test merging transformer-body + shared-path cleanup into one end-of-pass cleanup as a separate factor
- [ ] If cleanup gains saturate, return to Stretch 024 compute evidence: MLP ~2.66x attention, with gate/up/down major projections
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
