# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_021_M5_H24_H32_BALANCED_HOTSET_COMPARISON_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not a PASS threshold for intermediate experiments.

## Research rules

- Preserve verified models/results; do not silently delete them.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- Do not weaken resource or numerical parity gates post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No hidden rescue ladders/retries.
- No deliberate macOS cache purge to manufacture host state.
- Darwin process-I/O accounting is diagnostic, not forensic per-file SSD tracing.
- No new large-model download while existing artifacts suffice.
- Update `HANDOFF.md` and `ROADMAP.md` after every meaningful result/decision.

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
- quantization 3-bit / group64.

Frozen runtime:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Raw weights:
- total 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Other active track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Stretch history

### Stretch 001–009 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O
- bounded MLX materialization/eviction
- exact streamed block parity
- full 36-layer body/full-logit parity
- persistent ordinary KV
- exact autoregressive feedback through four tokens.

### Stretch 010 — COMPLETE PASS

`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`, run `20260819-183844`:
- exact 16-token sequence/parity
- final KV offset 20
- logical throughput 0.346144 token/s
- late materialization slowdown isolated while forward remained much flatter.

### Stretch 011 — COMPLETE PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`, run `20260819-185036`:
- late transformer materialization ~3.039 GB/token process reads
- late full pass ~3.584 GB/token
- materialization-time/process-read Pearson 0.9995866107996246
- logical throughput 0.312407 token/s.

Decision: repeated target-weight traversal/materialization is the dominant late cost under current accounting.

### Stretch 012 — COMPLETE PASS

`EIGHT_LAYER_PERSISTENT_HOTSET_PASS`, run `20260819-192349`:
- persistent layers 0..7
- hotset 675,418,112 B
- exact 16-token parity
- logical throughput 0.477929 token/s
- ~52.98% improvement vs Stretch 011.

### Stretch 013 — COMPLETE PASS

`FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS`, run `20260819-193702`:
- 4 x 4-token oracle target traversals
- all 16 position logits/top-1 exact
- KV `4 -> 8 -> 12 -> 16 -> 20`
- oracle target rate 1.8857486198 token/s.

Boundary: oracle upper bound only; no real drafter/draft/rejection/rollback cost.

### Stretch 014 — COMPLETE VALID FAIL

`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`, valid run `20260820-122922`:
- M=8 target blocks
- numerical divergence begins at first target position
- top-1 differs by step 16
- KV remains correct
- not a host/resource failure.

Decision: do not relax parity and do not advance directly to larger exact blocks.

### Stretch 015 — COMPLETE ATTRIBUTION PASS

`QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`, run `20260820-124515`:
- M4/M8 remains exact through attention/post-attention norm
- first divergence at `gate_proj`
- gate/up/down are shape-dependent at M8
- q/k/v/o remain exact at M8.

Canonical attribution: Stretch 014 fails because frozen MLX 0.31.2 quantized-linear execution is M/shape dependent; first observed block divergence is in the MLP, not attention/RoPE/KV.

### Stretch 016 — COMPLETE PASS

`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`, run `20260820-125212`:
- q/k/v/o exact through M=9; first divergent M=10
- gate/up/down exact through M=5; first divergent M=6.

Decision:
- MLP is limiting exactness component
- M=5 is largest relevant exact candidate under frozen runtime
- M>=6 is not an exact-parity path under current policy.

### Stretch 017 — COMPLETE PASS

`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, run `20260820-130124`:
- three 5-token oracle traversals
- all 15 logits max/mean diff 0.0 / 0.0
- all top-1 equal
- all 15 oracle tokens accepted
- streamed KV `4 -> 9 -> 14 -> 19`.

Decision: **M=5 = maximum demonstrated end-to-end exact oracle block** under MLX 0.31.2.

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`, run `20260820-131448`.

Balanced order:
`M4 -> M5 -> M5 -> M4`.

Controlled result:
- M4 pooled target rate 1.6983236855 token/s
- M5 pooled target rate 1.8646802766 token/s
- M5/M4 = 1.09795340695x (~+9.80%).

Decision: **M=5 is the preferred exact block**. Block-size scaling is closed for frozen MLX 0.31.2 because M>=6 is non-exact.

### Stretch 019 — COMPLETE PASS

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-132820`.

Balanced order:
`H8 -> H16 -> H16 -> H8`.

Controlled result:
- H8 pooled target rate 1.6634679103 token/s
- H16 pooled target rate 2.6094542092 token/s
- H16/H8 = 1.56868322678x (~+56.87%)
- H16/H8 median materialization ratio 0.10130580024x
- H16/H8 mean full-pass process-read bytes/block ratio 0.04627184541x
- H16 hotset 1,350,836,224 B
- H16 minimum observed free memory 22%.

Decision: residency/materialization is the highest-leverage active speed axis.

Result:
`research/stretch/m5-h8-h16-balanced-hotset-comparison-019-result.md`

### Stretch 020 — COMPLETE PASS

`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`, valid run `20260820-144043`.

Plan/result:
- `research/stretch/m5-h16-h24-balanced-hotset-comparison-020-plan.md`
- `research/stretch/m5-h16-h24-balanced-hotset-comparison-020-result.md`.

Frozen sources:
- H16 helper blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`
- H24 helper blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`
- balanced runner blob `d2f891462a786f334ceb11bb2e2528e9c2f0203d`.

Balanced order:
`H16 -> H24 -> H24 -> H16`.

Controlled result:
- H16 pooled target rate `1.8043852696963538 token/s`
- H24 pooled target rate `2.433357437090613 token/s`
- H24/H16 target-rate ratio `1.3485797506538635x` (~+34.86%)
- H16 median block wall `2.7883325 s`
- H24 median block wall `2.0068175 s`
- H24/H16 median materialization ratio `0.16043963086388105x`
- H24/H16 median forward ratio `0.7771261247356858x`
- H24/H16 mean full-pass process-read bytes/block ratio `0.024249004705030764x`.

Residency/resource telemetry:
- H16 hotset `1,350,836,224 B`
- H24 hotset `2,026,254,336 B`
- H16 hybrid raw-weight budget `1,623,105,536 B`
- H24 hybrid raw-weight budget `2,298,523,648 B`
- H16 min free `16%`, peak swap `2199.81 MB`
- H24 min free `21%`, peak swap `2288.56 MB`.

Interpretation:
- H24 materially improves the controlled target rate.
- The gain remains dominated by lower materialization/process-read cost.
- Do not interpret H24's higher observed minimum-free percentage as intrinsically lower RAM use; system telemetry is host-state dependent.
- Do not compare absolute rates across separate Stretch experiments causally; use within-experiment balanced ratios.

Decision:
- **M5 + H24 = best demonstrated target-side profile so far** under the frozen runtime.
- one further bounded residency point H32 is justified.

Latest disk after Stretch 020: ~35.687 GiB free.

## Stretch 021 — M5 H24 vs H32 Balanced Hotset Comparison — READY

Plan:
`research/stretch/m5-h24-h32-balanced-hotset-comparison-021-plan.md`

Frozen H24 source:
- `scripts/stretch_five_token_h24_hotset_variant_020.py`
- blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`.

Frozen H32 helper:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`.

Frozen balanced runner:
- `scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py`
- blob `fa52f21a7ae02a4fcae6c73416ad2ef63cc0ae45`.

Scientific factor only:
- H24 persistent transformer layers `0..23`
- H32 persistent transformer layers `0..31`.

Frozen:
- exact block size M=5
- three 5-token oracle target traversals
- model/runtime/quantization
- BF16 KV
- parity/top-1 policy
- shared-stage streaming
- I/O/host/resource gates
- no drafter, prefetch, KV quantization, runtime upgrade or cache purge.

Expected raw geometry:
- H24 hotset `2,026,254,336 B`
- H32 hotset `2,701,672,448 B`
- H32 nominal hybrid raw-weight budget `2,973,941,760 B` (~2.77 GiB), assuming the same 272,269,312 B maximum shared stage.

Balanced order:
`H24 -> H32 -> H32 -> H24`.

Every constituent must independently reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, retain M=5, accept all 15 oracle tokens, and expose the exact expected hotset IDs.

Any partial/failing sequence => `HOTSET_COMPARISON_INCOMPLETE`; no winner is inferred and no automatic rescue/retry is allowed.

Primary PASS:
`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h32_hotset_variant_021.py
python3 -m py_compile scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py
python3 scripts/stretch_m5_h24_h32_balanced_hotset_comparison_021.py
```

No download is expected.

## Open questions after Stretch 021

1. Does H32 materially improve the controlled M5 target rate versus H24?
2. Does H32 remain inside the frozen 8 GB resource envelope without approaching the abort gates?
3. If H32 passes and gains materially, is one separately preregistered H36 ceiling test justified?
4. If H32 is flat/slower/resource-limited, stop residency scaling and move to prefetch/double-buffering or another independent factor.
5. Real drafter selection remains deferred until the target-side architecture is sufficiently characterized.
6. Any newer MLX runtime must remain a separate environment experiment and must not redefine the frozen 0.31.2 baseline.
