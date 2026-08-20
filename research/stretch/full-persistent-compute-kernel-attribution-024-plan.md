# LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution — Preregistered Plan

Status: **READY / NOT YET RUN**

## Question

After Stretch 023 removed raw-weight residency as an optimization axis, what dominates the remaining M5/H36/full-persistent target-block wall under the frozen MLX 0.31.2 runtime?

Stretch 024 is an **instrumentation experiment**, not an optimization experiment.

## Canonical architecture

Frozen from Stretch 023:
- Apple M1 / 8 GB reference machine;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- exact oracle block size `M=5`;
- H36 transformer hotset, layers `0..35`;
- embedding + final RMSNorm + LM head persistent;
- full raw model payload persistent: `3,583,928,320 B`;
- ordinary BF16 KV;
- three target blocks / 15 accepted oracle tokens per constituent run;
- exact numerical/top-1 policy;
- inherited host/resource/I-O gates;
- no tokenizer, sampling, real drafter, KV quantization, runtime upgrade, prefetch or deliberate cache purge.

Canonical Stretch 023 treatment source:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

## Frozen upstream anatomy

The component boundaries follow the exact `mlx-lm v0.31.3` Qwen3 implementation.

`TransformerBlock` order:
1. input RMSNorm;
2. self-attention;
3. first residual add;
4. post-attention RMSNorm;
5. MLP;
6. second residual add.

Qwen3 MLP order:
1. `gate_proj`;
2. `up_proj`;
3. SwiGLU;
4. `down_proj`.

Reference source:
`ml-explore/mlx-lm`, tag `v0.31.3`, `mlx_lm/models/qwen3.py`.

Stretch 024 does not change module parameters, tensor shapes, cache semantics or arithmetic definitions.

## Instrumentation factor

Two variants only:

### CONTROL

Canonical Stretch 023 full-persistent target with no new component evaluation boundaries.

### PROFILED

Same architecture, but the **three M=5 target blocks only** receive explicit `mx.eval` boundaries after the following transformer components:
- input RMSNorm;
- self-attention total;
- first residual add;
- post-attention RMSNorm;
- `gate_proj`;
- `up_proj`;
- SwiGLU;
- `down_proj`;
- second residual add.

The prompt remains on the canonical unprofiled path.

PROFILED also times the existing per-layer:
- persistent-block lookup/build-reuse wall;
- parameter-materialization wall;
- cleanup wall (`gc.collect` / `mx.clear_cache` path).

Shared persistent embedding/final-norm/LM-head materialization and forward walls remain measured by the inherited Stretch instrumentation.

## Measurement caveat

Explicit `mx.eval` boundaries deliberately perturb MLX scheduling/fusion/laziness.

Therefore:
- PROFILED token/s is **not** a canonical performance result;
- CONTROL vs PROFILED rate/wall is recorded only to quantify instrumentation perturbation;
- component wall shares/ranking are interpreted as synchronized attribution evidence, not as proof that an uninstrumented kernel consumes the identical absolute wall time;
- no optimization winner is selected from CONTROL vs PROFILED.

## Frozen sources

Initial attribution helper, superseded during preflight before any run:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled.py`
- blob `b9c233415386ce796a2331cbfd011881b844cb91`.

The initial helper was never executed scientifically. A source-edit anchor for cycle telemetry was ambiguous and was corrected before preregistration.

Canonical PROFILED entrypoint:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py`
- blob `845b10da26a70455cd40f483cea5d313f9ac12dd`.

Initial balanced runner, superseded during preflight before any run:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024.py`
- blob `88ef0115d7b806d52d390fb660c852ff96b9fc84`.

Its only preflight issue was a consumer field name for slowest-layer candidates.

Canonical balanced runner:
- `scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py`
- blob `f298d32f39cbed6410a1d395a735fce819f354f3`.

These preflight fixes are harness-only and occurred before Stretch 024 execution; no scientific data were observed while designing them.

## Balanced order

`CONTROL -> PROFILED -> PROFILED -> CONTROL`

No automatic retry. No deliberate cache purge between constituents.

## Required constituent gates

Every CONTROL and PROFILED run must independently:
- return code 0;
- reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
- retain exact H36 layer IDs `0..35`;
- retain full persistent raw weights near `3,583,928,320 B` within the frozen accounting tolerance;
- retain `M=5`;
- accept all 15 oracle tokens;
- pass exact position-logit/top-1 gates;
- remain inside inherited host/resource limits.

PROFILED additionally must expose:
- exactly `108` target layer profiles = 3 target blocks x 36 layers;
- exactly three block attribution summaries;
- build-reuse and cleanup timing for all 36 layer cycles in each target block.

Any failure => `COMPUTE_ATTRIBUTION_INCOMPLETE`; stop with no attribution conclusion and no automatic rescue.

## Primary attribution outputs

Across the two PROFILED constituents / six M5 target blocks:
- mean wall per transformer component;
- component share of synchronized profiled transformer compute;
- ranked component list;
- mean attention-path wall;
- mean MLP-path wall;
- MLP/attention-path ratio;
- mean persistent-layer build/reuse wall;
- mean persistent-layer cleanup wall;
- mean shared-stage forward wall;
- mean shared-stage materialization wall;
- mean residual/unattributed wall;
- accounted share of PROFILED full block wall;
- slowest layer candidates among the top-eight exported by each PROFILED constituent.

## Instrumentation-perturbation outputs

Balanced CONTROL and PROFILED results also report:
- pooled target-verification rate;
- median target block wall;
- PROFILED/CONTROL rate ratio;
- PROFILED/CONTROL median block-wall ratio.

These are **measurement-overhead diagnostics only**.

## Success classification

If all four constituents and attribution gates pass:

`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

This classification means the component profile is valid under the declared synchronized instrumentation. It does not promote PROFILED as a production execution path.

## Interpretation policy

1. If MLP dominates, prioritize quantized-linear/MLP kernel or runtime work as the next independent factor.
2. If attention dominates, prioritize attention/SDPA path work.
3. If cleanup/framework residual is large, test removal/restructuring of per-layer GC/cache-clear work as a separate controlled factor before changing numerical kernels.
4. If the shared forward path remains material, isolate embedding/head compute separately.
5. Do not change MLX version inside Stretch 024.
6. A newer MLX runtime, if justified by the attribution, must be a separately preregistered environment comparison against the frozen 0.31.2 architecture.
7. Real speculative-drafter integration remains separate; Stretch 024 is still target-side oracle verification.

## Exact run command

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_full_persistent_compute_attribution_024_profiled.py
python3 -m py_compile scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py
python3 -m py_compile scripts/stretch_full_persistent_compute_kernel_attribution_024.py
python3 -m py_compile scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py
python3 scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py
```

No model download is expected.
