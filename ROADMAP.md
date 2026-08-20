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

### Stretch 017 — Five-token oracle block confirmation — CURRENT / READY
- [x] Preregister `research/stretch/five-token-oracle-block-confirmation-017-plan.md`
- [x] Add `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- [x] Freeze runner blob `6171440736badf5150297f9c8945209fe49d0826`
- [x] Preserve Stretch 013 runtime/model/KV/hotset/parity/safety policy
- [x] Use frozen first-15 oracle prefix
- [x] Resident sequential continuation length 15
- [x] Stream target as 3 x 5-token blocks
- [x] Expected streamed KV `4 -> 9 -> 14 -> 19`
- [x] Treat timing as secondary characterization, not pure A/B vs Stretch 013
- [ ] Run Stretch 017
- [ ] Freeze result

### Stretch 018+ — conditional path
- [ ] If Stretch 017 passes, freeze M=5 as maximum demonstrated exact oracle block under MLX 0.31.2
- [ ] Decide whether M=5 offers enough operational value to retain
- [ ] Evaluate residual I/O/residency/prefetch as a separate speed axis
- [ ] Consider a newer-MLX experiment only as a separately preregistered environment change
- [ ] Never overwrite/reinterpret frozen MLX 0.31.2 results with newer-runtime results
- [ ] Select a real drafter only after exact oracle target-side frontier is settled
- [ ] Measure real acceptance rate and end-to-end tok/s including draft/rejection/rollback cost
- [ ] Test KV capacity, KV quantization and prefetch separately
- [ ] Do not promote interactive profile until speed approaches frozen ~20 token/s target

## Phase 8 — Synthesis
- [ ] Capability vs memory vs time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
