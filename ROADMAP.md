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
Historical canonical runtime through Stretch 029: mlx 0.31.2 + mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
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
- [x] M5 ~+9.80% vs M4

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
- [x] Restore Stretch 027 as preferred 0.31.2 architecture

### Stretch 030 — COHERENT MLX 0.31.2 vs 0.32.0 — CURRENT / FIX3 READY
- [x] Preregister runtime as one independent factor
- [x] Freeze Qwen3, M5, H36, full persistence, one cleanup/pass, BF16 KV and gates
- [x] Keep mlx-lm 0.31.3 / Transformers 5.12.1 fixed
- [x] Preserve original shell-Python setup failure / no science
- [x] Setup Fix1 clones canonical venv and upgrades clone only
- [x] Setup Fix1 PASS: CONTROL mlx/mlx-metal 0.31.2; TREATMENT 0.32.0
- [x] Preserve treatment clone `.venvs/stretch030-mlx0320-fix1`
- [x] Preserve runner Fix1 invariant failure / no science
- [x] Preserve runner Fix2 environment-provenance failure / no science
- [x] Fix2 root cause: `.resolve()` dereferenced macOS venv `bin/python` symlink to framework Python
- [x] Record Fix2 defect `research/stretch/mlx-0312-0320-runtime-comparison-030-runner-defect-fix2-20260820-1745.md`
- [x] Create portable workload Fix1 `scripts/stretch_runtime_portable_single_pass_030_fix1.py`
- [x] Portable Fix1 blob `44251a524c77a379f43445444fa8a2643f1bfbdf`
- [x] Inner child keeps `Path(sys.executable)` without `.resolve()`
- [x] Inner runtime gate allows only preregistered mlx `{0.31.2, 0.32.0}` and keeps mlx-lm/Transformers fixed
- [x] Create balanced runner Fix3 `scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix3.py`
- [x] Runner Fix3 blob `108aed0e7e66fafe9b3213e33a57c34f9e0602d2`
- [x] CONTROL executes canonical venv `bin/python` without resolving symlink
- [x] TREATMENT executes validated treatment clone `bin/python`
- [x] Runner gates actual inner-child runtime provenance per variant
- [x] Balanced order `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`
- [x] Genuine treatment exactness outcome = `MLX_0320_RUNTIME_EXACTNESS_FAIL`
- [x] Complete exact ABBA outcome = `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`
- [x] Preregister Fix3 `research/stretch/mlx-0312-0320-runtime-comparison-030-harness-fix3.md`
- [ ] Run fresh Fix3 ABBA
- [ ] Freeze scientific outcome

### Stretch 031+ — CONDITIONAL
- [ ] If MLX 0.32.0 exact + faster: separately remap M exactness boundary under 0.32.0
- [ ] If exact + flat/slower: retain 0.31.2 and choose another compute factor
- [ ] If exactness FAIL: preserve FAIL; no mixed-package rescue
- [ ] Consider attention/SDPA separately
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
