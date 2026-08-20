# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_022_M5_H32_H36_BALANCED_HOTSET_CEILING_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate PASS threshold.

## Research rules

- Preserve verified models/results; never silently delete them.
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
- Qwen3, hidden size 4096
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

## Stretch history / current evidence

### Stretch 001–013 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O
- bounded MLX materialization/eviction
- exact streamed body/full-logit parity
- persistent ordinary KV
- exact autoregressive feedback
- full 36-layer streamed target path
- repeated target-weight traversal/materialization as dominant late cost
- H8 persistent hotset improvement
- exact M4 oracle-block verification upper bound.

Key rates:
- Stretch 010 sequential: 0.346144 token/s
- Stretch 012 H8 sequential: 0.477929 token/s
- Stretch 013 M4 oracle: 1.8857486198 token/s.

### Stretch 014–017 — exact block-size frontier characterized

Stretch 014:
- valid `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL` at M=8.

Stretch 015:
- `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`
- first M4/M8 divergence at layer-0 `gate_proj`; attention path remains exact there.

Stretch 016:
- `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`
- q/k/v/o exact through M=9; first divergence M=10
- gate/up/down exact through M=5; first divergence M=6.

Stretch 017:
- `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- M=5 exact end-to-end across all 36 layers
- 15/15 logits exact, 15/15 top-1 equal, all oracle tokens accepted
- KV `4 -> 9 -> 14 -> 19`.

Canonical exactness conclusion:
- **M=5 = maximum demonstrated exact oracle block under MLX 0.31.2**
- **M>=6 = not an exact-parity path under the frozen policy**.

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`, run `20260820-131448`.

Balanced order:
`M4 -> M5 -> M5 -> M4`.

Controlled result:
- M4 pooled 1.6983236855 token/s
- M5 pooled 1.8646802766 token/s
- M5/M4 = 1.09795340695x (~+9.80%).

Decision:
- **M=5 is the preferred exact block**.
- block-size scaling is closed for frozen MLX 0.31.2.

### Stretch 019 — COMPLETE PASS

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-132820`.

Controlled result:
- H8 pooled 1.6634679103 token/s
- H16 pooled 2.6094542092 token/s
- H16/H8 = 1.56868322678x (~+56.87%)
- median materialization ratio 0.10130580024x
- full-pass process-read bytes/block ratio 0.04627184541x.

Decision: residency/materialization is the primary active speed axis.

### Stretch 020 — COMPLETE PASS

`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-144043`.

Controlled result:
- H16 pooled 1.8043852697 token/s
- H24 pooled 2.4333574371 token/s
- H24/H16 = 1.34857975065x (~+34.86%)
- median block-wall ratio ~0.71972x
- median materialization ratio 0.160439630864x
- median forward ratio 0.777126124736x
- full-pass process reads/block ratio 0.024249004705x.

H24:
- hotset 2,026,254,336 B
- hybrid raw-weight budget 2,298,523,648 B
- min observed free 21%
- peak swap 2288.56 MB.

### Stretch 021 — COMPLETE PASS

`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`, valid run `20260820-145035`.

Plan/result:
- `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-plan.md`
- `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-result.md`.

Frozen sources:
- H24 helper blob `09363f4ce669a7de7b2f16fe4dfb63519c72eb9f`
- H32 helper blob `b6b39dfb095b905ed659d52903309783efc02be7`
- balanced runner blob `fa52f21a7ae02a4fcae6c73416ad2ef63cc0ae45`.

Balanced order:
`H24 -> H32 -> H32 -> H24`.

Controlled result:
- H24 pooled target rate `2.7358720706219777 token/s`
- H32 pooled target rate `3.0490014164644244 token/s`
- H32/H24 target-rate ratio `1.1144532119044803x` (~+11.45%)
- H24 median block wall `1.807173 s`
- H32 median block wall `1.6119785 s`
- H32/H24 median materialization ratio `0.3422754314008055x`
- H32/H24 median forward ratio `0.964972714944873x`
- H32/H24 mean full-pass process-read bytes/block ratio `0.006146087778740841x`.

Residency/resource telemetry:
- H24 hotset `2,026,254,336 B`
- H32 hotset `2,701,672,448 B`
- H24 hybrid raw-weight budget `2,298,523,648 B`
- H32 hybrid raw-weight budget `2,973,941,760 B`
- H24 min free `21%`, peak swap `2076.62 MB`
- H32 min free `25%`, peak swap `2124.25 MB`.

Canonical interpretation:
- H32 remains faster, but marginal residency gain has fallen to ~11.45%.
- forward time is nearly unchanged while transformer materialization/process reads continue to collapse.
- actual compute/shared-stage work is becoming the dominant residual cost.
- do not compare absolute rates across separate Stretch experiments causally; use within-experiment balanced ratios.

Decision:
- **M5 + H32 = best demonstrated target-side profile so far**.
- one final H36 transformer-residency ceiling experiment is justified.
- after H36, transformer-hotset scaling closes regardless of outcome.

Latest disk after Stretch 021: ~35.684 GiB free.

## Stretch 022 — M5 H32 vs H36 Balanced Hotset Ceiling — READY

Plan:
`research/stretch/m5-h32-h36-balanced-hotset-comparison-022-plan.md`

Frozen H32 source:
- `scripts/stretch_five_token_h32_hotset_variant_021.py`
- blob `b6b39dfb095b905ed659d52903309783efc02be7`.

Frozen H36 helper:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`.

Frozen balanced runner:
- `scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py`
- blob `c9ed18984896835c99a22c68aaedb330d030ec7e`.

Scientific factor only:
- H32 persistent transformer layers `0..31`
- H36 persistent transformer layers `0..35`.

H36 removes transformer-layer streaming entirely; shared embedding/final norm/LM head remain handled by the inherited streamed/shared-stage path.

Frozen:
- exact block size M=5
- 3 x 5-token oracle target traversals
- model/runtime/quantization
- BF16 KV
- parity/top-1 policy
- shared-stage behavior
- I/O/host/resource gates
- no real drafter, prefetch, KV quantization, runtime upgrade, download or cache purge.

Expected raw geometry:
- H32 hotset `2,701,672,448 B`
- H36 hotset `3,039,381,504 B`
- H32 nominal hybrid raw-weight budget `2,973,941,760 B`
- H36 nominal hybrid raw-weight budget `3,311,650,816 B` (~3.08 GiB), assuming the same 272,269,312 B maximum shared stage.

Balanced order:
`H32 -> H36 -> H36 -> H32`.

Every constituent must independently reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`, retain M=5, accept all 15 oracle tokens, expose exact expected hotset IDs, and pass all inherited host/resource/numerical/I-O gates.

Any partial/failing sequence => `HOTSET_COMPARISON_INCOMPLETE`; no winner is inferred, no automatic retry is allowed, and H33-H35 will not be searched post-hoc.

Primary PASS:
`M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h36_hotset_variant_022.py
python3 -m py_compile scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py
python3 scripts/stretch_m5_h32_h36_balanced_hotset_comparison_022.py
```

No download is expected.

## Open questions after Stretch 022

1. Does full transformer residency H36 materially improve the balanced M5 target rate over H32?
2. Does H36 remain within the frozen 8 GB resource envelope?
3. How much residual wall remains in forward/shared stages once transformer rematerialization is eliminated?
4. Regardless of result, transformer-hotset scaling closes after Stretch 022.
5. Next factor should be selected from residual evidence: shared-stage residency/prefetch, double-buffering, or a separately preregistered runtime/kernel experiment.
6. Real drafter selection remains deferred until target-side architecture is sufficiently characterized.
