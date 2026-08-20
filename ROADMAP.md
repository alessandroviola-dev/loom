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
- [x] Exact streamed block parity
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
- [x] Materialization-time/disk-read Pearson 0.9995866107996246
- [x] Freeze repeated target-weight traversal as dominant late cost under current accounting

### Stretch 012 — COMPLETE PASS
- [x] `EIGHT_LAYER_PERSISTENT_HOTSET_PASS`
- [x] Hotset layers 0..7 = 675,418,112 B
- [x] Exact 16-token parity
- [x] Logical throughput **0.477929 token/s**
- [x] ~52.98% improvement vs 011
- [x] Decide residency alone is insufficient

### Stretch 013 — COMPLETE PASS
- [x] `FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`
- [x] 4 x 4-token causal oracle target traversals
- [x] Exact all 16 position logits/top-1
- [x] KV `4 -> 8 -> 12 -> 16 -> 20`
- [x] Oracle target-verification throughput **1.8857486198 token/s**
- [x] Rate ratio vs Stretch 012 **3.9456668664x**
- [x] Preserve oracle-only upper-bound interpretation

### Stretch 014 — COMPLETE VALID FAIL
- [x] 2 x 8-token oracle traversals
- [x] Host/resource gates valid
- [x] `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`
- [x] Numerical divergence begins at first target position
- [x] Top-1 differs by step 16
- [x] KV state remains correct
- [x] Do not relax parity / do not advance to M=16

### Stretch 015 — COMPLETE ATTRIBUTION PASS
- [x] `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`
- [x] M1/M4 exact at layer 0
- [x] M4/M8 exact through attention and post-attention norm
- [x] First M4/M8 divergence at `gate_proj`
- [x] gate/up/down shape-dependent at M8
- [x] q/k/v/o exact at M8
- [x] Freeze result

### Stretch 016 — COMPLETE PASS
- [x] Valid run `20260820-125212`
- [x] `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`
- [x] Sweep M=1..16 on actual layer-0 quantized projections
- [x] q/k/v/o exact through M=9; first divergent M=10
- [x] gate/up/down exact through M=5; first divergent M=6
- [x] MLP identified as limiting exactness component
- [x] Freeze M=5 as largest layer-0 exact candidate under MLX 0.31.2
- [x] Freeze `research/stretch/quantized-linear-m-boundary-mapping-016-result.md`

### Stretch 017 — COMPLETE PASS
- [x] Valid run `20260820-130124`
- [x] `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- [x] Preserve Stretch 013 runtime/model/KV/hotset/parity/safety policy
- [x] Use frozen first-15 oracle prefix
- [x] Resident sequential continuation length 15
- [x] Stream target as 3 x 5-token blocks
- [x] Exact all 15 position logits/top-1
- [x] All 15 oracle tokens accepted
- [x] Streamed KV `4 -> 9 -> 14 -> 19`
- [x] Freeze M=5 as maximum demonstrated end-to-end exact oracle block under MLX 0.31.2
- [x] Preserve standalone-timing warning due host/cache/I-O differences
- [x] Freeze `research/stretch/five-token-oracle-block-confirmation-017-result.md`

### Stretch 018 — COMPLETE PASS
- [x] Valid run `20260820-131448`
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] Balanced order `M4 -> M5 -> M5 -> M4`
- [x] No deliberate cache purge
- [x] Every constituent inherited PASS gate succeeded
- [x] M4 pooled target rate `1.6983236855 token/s`
- [x] M5 pooled target rate `1.8646802766 token/s`
- [x] M5/M4 target-rate ratio `1.09795340695x` (~+9.80%)
- [x] M5/M4 median materialization ratio `2.19265232975x`
- [x] M5/M4 median forward ratio `1.16365164669x`
- [x] M5/M4 mean full-pass process-read bytes/block ratio `1.72894269309x`
- [x] Freeze M=5 as preferred exact block under controlled M4/M5 evidence
- [x] Close block-size scaling axis for frozen MLX 0.31.2; M>=6 remains non-exact
- [x] Freeze `research/stretch/m4-m5-balanced-target-cost-comparison-018-result.md`

### Stretch 019 — Balanced M5 H8 vs H16 hotset comparison — CURRENT / READY
- [x] Keep exact block size M=5 frozen
- [x] Scientific factor = persistent transformer residency H8 -> H16 only
- [x] H8 layers `0..7`, expected raw hotset 675,418,112 B
- [x] H16 layers `0..15`, expected raw hotset 1,350,836,224 B
- [x] Preserve model/runtime/quantization/KV/parity/I-O/safety policy
- [x] Preserve no-cache-purge policy
- [x] Add H16 helper `scripts/stretch_five_token_h16_hotset_variant_019.py`
- [x] Freeze H16 helper blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`
- [x] Add balanced runner `scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py`
- [x] Freeze balanced runner blob `8ad0666624069d4852daed1188d634806b570ecc`
- [x] Preregister `research/stretch/m5-h8-h16-balanced-hotset-comparison-019-plan.md`
- [x] Balanced order `H8 -> H16 -> H16 -> H8`
- [x] Require every constituent to reach inherited PASS and exact expected hotset IDs
- [x] Any partial sequence => `HOTSET_COMPARISON_INCOMPLETE`, no winner
- [ ] Run Stretch 019
- [ ] Freeze H8/H16 result
- [ ] Decide whether further bounded residency scaling is justified

### Stretch 020+ — conditional path
- [ ] If H16 materially improves M5 target rate and resource headroom remains adequate, consider one further preregistered residency point
- [ ] If H16 is flat/slower or resource-limited, stop hotset scaling and inspect prefetch/double-buffering
- [ ] Test prefetch/double-buffering as a separate factor
- [ ] Consider a newer-MLX experiment only as a separately preregistered environment change
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after target-side performance architecture is sufficiently characterized
- [ ] Measure real acceptance rate and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity and KV quantization separately
- [ ] Do not promote interactive profile until speed approaches frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
