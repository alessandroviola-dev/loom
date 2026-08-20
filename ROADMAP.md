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
- [x] Exact streamed block/body/full-logit parity
- [x] Persistent ordinary KV
- [x] Exact autoregressive feedback through four tokens

### Stretch 010 — COMPLETE PASS
- [x] `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`
- [x] Exact 16-token sequence/parity
- [x] Logical throughput 0.346144 token/s
- [x] Identify late materialization slowdown

### Stretch 011 — COMPLETE PASS
- [x] `MATERIALIZATION_IO_ATTRIBUTION_PASS`
- [x] Late transformer materialization ~3.039 GB/token process reads
- [x] Late full pass ~3.584 GB/token
- [x] Materialization-time/process-read Pearson 0.9995866107996246
- [x] Freeze repeated target-weight traversal/materialization as dominant late cost

### Stretch 012 — COMPLETE PASS
- [x] `EIGHT_LAYER_PERSISTENT_HOTSET_PASS`
- [x] H8 = layers 0..7 = 675,418,112 B
- [x] Exact 16-token parity
- [x] Logical throughput 0.477929 token/s

### Stretch 013 — COMPLETE PASS
- [x] `FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`
- [x] 4 x M4 oracle traversals
- [x] Exact all 16 position logits/top-1
- [x] Oracle target rate 1.8857486198 token/s

### Stretch 014 — COMPLETE VALID FAIL
- [x] M8 oracle verification
- [x] `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`
- [x] Numerical divergence begins at first target position
- [x] KV remains correct
- [x] Do not relax parity

### Stretch 015 — COMPLETE ATTRIBUTION PASS
- [x] `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`
- [x] First M4/M8 divergence at `gate_proj`
- [x] Attribute failure to M-dependent quantized-linear execution under frozen MLX 0.31.2

### Stretch 016 — COMPLETE PASS
- [x] `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`
- [x] q/k/v/o exact through M=9; first divergence M=10
- [x] gate/up/down exact through M=5; first divergence M=6
- [x] Freeze M=5 as largest relevant exact candidate

### Stretch 017 — COMPLETE PASS
- [x] `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- [x] 3 x M5 oracle traversals
- [x] Exact all 15 logits/top-1
- [x] All 15 oracle tokens accepted
- [x] Freeze M=5 as maximum demonstrated end-to-end exact oracle block

### Stretch 018 — COMPLETE PASS
- [x] `M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- [x] Balanced `M4 -> M5 -> M5 -> M4`
- [x] M4 pooled 1.6983236855 token/s
- [x] M5 pooled 1.8646802766 token/s
- [x] M5/M4 = 1.09795340695x (~+9.80%)
- [x] Freeze M=5 as preferred exact block
- [x] Close block-size scaling for frozen MLX 0.31.2

### Stretch 019 — COMPLETE PASS
- [x] `M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Balanced `H8 -> H16 -> H16 -> H8`
- [x] H8 pooled 1.6634679103 token/s
- [x] H16 pooled 2.6094542092 token/s
- [x] H16/H8 = 1.56868322678x (~+56.87%)
- [x] Confirm residency/materialization as primary active speed axis
- [x] Freeze result

### Stretch 020 — COMPLETE PASS
- [x] `M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Balanced `H16 -> H24 -> H24 -> H16`
- [x] H16 pooled 1.8043852697 token/s
- [x] H24 pooled 2.4333574371 token/s
- [x] H24/H16 = 1.34857975065x (~+34.86%)
- [x] H24/H16 median materialization = 0.160439630864x
- [x] H24/H16 median forward = 0.777126124736x
- [x] Freeze M5+H24 as best demonstrated profile at that checkpoint
- [x] Freeze result

### Stretch 021 — COMPLETE PASS
- [x] Valid run `20260820-145035`
- [x] `M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`
- [x] Balanced `H24 -> H32 -> H32 -> H24`
- [x] H24 pooled 2.7358720706 token/s
- [x] H32 pooled 3.0490014165 token/s
- [x] H32/H24 = 1.11445321190x (~+11.45%)
- [x] H32/H24 median block wall ~0.8920x
- [x] H32/H24 median materialization = 0.342275431401x
- [x] H32/H24 median forward = 0.964972714945x
- [x] H32/H24 full-pass process reads/block = 0.006146087779x
- [x] H32 hotset = 2,701,672,448 B
- [x] H32 hybrid raw-weight budget = 2,973,941,760 B
- [x] H32 min observed free = 25%; peak swap = 2124.25 MB
- [x] Freeze M5+H32 as best demonstrated target-side profile so far
- [x] Observe diminishing residency returns: +56.87% -> +34.86% -> +11.45%
- [x] Freeze `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-result.md`

### Stretch 022 — M5 H32 vs H36 transformer-residency ceiling — CURRENT / READY
- [x] Keep exact block size M=5 frozen
- [x] Scientific factor = persistent transformer residency H32 -> H36 only
- [x] H32 layers `0..31`, hotset 2,701,672,448 B
- [x] H36 layers `0..35`, expected hotset 3,039,381,504 B
- [x] H36 nominal hybrid raw-weight budget 3,311,650,816 B (~3.08 GiB)
- [x] Preserve model/runtime/quantization/KV/parity/I-O/safety policy
- [x] Preserve no-cache-purge policy
- [x] H32 helper blob `b6b39dfb095b905ed659d52903309783efc02be7`
- [x] Add H36 helper `scripts/stretch_five_token_h36_hotset_variant_022.py`
- [x] Freeze H36 helper blob `9111dde483206a774a9fe5426522dab6e77cecca`
- [x] Add balanced runner `scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py`
- [x] Freeze balanced runner blob `c9ed18984896835c99a22c68aaedb330d030ec7e`
- [x] Preregister `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-plan.md`
- [x] Balanced order `H32 -> H36 -> H36 -> H32`
- [x] Require every constituent to reach inherited PASS and exact expected hotset IDs
- [x] Any partial/failing sequence => `HOTSET_COMPARISON_INCOMPLETE`, no winner and no automatic rescue
- [x] Freeze policy: no post-hoc H33-H35 sweep
- [ ] Run Stretch 022
- [ ] Freeze H32/H36 result
- [ ] Close transformer-hotset scaling regardless of outcome

### Stretch 023+ — next independent axis after ceiling
- [ ] Select next factor from Stretch 022 residual evidence
- [ ] Consider shared-stage residency/prefetch or double buffering separately
- [ ] Consider newer MLX only as a separately preregistered environment change
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after target-side architecture is sufficiently characterized
- [ ] Measure actual acceptance rate and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity and KV quantization separately
- [ ] Do not promote an interactive profile until speed approaches frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
