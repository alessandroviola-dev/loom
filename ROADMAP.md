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

### Stretch 001–009 — COMPLETE PASS
- [x] Layer-addressable I/O
- [x] Bounded materialization/eviction
- [x] Exact streamed transformer parity
- [x] Full 36-layer body parity
- [x] Full-logit parity
- [x] Persistent ordinary KV
- [x] Exact autoregressive feedback through 4 tokens

### Stretch 010 — COMPLETE PASS
- [x] `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`
- [x] Exact 16-token sequence/parity
- [x] Final KV offset 20
- [x] Logical throughput 0.346144 token/s
- [x] Identify late materialization slowdown

### Stretch 011 — COMPLETE PASS
- [x] `MATERIALIZATION_IO_ATTRIBUTION_PASS`
- [x] Late transformer materialization ~3.039 GB/token process reads
- [x] Late full pass ~3.584 GB/token
- [x] Materialization-time/process-read correlation ~0.9996
- [x] Freeze repeated target-weight traversal as dominant late cost under current accounting

### Stretch 012 — COMPLETE PASS
- [x] `EIGHT_LAYER_PERSISTENT_HOTSET_PASS`
- [x] H8 layers 0..7 = 675,418,112 B
- [x] Exact 16-token parity
- [x] Logical throughput 0.477929 token/s
- [x] ~52.98% improvement vs Stretch 011

### Stretch 013 — COMPLETE PASS
- [x] `FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`
- [x] 4 x 4-token oracle target traversals
- [x] Exact all 16 position logits/top-1
- [x] KV `4 -> 8 -> 12 -> 16 -> 20`
- [x] Oracle target-verification throughput 1.8857486198 token/s

### Stretch 014 — COMPLETE VALID FAIL
- [x] M=8 oracle blocks
- [x] `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`
- [x] Numerical divergence begins at first target position
- [x] KV state remains correct
- [x] No threshold relaxation

### Stretch 015 — COMPLETE ATTRIBUTION PASS
- [x] `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`
- [x] M4/M8 exact through attention/post-attention norm
- [x] First M4/M8 divergence at MLP `gate_proj`
- [x] gate/up/down shape-dependent at M8

### Stretch 016 — COMPLETE PASS
- [x] Valid run `20260820-125212`
- [x] `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`
- [x] q/k/v/o exact through M=9; first divergent M=10
- [x] gate/up/down exact through M=5; first divergent M=6
- [x] MLP sets exactness frontier

### Stretch 017 — COMPLETE PASS
- [x] Valid run `20260820-130124`
- [x] `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- [x] Full-model M=5 exact end-to-end
- [x] Exact all 15 position logits/top-1
- [x] All 15 oracle tokens accepted
- [x] KV `4 -> 9 -> 14 -> 19`
- [x] Freeze M=5 as maximum demonstrated exact block under MLX 0.31.2

### Stretch 018 — COMPLETE PASS
- [x] Valid run `20260820-131448`
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] Balanced order `M4 -> M5 -> M5 -> M4`
- [x] M4 pooled target rate 1.6983236855 token/s
- [x] M5 pooled target rate 1.8646802766 token/s
- [x] M5/M4 ratio ~1.09795x (~+9.80%)
- [x] Freeze M=5 as preferred exact block
- [x] Close block-size scaling axis for frozen MLX 0.31.2
- [x] Freeze `research/stretch/m4-m5-balanced-target-cost-comparison-018-result.md`

### Stretch 019 — COMPLETE PASS
- [x] Valid run `20260820-132820`
- [x] `M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Keep exact block M=5 fixed
- [x] Balanced order `H8 -> H16 -> H16 -> H8`
- [x] H8 pooled target rate `1.6634679102900627 token/s`
- [x] H16 pooled target rate `2.609454209167065 token/s`
- [x] H16/H8 target-rate ratio `1.568683226784969` (~+56.87%)
- [x] H16/H8 median materialization ratio `0.10130580024003226`
- [x] H16/H8 median forward ratio `0.8922774748455992`
- [x] H16/H8 mean full-pass process-read bytes/block ratio `0.04627184541030809`
- [x] H16 hotset `1,350,836,224 B`
- [x] Minimum observed free memory H16 22%
- [x] Freeze H16 as preferred demonstrated residency point
- [x] Freeze `research/stretch/m5-h8-h16-balanced-hotset-comparison-019-result.md`

### Stretch 020 — M5 H16 vs H24 balanced hotset comparison — CURRENT / READY
- [x] Keep exact block M=5 frozen
- [x] Scientific factor = persistent transformer residency H16 -> H24 only
- [x] H16 layers `0..15`, expected hotset `1,350,836,224 B`
- [x] H24 layers `0..23`, expected hotset `2,026,254,336 B`
- [x] Nominal H24 hybrid raw-weight budget `2,298,523,648 B` (~2.14 GiB)
- [x] Preserve model/runtime/quantization/KV/parity/I-O/safety policy
- [x] Preserve no-cache-purge policy
- [x] Add H24 helper `scripts/stretch_five_token_h24_hotset_variant_020.py`
- [x] Freeze H24 helper blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`
- [x] Add balanced runner `scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py`
- [x] Freeze balanced runner blob `d2f891462a786f334ceb11bb2e2528e9c2f0203d`
- [x] Preregister `research/stretch/m5-h16-h24-balanced-hotset-comparison-020-plan.md`
- [x] Balanced order `H16 -> H24 -> H24 -> H16`
- [x] Require every constituent to reach inherited PASS and exact expected hotset IDs
- [x] Any partial sequence => `HOTSET_COMPARISON_INCOMPLETE`, no winner
- [ ] Run Stretch 020
- [ ] Freeze H16/H24 result
- [ ] Decide whether residency scaling still has sufficient marginal return

### Stretch 021+ — conditional path
- [ ] If H24 materially improves target rate with safe headroom, decide whether one more bounded residency point is justified
- [ ] If H24 is flat/slower or resource-limited, stop hotset scaling
- [ ] Test prefetch/double buffering as a separate scientific factor
- [ ] Consider newer MLX only as a separately preregistered environment change
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after target-side performance architecture is sufficiently characterized
- [ ] Measure real acceptance rate and end-to-end token/s including draft/rejection/rollback cost
- [ ] Test KV capacity / KV quantization separately
- [ ] Do not promote an interactive profile until speed approaches the frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
