# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_024_FULL_PERSISTENT_COMPUTE_KERNEL_ATTRIBUTION_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- Preserve verified models/results; never silently delete them.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness defects are not model failures.
- Do not weaken numerical/resource gates post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No hidden rescue ladders/retries.
- No deliberate macOS cache purge to manufacture host state.
- Darwin process-I/O counters are diagnostic, not forensic physical-SSD attribution.
- No new large-model download while existing artifacts suffice.
- A newer runtime must be preregistered separately and must not rewrite the frozen baseline.
- Update `HANDOFF.md` and `ROADMAP.md` after meaningful results/decisions.

## Frozen target/environment

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Configuration:
- Qwen3
- hidden size 4096
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

### Stretch 001–017 — architecture and exact block frontier

Established:
- layer-addressable safetensors I/O;
- bounded MLX materialization/eviction;
- exact streamed body/full-logit parity;
- persistent ordinary BF16 KV;
- repeated target-weight traversal/materialization attribution;
- persistent transformer hotset mechanism;
- oracle target verification;
- quantized-linear M/shape dependence under MLX 0.31.2.

Exactness frontier:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M=9, first divergent M=10;
- gate/up/down exact through M=5, first divergent M=6;
- Stretch 017 confirms M5 exact end-to-end across all 36 layers and 15 oracle tokens.

Canonical conclusion:
- **M=5 is the maximum demonstrated exact oracle block under MLX 0.31.2**.

### Stretch 018 — COMPLETE PASS

`M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS`

- M4 pooled `1.6983236855 token/s`
- M5 pooled `1.8646802766 token/s`
- M5/M4 `1.09795340695x` (~+9.80%).

Decision: M5 is the preferred exact target block; block-size scaling is closed for the frozen runtime.

### Stretch 019–022 — transformer-residency curve COMPLETE

Controlled gains:
- H8 -> H16: ~+56.87%
- H16 -> H24: ~+34.86%
- H24 -> H32: ~+11.45%
- H32 -> H36: ~+10.50%.

Stretch 022 valid run `20260820-145851`:
- `M5_H32_H36_BALANCED_HOTSET_COMPARISON_PASS`
- H32 pooled `2.763691141669756 token/s`
- H36 pooled `3.0539262293580034 token/s`
- H36/H32 `1.105017193604671x`
- H36 transformer hotset `3,039,381,504 B`
- H36 hybrid raw-weight budget `3,311,650,816 B`.

Decision:
- H36 is the physical transformer-residency ceiling;
- no H33–H35 rescue search;
- transformer streaming/materialization is closed as an optimization axis.

Result:
`research/stretch/m5-h32-h36-balanced-hotset-comparison-022-result.md`

## Stretch 023 — COMPLETE PASS / FULL RAW-WEIGHT PERSISTENCE

Scientific plan:
`research/stretch/m5-h36-shared-stage-persistence-023-plan.md`

### Preserved harness defect

Initial run `20260820-151540` is **HARNESS DEFECT / NO SCIENTIFIC RESULT**.

Cause:
- original treatment applied `add_shared_persistence()` to wrapper text instead of the generated runtime source;
- it failed before scientific execution with `expected 1 occurrence, found 0`;
- no memory/model conclusion is permitted from that run.

Preserved record:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-defect-20260820-151540.md`

Harness-only fix preregistration:
`research/stretch/m5-h36-shared-stage-persistence-023-harness-fix1.md`

### Valid scientific run

Run:
`20260820-153308`

Classification:
`M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS`

Balanced order:
`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`.

Frozen sources:
- STREAMED H36 blob `9111dde483206a774a9fe5426522dab6e77cecca`
- PERSISTENT fix1 blob `120ad7be2f275559898bf636ca8e8fe039a56c60`
- balanced fix1 runner blob `dfa4c25b71108e258f4d311a65ae038b45be16dc`.

Controlled result:
- STREAMED pooled `2.2094465476329797 token/s`
- PERSISTENT pooled `3.532597336303855 token/s`
- PERSISTENT/STREAMED `1.5988607373590418x` = **~+59.89%**
- STREAMED median block `2.2416415 s`
- PERSISTENT median block `1.416072 s` = **~36.83% lower**
- shared-materialization ratio `0.0001720537125220692x`
- shared-forward ratio `0.7076299067105323x`
- full-pass process-read bytes/block ratio `4.009422142033779e-05x`
- shared-materialize process-read ratio `0.0x`.

Full persistence:
- transformer H36 `3,039,381,504 B`
- full persistent raw model `3,583,928,320 B`
- mean one-time shared setup `0.3723145 s`
- estimated setup break-even `0.439246432072825` target blocks.

Resource telemetry:
- STREAMED min free `21%`, peak swap `2335.5 MB`
- PERSISTENT min free `23%`, peak swap `2487.69 MB`.

Canonical decision:
- **M5 + H36 + full raw-weight persistence is the best demonstrated target-side architecture under MLX 0.31.2**;
- raw-weight residency is now fully closed: every model weight is persistent;
- remaining target cost must be attributed to compute/kernel/framework work rather than further weight residency.

Canonical result:
`research/stretch/m5-h36-shared-stage-persistence-023-result.md`

## Stretch 024 — FULL-PERSISTENT COMPUTE/KERNEL ATTRIBUTION — READY

Plan:
`research/stretch/full-persistent-compute-kernel-attribution-024-plan.md`

Question:
> Under canonical M5 + H36 + full-weight persistence, which synchronized components dominate the remaining target-block wall?

Exact upstream component anatomy is frozen to `mlx-lm v0.31.3` Qwen3:
- input RMSNorm -> attention -> residual
- post-attention RMSNorm -> gate_proj + up_proj -> SwiGLU -> down_proj -> residual.

### CONTROL

Canonical Stretch 023 full-persistent helper:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

### PROFILED

Base profiling helper, superseded during preflight before any run:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled.py`
- blob `b9c233415386ce796a2331cbfd011881b844cb91`.

Canonical PROFILED entrypoint:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py`
- blob `845b10da26a70455cd40f483cea5d313f9ac12dd`.

It adds explicit `mx.eval` boundaries on the three target blocks only for:
- input norm
- attention
- residual 1
- post-attention norm
- gate projection
- up projection
- SwiGLU
- down projection
- residual 2.

It also times persistent-layer build/reuse and cleanup paths. Prompt remains unprofiled.

### Balanced runner

Base runner, superseded during preflight before any run:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024.py`
- blob `88ef0115d7b806d52d390fb660c852ff96b9fc84`.

Canonical runner:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py`
- blob `f298d32f39cbed6410a1d395a735fce819f354f3`.

Balanced order:
`CONTROL -> PROFILED -> PROFILED -> CONTROL`.

Success classification:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`.

Any constituent/profile failure:
`COMPUTE_ATTRIBUTION_INCOMPLETE` with no automatic retry/rescue.

### Interpretation discipline

PROFILED uses explicit synchronization boundaries and therefore perturbs MLX scheduling/fusion/laziness.

Consequently:
- PROFILED token/s is **not** a production/canonical speed result;
- CONTROL vs PROFILED speed is instrumentation-overhead telemetry only;
- the scientific output is component ranking/share plus attention-vs-MLP, cleanup/shared, and residual overhead attribution;
- all profiled constituents must still pass inherited exactness and resource gates.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_compute_attribution_024_profiled.py
python3 -m py_compile scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py
python3 -m py_compile scripts/stretch_full_persistent_compute_kernel_attribution_024.py
python3 -m py_compile scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py
python3 scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py
```

No download is expected.

## Open questions after Stretch 024

1. Does MLP or attention dominate synchronized target compute?
2. Within MLP, which of gate/up/down/SwiGLU is the largest measured component?
3. Is per-layer GC/cache-clear cleanup a material fraction of target wall after full persistence?
4. How much target wall remains residual/unattributed after synchronized components, cleanup and shared stages?
5. Does attribution justify a quantized-linear/kernel experiment, an attention experiment, or a framework-loop cleanup experiment next?
6. A newer MLX runtime remains a separate future environment comparison, not part of Stretch 024.
7. Real drafter integration remains separate; current target rates are oracle upper-bound verification rates.
