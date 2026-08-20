# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_030_MLX_0312_0320_RUNTIME_COMPARISON_ENV_SETUP_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- One scientific factor at a time.
- Preserve valid PASS, scientific FAIL and harness-defect evidence.
- No post-hoc gate weakening, hidden rescue ladders or automatic retries.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- No deliberate macOS cache purge to manufacture host state.
- Darwin process-I/O counters are diagnostic, not forensic physical SSD reads.
- Balanced within-experiment ratios are causal evidence; absolute throughput across separate experiments is host/cache-state dependent.
- Runtime/model upgrades are separate preregistered factors and never rewrite frozen historical evidence.
- Update HANDOFF and ROADMAP after meaningful checkpoints.

## Frozen model / canonical pre-030 runtime

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Qwen3 geometry:
- hidden 4096
- 36 transformer layers
- vocab 151936
- 32 attention heads / 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- 3-bit/group64 affine quantization.

Canonical historical runtime:
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

Ordinary BF16 KV remains frozen.

## Other track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Canonical Stretch evidence

### Stretch 001–017 — exact architecture / block frontier

Established:
- layer-addressable I/O and bounded materialization;
- streamed/full-logit parity;
- persistent BF16 KV;
- persistent transformer hotsets;
- target oracle verification.

Frozen 0.31.2 exactness frontier:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M9, first divergence M10;
- gate/up/down exact through M5, first divergence M6;
- Stretch 017 confirms M5 exact end-to-end over 15 oracle tokens.

Decision: **M5 maximum demonstrated exact oracle block under MLX 0.31.2**.

### Stretch 018 — M4/M5 balanced cost — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- M5/M4 `1.09795340695x` (~+9.80%).

Decision: freeze M5 for 0.31.2.

### Stretch 019–022 — transformer residency — COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Decision: H36 physical transformer-residency ceiling.

### Stretch 023 — full raw-weight persistence — COMPLETE PASS

Initial `20260820-151540`: harness defect / no scientific result.

Valid Fix1 `20260820-153308`:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- PERSISTENT/STREAMED `1.5988607373590418x` (~+59.89%)
- full persistent raw model `3,583,928,320 B`.

Decision: freeze M5 + H36 + full persistence.

Result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — compute/framework attribution — COMPLETE PASS

Fix1 `20260820-155313`: telemetry harness defect / no scientific result.

Valid Fix2 `20260820-160140`:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`
- transformer compute `0.8081826820 s/block`
- attention `0.2207656117 s/block`
- MLP `0.5874170703 s/block`
- MLP/attention `2.6608178049x`
- old per-layer cleanup `0.9268928333 s/block`.

Decision: cleanup schedule first.

### Stretch 025 — transformer cleanup batching — COMPLETE PASS

Valid `20260820-161317`:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`
- BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- median block wall ~70.34% lower.

Decision: 36 per-layer cleanups -> one post-body cleanup.

### Stretch 026 — shared cleanup batching — COMPLETE PASS

Valid `20260820-162951`:
`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`
- SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%).

Decision: one body cleanup + one final shared cleanup.

### Stretch 027 — one cleanup/pass — COMPLETE PASS / CANONICAL WORKLOAD

Valid `20260820-163715`:
`FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`
- SINGLE_PASS/SHARED_BATCHED `1.0867142143618256x` (~+8.67%)
- SINGLE_PASS pooled `12.730685322495841 token/s`
- median block `0.396305 s`
- final cleanup `0.05584016666666667 s/block`.

Decision: freeze **M5 + H36 + full persistence + one final cleanup/pass**.

Canonical workload helper:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`
blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

### Stretch 028 — compute re-attribution on SINGLE_PASS — COMPLETE PASS

Valid `20260820-164802`:
`SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`

Key synchronized attribution:
- transformer compute `0.44969600122810033 s/block`
- attention path `0.1231006117692838 s/block`
- MLP path `0.3265953894588165 s/block`
- MLP/attention `2.653076899982628x`
- up_proj `0.09931493003387004 s/block`
- attention `0.09857969474978745 s/block`
- gate_proj `0.0965807989705354 s/block`
- down_proj `0.09428692991302039 s/block`
- final cleanup `0.0617505 s/block`
- shared forward `0.028035333333333332 s/block`
- accounted wall ~93.95%.

Decision: true transformer compute is now primary target.

Result:
`research/stretch/single-pass-compute-reattribution-028-result.md`

### Stretch 029 — gate+up quantized fusion — COMPLETE PASS / NOT PROMOTED

Scientific plan:
`research/stretch/gate-up-quantized-fusion-029-plan.md`

Initial run `20260820-170503`:
- `GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`
- pure wrapper-phase harness defect;
- FUSED treatment never launched;
- scientific result NONE.

Preserved defect:
`research/stretch/gate-up-quantized-fusion-029-harness-defect-20260820-170503.md`

Harness Fix1 preserved original scientific fusion callback unchanged.

Valid fresh ABBA `20260820-171714`:
`GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`

Metrics:
- CONTROL `13.228627278575932 token/s`
- FUSED `12.352399124132555 token/s`
- FUSED/CONTROL `0.933762730176664x` (~6.62% slower)
- CONTROL median block `0.374359 s`
- FUSED median block `0.406644 s`
- FUSED/CONTROL median wall `1.0862407475177571x` (~8.62% higher)
- CONTROL mean final cleanup `0.05385683333333333 s`
- FUSED mean final cleanup `0.06512233333333334 s`
- CONTROL min free `19%`
- FUSED min free `22%`
- CONTROL peak swap `2575.56 MB`
- FUSED peak swap `2614.5 MB`.

Interpretation:
- fused gate+up is exact at frozen M5 gates;
- it is slower under MLX 0.31.2;
- do not promote;
- no rescue ordering, partial fusion or threshold relaxation.

Canonical result:
`research/stretch/gate-up-quantized-fusion-029-result.md`

Decision: restore Stretch 027 SINGLE_PASS as preferred 0.31.2 architecture and close this fusion path.

## Stretch 030 — isolated MLX 0.31.2 vs 0.32.0 runtime comparison — READY FOR ENV SETUP

Plan:
`research/stretch/mlx-0312-0320-runtime-comparison-030-plan.md`

Scientific question:
Does changing only MLX `0.31.2 -> 0.32.0` preserve frozen M5 correctness and improve target-verification cost?

Motivation frozen before run:
- official MLX v0.32.0 release includes `[Metal][Performance]: Add split-K for quantized matmul (small M)` and generated qmm implementation changes;
- official mlx-lm 0.31.3 metadata accepts `mlx>=0.31.2` on Darwin.

CONTROL and MLX0320 execute the **same exact workload source**:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`
blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

Treatment environment:
`.venvs/stretch030-mlx0320`

Environment setup utility:
`scripts/stretch_mlx_0320_env_setup_030.py`
blob `fde39967be02cba81ea14bb043c9fdacd24db861`.

Setup policy:
- `venv --system-site-packages` from canonical interpreter;
- overlay only `mlx==0.32.0 --no-deps`;
- canonical environment untouched;
- require same Python, mlx-lm 0.31.3, Transformers 5.12.1, NumPy and safetensors;
- no package installation during the scientific comparison.

Balanced runner:
`scripts/stretch_mlx_0312_0320_runtime_comparison_030.py`
blob `0d0a27549067cef61a1dca7d3bf8f0e1f954d98b`.

Balanced order:
`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`.

Outcome policy:
- first MLX0320 frozen numerical/top1/oracle failure => `MLX_0320_RUNTIME_EXACTNESS_FAIL`, valid scientific FAIL, stop, no rescue;
- complete exact ABBA => `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`;
- environment/harness/resource failure => `MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE`.

If 0.32.0 is exact + faster, do **not** immediately increase M inside Stretch 030. First freeze 030, then separately preregister a new M-boundary mapping under 0.32.0 because the old M5 ceiling is 0.31.2-specific.

## Exact next step

From canonical repo path:

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_mlx_0320_env_setup_030.py
python3 scripts/stretch_mlx_0320_env_setup_030.py
```

Only if setup prints `Environment setup: PASS`:

```bash
python3 -m py_compile scripts/stretch_mlx_0312_0320_runtime_comparison_030.py
python3 scripts/stretch_mlx_0312_0320_runtime_comparison_030.py
```

Do not run the canonical workload manually between balanced constituents. Do not delete/rebuild the treatment venv unless setup reports it invalid.

## Open questions after Stretch 030

1. Does MLX 0.32.0 preserve frozen M5 exactness?
2. If exact, what is the balanced target-rate ratio vs 0.31.2?
3. Does resource behavior remain acceptable on 8 GB?
4. If exact + faster, where is the new M exactness boundary under 0.32.0?
5. If exact + flat/slower, which independent compute axis is next: attention/SDPA or another kernel/runtime mechanism?
6. Real drafter integration remains separate; current target rates are oracle-verification upper bounds.
