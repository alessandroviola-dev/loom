# LOOM Roadmap

## Phase 0 — Foundation
- [x] Project name / mission / handoff discipline
- [x] Private repository `Ilcoach/loom`

## Phase 1 — Baseline
- [x] Canonical Ollama/MLX 4B baseline
- [x] Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6

## Phase 2 — Benchmark framework
- [x] Coding Benchmark 01 v1.0.1
- [ ] Reasoning benchmark later

## Phase 3 — Local agent investigation
- [x] Pi Agentic Coding Benchmark 001: delivery-adjusted 77.15, delivery 6/6

## Phase 4 — llama.cpp frontier — CHARACTERIZED
- [x] 4B Q4 efficiency control
- [x] 8B Q4/Q3/Q2 memory/quality boundaries characterized

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified artifacts

## Phase 6 — Amplify — ACTIVE / QUEUED BEHIND STRETCH
- [x] Amplifier 001–003 resource boundary characterized
- [x] Do not claim leak/KV/allocator root cause
- [x] Amplifier 004 compact-feedback plan/runner frozen
- [ ] Run Amplifier 004 after current Stretch architectural sequence

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Frozen subject: Qwen3-8B 3-bit, 36 layers, vocab 151936, untied embedding/head, 3-bit/group64.

Usability promotion target:
- [x] Freeze ~20 token/s as interactive target (`research/usability-speed-target-v1.md`)
- [x] Keep target separate from scientific PASS gates for intermediate experiments

### Stretch 001 — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact and selectively readable

### Stretch 002 — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] one layer 0 -> 84,427,264 -> 0 B active

### Stretch 003 — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] repeated one-layer cycles remain bounded

### Stretch 004 — COMPLETE PASS
- [x] `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [x] real Qwen3 block compute
- [x] exact numerical parity

### Stretch 005 — COMPLETE PASS
- [x] `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`
- [x] resident/streamed ratio ~8x
- [x] exact numerical parity

### Stretch 006 — COMPLETE PASS
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] resident body 3,039,315,964 B
- [x] max streamed layer 84,427,264 B
- [x] ratio 35.99922371048291x
- [x] exact full-body parity

### Stretch 007A — COMPLETE PASS
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] embedding 272,269,312 B
- [x] norm 8,192 B
- [x] LM head 272,269,312 B

### Stretch 007B — COMPLETE PASS
- [x] `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`
- [x] resident model 3,583,928,320 B
- [x] max streamed stage 272,269,312 B
- [x] ratio 13.16317396798652x
- [x] exact full logits

### Stretch 008 — COMPLETE PASS
- [x] `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] persistent KV reuse offsets 4 -> 5
- [x] exact prompt/post-token resident parity
- [x] stdout-pipe incident frozen as harness-only

### Stretch 009 — COMPLETE PASS
- [x] `FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] exact four-token sequence `[1,374,264,4647]`
- [x] KV offsets 4 -> 8
- [x] mean layer materialization 0.188658 s/token
- [x] mean layer forward 0.192317 s/token

### Stretch 010 — COMPLETE PASS
- [x] `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`
- [x] exact 16-token resident/streamed sequence
- [x] KV final offset 20, allocation 37,748,736 B
- [x] logical throughput 0.346144 token/s
- [x] identify materialization transition ~0.19 -> ~1.4 s while forward stays ~0.19 s
- [x] freeze canonical result

### Stretch 011 — COMPLETE PASS
- [x] `MATERIALIZATION_IO_ATTRIBUTION_PASS`
- [x] exact 16-token correctness retained
- [x] late transformer materialization reads ~3,039,395,840 B/token
- [x] late full-pass process reads ~3.584 GB/token
- [x] materialization-time/disk-read Pearson 0.9995866107996246
- [x] identify repeated target-weight traversal as dominant late cost under current accounting
- [x] preserve non-forensic interpretation boundary
- [x] freeze canonical result

### Stretch 012 — Eight-layer persistent hotset — COMPLETE PASS
- [x] Valid run `20260819-192349`
- [x] `EIGHT_LAYER_PERSISTENT_HOTSET_PASS`
- [x] Retain layers 0..7 across prompt + 16 tokens
- [x] Exact prompt + all 16 feedback logits
- [x] Same frozen 16-token sequence
- [x] Hotset exactly 675,418,112 B
- [x] Hybrid simultaneous raw-weight budget 947,687,424 B
- [x] Resident/hybrid raw-weight ratio 3.7817620338074676x
- [x] Mean layer materialization 0.407471 s/token
- [x] Mean layer forward 0.190394 s/token
- [x] Mean full pass 2.092360 s/token
- [x] Logical throughput **0.477929 token/s**
- [x] Improvement vs 011 ~52.98%
- [x] Late full-pass process reads mean ~899,052,885 B/token
- [x] Observe strong host/cache interaction beyond simple 8-layer payload subtraction
- [x] Stream-token bucket min free 59%
- [x] Freeze `research/stretch/eight-layer-persistent-hotset-012-result.md`
- [x] Decide hotset-only scaling is insufficient for ~20 token/s target

### Stretch 013 — Four-token oracle block verification — COMPLETE PASS
- [x] Valid run `20260819-193702`
- [x] `FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`
- [x] Preserve Stretch 012 eight-layer hotset
- [x] Change 16 one-token target traversals -> four causal blocks of four oracle tokens
- [x] All 16 oracle tokens accepted
- [x] All 16 block-position logits exact vs resident sequential control
- [x] Top-1 equality at all 16 positions
- [x] Streamed KV offsets 4 -> 8 -> 12 -> 16 -> 20
- [x] Accepted tokens/target traversal = 4.0
- [x] Target block total wall 8.484694 s
- [x] Oracle target-verification throughput **1.8857486198 token/s**
- [x] Rate ratio vs Stretch 012 **3.9456668664x**
- [x] Freeze `research/stretch/four-token-oracle-block-verification-013-result.md`

### Stretch 014 — Eight-token oracle block verification — COMPLETE VALID FAIL
- [x] Preserve exact Stretch 013 source blob `deeb0339294162f38cd4522d2890b6a0c728f96e`
- [x] Freeze runner blob `6d7afd43969e752a7cce39ae474d7054ccc7edd8`
- [x] Earlier launch-only attempt `HOST_STATE_NOT_READY`; no scientific result
- [x] Valid run `20260820-122922`
- [x] `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`
- [x] Prompt parity exact
- [x] Numerical divergence starts at global step 1; max abs diff `0.34375`
- [x] All 16 position-level numerical gates fail
- [x] Top-1 differs at step 16
- [x] Final resident/streamed KV offsets both 20; KV bytes both 37,748,736 B
- [x] Failure is not a resource abort
- [x] Freeze `research/stretch/eight-token-oracle-block-verification-014-result.md`
- [x] Do not relax parity or advance directly to a 16-token block

### Stretch 015 — Eight-token divergence attribution — COMPLETE ATTRIBUTION PASS
- [x] Valid run `20260820-124515`
- [x] `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`
- [x] Host-state/provenance/version/config/layer-0 gates PASS
- [x] `M=1` vs `M=4`: no traced layer-0 divergence
- [x] `M=4` vs `M=8`: q/k/v/o remain exact
- [x] First direct QuantizedLinear divergence: `gate_proj`
- [x] Direct `gate_proj` M4/M8 max abs diff `0.001220703125`
- [x] Direct `up_proj` M4/M8 max abs diff `0.0009765625`
- [x] Direct `down_proj` M4/M8 max abs diff `1.75`
- [x] Layer-0 trace remains exact through post-attention layernorm
- [x] First traced divergence: `gate_proj`
- [x] Block-output M4/M8 max abs diff `0.0625`
- [x] Freeze `research/stretch/eight-token-divergence-attribution-015-result.md`
- [x] Attribute Stretch 014 failure to shape-dependent quantized-linear execution under frozen MLX 0.31.2

### Stretch 016 — QuantizedLinear M-boundary mapping — CURRENT / READY
- [x] Preserve MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- [x] Preserve Qwen3-8B 3-bit/group64 and actual layer-0 quantized weights
- [x] Sweep `M=1..16`
- [x] Compare identical first output row vs `M=1`
- [x] Test q/k/v/o/gate/up/down independently
- [x] Keep down-projection probe independent of upstream gate/up divergence
- [x] Preregister `research/stretch/quantized-linear-m-boundary-mapping-016-plan.md`
- [x] Add `scripts/stretch_quantized_linear_m_boundary_mapping_016.py`
- [x] Freeze runner blob `a5c3f4acd6a4150d2db7477f3f20d01a00b4f759`
- [ ] Run Stretch 016
- [ ] Freeze exact M-boundary result

### Stretch 017+ — conditional path
- [ ] If a sharp M boundary is mapped, preserve block size 4 as the exact 0.31.2 baseline unless evidence supports another exact size
- [ ] Decide between another speed axis and a separately preregistered runtime/kernel experiment
- [ ] Do not assume MLX 0.32 `qmv_wide` fixes Apple M1 affine 3-bit; its affine path is gated to newer GPU generations
- [ ] Resume oracle block-size scaling only after the numerical boundary is understood
- [ ] Select/implement a real draft model only after the oracle target-side boundary is characterized
- [ ] Measure real acceptance rate + actual end-to-end tok/s including draft cost and rejection behavior
- [ ] Keep hotset and speculative/block verification as separable optimization axes
- [ ] Test prefetch/double buffering separately
- [ ] Test KV quantization separately
- [ ] Do not promote any profile as interactive until speed approaches the frozen usability target

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
