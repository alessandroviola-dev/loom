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
- [x] Identify 36x cleanup as largest old-schedule cost

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

### Stretch 030 — COHERENT MLX 0.31.2 vs 0.32.0 — CURRENT / FIX2 READY
- [x] Preregister runtime as independent factor
- [x] Freeze Qwen3, M5, H36, full persistence, one cleanup/pass, BF16 KV and gates
- [x] Keep mlx-lm 0.31.3 / Transformers 5.12.1 fixed
- [x] Preserve original shell-Python setup failure / no science
- [x] Identify canonical LOOM interpreter `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`
- [x] Correct runtime factor to coherent package pair `mlx + mlx-metal`
- [x] Setup Fix1 clones canonical venv and upgrades clone only
- [x] Setup Fix1 PASS: CONTROL 0.31.2/0.31.2 and TREATMENT 0.32.0/0.32.0 validated
- [x] Preserve treatment clone `.venvs/stretch030-mlx0320-fix1`
- [x] Preserve runner Fix1 preflight failure / no science
- [x] Exact Fix1 defect: required nonexistent `MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL`
- [x] Record `research/stretch/mlx-0312-0320-runtime-comparison-030-runner-defect-20260820-1738.md`
- [x] Identify historical inner-child hard-coded canonical venv problem before scientific rerun
- [x] Create identical runtime-portable workload for both variants
- [x] Portable workload `scripts/stretch_runtime_portable_single_pass_030.py`
- [x] Portable blob `16243fd78a6eb5a831c426e0c1e432a4f45db988`
- [x] Inner child inherits selected outer `sys.executable`
- [x] Inner version gate allows only preregistered mlx `{0.31.2, 0.32.0}` while keeping mlx-lm/Transformers fixed
- [x] Create balanced runner Fix2 `scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix2.py`
- [x] Runner Fix2 blob `6dd993418bff0bf9ec65c6b9a80f4bb382eb4976`
- [x] Runner gates actual inner child version per ABBA variant
- [x] Balanced order `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`
- [x] Correct genuine treatment exactness outcome = `MLX_0320_RUNTIME_EXACTNESS_FAIL`
- [x] Complete exact ABBA outcome = `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`
- [x] Preregister Fix2 `research/stretch/mlx-0312-0320-runtime-comparison-030-harness-fix2.md`
- [ ] Run fresh Fix2 ABBA
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
