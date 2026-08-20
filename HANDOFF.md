# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_023_M5_H36_SHARED_STAGE_PERSISTENCE_COMPARISON_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This remains a promotion target, not an intermediate PASS threshold.

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
- total `3,583,928,320 B`
- embedding `272,269,312 B`
- transformer body `3,039,381,504 B`
- each transformer layer `84,427,264 B` / 25 tensors
- final RMSNorm `8,192 B`
- LM head `272,269,312 B`.

## Other active track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Stretch history / canonical evidence

### Stretch 001–013 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O;
- bounded MLX materialization/eviction;
- exact streamed body/full-logit parity;
- persistent ordinary KV;
- exact autoregressive feedback;
- full 36-layer streamed target path;
- repeated target-weight traversal/materialization as dominant late cost;
- H8 persistent transformer hotset benefit;
- exact M4 oracle-block target upper bound.

Key historical rates:
- Stretch 010 sequential: `0.346144 token/s`
- Stretch 012 H8 sequential: `0.477929 token/s`
- Stretch 013 M4 oracle: `1.8857486198 token/s`.

### Stretch 014–017 — exact block-size frontier characterized

Stretch 014:
- valid `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL` at M=8.

Stretch 015:
- `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`;
- first M4/M8 divergence at layer-0 `gate_proj`; attention path remains exact there.

Stretch 016:
- `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`;
- q/k/v/o exact through M=9, first divergence M=10;
- gate/up/down exact through M=5, first divergence M=6.

Stretch 017:
- `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
- M=5 exact end-to-end across all 36 layers;
- 15/15 logits exact, 15/15 top-1 equal, all oracle tokens accepted;
- KV `4 -> 9 -> 14 -> 19`.

Canonical exactness conclusion:
- **M=5 = maximum demonstrated exact oracle block under MLX 0.31.2**;
- **M>=6 = not an exact-parity path under the frozen policy**.

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`, run `20260820-131448`.

Balanced `M4 -> M5 -> M5 -> M4`:
- M4 pooled `1.6983236855 token/s`;
- M5 pooled `1.8646802766 token/s`;
- M5/M4 `1.09795340695x` (~+9.80%).

Decision:
- **M=5 is the preferred exact block**;
- block-size scaling is closed for frozen MLX 0.31.2.

### Stretch 019 — COMPLETE PASS

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-132820`.

Balanced result:
- H8 pooled `1.6634679103 token/s`;
- H16 pooled `2.6094542092 token/s`;
- H16/H8 `1.56868322678x` (~+56.87%);
- median materialization ratio `0.10130580024x`;
- full-pass process-read bytes/block ratio `0.04627184541x`.

Decision: transformer residency/materialization became the primary active speed axis.

### Stretch 020 — COMPLETE PASS

`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-144043`.

Balanced result:
- H16 pooled `1.8043852697 token/s`;
- H24 pooled `2.4333574371 token/s`;
- H24/H16 `1.34857975065x` (~+34.86%);
- median materialization ratio `0.160439630864x`;
- median forward ratio `0.777126124736x`;
- full-pass process reads/block ratio `0.024249004705x`.

H24:
- hotset `2,026,254,336 B`;
- hybrid raw-weight budget `2,298,523,648 B`.

### Stretch 021 — COMPLETE PASS

`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-145035`.

Plan/result:
- `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-plan.md`
- `research/stretch/m5-h24-h32-balanced-hotset-comparison-021-result.md`.

Balanced result:
- H24 pooled `2.7358720706219777 token/s`;
- H32 pooled `3.0490014164644244 token/s`;
- H32/H24 `1.1144532119044803x` (~+11.45%);
- H24 median block wall `1.807173 s`;
- H32 median block wall `1.6119785 s`;
- median materialization ratio `0.3422754314008055x`;
- median forward ratio `0.964972714944873x`;
- mean full-pass process-read bytes/block ratio `0.006146087778740841x`.

H32:
- hotset `2,701,672,448 B`;
- hybrid raw-weight budget `2,973,941,760 B`;
- minimum observed free `25%`;
- peak swap `2124.25 MB`.

Decision:
- residency returns were diminishing;
- one final H36 transformer-residency ceiling was justified.

### Stretch 022 — COMPLETE PASS / TRANSFORMER RESIDENCY CEILING

`M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`, valid run `20260820-145851`.

Plan/result:
- `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-plan.md`
- `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-result.md`.

Frozen sources:
- H32 helper blob `b6b39dfb095b905ed659d52903309783efc02be7`;
- H36 helper blob `9111dde483206a774a9fe5426522dab6e77cecca`;
- balanced runner blob `c9ed18984896835c99a22c68aaedb330d030ec7e`.

Balanced order:
`H32 -> H36 -> H36 -> H32`.

Controlled result:
- H32 pooled target rate `2.763691141669756 token/s`;
- H36 pooled target rate `3.0539262293580034 token/s`;
- H36/H32 rate ratio `1.105017193604671x` (~+10.50%);
- H32 median block wall `1.722024 s`;
- H36 median block wall `1.5799655 s`;
- H36/H32 median transformer-materialization ratio `0.037393043671519056x` (~96.26% lower);
- H36/H32 median transformer-forward ratio `0.9246821007589214x` (~7.53% lower);
- H36/H32 mean full-pass process-read bytes/block ratio `0.08764572674662417x` (~91.24% lower).

Residency/resource telemetry:
- H32 transformer hotset `2,701,672,448 B`;
- H36 transformer hotset `3,039,381,504 B`;
- H32 hybrid raw-weight budget `2,973,941,760 B`;
- H36 hybrid raw-weight budget `3,311,650,816 B`;
- H32 minimum observed free `15%`, peak swap `1992.44 MB`;
- H36 minimum observed free `25%`, peak swap `2040.5 MB`.

Canonical interpretation:
- **M5 + H36 is the best demonstrated transformer-resident target profile**;
- all 36 transformer layers are persistent;
- transformer streaming/materialization is now physically eliminated as a tunable axis;
- residual steady-state cost is primarily transformer compute plus the still-streamed shared stages;
- transformer-residency scaling is permanently closed: no H33–H35 rescue search.

Controlled residency gain curve:
- H8 -> H16: ~+56.87%;
- H16 -> H24: ~+34.86%;
- H24 -> H32: ~+11.45%;
- H32 -> H36: ~+10.50%.

Latest disk after Stretch 022: ~`35.673 GiB` free.

## Stretch 023 — M5/H36 Shared-Stage Persistence — READY

Question:
> With M=5 and all 36 transformer layers already persistent, does retaining embedding + final RMSNorm + LM head improve steady-state target verification versus rebuilding those shared stages each pass?

Plan:
`research/stretch/m5-h36-shared-stage-persistence-023-plan.md`

Frozen control — H36 with shared stages streamed:
- `scripts/stretch_five_token_h36_hotset_variant_022.py`
- blob `9111dde483206a774a9fe5426522dab6e77cecca`.

Frozen treatment — H36 with all shared weights persistent:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
- blob `8c263e7be15441581e481e6f41cbd16f87d4df4b`.

Frozen balanced runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py`
- blob `b8d69c218ee251662fc54a809ca6bf13a4a4e4da`.

Scientific factor only:
- control: embedding, final norm and LM head streamed/materialized per pass;
- treatment: those same three stages materialized once and retained persistently.

Frozen:
- M=5 exact oracle geometry;
- H36 transformer hotset;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- ordinary BF16 KV;
- exact numerical/top-1 gates;
- host/resource/I-O policy;
- no real drafter, prefetch, KV quantization, runtime upgrade, download or cache purge.

Shared weight payload:
- embedding `272,269,312 B`;
- final norm `8,192 B`;
- LM head `272,269,312 B`;
- total `544,546,816 B`.

Treatment full persistent raw model payload:
`3,583,928,320 B` (~3.34 GiB).

Balanced order:
`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`.

Primary comparison:
- pooled steady-state accepted-token target rate;
- treatment one-time shared setup is deliberately excluded from steady-state rate but measured separately;
- runner estimates break-even target blocks from setup wall vs steady-state block-wall savings.

Secondary attribution:
- full block wall;
- transformer materialization/forward;
- shared-stage materialization/forward;
- full-pass and shared-materialization process reads;
- persistent raw-weight bytes;
- free memory / swap.

Any constituent failure or invalid persistence provenance => `SHARED_STAGE_COMPARISON_INCOMPLETE`; stop with no winner and no automatic retry.

Primary PASS:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`.

Stretch 023 is intended to close the raw-weight residency axis regardless of outcome.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py
python3 -m py_compile scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py
python3 scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py
```

No download is expected.

## Open questions after Stretch 023

1. Does full raw-weight persistence materially improve steady-state M5/H36 target rate?
2. What is the one-time shared-persistence setup cost and approximate target-block break-even?
3. Once all weight residency is removed as a bottleneck, how much residual block wall is transformer/shared compute?
4. If the gain is small, move to compute/kernel/runtime rather than further residency variants.
5. If the gain is meaningful and resource-safe, freeze full-weight persistence as the preferred target architecture, then move to the next independent speed axis.
6. Real drafter selection remains separate; current target rates are oracle verification upper bounds and exclude draft/rejection/rollback costs.
