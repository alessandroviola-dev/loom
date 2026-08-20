# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_024_FULL_PERSISTENT_COMPUTE_KERNEL_ATTRIBUTION_FIX2_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate PASS gate.

## Research rules

- Preserve verified models/results and failed scientific/harness runs.
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
- Update this handoff and `ROADMAP.md` after meaningful checkpoints.

## Frozen target/environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Qwen3 geometry:
- hidden size 4096
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

Established:
- layer-addressable safetensors I/O;
- bounded MLX materialization/eviction;
- exact streamed body/full-logit parity;
- persistent BF16 KV;
- materialization/process-I/O attribution;
- persistent transformer hotset mechanism;
- oracle target verification;
- quantized-linear shape dependence under MLX 0.31.2.

Exactness frontier:
- M8 valid numerical parity FAIL;
- q/k/v/o exact through M=9, first divergence M=10;
- gate/up/down exact through M=5, first divergence M=6;
- Stretch 017 confirms M5 exact end-to-end over 15 oracle tokens.

Decision:
**M=5 is the maximum demonstrated exact oracle block under MLX 0.31.2.**

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

- M4 pooled `1.6983236855 token/s`
- M5 pooled `1.8646802766 token/s`
- M5/M4 `1.09795340695x` (~+9.80%).

Decision: freeze M5 as preferred exact block; block-size scaling closed for frozen runtime.

### Stretch 019–022 — transformer residency COMPLETE

Controlled gains:
- H8 -> H16: ~+56.87%
- H16 -> H24: ~+34.86%
- H24 -> H32: ~+11.45%
- H32 -> H36: ~+10.50%.

Stretch 022 valid run `20260820-145851`:
- `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- H32 pooled `2.763691141669756 token/s`
- H36 pooled `3.0539262293580034 token/s`
- H36/H32 `1.105017193604671x`.

H36:
- transformer hotset `3,039,381,504 B`
- hybrid raw-weight budget `3,311,650,816 B`.

Decision:
- H36 is the physical transformer-residency ceiling;
- no H33–H35 search;
- transformer streaming/materialization closed as an optimization axis.

Canonical result:
`research/stretch/m5-h32-h36-balanced-hotset-comparison-022-result.md`

## Stretch 023 — COMPLETE PASS / FULL RAW-WEIGHT PERSISTENCE

Scientific plan:
`research/stretch/m5-h36-shared-stage-persistence-023-plan.md`

### Preserved initial harness defect

Run `20260820-151540`:
**HARNESS DEFECT / NO SCIENTIFIC RESULT**.

Cause: treatment applied `add_shared_persistence()` to wrapper text rather than generated runtime source.

Record:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-defect-20260820-151540.md`

### Valid Fix1 scientific run

Run:
`20260820-153308`

Classification:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

Order:
`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`

Frozen sources:
- H36 STREAMED blob `9111dde483206a774a9fe5426522dab6e77cecca`
- PERSISTENT Fix1 blob `120ad7be2f275559898bf636ca8e8fe039a56c60`
- balanced runner Fix1 blob `dfa4c25b71108e258f4d311a65ae038b45be16dc`.

Controlled result:
- STREAMED pooled `2.2094465476329797 token/s`
- PERSISTENT pooled `3.532597336303855 token/s`
- PERSISTENT/STREAMED `1.5988607373590418x` = ~+59.89%
- STREAMED median block `2.2416415 s`
- PERSISTENT median block `1.416072 s` = ~36.83% lower
- shared-materialization ratio `0.0001720537125220692x`
- shared-forward ratio `0.7076299067105323x`
- full-pass process-read bytes/block ratio `4.009422142033779e-05x`
- shared-materialize process-read ratio `0.0x`.

Full persistence:
- total persistent raw model `3,583,928,320 B`
- mean one-time shared setup `0.3723145 s`
- estimated break-even `0.439246432072825` target blocks.

Resource telemetry:
- STREAMED min free `21%`, peak swap `2335.5 MB`
- PERSISTENT min free `23%`, peak swap `2487.69 MB`.

Decision:
**M5 + H36 + full raw-weight persistence is the best demonstrated target-side architecture under MLX 0.31.2.**

Raw-weight residency is closed: every model weight is persistent.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

## Stretch 024 — FULL-PERSISTENT COMPUTE/KERNEL ATTRIBUTION — FIX2 READY

Original plan:
`research/stretch/full-persistent-compute-kernel-attribution-024-plan.md`

Question:
> Under canonical M5 + H36 + full-weight persistence, which synchronized components dominate the remaining target-block wall?

Frozen Qwen3 block anatomy:
- input RMSNorm -> attention -> residual
- post-attention RMSNorm -> gate_proj + up_proj -> SwiGLU -> down_proj -> residual.

### CONTROL

Canonical full-persistent helper:
`scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`

Blob:
`120ad7be2f275559898bf636ca8e8fe039a56c60`

### Profiling design

Target blocks only receive explicit `mx.eval` timing boundaries for:
1. input norm
2. attention
3. residual 1
4. post-attention norm
5. gate projection
6. up projection
7. SwiGLU
8. down projection
9. residual 2.

Also measured:
- persistent-layer build/reuse wall
- per-layer cleanup (`gc.collect` / `mx.clear_cache`) wall
- transformer materialization/forward telemetry
- shared-stage materialization/forward
- residual/unattributed wall.

Prompt remains unprofiled.

PROFILED throughput is intentionally perturbed and is **not** a canonical speed result. CONTROL/PROFILED rate difference measures instrumentation perturbation only.

### Preserved Stretch 024 Fix1 harness defect

Incomplete run:
`20260820-155313`

Run directory:
`results-local/stretch/full-persistent-compute-kernel-attribution-024-fix1/20260820-155313`

Observed:
- attempt 1 CONTROL completed;
- attempt 2 PROFILED child returned rc `12`;
- classification `COMPUTE_ATTRIBUTION_TELEMETRY_FAIL`;
- failure reason `compute attribution incomplete: NameError: name 'args' is not defined`;
- attempts 3–4 were not run.

Scientific result: **NONE**.

Exact cause:
parent-side compute-attribution aggregation referenced child-local `args.num_hidden_layers` in three geometry expressions.

Preserved record:
`research/stretch/full-persistent-compute-kernel-attribution-024-harness-defect-20260820-155313.md`

No data from this sequence are reused.

### Harness Fix2

Preregistration:
`research/stretch/full-persistent-compute-kernel-attribution-024-harness-fix2.md`

Fix2 replaces only the three invalid parent geometry references with frozen H36 geometry:
`len(HOTSET_LAYER_IDS) == 36`.

Canonical PROFILED Fix2:
`scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py`

Blob:
`83f9e12dfa30445810ca4d39150dbcd151ad3e66`

Lineage preserved:
- base PROFILED blob `b9c233415386ce796a2331cbfd011881b844cb91`
- preflight PROFILED Fix1 blob `845b10da26a70455cd40f483cea5d313f9ac12dd`.

Canonical balanced runner Fix2:
`scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py`

Blob:
`de464c4fe5dca90c2fe110337f12e3f6424ea937`

Runner lineage:
- base runner blob `88ef0115d7b806d52d390fb660c852ff96b9fc84`
- runner preflight Fix1 blob `f298d32f39cbed6410a1d395a735fce819f354f3`.

Balanced order remains:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`

A completely new four-run sequence is required.

Success:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Any constituent/profile failure:
`COMPUTE_ATTRIBUTION_INCOMPLETE`

No auto retry/rescue and no partial component ranking.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py
python3 -m py_compile scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py
python3 scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py
```

No download is expected.

## Open questions after Stretch 024

1. Does MLP or attention dominate synchronized target compute?
2. Within MLP, which of gate/up/down/SwiGLU dominates?
3. Is per-layer cleanup/framework overhead a material fraction of wall?
4. How much target wall remains unattributed after synchronized components, cleanup and shared stages?
5. Does the evidence justify a quantized-linear/MLP kernel experiment, attention/SDPA experiment, or framework-loop cleanup experiment?
6. A newer MLX runtime remains a separate future comparison.
7. Real drafter integration remains separate; current rates are oracle target-verification upper bounds.
