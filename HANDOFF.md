# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_026_FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_READY`

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
- each transformer layer `84,427,264 B`
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

Decision: freeze M5 as preferred exact block; block-size scaling closed for frozen runtime.

### Stretch 019–022 — transformer residency COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Stretch 022 valid run `20260820-145851`:
- `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- H36 pooled `3.0539262293580034 token/s`
- H36 transformer hotset `3,039,381,504 B`.

Decision: H36 is the physical transformer-residency ceiling; transformer residency is closed.

### Stretch 023 — COMPLETE PASS / FULL RAW-WEIGHT PERSISTENCE

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

### Stretch 024 — COMPLETE PASS / COMPUTE + FRAMEWORK ATTRIBUTION

Original Fix1 sequence `20260820-155313` is preserved as harness/telemetry defect / no scientific result.

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
- accounted share `0.947368373509772` (~94.74%).

Largest transformer components:
- up_proj ~23.36%
- gate_proj ~23.24%
- attention ~22.75%
- down_proj ~22.21%.

Decision: cleanup/framework overhead is the largest measured remaining category; test cleanup schedule before kernel/runtime changes.

Canonical result:
`research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

## Stretch 025 — COMPLETE PASS / BATCHED TRANSFORMER CLEANUP

Plan:
`research/stretch/full-persistent-batched-cleanup-comparison-025-plan.md`

Valid run:
`20260820-161317`

Classification:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

Balanced order:
`CONTROL -> BATCHED -> BATCHED -> CONTROL`.

Frozen sources:
- CONTROL full-persistent Fix1 blob `120ad7be2f275559898bf636ca8e8fe039a56c60`;
- BATCHED blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`;
- balanced runner blob `5fa702d7236888a55b33031c832ce12c79c0e55a`.

Scientific factor only:
- CONTROL cleanup after each of 36 persistent transformer layers;
- BATCHED removes those 36 per-layer cleanup calls and executes the same `gc.collect() -> mx.clear_cache() -> gc.collect()` sequence once after the 36-layer transformer body;
- shared-stage cleanup unchanged.

Controlled result:
- CONTROL pooled `2.761599662127487 token/s`;
- BATCHED pooled `10.667447997968917 token/s`;
- BATCHED/CONTROL `3.8627785715149265x` = **~+286.28%**;
- CONTROL median block `1.5667445 s`;
- BATCHED median block `0.464723 s`;
- median block wall reduction **~70.34%**;
- BATCHED mean one-per-body cleanup `0.060996 s`.

Resource telemetry:
- CONTROL min free `17%`, peak swap `2484.94 MB`;
- BATCHED min free `23%`, peak swap `2535.12 MB`;
- disk after `35.668 GiB`.

Decision:
**M5 + H36 + full raw-weight persistence + one transformer cleanup per body is the new preferred target execution schedule under MLX 0.31.2.**

Causal evidence is the within-Stretch-025 `3.8627785715x` ratio. Absolute rates from separate experiments remain non-causal comparisons.

Canonical result:
`research/stretch/full-persistent-batched-cleanup-comparison-025-result.md`

## Stretch 026 — SHARED-STAGE BATCHED CLEANUP — READY

Plan:
`research/stretch/full-persistent-shared-batched-cleanup-comparison-026-plan.md`

Question:
> With the successful one-per-transformer-body cleanup frozen, can cleanup around persistent embedding/final norm/LM head be consolidated from 3 sequences to 1 post-head sequence?

BATCHED baseline:
- `scripts/stretch_full_persistent_batched_cleanup_025.py`
- blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`.

SHARED_BATCHED treatment:
- `scripts/stretch_full_persistent_shared_batched_cleanup_026.py`
- blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`.

Balanced runner:
- `scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py`
- blob `e958bde5d8a239ffa5fd192922e0693854d478e0`.

Scientific factor only:
- transformer-body cleanup remains once per body in both variants;
- BATCHED retains inherited cleanup after embedding, final norm, and LM head;
- SHARED_BATCHED removes those three cleanup sequences and executes the identical cleanup once after the complete shared-stage path.

Balanced order:
`BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`.

Success:
`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`.

Failure/incomplete:
`SHARED_CLEANUP_COMPARISON_INCOMPLETE`.

No automatic retry, no cache purge, no post-hoc partial shared-stage subset search.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_shared_batched_cleanup_026.py
python3 -m py_compile scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py
python3 scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py
```

No download is expected.

## Open questions after Stretch 026

1. Does consolidating persistent shared-stage cleanup materially improve the new ~10.67 token/s class target schedule?
2. What is the one-per-shared-path cleanup wall?
3. If SHARED_BATCHED wins safely, should transformer-body and shared-path cleanup be merged into one final end-of-pass cleanup as a separate factor?
4. If cleanup gains saturate, return to Stretch 024 compute evidence: MLP ~2.66x attention with gate/up/down as the largest measured projections.
5. Newer MLX and real drafter integration remain separate future factors.
