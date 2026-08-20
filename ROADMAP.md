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

## Phase 7 — Stretch / Memory Hierarchy + Compute — ACTIVE

Frozen subject: Qwen3-8B 3-bit/group64, 36 layers, Apple M1 / 8 GB.
Preferred runtime after Stretch 030: mlx 0.31.2 + mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
Promotion target: ~20 token/s.

### Stretch 001–017 — COMPLETE / EXACT BLOCK FRONTIER
- [x] Layer-addressable I/O and bounded materialization
- [x] Exact streamed/full-logit parity
- [x] Persistent BF16 KV
- [x] Persistent transformer hotsets
- [x] M8 valid numerical-parity FAIL
- [x] q/k/v/o exact through M9
- [x] gate/up/down exact through M5; first divergence M6
- [x] M5 exact end-to-end over 15 oracle tokens
- [x] Freeze M5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] M5 ~+9.80% vs M4 on the pre-persistence/pre-cleanup schedule

### Stretch 019–022 — TRANSFORMER RESIDENCY — COMPLETE
- [x] H8 -> H16 ~+56.87%
- [x] H16 -> H24 ~+34.86%
- [x] H24 -> H32 ~+11.45%
- [x] H32 -> H36 ~+10.50%
- [x] Freeze H36 physical transformer-residency ceiling

### Stretch 023 — FULL RAW-WEIGHT PERSISTENCE — COMPLETE PASS
- [x] Preserve initial harness defect
- [x] Valid Fix1 PERSISTENT/STREAMED ~+59.89%
- [x] Freeze full model persistence

### Stretch 024 — COMPUTE/FRAMEWORK ATTRIBUTION — COMPLETE PASS
- [x] Preserve telemetry defect
- [x] MLP/attention `2.6608x`
- [x] Identify old 36x cleanup as largest old-schedule cost

### Stretch 025–027 — CLEANUP SCHEDULE — COMPLETE
- [x] 025 BATCHED/CONTROL `3.8628x`
- [x] 026 SHARED_BATCHED/BATCHED `1.1411x`
- [x] 027 SINGLE_PASS/SHARED_BATCHED `1.0867x`
- [x] Freeze one final cleanup/pass
- [x] Stretch 027 pooled `12.7307 token/s`
- [x] Canonical 027 blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`

### Stretch 028 — COMPUTE RE-ATTRIBUTION — COMPLETE PASS
- [x] Transformer compute `0.449696 s/block`
- [x] Attention `0.123101 s/block`
- [x] MLP `0.326595 s/block`
- [x] MLP/attention `2.6531x`
- [x] up/attention/gate/down each ~0.095–0.099 s/block

### Stretch 029 — GATE+UP QUANTIZED FUSION — COMPLETE PASS / PATH CLOSED
- [x] Preserve initial harness defect / no science
- [x] Fresh valid Fix1 ABBA `20260820-171714`
- [x] CONTROL `13.2286 token/s`
- [x] FUSED `12.3524 token/s`
- [x] FUSED exact but ~6.62% slower
- [x] Do not promote fusion; no rescue variants

### Stretch 030 — COHERENT MLX 0.31.2 vs 0.32.0 — COMPLETE PASS / 0.32.0 NOT PROMOTED
- [x] Preregister runtime as independent factor
- [x] Preserve original setup failure / no science
- [x] Setup Fix1 creates isolated coherent mlx/mlx-metal 0.32.0 treatment clone
- [x] Preserve runner Fix1 invariant failure / no science
- [x] Preserve runner Fix2 venv-symlink provenance failure / no science
- [x] Fix3 preserves selected venv `bin/python` paths and gates real child runtime
- [x] Valid Fix3 ABBA `20260820-175251`
- [x] `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`
- [x] MLX0312 `13.0748237296 token/s`
- [x] MLX0320 `12.3417530144 token/s`
- [x] MLX0320/0312 `0.9439326502x` (~5.61% slower)
- [x] Median block wall treatment ~6.84% higher
- [x] MLX 0.32.0 exact at M5 but not promoted
- [x] Retain coherent MLX 0.31.2 runtime
- [x] Do not remap M under 0.32.0 because `exact + faster` condition failed
- [x] Freeze `research/stretch/mlx-0312-0320-runtime-comparison-030-result.md`

### Stretch 031 — COMPLETE PASS — M5 GEOMETRY RETAINED
- [x] Re-open throughput-optimal block geometry on the current optimized schedule
- [x] Keep MLX 0.31.2, H36, full persistence, one cleanup/pass, BF16 KV frozen
- [x] Normalize both variants to the same first 10 frozen oracle tokens
- [x] M5 CONTROL = 2 x 5-token blocks
- [x] M2 TREATMENT = 5 x 2-token blocks
- [x] Apply geometry only after inherited Stretch 017/H36 source-provenance preflight
- [x] M5 helper `scripts/stretch_single_pass_m5_ten_token_control_031.py`
- [x] M5 blob `5f047b9e5f42bed959ced59e9329a8c8d7e3fc25`
- [x] M2 helper `scripts/stretch_single_pass_m2_ten_token_variant_031.py`
- [x] M2 blob `6005ff3a285760457d3255bc6505f2987c1fa4e8`
- [x] Balanced runner `scripts/stretch_single_pass_m2_m5_geometry_comparison_031.py`
- [x] Runner blob `bc3b21ff504c65d0852aad68a566cba924888d90`
- [x] Balanced order `M5 -> M2 -> M2 -> M5`
- [x] Primary metric = pooled accepted oracle tokens / target-block wall seconds
- [x] First genuine M2 frozen-gate failure = valid `M2_SINGLE_PASS_GEOMETRY_EXACTNESS_FAIL`; stop/no rescue
- [x] Complete exact ABBA = `SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS`
- [x] Preregister `research/stretch/single-pass-m2-m5-geometry-comparison-031-plan.md`
- [x] Preserve original M5 source-transform harness defect `20260820-180652`; scientific result NONE
- [x] Add Fix1 generated-runtime-source preflight; M5/M2 render, compile, frozen facts and normalized single-factor diff PASS
- [x] Preserve Fix1 fresh M5 parent/child-dispatch harness failure `20260820-182206`; scientific result NONE, no retry
- [x] Preserve Fix2 source/render PASS but M5 no-model dispatch-preflight failure `20260820-183232`; `.resolve()` dereferenced canonical venv Python, scientific result NONE
- [x] Fix3 preserves literal canonical venv `bin/python`; static regression guard and M5+M2 no-model dispatch markers PASS
- [x] Fresh valid Fix3 ABBA `20260820-184128`: `SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS`
- [x] M5 `14.3307 tok/s`, M2 `11.8349 tok/s`, M2/M5 `0.82584`; retain M5 geometry
- [x] Freeze result `research/stretch/single-pass-m2-m5-geometry-comparison-031-result.md`

### Stretch 032 candidate — M5 row-chunked quantized matmul — NO-GO
- [x] Diagnostic real-weight M5 `2+2+1` feasibility, layer 0, 3-bit/group64 affine, canonical venv
- [x] All q/k/v/o/gate/up/down outputs bit-exact; chunked slower for every projection
- [x] MLP-only diagnostic weighting estimates `-5.3249%` of Stretch 031 M5 median block wall; no Stretch 032 plan/ABBA
- [x] Preserve `research/stretch/m5-row-chunked-quantized-matmul-032-feasibility.md`; monolithic M5 qmatmul remains canonical

### Stretch 033+ — CONDITIONAL
- [x] M5 beat M2 in Stretch 031; retain M5 geometry and move only to another independently preregistered compute factor
- [ ] Select a new independent compute factor; do not revisit M geometry or row splits without a new authorization
- [ ] Consider attention/SDPA separately after geometry decision
- [ ] Consider later MLX small-M kernel developments only as separately pinned runtime/kernel experiments
- [ ] Real drafter only after target-side architecture is sufficiently optimized
- [ ] Measure real acceptance and end-to-end tok/s including draft/rejection/rollback
- [ ] Test KV capacity/quantization separately
- [ ] Promote interactive profile only when speed/quality evidence supports ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed/profiled evidence
- [ ] Publish findings when ready
