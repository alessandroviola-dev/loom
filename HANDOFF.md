# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_020_M5_H16_H24_BALANCED_HOTSET_COMPARISON_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS threshold.

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
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B

## Stretch history / canonical checkpoints

### Stretch 001–009 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O
- bounded MLX materialization/eviction
- exact streamed transformer-block parity
- full 36-layer streamed-body parity
- exact full-logit parity
- persistent ordinary KV cache
- exact sequential autoregressive parity through four feedback tokens.

### Stretch 010 — COMPLETE PASS

`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact prompt + 16 feedback logits
- identical frozen 16-token sequence
- final KV offset 20
- logical throughput 0.346144 token/s
- late materialization cost rises strongly while forward stays near ~0.19 s/token.

### Stretch 011 — COMPLETE PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- late transformer materialization ~3.039 GB/token process reads
- late full pass ~3.584 GB/token
- materialization-time/process-read Pearson 0.9995866108
- logical throughput 0.312407 token/s.

Decision: repeated target-weight traversal is the dominant late cost under current accounting.

### Stretch 012 — COMPLETE PASS

`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`, run `20260819-192349`:
- persistent layers 0..7
- hotset 675,418,112 B
- hybrid simultaneous raw-weight budget 947,687,424 B
- exact 16-token parity
- logical throughput 0.477929 token/s
- ~52.98% improvement vs Stretch 011.

### Stretch 013 — COMPLETE PASS

`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`, run `20260819-193702`:
- 4 x 4-token causal oracle target traversals
- exact all 16 position logits/top-1
- streamed KV `4 -> 8 -> 12 -> 16 -> 20`
- oracle target-verification throughput **1.8857486198 token/s**
- ~3.9457x vs Stretch 012.

Boundary: oracle upper bound only; no real drafter/draft/rejection/rollback cost.

### Stretch 014 — COMPLETE VALID FAIL

`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`, valid run `20260820-122922`:
- block size M=8
- first target position already diverges numerically
- top-1 differs by step 16
- KV state remains correct
- failure is numerical, not host/resource.

Decision: no parity relaxation; no direct advance to M=16.

### Stretch 015 — COMPLETE ATTRIBUTION PASS

`QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`, run `20260820-124515`:
- M1/M4 exact through layer-0 trace
- M4/M8 exact through attention/post-attention norm
- first divergence at MLP `gate_proj`
- gate/up/down shape-dependent at M8
- q/k/v/o exact at M8.

Canonical attribution: Stretch 014 fails because the frozen MLX 0.31.2 quantized-linear path is shape-dependent; first observed full-block divergence is in the MLP.

Result:
`research/stretch/eight-token-divergence-attribution-015-result.md`

### Stretch 016 — COMPLETE PASS

`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`, run `20260820-125212`:
- q/k/v/o exact through M=9; first divergent M=10
- gate/up/down exact through M=5; first divergent M=6
- MLP sets the first exactness boundary.

Result:
`research/stretch/quantized-linear-m-boundary-mapping-016-result.md`

### Stretch 017 — COMPLETE PASS

`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, run `20260820-130124`:
- full 36-layer streamed/hotset target path
- 3 x 5-token oracle target blocks
- prompt exact
- all 15 position logits exact (max/mean diff 0.0 / 0.0)
- top-1 equality all 15
- all 15 oracle tokens accepted
- streamed KV `4 -> 9 -> 14 -> 19`.

Canonical exactness frontier:
- **M=5 = maximum demonstrated exact end-to-end oracle block**
- M>=6 is not an exact-parity path under frozen MLX 0.31.2 based on Stretch 016.

Result:
`research/stretch/five-token-oracle-block-confirmation-017-result.md`

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`, run `20260820-131448`.

Balanced order:
`M4 -> M5 -> M5 -> M4`.

Controlled result:
- M4 pooled target rate: 1.6983236855 token/s
- M5 pooled target rate: 1.8646802766 token/s
- M5/M4 ratio: 1.09795340695x (~+9.80%)
- M5 is both maximum exact and preferred controlled exact block under MLX 0.31.2.

Decision: block-size axis sufficiently characterized; keep M=5 fixed for subsequent residency work.

Result:
`research/stretch/m4-m5-balanced-target-cost-comparison-018-result.md`

### Stretch 019 — COMPLETE PASS

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-132820`.

Balanced order:
`H8 -> H16 -> H16 -> H8`.

Frozen M=5 throughout.

Controlled result:
- H8 pooled target rate: `1.6634679102900627 token/s`
- H16 pooled target rate: `2.609454209167065 token/s`
- H16/H8 target-rate ratio: `1.568683226784969` (~+56.87%)
- H8 median block wall: `3.2671415 s`
- H16 median block wall: `1.8776220000000001 s`
- H16/H8 median materialization ratio: `0.10130580024003226`
- H16/H8 median forward ratio: `0.8922774748455992`
- H16/H8 mean full-pass process-read bytes/block ratio: `0.04627184541030809`
- H8 hotset: `675,418,112 B`
- H16 hotset: `1,350,836,224 B`
- minimum observed free memory: H8 20%, H16 22%.

Canonical interpretation:
- increasing residency H8 -> H16 improves pooled M5 target rate by ~56.9%
- speedup is dominated by lower materialization/process-read cost, not pure forward compute
- residency/materialization is the current high-leverage optimization axis.

Preferred demonstrated exact profile after Stretch 019:
- block size: **M=5**
- persistent hotset: **H16**
- controlled target-verification rate: **2.609454209167065 token/s**.

Result:
`research/stretch/m5-h8-h16-balanced-hotset-comparison-019-result.md`

Latest disk after Stretch 019: ~35.684 GiB free.

## Stretch 020 — M5 H16 vs H24 Balanced Hotset Comparison — READY

Plan:
`research/stretch/m5-h16-h24-balanced-hotset-comparison-020-plan.md`

Frozen H16 source:
- `scripts/stretch_five_token_h16_hotset_variant_019.py`
- blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`.

Frozen H24 helper:
- `scripts/stretch_five_token_h24_hotset_variant_020.py`
- blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`.

Balanced comparison runner:
- `scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py`
- blob `d2f891462a786f334ceb11bb2e2528e9c2f0203d`.

Scientific factor:
- H16 persistent layers `0..15`
- H24 persistent layers `0..23`
- no other intended scientific change.

Frozen:
- exact M=5 oracle block
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- resident sequential control
- ordinary BF16 KV
- exact parity/top-1 gates
- shared-stage streaming
- Darwin process-I/O telemetry
- host/resource gates
- no real drafter
- no tokenizer/sampling
- no KV quantization
- no prefetch
- no runtime upgrade
- no cache purge
- no new model download.

Expected persistent raw-weight payloads:
- H16: `1,350,836,224 B`
- H24: `2,026,254,336 B`.

Nominal H24 hybrid raw-weight budget with the existing 272,269,312 B shared stage:
`2,298,523,648 B` (~2.14 GiB).

Balanced order:
`H16 -> H24 -> H24 -> H16`.

Every constituent run must independently reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, preserve M=5, accept all 15 oracle tokens, and expose exact expected hotset IDs. Any constituent failure yields `HOTSET_COMPARISON_INCOMPLETE`; no winner is inferred from partial data.

Primary PASS:
`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h24_hotset_variant_020.py
python3 -m py_compile scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py
python3 scripts/stretch_m5_h16_h24_balanced_hotset_comparison_020.py
```

No download is expected.

## Open questions after Stretch 020

1. Does H24 materially improve the controlled M5 target rate over H16?
2. Does the H24 gain, if any, continue to track lower materialization/process-read cost?
3. Is H24 still comfortably inside the inherited system-wide free-memory/swap envelope?
4. Are residency returns beginning to diminish enough to stop at H16/H24 and move to prefetch/double buffering?
5. Real drafter selection remains deferred until the target-side performance architecture is sufficiently characterized.
6. Any newer MLX runtime remains a separate scientific factor and must not overwrite the frozen 0.31.2 baseline.
