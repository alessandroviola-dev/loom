# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_019_M5_H8_H16_BALANCED_HOTSET_COMPARISON_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This remains a promotion target, not a PASS threshold for intermediate research.

## Research rules

- Never reset/replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime abort where applicable: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- Do not weaken resource or parity gates post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No hidden rescue ladders/retries.
- No new large-model download while existing artifacts suffice.
- Treat Darwin process-I/O accounting as diagnostic, not forensic per-file SSD tracing.
- Do not purge macOS caches to manufacture host state.
- After every meaningful result/decision update `HANDOFF.md` and `ROADMAP.md`.

## Frozen target/environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Configuration:
- Qwen3
- hidden size 4096
- 36 transformer layers
- vocab 151936
- 32 attention heads / 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- quantization 3-bit / group64

Frozen runtime:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Weights:
- total 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B

## Stretch history

### Stretch 001–009 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O
- bounded MLX materialization/eviction
- exact resident/streamed block parity
- full 36-layer streamed body parity
- exact full-logit parity
- persistent ordinary KV cache
- exact sequential autoregressive parity through 4 feedback tokens.

### Stretch 010 — COMPLETE PASS

`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact prompt + 16 feedback logits
- identical sequence `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- final KV offset 20
- logical throughput 0.346144 token/s
- late materialization cost rises strongly while layer forward stays ~0.19 s/token.

### Stretch 011 — COMPLETE PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- late transformer materialization reads ~3.039 GB/token under Darwin process accounting
- late full pass ~3.584 GB/token
- materialization-time/disk-read Pearson 0.9995866107996246
- logical throughput 0.312407 token/s.

Decision: repeated target-weight traversal is the dominant late cost under current accounting.

### Stretch 012 — COMPLETE PASS

`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`, run `20260819-192349`:
- persistent layers 0..7
- hotset 675,418,112 B
- hybrid simultaneous raw-weight budget 947,687,424 B
- exact 16-token parity
- logical throughput **0.477929 token/s**
- ~52.98% improvement vs 011.

Decision: residency helps but is insufficient alone for ~20 token/s.

### Stretch 013 — COMPLETE PASS

`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`, run `20260819-193702`:
- four causal target traversals x four known-correct oracle tokens
- all 16 position logits exact vs resident sequential control
- all oracle tokens accepted
- streamed KV `4 -> 8 -> 12 -> 16 -> 20`
- target-block total wall 8.484694 s
- oracle target-verification throughput **1.8857486198 token/s**
- rate ratio vs Stretch 012: **3.9456668664x**.

Boundary: oracle upper bound only; no real drafter/draft/rejection/rollback cost.

### Stretch 014 — COMPLETE VALID FAIL

`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`, valid run `20260820-122922`:
- block size 8 / two traversals
- prompt exact
- first target position already diverges, max abs 0.34375
- all 16 numerical gates fail
- top-1 differs by step 16
- KV state/bytes remain correct
- failure is numerical, not host/resource.

Decision: do not relax parity and do not advance to M=16.

### Stretch 015 — COMPLETE ATTRIBUTION PASS

`QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`, run `20260820-124515`:
- M1 vs M4 exact through layer-0 trace
- M4 vs M8 exact through attention/post-attention norm
- first M4/M8 divergence: `gate_proj`
- gate/up/down shape-dependent at M8
- q/k/v/o remain exact at M8.

Canonical attribution:
> Stretch 014 fails because the frozen MLX 0.31.2 quantized-linear path is shape-dependent; the first observed full-block divergence is in the MLP, not attention/RoPE/KV.

Result:
`research/stretch/eight-token-divergence-attribution-015-result.md`

### Stretch 016 — COMPLETE PASS

`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`, run `20260820-125212`.

Runner/blob:
- `scripts/stretch_quantized_linear_m_boundary_mapping_016.py`
- `a5c3f4acd6a4150d2db7477f3f20d01a00b4f759`

Exact M boundary:
- q/k/v/o exact through M=9; first divergent M=10
- gate/up/down exact through M=5; first divergent M=6.

Largest relevant exact candidate under frozen runtime: **M=5**.

Result:
`research/stretch/quantized-linear-m-boundary-mapping-016-result.md`

### Stretch 017 — COMPLETE PASS

`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, valid run `20260820-130124`.

Plan/result:
- `research/stretch/five-token-oracle-block-confirmation-017-plan.md`
- `research/stretch/five-token-oracle-block-confirmation-017-result.md`

Runner/blob:
- `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- `6171440736badf5150297f9c8945209fe49d0826`

Correctness:
- resident continuation = first 15 frozen oracle tokens
- streamed target = 3 x 5-token oracle blocks
- prompt exact
- all 15 position logits max/mean diff 0.0 / 0.0
- top-1 equality all 15 positions
- all 15 oracle tokens accepted
- resident/streamed KV final offset 19
- final KV bytes 37,748,736 / 37,748,736 B.

Canonical exactness conclusion:
> M=5 is demonstrated exact end-to-end across the full 36-layer streamed/hotset target path under the frozen MLX 0.31.2 baseline.

Secondary standalone performance from 017:
- oracle target rate 1.3629385391 token/s
- process-I/O state differed materially from Stretch 013, so 013-vs-017 historical timing is not a causal M4/M5 A/B.

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`, valid run `20260820-131448`.

Plan/result:
- `research/stretch/m4-m5-balanced-target-cost-comparison-018-plan.md`
- `research/stretch/m4-m5-balanced-target-cost-comparison-018-result.md`

Runner/blob:
- `scripts/stretch_m4_m5_balanced_target_cost_comparison_018.py`
- `0a745a2ea4fd6adf70d33b82156ec9c3889a1498`

Balanced order:
`M4 -> M5 -> M5 -> M4`

No deliberate cache purge; every constituent inherited PASS gate succeeded.

Controlled result:
- M4 pooled target-verification rate: `1.6983236855 token/s`
- M5 pooled target-verification rate: `1.8646802766 token/s`
- M5/M4 rate ratio: `1.09795340695x` (~+9.80%)
- M4 median block wall: `2.261242 s`
- M5 median block wall: `2.7130515 s`
- M5/M4 median materialization ratio: `2.19265232975x`
- M5/M4 median forward ratio: `1.16365164669x`
- M5/M4 mean full-pass process-read bytes/block ratio: `1.72894269309x`.

Canonical performance conclusion:
> M5 is both the maximum demonstrated exact block and the better measured exact block in the controlled M4/M5 comparison, improving pooled target rate by ~9.8% despite higher per-block materialization/forward/I-O cost.

Therefore the frozen MLX 0.31.2 block-size axis is considered sufficiently characterized:
- preferred exact block: **M=5**
- M>=6: not exact under current numerical policy.

Latest disk after Stretch 018: ~35.691 GiB free.

## Stretch 019 — Balanced M5 H8 vs H16 Hotset Comparison — READY

Plan:
`research/stretch/m5-h8-h16-balanced-hotset-comparison-019-plan.md`

Frozen H8 source:
- `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- blob `6171440736badf5150297f9c8945209fe49d0826`.

Frozen H16 helper:
- `scripts/stretch_five_token_h16_hotset_variant_019.py`
- blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`.

Balanced comparison runner:
- `scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py`
- blob `8ad0666624069d4852daed1188d634806b570ecc`.

Scientific factor:
- H8 persistent layers `0..7` -> H16 persistent layers `0..15` ONLY.

Frozen:
- exact block size M=5
- 3 x 5-token oracle traversals over the frozen first-15 sequence
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- ordinary BF16 KV
- exact parity/top-1 gates
- shared-stage streaming
- I/O/resource/host gates
- no real drafter, tokenizer, sampling, KV quantization, prefetch, runtime upgrade or cache purge.

Expected raw hotsets:
- H8: 675,418,112 B
- H16: 1,350,836,224 B.

Derived hybrid raw-weight budgets if max new shared stage stays 272,269,312 B:
- H8: 947,687,424 B
- H16: 1,623,105,536 B (~1.51 GiB).

Balanced order:
`H8 -> H16 -> H16 -> H8`.

Every constituent must independently reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS` and expose exact expected hotset IDs. Any failure yields `HOTSET_COMPARISON_INCOMPLETE`; no winner is inferred from partial data.

Primary PASS:
`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`.

Primary outputs:
- pooled target-verification token/s
- median block wall
- median materialization wall
- median forward wall
- process-read bytes/block and per token
- actual hotset/hybrid raw-weight bytes
- minimum free memory / peak swap.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h16_hotset_variant_019.py
python3 -m py_compile scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py
python3 scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py
```

No download is expected.

## Open questions after Stretch 019

1. Does doubling persistent transformer residency improve M5 pooled target rate under balanced host/cache ordering?
2. Does any gain track reduced materialization time/process reads strongly enough to justify further bounded residency scaling?
3. Is H16 still comfortably inside the 8 GB system-wide resource envelope?
4. If residency saturates or hurts, should the next independent speed axis be prefetch/double-buffering or a separately preregistered newer-MLX runtime experiment?
5. Real drafter selection remains deferred until the target-side performance architecture is sufficiently characterized.
6. Any newer MLX runtime must remain a separate environment experiment and must not overwrite the frozen 0.31.2 baseline.
