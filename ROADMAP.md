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
Historical canonical runtime through Stretch 029: mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.
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
- [x] Freeze M5 as preferred exact block for 0.31.2

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
- [x] Close cleanup-frequency axis; zero-cleanup remains unproven
- [x] Canonical workload blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`

### Stretch 028 — SINGLE_PASS COMPUTE RE-ATTRIBUTION — COMPLETE PASS
- [x] Valid ABBA `20260820-164802`
- [x] Transformer compute `0.4496960012 s/block`
- [x] Attention path `0.1231006118 s/block`
- [x] MLP path `0.3265953895 s/block`
- [x] MLP/attention `2.6530769000x`
- [x] up/attention/gate/down each ~0.095–0.099 s/block
- [x] Select quantized compute path as next axis

### Stretch 029 — GATE+UP QUANTIZED FUSION — COMPLETE PASS / PATH CLOSED
- [x] Preregister exact single-factor fusion
- [x] Preserve initial `20260820-170503` wrapper harness defect / no scientific result
- [x] Harness Fix1 leaves original scientific fusion callback unchanged
- [x] Fresh valid ABBA `20260820-171714`
- [x] `GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`
- [x] CONTROL `13.2286272786 token/s`
- [x] FUSED `12.3523991241 token/s`
- [x] FUSED/CONTROL `0.9337627302x` (~6.62% slower)
- [x] FUSED exact under frozen M5 gates
- [x] FUSED median block wall ~8.62% higher
- [x] Do not promote fusion
- [x] No rescue ordering / partial fusion / threshold relaxation
- [x] Freeze `research/stretch/gate-up-quantized-fusion-029-result.md`
- [x] Restore Stretch 027 SINGLE_PASS as preferred 0.31.2 workload

### Stretch 030 — ISOLATED MLX 0.31.2 vs 0.32.0 — CURRENT / READY FOR ENV SETUP
- [x] Preregister runtime as one independent factor
- [x] CONTROL and TREATMENT execute exact same Stretch 027 source/blob
- [x] Keep Qwen3 3-bit/group64, M5, H36, full persistence, one cleanup/pass, BF16 KV and gates frozen
- [x] Keep mlx-lm 0.31.3 and transformers 5.12.1 frozen
- [x] Treatment venv uses `--system-site-packages`
- [x] Overlay only `mlx==0.32.0 --no-deps`
- [x] Require Python/NumPy/safetensors parity across environments
- [x] Do not modify canonical environment
- [x] Do not install packages during scientific runner
- [x] Environment setup utility `scripts/stretch_mlx_0320_env_setup_030.py`
- [x] Setup blob `fde39967be02cba81ea14bb043c9fdacd24db861`
- [x] Balanced runner `scripts/stretch_mlx_0312_0320_runtime_comparison_030.py`
- [x] Runner blob `0d0a27549067cef61a1dca7d3bf8f0e1f954d98b`
- [x] Balanced order `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`
- [x] First MLX0320 frozen numerical/top1/oracle failure = valid `MLX_0320_RUNTIME_EXACTNESS_FAIL`; stop/no rescue
- [x] Complete exact ABBA = `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`
- [x] Preregister `research/stretch/mlx-0312-0320-runtime-comparison-030-plan.md`
- [ ] Provision isolated MLX0320 environment and require `Environment setup: PASS`
- [ ] Run balanced Stretch 030
- [ ] Freeze scientific outcome

### Stretch 031+ — CONDITIONAL
- [ ] If MLX 0.32.0 exact + faster: promote only on new runtime evidence branch
- [ ] If 0.32.0 exact + faster: separately remap M exactness boundary under 0.32.0; never inherit old M5 ceiling blindly
- [ ] If 0.32.0 exact + flat/slower: retain 0.31.2 and choose different compute factor
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
