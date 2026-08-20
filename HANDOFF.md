# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_028_SINGLE_PASS_COMPUTE_REATTRIBUTION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- Preserve verified results plus failed scientific/harness runs.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- Do not weaken numerical/resource gates post-hoc.
- Change one scientific factor at a time.
- No hidden rescue ladders or automatic retries.
- No deliberate macOS cache purge to manufacture host state.
- Darwin process-I/O counters are diagnostic, not forensic physical-SSD reads.
- Runtime upgrades are separate preregistered environment changes.
- Absolute throughput across separate experiments is host/cache-state dependent; balanced within-experiment ratios are the causal evidence.
- Update this file and `ROADMAP.md` after meaningful checkpoints.

## Frozen target/environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Qwen3:
- hidden 4096
- 36 transformer layers
- vocab 151936
- 32 attention heads / 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- 3-bit / group64 quantization.

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

Ordinary BF16 KV remains frozen for this sequence.

## Other track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Canonical Stretch evidence

### Stretch 001–017 — architecture + exact block frontier

Established layer-addressable I/O, bounded materialization, exact streamed/full-logit parity, persistent BF16 KV, materialization/process-I/O attribution, persistent hotsets and oracle target verification.

Exactness frontier under MLX 0.31.2:
- M8 valid numerical parity FAIL;
- q/k/v/o exact through M9, first divergence M10;
- gate/up/down exact through M5, first divergence M6;
- Stretch 017 confirms M5 exact end-to-end over 15 oracle tokens.

Decision: **M=5 is the maximum demonstrated exact oracle block under MLX 0.31.2.**

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

- M5/M4 `1.09795340695x` (~+9.80%).

Decision: freeze M5 as preferred exact block; block-size scaling closed for frozen runtime.

### Stretch 019–022 — transformer residency COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Decision: H36 is the physical transformer-residency ceiling; transformer residency is closed.

### Stretch 023 — COMPLETE PASS / full raw-weight persistence

Initial `20260820-151540` preserved as harness defect / no scientific result.

Valid Fix1 `20260820-153308`:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

- PERSISTENT/STREAMED `1.5988607373590418x` = ~+59.89%
- full persistent raw model `3,583,928,320 B`
- mean one-time shared setup `0.3723145 s`
- break-even `0.439246432072825` target blocks.

Decision: **M5 + H36 + full raw-weight persistence** is the frozen weight-residency architecture. Raw-weight residency is closed.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — COMPLETE PASS / compute + framework attribution

Fix1 `20260820-155313` preserved as telemetry harness defect / no scientific result.

Valid Fix2 `20260820-160140`:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Old-schedule attribution per target block:
- transformer compute `0.808182682027109 s`
- attention path `0.22076561170009276 s`
- MLP path `0.5874170703270162 s`
- MLP/attention `2.6608178049261344x`
- per-layer cleanup sum `0.9268928333333333 s`
- shared forward `0.05525783333333333 s`
- residual unattributed `0.09952548463955764 s`
- accounted share ~94.74%.

Largest transformer components in that profiled schedule:
- up_proj ~23.36%
- gate_proj ~23.24%
- attention ~22.75%
- down_proj ~22.21%.

Decision: cleanup/framework overhead was the largest measured category; optimize cleanup before kernel/runtime changes.

Canonical result:
`research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

### Stretch 025 — COMPLETE PASS / batched transformer cleanup

Valid `20260820-161317`:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

- CONTROL pooled `2.761599662127487 token/s`
- BATCHED pooled `10.667447997968917 token/s`
- BATCHED/CONTROL `3.8627785715149265x` = **~+286.28%**
- median block wall reduction ~70.34%
- BATCHED mean one-per-body cleanup `0.060996 s`.

Decision: replace 36 per-layer cleanup sequences with one post-transformer-body cleanup.

Canonical result:
`research/stretch/full-persistent-batched-cleanup-comparison-025-result.md`

### Stretch 026 — COMPLETE PASS / shared-stage batched cleanup

Valid `20260820-162951`:
`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`

- BATCHED pooled `11.1287398593995 token/s`
- SHARED_BATCHED pooled `12.69867607836099 token/s`
- ratio `1.1410704391329174x` = **~+14.11%**
- median block wall reduction ~11.19%
- SHARED_BATCHED mean body cleanup `0.047733333333333336 s`
- SHARED_BATCHED mean post-shared cleanup `0.031349 s`.

Decision: consolidate embedding/norm/head cleanup to one post-head cleanup while retaining one post-body cleanup.

Canonical result:
`research/stretch/full-persistent-shared-batched-cleanup-comparison-026-result.md`

## Stretch 027 — COMPLETE PASS / single final cleanup

Plan:
`research/stretch/full-persistent-single-pass-cleanup-comparison-027-plan.md`

Valid run:
`20260820-163715`

Classification:
`FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`

Balanced order:
`SHARED_BATCHED -> SINGLE_PASS -> SINGLE_PASS -> SHARED_BATCHED`.

Frozen sources:
- SHARED_BATCHED baseline blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`
- SINGLE_PASS treatment blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`
- runner blob `665ca882f5067e65779e7e3f1a0c352432aeb113`.

Scientific factor only:
- baseline has one cleanup after transformer body plus one after LM head;
- SINGLE_PASS removes the intermediate body cleanup and retains one final post-head cleanup for the full pass;
- zero-cleanup was not tested.

Controlled result:
- SHARED_BATCHED pooled `11.71484200192592 token/s`
- SINGLE_PASS pooled `12.730685322495841 token/s`
- SINGLE_PASS/SHARED_BATCHED `1.0867142143618256x` = **~+8.67%**
- SHARED_BATCHED median block `0.4188015 s`
- SINGLE_PASS median block `0.396305 s`
- median reduction **~5.37%**.

Cleanup telemetry:
- baseline body cleanup `0.05322433333333333 s/block`
- baseline final cleanup `0.03469283333333333 s/block`
- baseline combined `0.08791716666666666 s/block`
- SINGLE_PASS final cleanup `0.05584016666666667 s/block`.

Resource telemetry:
- SHARED_BATCHED min free `18%`, peak swap `2509.62 MB`
- SINGLE_PASS min free `23%`, peak swap `2562.94 MB`
- disk after `35.660 GiB`.

Decision:
**Freeze `M5 + H36 + full raw-weight persistence + one final cleanup per pass` as the preferred frozen-runtime target schedule.**

Cleanup-frequency consolidation is closed at one final cleanup per pass. The remaining measured cleanup is ~14.1% of the observed median wall; even idealized removal of all of it would imply only ~`14.7 token/s` from the same median geometry, still below the ~20 token/s promotion target. Further gains must mainly come from compute/kernel/runtime work.

Canonical result:
`research/stretch/full-persistent-single-pass-cleanup-comparison-027-result.md`

## Stretch 028 — SINGLE_PASS compute re-attribution — READY

Plan:
`research/stretch/single-pass-compute-reattribution-028-plan.md`

Question:
> Under the new canonical one-cleanup-per-pass schedule, which synchronized compute components now dominate the target block?

Reason:
Stretch 024 profiling was collected under the obsolete per-layer cleanup schedule. It remains valid historical evidence but should not be the final component ranking for the optimized path.

CONTROL:
- `scripts/stretch_full_persistent_single_pass_cleanup_027.py`
- blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

PROFILED:
- `scripts/stretch_single_pass_compute_reattribution_028_profiled.py`
- blob `0858e39a46bf09fe7750691b6dcd95b6753e5c70`.

Balanced runner:
- `scripts/stretch_single_pass_compute_reattribution_comparison_028.py`
- blob `65d1c93967ed786623a3899e0f510ad9ef8de1e2`.

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`.

Scientific change:
explicit `mx.eval` timing boundaries on target transformer components only. Prompt, M5, H36, full persistence, one-final-cleanup schedule, runtime, KV and all inherited gates remain unchanged.

PROFILED throughput is perturbation telemetry only, not an optimization result.

Primary outputs:
- transformer compute/block
- attention path
- MLP path
- MLP/attention ratio
- component ranking
- final cleanup wall
- shared-stage forward/materialization
- residual unattributed wall
- accounted share
- slowest layer candidates.

Success:
`SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`.

Failure/incomplete:
`SINGLE_PASS_COMPUTE_REATTRIBUTION_INCOMPLETE`.

No automatic retry/rescue.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_single_pass_compute_reattribution_028_profiled.py
python3 -m py_compile scripts/stretch_single_pass_compute_reattribution_comparison_028.py
python3 scripts/stretch_single_pass_compute_reattribution_comparison_028.py
```

No download is expected.

## Open questions after Stretch 028

1. Does MLP remain the dominant compute path after cleanup optimization?
2. Which of gate/up/down/attention now dominates synchronized wall?
3. Is residual/framework wall now small enough to justify direct kernel work?
4. If MLP dominates, choose one separately preregistered MLP/quantized-linear factor.
5. If attention dominates, choose an attention/SDPA factor instead.
6. A newer MLX runtime remains a separate environment comparison and must not rewrite MLX 0.31.2 evidence.
7. Real drafter integration remains separate; current rates are oracle target-verification upper bounds.
