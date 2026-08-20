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
Canonical MLX child interpreter: `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`.
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

### Stretch 019–022 — TRANSFORMER RESIDENCY — COMPLETE
- [x] H8 -> H16 ~+56.87%
- [x] H16 -> H24 ~+34.86%
- [x] H24 -> H32 ~+11.45%
- [x] H32 -> H36 ~+10.50%
- [x] Freeze H36 physical transformer-residency ceiling

### Stretch 023 — FULL RAW-WEIGHT PERSISTENCE — COMPLETE PASS
- [x] Preserve initial harness defect `20260820-151540`
- [x] Valid Fix1 `20260820-153308`
- [x] PERSISTENT/STREAMED ~+59.89%
- [x] Freeze full persistent raw model `3,583,928,320 B`

### Stretch 024 — COMPUTE/FRAMEWORK ATTRIBUTION — COMPLETE PASS
- [x] Preserve telemetry defect `20260820-155313`
- [x] Valid Fix2 `20260820-160140`
- [x] MLP/attention `2.6608178049x`
- [x] Identify old 36x cleanup as largest old-schedule category

### Stretch 025 — BATCHED TRANSFORMER CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-161317`
- [x] BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- [x] 36 per-layer cleanups -> one post-body cleanup

### Stretch 026 — SHARED-STAGE BATCHED CLEANUP — COMPLETE PASS
- [x] Valid ABBA `20260820-162951`
- [x] SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%)
- [x] Shared-stage cleanup 3x -> 1x post-head

### Stretch 027 — SINGLE END-OF-PASS CLEANUP — COMPLETE PASS / CANONICAL WORKLOAD
- [x] Valid ABBA `20260820-163715`
- [x] SINGLE_PASS/SHARED_BATCHED `1.0867142144x` (~+8.67%)
- [x] SINGLE_PASS pooled `12.7306853225 token/s`
- [x] Freeze one final cleanup/pass
- [x] Canonical workload blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`

### Stretch 028 — SINGLE_PASS COMPUTE RE-ATTRIBUTION — COMPLETE PASS
- [x] Valid ABBA `20260820-164802`
- [x] Transformer compute `0.4496960012 s/block`
- [x] Attention path `0.1231006118 s/block`
- [x] MLP path `0.3265953895 s/block`
- [x] MLP/attention `2.6530769000x`
- [x] up/attention/gate/down each ~0.095–0.099 s/block

### Stretch 029 — GATE+UP QUANTIZED FUSION — COMPLETE PASS / PATH CLOSED
- [x] Preserve initial `20260820-170503` wrapper harness defect / no scientific result
- [x] Fresh valid Fix1 ABBA `20260820-171714`
- [x] `GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`
- [x] CONTROL `13.2286272786 token/s`
- [x] FUSED `12.3523991241 token/s`
- [x] FUSED/CONTROL `0.9337627302x` (~6.62% slower)
- [x] FUSED exact under frozen M5 gates
- [x] Do not promote; no rescue variants
- [x] Freeze result and restore Stretch 027 as preferred 0.31.2 workload

### Stretch 030 — ISOLATED COHERENT MLX 0.31.2 vs 0.32.0 — CURRENT / ENV FIX1 READY
- [x] Preregister runtime as one independent factor
- [x] CONTROL and TREATMENT execute exact same Stretch 027 source/blob
- [x] Keep Qwen3, M5, H36, full persistence, one cleanup/pass, BF16 KV and gates frozen
- [x] Keep mlx-lm 0.31.3 and transformers 5.12.1 frozen
- [x] Preserve original setup failure: shell Python had MLX stack MISSING; no scientific result
- [x] Identify canonical LOOM MLX interpreter `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`
- [x] Record setup defect `research/stretch/mlx-0312-0320-runtime-comparison-030-setup-defect-20260820.md`
- [x] Correct treatment isolation: clone canonical venv rather than use shell/system site-packages
- [x] Correct macOS runtime factor to coherent package pair `mlx + mlx-metal`
- [x] CONTROL requires `mlx==0.31.2`, `mlx-metal==0.31.2`
- [x] TREATMENT requires `mlx==0.32.0`, `mlx-metal==0.32.0`
- [x] Keep Python/NumPy/safetensors/mlx-lm/Transformers identical
- [x] Never modify canonical venv
- [x] No package install during scientific runner
- [x] Setup Fix1 `scripts/stretch_mlx_0320_env_setup_030_fix1.py`
- [x] Setup Fix1 blob `dfcc05aa6f730756056a75d5bf867bbd717ac31f`
- [x] Runner Fix1 `scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix1.py`
- [x] Runner Fix1 blob `eb629a518edba8b9665785858bfe37402adc17e2`
- [x] Preregister Fix1 `research/stretch/mlx-0312-0320-runtime-comparison-030-harness-fix1.md`
- [x] Balanced order `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`
- [x] First MLX0320 frozen numerical/top1/oracle failure = valid `MLX_0320_RUNTIME_EXACTNESS_FAIL`; stop/no rescue
- [x] Complete exact ABBA = `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`
- [ ] Provision treatment clone with Setup Fix1 and require `Environment setup FIX1: PASS`
- [ ] Run balanced Fix1 Stretch 030
- [ ] Freeze scientific outcome

### Stretch 031+ — CONDITIONAL
- [ ] If MLX 0.32.0 exact + faster: separately remap M exactness boundary under 0.32.0
- [ ] If 0.32.0 exact + flat/slower: retain 0.31.2 and choose another compute factor
- [ ] If 0.32.0 exactness FAIL: preserve FAIL, no rescue package mix
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
