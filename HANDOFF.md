# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_025_FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_READY`

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

Decision: **M5 + H36 + full raw-weight persistence is the best demonstrated target-side architecture under MLX 0.31.2.** Raw-weight residency is closed.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

## Stretch 024 — COMPLETE PASS / COMPUTE + FRAMEWORK ATTRIBUTION

Original Fix1 sequence `20260820-155313` is preserved as harness/telemetry defect / no scientific result because parent aggregation referenced child-local `args.num_hidden_layers`.

Valid Fix2 run:
`20260820-160140`

Classification:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Frozen CONTROL:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

PROFILED Fix2:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py`
- blob `83f9e12dfa30445810ca4d39150dbcd151ad3e66`.

Balanced runner Fix2:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py`
- blob `de464c4fe5dca90c2fe110337f12e3f6424ea937`.

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`.

Instrumentation perturbation telemetry:
- CONTROL pooled `2.6093073645786875 token/s`
- PROFILED pooled `2.644128118583858 token/s`
- PROFILED/CONTROL `1.0133448264768887x`.

Do not treat PROFILED throughput as an optimization result; explicit `mx.eval` boundaries perturb scheduling.

Synchronized target attribution per block:
- transformer compute `0.808182682027109 s`
- attention path `0.22076561170009276 s`
- MLP path `0.5874170703270162 s`
- MLP/attention `2.6608178049261344x`
- per-layer cleanup sum `0.9268928333333333 s`
- shared forward `0.05525783333333333 s`
- residual unattributed `0.09952548463955764 s`
- accounted share `0.947368373509772` (~94.74%).

Largest transformer components:
- up_proj ~23.36% of profiled transformer compute
- gate_proj ~23.24%
- attention ~22.75%
- down_proj ~22.21%.

Resource telemetry:
- CONTROL min free `19%`, peak swap `2394.75 MB`
- PROFILED min free `24%`, peak swap `2439.38 MB`.

Canonical interpretation:
- cleanup/framework overhead is the largest measured remaining category;
- summed per-layer cleanup is ~`1.1469x` synchronized transformer compute;
- within true compute, MLP is ~`2.66x` attention;
- kernel/runtime tuning should follow cleanup-schedule testing.

Canonical result:
`research/stretch/full-persistent-compute-kernel-attribution-024-result.md`

## Stretch 025 — FULL-PERSISTENT BATCHED CLEANUP — READY

Plan:
`research/stretch/full-persistent-batched-cleanup-comparison-025-plan.md`

Question:
> With all weights persistent, can the transformer-loop cleanup sequence be batched once per 36-layer body instead of repeated after every layer?

CONTROL:
- canonical full-persistent helper
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

BATCHED treatment:
- `scripts/stretch_full_persistent_batched_cleanup_025.py`
- blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`.

Treatment changes one factor only:
- CONTROL: `gc.collect() -> mx.clear_cache() -> gc.collect()` after each of 36 persistent transformer layers;
- BATCHED: remove those 36 per-layer calls and execute the same cleanup sequence once after the transformer body;
- shared-stage cleanup remains unchanged.

Balanced runner:
- `scripts/stretch_full_persistent_batched_cleanup_comparison_025.py`
- blob `5fa702d7236888a55b33031c832ce12c79c0e55a`.

Balanced order:
`CONTROL -> BATCHED -> BATCHED -> CONTROL`.

Primary metric:
pooled target verification rate within the balanced experiment.

Secondary:
- median/mean target block wall
- one-per-body BATCHED cleanup wall
- min free memory
- peak swap
- all inherited exactness/KV/resource gates.

Success:
`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

Failure/incomplete:
`CLEANUP_COMPARISON_INCOMPLETE`

No automatic retry, no cache purge, no post-hoc intermediate cleanup-frequency search.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_batched_cleanup_025.py
python3 -m py_compile scripts/stretch_full_persistent_batched_cleanup_comparison_025.py
python3 scripts/stretch_full_persistent_batched_cleanup_comparison_025.py
```

No download is expected.

## Open questions after Stretch 025

1. Does batching cleanup materially improve controlled target throughput while preserving correctness/resource gates?
2. What is the actual one-per-body cleanup wall after removing 35 redundant cleanup points?
3. Does BATCHED increase memory/swap enough to offset its speed benefit?
4. If BATCHED wins, freeze it as the new canonical target schedule and decide whether to re-profile or move directly to quantized-linear/MLP optimization.
5. If BATCHED is flat/slower, retain per-layer cleanup and move to MLP/quantized-linear work.
6. Newer MLX and real drafter integration remain separate future factors.
