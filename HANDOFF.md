# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_029_GATE_UP_QUANTIZED_FUSION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- Preserve verified results plus scientific/harness failures.
- Change one scientific factor at a time.
- No post-hoc gate weakening, hidden rescue ladders, or automatic retries.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- No deliberate macOS cache purge to manufacture host state.
- Darwin process-I/O counters are diagnostic, not forensic physical-SSD reads.
- Absolute throughput across separate experiments is host/cache-state dependent; balanced within-experiment ratios are the causal evidence.
- Runtime/model upgrades are separate preregistered factors and do not rewrite frozen evidence.
- Update `HANDOFF.md` and `ROADMAP.md` after meaningful checkpoints.

## Frozen target/environment

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

Ordinary BF16 KV remains frozen.

## Other track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Canonical Stretch evidence

### Stretch 001–017 — exact architecture/block frontier

Established layer-addressable I/O, bounded materialization, exact streamed/full-logit parity, persistent BF16 KV, persistent hotsets and oracle target verification.

Exactness frontier under MLX 0.31.2:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M9, first divergence M10;
- gate/up/down exact through M5, first divergence M6;
- Stretch 017 confirms M5 exact end-to-end over 15 oracle tokens.

Decision: **M=5 is the maximum demonstrated exact oracle block under MLX 0.31.2.**

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`
- M5/M4 `1.09795340695x` (~+9.80%).

Decision: freeze M5; block-size scaling closed for frozen runtime.

### Stretch 019–022 — transformer residency COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Decision: H36 is the physical transformer-residency ceiling; transformer residency closed.

### Stretch 023 — full raw-weight persistence COMPLETE PASS

Initial `20260820-151540` preserved as harness defect / no scientific result.

Valid Fix1 `20260820-153308`:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`
- PERSISTENT/STREAMED `1.5988607373590418x` (~+59.89%)
- full persistent raw model `3,583,928,320 B`
- shared setup `0.3723145 s`
- break-even `0.439246432072825` target blocks.

Decision: freeze **M5 + H36 + full raw-weight persistence**. Raw-weight residency closed.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — compute/framework attribution COMPLETE PASS

Fix1 `20260820-155313` preserved as telemetry harness defect / no scientific result.

Valid Fix2 `20260820-160140`:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`
- transformer compute `0.8081826820 s/block`
- attention path `0.2207656117 s/block`
- MLP path `0.5874170703 s/block`
- MLP/attention `2.6608178049x`
- old per-layer cleanup sum `0.9268928333 s/block`.

Decision: cleanup/framework was the largest category; optimize schedule first.

Canonical result:
`research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

### Stretch 025 — batched transformer cleanup COMPLETE PASS

Valid `20260820-161317`:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`
- BATCHED/CONTROL `3.8627785715x` (~+286.28%)
- median block wall ~70.34% lower
- one post-body cleanup `0.060996 s/block`.

Decision: replace 36 per-layer cleanups with one post-body cleanup.

Canonical result:
`research/stretch/full-persistent-batched-cleanup-comparison-025-result.md`

### Stretch 026 — shared-stage cleanup consolidation COMPLETE PASS

Valid `20260820-162951`:
`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`
- SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%)
- median block wall ~11.19% lower.

Decision: one body cleanup + one post-head cleanup.

Canonical result:
`research/stretch/full-persistent-shared-batched-cleanup-comparison-026-result.md`

### Stretch 027 — single final cleanup COMPLETE PASS

Valid `20260820-163715`:
`FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`
- SHARED_BATCHED pooled `11.71484200192592 token/s`
- SINGLE_PASS pooled `12.730685322495841 token/s`
- SINGLE_PASS/SHARED_BATCHED `1.0867142143618256x` (~+8.67%)
- median block `0.396305 s`
- final cleanup `0.05584016666666667 s/block`
- min free `23%`
- peak swap `2562.94 MB`.

Decision: freeze **M5 + H36 + full persistence + one final cleanup/pass**. Cleanup-frequency axis closed; zero-cleanup remains unproven.

Canonical result:
`research/stretch/full-persistent-single-pass-cleanup-comparison-027-result.md`

## Stretch 028 — COMPLETE PASS / compute re-attribution on SINGLE_PASS

Valid run:
`20260820-164802`

Classification:
`SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`

Frozen sources:
- CONTROL Stretch 027 blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`
- PROFILED blob `0858e39a46bf09fe7750691b6dcd95b6753e5c70`
- runner blob `65d1c93967ed786623a3899e0f510ad9ef8de1e2`.

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`.

Instrumentation perturbation:
- CONTROL pooled `12.707685947332573 token/s`
- PROFILED pooled `8.706180343302105 token/s`
- PROFILED/CONTROL `0.6851113868713122x`
- CONTROL median block `0.394962 s`
- PROFILED median block `0.609049 s`.

PROFILED absolute speed is not an optimization result.

Synchronized re-attribution:
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
- residual unattributed `0.034740665438566354 s/block`
- accounted share `0.9395083002891038` (~93.95%).

Interpretation:
- true transformer compute is now the main optimization target;
- MLP remains ~2.653x attention because it contains three large quantized projections;
- gate/up/down together are ~`0.29018 s/block` in the synchronized PROFILED path;
- individually up/attention/gate/down are all near the same ~0.095–0.099 s/block scale.

Canonical result:
`research/stretch/single-pass-compute-reattribution-028-result.md`

## Stretch 029 — GATE+UP QUANTIZED FUSION — READY

Plan:
`research/stretch/gate-up-quantized-fusion-029-plan.md`

Official frozen-runtime anatomy supporting the design:
- mlx-lm v0.31.3 Qwen3 MLP: `down_proj(swiglu(gate_proj(x), up_proj(x)))`;
- MLX v0.31.2 QuantizedLinear delegates to `mx.quantized_matmul(..., transpose=True)`.

CONTROL:
- `scripts/stretch_full_persistent_single_pass_cleanup_027.py`
- blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

FUSED:
- `scripts/stretch_gate_up_quantized_fusion_029.py`
- blob `c37ff6313106807c1e2e5070b7fb8f19e97abea6`.

FUSED changes one factor only:
- gate + up packed weight/scales/affine biases are concatenated once by output row during block setup;
- the original two persistent module references are removed after fused materialization;
- no per-forward weight concatenation;
- one `mx.quantized_matmul` produces gate+up output, then `mx.split` restores the two halves;
- SwiGLU and down_proj are unchanged.

Balanced runner:
- `scripts/stretch_gate_up_quantized_fusion_comparison_029.py`
- blob `8d89665b5d3061891a53f1734e19331aa1a4fb34`.

Balanced order:
`CONTROL -> FUSED -> FUSED -> CONTROL`.

Critical preregistered exactness rule:
- if the first FUSED produces prompt/oracle numerical, top-1, acceptance, or generated-sequence mismatch, stop immediately;
- classify `GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL` as a valid scientific result;
- no rescue ordering, partial fusion, threshold relaxation, or retry.

Complete exact ABBA success:
`GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`.

Harness/resource/provenance failure:
`GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_gate_up_quantized_fusion_029.py
python3 -m py_compile scripts/stretch_gate_up_quantized_fusion_comparison_029.py
python3 scripts/stretch_gate_up_quantized_fusion_comparison_029.py
```

No download is expected.

## Open questions after Stretch 029

1. Is one fused gate+up quantized call exact under frozen M5 gates?
2. If exact, does it beat separate gate/up within balanced ABBA?
3. Does the fused representation preserve full persistent raw-weight/resource behavior?
4. If fusion fails exactness, preserve the FAIL and move to a different compute factor rather than rescuing the fusion.
5. If fusion is exact but flat/slower, close this fusion implementation and choose the next independent kernel factor.
6. A newer MLX runtime remains a separate environment factor.
7. Real drafter integration remains separate; current target rates are oracle verification upper bounds.
