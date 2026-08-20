# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_027_FULL_PERSISTENT_SINGLE_PASS_CLEANUP_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate PASS gate.

## Research rules

- Preserve verified results and failed scientific/harness runs.
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

Qwen3 geometry:
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

Ordinary BF16 KV remains frozen.

## Other track

Amplify remains queued behind Stretch.

Frozen next Amplify work:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.

## Canonical Stretch evidence

### Stretch 001–017 — architecture + exact block frontier

Established layer-addressable I/O, bounded materialization, exact streamed parity, persistent BF16 KV, materialization/process-I/O attribution, persistent hotsets, and oracle target verification.

Exactness frontier under MLX 0.31.2:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M=9, first divergence M=10;
- gate/up/down exact through M=5, first divergence M=6;
- Stretch 017 confirms M5 exact end-to-end over 15 oracle tokens.

Decision: **M=5 is the maximum demonstrated exact oracle block under MLX 0.31.2.**

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

- M4 pooled `1.6983236855 token/s`
- M5 pooled `1.8646802766 token/s`
- M5/M4 ~+9.80%.

Decision: M5 is the preferred exact block; block-size scaling closed for the frozen runtime.

### Stretch 019–022 — transformer residency COMPLETE

Controlled residency gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Stretch 022 valid run `20260820-145851`:
- `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- H36 pooled `3.0539262293580034 token/s`
- H36 transformer hotset `3,039,381,504 B`.

Decision: H36 is the physical transformer-residency ceiling; transformer residency is closed.

### Stretch 023 — COMPLETE PASS / full raw-weight persistence

Initial run `20260820-151540` is preserved as harness defect / no scientific result.

Valid Fix1 run `20260820-153308`:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

Balanced `STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`:
- STREAMED pooled `2.2094465476329797 token/s`
- PERSISTENT pooled `3.532597336303855 token/s`
- controlled gain ~+59.89%
- median block wall ~36.83% lower
- full persistent raw model `3,583,928,320 B`
- mean shared setup `0.3723145 s`
- break-even `0.439246432072825` target blocks
- PERSISTENT min free `23%`; peak swap `2487.69 MB`.

Decision: **M5 + H36 + full raw-weight persistence is the best demonstrated weight-residency architecture under MLX 0.31.2.** Raw-weight residency is closed.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

### Stretch 024 — COMPLETE PASS / compute + framework attribution

Fix1 run `20260820-155313` is preserved as telemetry harness defect / no scientific result.

Valid Fix2 run `20260820-160140`:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Attribution per target block:
- transformer compute `0.808182682027109 s`
- attention path `0.22076561170009276 s`
- MLP path `0.5874170703270162 s`
- MLP/attention `2.6608178049261344x`
- per-layer cleanup sum `0.9268928333333333 s`
- shared forward `0.05525783333333333 s`
- residual unattributed `0.09952548463955764 s`
- accounted share ~94.74%.

Largest transformer components:
- up_proj ~23.36%
- gate_proj ~23.24%
- attention ~22.75%
- down_proj ~22.21%.

Decision: cleanup/framework overhead was the largest measured category; optimize cleanup scheduling before kernel/runtime changes.

Canonical result:
`research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

### Stretch 025 — COMPLETE PASS / batched transformer cleanup

Valid run `20260820-161317`:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

Balanced `CONTROL -> BATCHED -> BATCHED -> CONTROL`:
- CONTROL pooled `2.761599662127487 token/s`
- BATCHED pooled `10.667447997968917 token/s`
- BATCHED/CONTROL `3.8627785715149265x` = ~+286.28%
- CONTROL median block `1.5667445 s`
- BATCHED median block `0.464723 s` = ~70.34% lower
- BATCHED mean one-per-body cleanup `0.060996 s`.

Resource telemetry:
- CONTROL min free `17%`, peak swap `2484.94 MB`
- BATCHED min free `23%`, peak swap `2535.12 MB`.

Decision: replace 36 per-layer cleanup sequences with one cleanup after the transformer body.

Canonical result:
`research/stretch/full-persistent-batched-cleanup-comparison-025-result.md`

## Stretch 026 — COMPLETE PASS / shared-stage batched cleanup

Plan:
`research/stretch/full-persistent-shared-batched-cleanup-comparison-026-plan.md`

Valid run:
`20260820-162951`

Classification:
`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`

Balanced order:
`BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`.

Frozen sources:
- BATCHED baseline blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`
- SHARED_BATCHED treatment blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`
- balanced runner blob `e958bde5d8a239ffa5fd192922e0693854d478e0`.

Scientific factor only:
- transformer cleanup remains once per body in both variants;
- BATCHED performs inherited cleanup separately after embedding, final norm and LM head;
- SHARED_BATCHED consolidates those three shared-stage cleanup sequences into one cleanup after LM head.

Controlled result:
- BATCHED pooled `11.1287398593995 token/s`
- SHARED_BATCHED pooled `12.69867607836099 token/s`
- SHARED_BATCHED/BATCHED `1.1410704391329174x` = **~+14.11%**
- BATCHED median block `0.4502915 s`
- SHARED_BATCHED median block `0.399913 s`
- median block wall reduction **~11.19%**
- BATCHED mean body cleanup `0.05014766666666667 s`
- SHARED_BATCHED mean body cleanup `0.047733333333333336 s`
- SHARED_BATCHED mean post-shared cleanup `0.031349 s`.

Resource telemetry:
- BATCHED min free `19%`, peak swap `2422.94 MB`
- SHARED_BATCHED min free `25%`, peak swap `2465.75 MB`
- disk after ~`35.655 GiB`.

Decision:
**M5 + H36 + full persistence + one cleanup after transformer body + one cleanup after LM head is the new preferred target schedule.**

This is already a `~12.70 token/s` class oracle target-verification path in the valid balanced run, but cross-experiment absolute rates remain non-causal.

Canonical result:
`research/stretch/full-persistent-shared-batched-cleanup-comparison-026-result.md`

## Stretch 027 — SINGLE END-OF-PASS CLEANUP — READY

Plan:
`research/stretch/full-persistent-single-pass-cleanup-comparison-027-plan.md`

Question:
> Can the remaining two cleanup points per target pass be consolidated to one final post-head cleanup while preserving exactness and resource safety?

SHARED_BATCHED baseline:
- `scripts/stretch_full_persistent_shared_batched_cleanup_026.py`
- blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`.

SINGLE_PASS treatment:
- `scripts/stretch_full_persistent_single_pass_cleanup_027.py`
- blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

Treatment changes one factor only:
- baseline: one cleanup after transformer body + one cleanup after LM head;
- treatment: remove the intermediate transformer-body cleanup and retain one cleanup after LM head as the only cleanup point in the target pass;
- zero-cleanup is explicitly not tested.

Balanced runner:
- `scripts/stretch_full_persistent_single_pass_cleanup_comparison_027.py`
- blob `665ca882f5067e65779e7e3f1a0c352432aeb113`.

Balanced order:
`SHARED_BATCHED -> SINGLE_PASS -> SINGLE_PASS -> SHARED_BATCHED`.

Primary metric:
pooled target-verification rate within the balanced experiment.

Secondary:
- median/mean block wall
- baseline body-cleanup wall
- final cleanup wall
- min free memory
- peak swap
- inherited exactness/KV/resource gates.

Success:
`FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`

Failure/incomplete:
`SINGLE_PASS_CLEANUP_COMPARISON_INCOMPLETE`

No automatic retry, no cache purge, no zero-cleanup rescue.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_single_pass_cleanup_027.py
python3 -m py_compile scripts/stretch_full_persistent_single_pass_cleanup_comparison_027.py
python3 scripts/stretch_full_persistent_single_pass_cleanup_comparison_027.py
```

No download is expected.

## Open questions after Stretch 027

1. Does one final cleanup per pass improve the ~12.70 token/s class schedule without violating resource gates?
2. If SINGLE_PASS wins safely, close cleanup-frequency consolidation at one cleanup/pass; zero cleanup remains unproven.
3. If SINGLE_PASS is flat/slower or unsafe, retain the Stretch 026 two-point schedule.
4. After cleanup closes, return to true compute: Stretch 024 measured MLP at ~2.66x attention, with gate/up/down as the dominant projection kernels.
5. A newer MLX runtime remains a separate preregistered environment factor.
6. Real drafter integration remains separate; current rates are oracle target-verification upper bounds.
