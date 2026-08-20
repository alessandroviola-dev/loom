# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_023_M5_H36_SHARED_STAGE_PERSISTENCE_HARNESS_FIX1_READY`

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

## Canonical Stretch evidence

### Stretch 001–013 — COMPLETE PASS

Established:
- layer-addressable safetensors I/O;
- bounded MLX materialization/eviction;
- exact streamed body/full-logit parity;
- persistent ordinary KV;
- exact autoregressive feedback;
- repeated target-weight traversal/materialization as dominant late cost;
- H8 persistent transformer hotset benefit;
- M4 exact oracle-block target upper bound.

Key historical rates:
- Stretch 010 sequential `0.346144 token/s`;
- Stretch 012 H8 sequential `0.477929 token/s`;
- Stretch 013 M4 oracle `1.8857486198 token/s`.

### Stretch 014–017 — EXACT BLOCK FRONTIER CHARACTERIZED

Stretch 014:
- valid M8 `ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`.

Stretch 015:
- `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`;
- first M4/M8 divergence at layer-0 `gate_proj`; attention path exact at that point.

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
- M>=6 is not an exact-parity path under the frozen policy.

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

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-132820`:
- H8 pooled `1.6634679103 token/s`;
- H16 pooled `2.6094542092 token/s`;
- H16/H8 `1.56868322678x` (~+56.87%);
- median materialization ratio `0.10130580024x`;
- full-pass process-read bytes/block ratio `0.04627184541x`.

Decision: transformer residency/materialization became the primary target-side speed axis.

### Stretch 020 — COMPLETE PASS

`M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-144043`:
- H16 pooled `1.8043852697 token/s`;
- H24 pooled `2.4333574371 token/s`;
- H24/H16 `1.34857975065x` (~+34.86%);
- median materialization ratio `0.160439630864x`;
- median forward ratio `0.777126124736x`.

### Stretch 021 — COMPLETE PASS

`M5_H24_H32_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-145035`:
- H24 pooled `2.7358720706219777 token/s`;
- H32 pooled `3.0490014164644244 token/s`;
- H32/H24 `1.1144532119044803x` (~+11.45%);
- H32 hotset `2,701,672,448 B`;
- H32 hybrid raw-weight budget `2,973,941,760 B`;
- H32 min observed free `25%`, peak swap `2124.25 MB`.

### Stretch 022 — COMPLETE PASS / TRANSFORMER RESIDENCY CEILING

`M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`, run `20260820-145851`.

Plan/result:
- `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-plan.md`
- `research/stretch/m5-h32-h36-balanced-hotset-comparison-022-result.md`.

Frozen sources:
- H32 helper `b6b39dfb095b905ed659d52903309783efc02be7`;
- H36 helper `9111dde483206a774a9fe5426522dab6e77cecca`;
- balanced runner `c9ed18984896835c99a22c68aaedb330d030ec7e`.

Controlled result:
- H32 pooled `2.763691141669756 token/s`;
- H36 pooled `3.0539262293580034 token/s`;
- H36/H32 `1.105017193604671x` (~+10.50%);
- H36 median block wall `1.5799655 s`;
- H36/H32 median transformer-materialization `0.037393043671519056x`;
- H36/H32 median transformer-forward `0.9246821007589214x`;
- H36/H32 full-pass process-read bytes/block `0.08764572674662417x`.

H36 resource geometry:
- transformer hotset `3,039,381,504 B`;
- hybrid raw-weight budget `3,311,650,816 B`;
- min observed free `25%`;
- peak swap `2040.5 MB`.

Decision:
- **M5 + H36 is the best demonstrated transformer-resident target profile**;
- transformer streaming/materialization is physically eliminated as a tunable axis;
- transformer-hotset scaling is permanently closed; no H33–H35 rescue search.

Controlled residency gain curve:
- H8 -> H16 ~+56.87%;
- H16 -> H24 ~+34.86%;
- H24 -> H32 ~+11.45%;
- H32 -> H36 ~+10.50%.

Latest disk after Stretch 022: ~`35.673 GiB` free.

## Stretch 023 — M5/H36 Shared-Stage Persistence

Scientific question:
> With M=5 and all 36 transformer layers persistent, does retaining embedding + final RMSNorm + LM head improve steady-state target verification versus rebuilding those shared stages each pass?

Original plan:
`research/stretch/m5-h36-shared-stage-persistence-023-plan.md`

Frozen scientific design:
- control `STREAMED`: H36 transformer hotset persistent; embedding/norm/head streamed each pass;
- treatment `PERSISTENT`: same H36 hotset plus embedding/norm/head materialized once and retained;
- balanced order `STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`;
- M=5, model/runtime/KV/parity/I-O/safety unchanged;
- no cache purge, hidden retry, fallback, prefetch, runtime upgrade or real drafter;
- one-time treatment setup excluded from steady-state target rate but reported separately.

Shared raw payload:
- embedding `272,269,312 B`;
- final RMSNorm `8,192 B`;
- LM head `272,269,312 B`;
- shared total `544,546,816 B`;
- full persistent raw model `3,583,928,320 B` (~3.34 GiB).

### Original attempt `20260820-151540` — HARNESS DEFECT / NO SCIENTIFIC RESULT

Outer classification:
`SHARED_STAGE_COMPARISON_INCOMPLETE`.

Preserved run:
`results-local/stretch/m5-h36-shared-stage-persistence-023/20260820-151540`.

Canonical defect record:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-defect-20260820-151540.md`.

Observed sequence:
- Attempt 1 STREAMED: inherited PASS, 15 accepted oracle tokens, `1.7713653826078375 token/s`;
- Attempt 2 PERSISTENT: return code 1 after ~0.37 s, no constituent summary;
- attempts 3–4 not executed.

Traceback root:
`RuntimeError: Stretch 023 transform failed for shared persistence constants: expected 1 occurrence, found 0`.

Root cause:
- frozen broken treatment helper `8c263e7be15441581e481e6f41cbd16f87d4df4b` applied `add_shared_persistence()` to the transformed Stretch 013 **wrapper source**;
- that callback searches fragments that exist only in the final generated runtime;
- failure occurred before model/scientific execution.

Therefore:
- no claim about full-weight persistence, memory feasibility, MLX behavior, parity or performance is allowed from this attempt;
- the single valid STREAMED control is audit-only and is not reused in the repaired ABBA comparison.

### Stretch 023 Harness Fix1 — READY

Amendment:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-fix1.md`.

Preserved broken files:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
  blob `8c263e7be15441581e481e6f41cbd16f87d4df4b`;
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py`
  blob `b8d69c218ee251662fc54a809ca6bf13a4a4e4da`.

New harness-fixed treatment:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

Fix mechanism:
- constructs the exact frozen M5/H36 wrapper;
- reuses the original broken helper's **unchanged** `add_shared_persistence()` implementation;
- injects that callback into the wrapper so it runs only after the wrapper has generated the final M5/H36 runtime source;
- no scientific factor, threshold, metric or gate changes.

New harness-fixed comparison runner:
- `scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023_fix1.py`
- blob `dfa4c25b71108e258f4d311a65ae038b45be16dc`.

Runner changes only:
1. PERSISTENT helper path/blob -> fix1;
2. output root -> `m5-h36-shared-stage-persistence-023-fix1`;
3. explicit `harness_revision: fix1` identity.

Scientific PASS remains:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`.

Any constituent/provenance/resource/correctness failure remains:
`SHARED_STAGE_COMPARISON_INCOMPLETE`.

The repaired run must start a completely new four-run ABBA sequence. No data from `20260820-151540` is carried into the comparison.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py
python3 -m py_compile scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023_fix1.py
python3 scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023_fix1.py
```

No download is expected.

If fix1 fails before producing a treatment summary, preserve all output and do not retry automatically.

## Open questions after valid Stretch 023

1. Does full raw-weight persistence materially improve steady-state M5/H36 target rate?
2. What is the one-time shared setup cost and approximate target-block break-even?
3. Once all weight residency is removed as a bottleneck, how much residual block wall is compute/kernel work?
4. Stretch 023 closes raw-weight residency regardless of valid outcome.
5. Next axis should be selected from residual evidence: compute/kernel/runtime or real speculative-drafter integration.
6. Any newer MLX experiment remains a separately preregistered environment change and must not redefine the frozen 0.31.2 baseline.
