# LOOM — Project Handoff

Last updated: 2026-08-20
Status: ACTIVE — Apple M1 / 8 GB reference system
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Current branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STRETCH_036_PERSISTENT_DEQUANTIZED_PROJECTION_FEASIBILITY_NO_GO`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**

Interactive promotion target: approximately **20 token/s**. This is a promotion target, not an intermediate scientific PASS gate.

## Research rules

- One scientific factor at a time.
- Preserve PASS, scientific FAIL and harness/setup defects.
- No post-hoc gate weakening, hidden rescue ladders or automatic retries.
- Runtime abort where inherited: free memory <5% OR swap >5600 MB.
- Launch gate where preregistered: free memory >=60%, swap <=5600 MB.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- No deliberate macOS cache purge to manufacture host state.
- Never dereference a virtualenv `bin/python` path before subprocess execution; preserve the venv launcher path and validate environment identity through `sys.prefix`/package metadata.
- Balanced within-experiment ratios are causal evidence; absolute cross-experiment throughput is host/cache-state dependent.
- Runtime/model upgrades are separately preregistered and never rewrite historical evidence.
- Update HANDOFF and ROADMAP after meaningful checkpoints.

## Frozen model / preferred runtime

Model:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Qwen3:
- hidden 4096
- 36 layers
- vocab 151936
- 32 attention heads / 8 KV heads / head dim 128
- RMSNorm eps 1e-6
- untied embedding/head
- 3-bit/group64 affine quantization.

Preferred runtime after Stretch 030:
- mlx 0.31.2
- mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Python 3.13.0.

Canonical MLX venv:
`results-local/mlx/venv-mlx-lm-0.31.3`

Raw weights:
- total `3,583,928,320 B`
- transformer body `3,039,381,504 B`
- each layer `84,427,264 B` / 25 tensors
- embedding `272,269,312 B`
- final RMSNorm `8,192 B`
- LM head `272,269,312 B`.

Ordinary BF16 KV remains frozen.

## Canonical Stretch evidence

### Stretch 001–017 — exact block frontier

Established layer-addressable I/O, streamed/full parity, persistent BF16 KV, persistent hotsets and oracle verification.

MLX 0.31.2 exactness frontier:
- M8 valid numerical-parity FAIL;
- q/k/v/o exact through M9, first divergence M10;
- gate/up/down exact through M5, first divergence M6;
- M5 exact end-to-end over 15 oracle tokens.

Decision: M5 is the maximum demonstrated exact oracle block under MLX 0.31.2, but not necessarily the throughput-optimal block size after later framework optimizations.

### Stretch 018 — M4/M5 cost — COMPLETE PASS

- M5/M4 `1.09795340695x` (~+9.80%).

This comparison predates full persistence and cleanup schedule optimization.

### Stretch 019–022 — transformer residency — COMPLETE

Controlled gains:
- H8 -> H16 ~+56.87%
- H16 -> H24 ~+34.86%
- H24 -> H32 ~+11.45%
- H32 -> H36 ~+10.50%.

Decision: H36 is the physical transformer-residency ceiling.

### Stretch 023 — full raw-weight persistence — COMPLETE PASS

Valid Fix1 `20260820-153308`:
- PERSISTENT/STREAMED `1.5988607374x` (~+59.89%).

Decision: freeze H36 + full persistence.

### Stretch 024 — compute/framework attribution — COMPLETE PASS

Valid Fix2 `20260820-160140`:
- transformer compute `0.8081826820 s/block`
- attention `0.2207656117 s/block`
- MLP `0.5874170703 s/block`
- old per-layer cleanup `0.9268928333 s/block`.

Decision: cleanup/framework first.

### Stretch 025–027 — cleanup schedule — COMPLETE

025:
- BATCHED/CONTROL `3.8627785715x` (~+286.28%).

026:
- SHARED_BATCHED/BATCHED `1.1410704391x` (~+14.11%).

027 valid `20260820-163715`:
- SINGLE_PASS/SHARED_BATCHED `1.0867142144x` (~+8.67%)
- pooled `12.7306853225 token/s`
- median block `0.396305 s`.

Decision: freeze **H36 + full persistence + one final cleanup/pass**.

Canonical Stretch 027 workload:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`
blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`.

### Stretch 028 — compute re-attribution — COMPLETE PASS

Valid `20260820-164802`:
- transformer compute `0.4496960012 s/block`
- attention path `0.1231006118 s/block`
- MLP path `0.3265953895 s/block`
- MLP/attention `2.6530769000x`
- up/attention/gate/down each ~0.095–0.099 s/block
- accounted wall ~93.95%.

Decision: true transformer compute is primary target.

### Stretch 029 — gate+up quantized fusion — COMPLETE PASS / NOT PROMOTED

Initial `20260820-170503`: wrapper harness defect / no science.

Valid Fix1 ABBA `20260820-171714`:
- CONTROL `13.2286272786 token/s`
- FUSED `12.3523991241 token/s`
- FUSED/CONTROL `0.9337627302x` (~6.62% slower)
- FUSED exact at M5
- median wall ~8.62% higher.

Decision: fusion path closed under MLX 0.31.2; no rescue variants.

Result:
`research/stretch/gate-up-quantized-fusion-029-result.md`

### Stretch 030 — coherent MLX 0.31.2 vs 0.32.0 — COMPLETE PASS / 0.32.0 NOT PROMOTED

Preserved pre-science defects:
1. original setup used shell Python instead of canonical LOOM venv;
2. runner Fix1 required a nonexistent failure-class string;
3. runner Fix2 dereferenced macOS venv `bin/python` symlinks with `.resolve()` and lost venv identity.

All three occurred before a valid scientific constituent and have scientific result NONE.

Setup Fix1 successfully created and validated treatment clone:
`.venvs/stretch030-mlx0320-fix1`

Treatment clone:
- mlx 0.32.0
- mlx-metal 0.32.0
- mlx-lm 0.31.3
- transformers 5.12.1
- numpy 2.5.2
- safetensors 0.8.0
- Python 3.13.0.

Valid Fix3 ABBA `20260820-175251`:
`MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`

Metrics:
- MLX0312 pooled `13.074823729584752 token/s`
- MLX0320 pooled `12.341753014370326 token/s`
- MLX0320/MLX0312 `0.9439326502310171x` (~5.61% slower)
- MLX0312 median block `0.3795345 s`
- MLX0320 median block `0.405476 s`
- median wall ratio `1.068350835036077x` (~6.84% higher)
- final cleanup mean `0.0554298333 s` vs `0.0636248333 s`
- minimum free memory `17%` vs `22%`
- peak swap `2801.88 MB` vs `2809.25 MB`.

Interpretation:
- MLX 0.32.0 is exact/admissible at frozen M5;
- it is slower on the M1 reference system;
- memory capacity is not the limiting difference.

Decision:
- retain coherent mlx/mlx-metal 0.31.2;
- do not remap M under 0.32.0 because the preregistered `exact + faster` condition was not met;
- preserve treatment venv for audit only.

Result:
`research/stretch/mlx-0312-0320-runtime-comparison-030-result.md`

## Stretch 031 — M2 vs M5 on current SINGLE_PASS schedule — COMPLETE PASS

### Checkpoint 20260820-182206

Objective remains a fresh, valid `M5 -> M2 -> M2 -> M5` comparison at common ten-token depth. Scientific result: **NONE**; no constituent reached numerical/top-1/oracle gates and no measurement is reusable.

The original failed run `20260820-180652` is preserved as a source-transform failure: its M5 geometry callback searched for a nonexistent final-source Stretch 027 summary literal. Fix1 preserved the originals, corrected that anchor, and added local final-source rendering/preflight. Fix1 preflight passed for both sides: M5 rendered SHA-256 `413af14cb19bc4b7c28110d78289080747ba46887c4b7a6bc885086cef0a4b69`; M2 `d09c6498c7bef6d8b7f80e501513cc0cf600ccd38d1dfb019d717acbf58b5b58`; normalized source equality proved geometry is the only scientific difference. It also confirmed the actual model-child interpreter path and versions: MLX `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`.

The fresh Fix1 ABBA `20260820-182206` then stopped at M5 before model work: the inherited parent derived its child executable script from `__file__`, but the new common-module shim supplied its own path. The canonical child executed that import-only module, exited `0`, and produced no child final/state payload. Parent classification is `SINGLE_PASS_M2_M5_GEOMETRY_COMPARISON_INCOMPLETE`; M5 child classification is `RUNTIME_FAIL`. Host gate metrics were free memory `71%` minimum and swap `1258.81 MB` peak. This is harness-only. No retry occurred.

Decision: preserve both failures and stop. Modified/created Fix1 files and exact evidence are recorded in `research/stretch/single-pass-m2-m5-geometry-comparison-031-harness-defect-20260820-180652.md`. Open problem: preflight must validate concrete final parent/child dispatch, not only rendered source/interpreter availability.

### Fix2 preflight checkpoint 20260820-183232

Fix2 created distinct shims, common harness and runner with explicit launcher-path propagation, rendered-source facts and a no-model parent/child marker contract. All Fix2 Python files passed `py_compile`; M5 and M2 source rendering/compilation and normalized geometry-only diff passed. The required M5 dispatch preflight then failed **before any model load**: `dispatch_preflight()` resolved the canonical venv `bin/python` symlink to framework Python (`/Library/Frameworks/.../python3.13`), so the child could not find `mlx` metadata and did not create its marker. Evidence: `results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix2/preflight/20260820-183232/` and `research/stretch/single-pass-m2-m5-geometry-comparison-031-fix2-amendment.md`.

Scientific result remains **NONE**. No ABBA began, no measurement was created/reused, and no retry occurred. Next exact step: preserve this checkpoint; create a distinct dispatch revision preserving the literal venv `bin/python` path (no `.resolve()`), then require fresh M5 **and** M2 no-model marker PASS before a new ABBA.

### Fix3 and valid ABBA checkpoint 20260820-184128

Fix3 preserved the literal canonical venv launcher, added a static venv-dereference regression guard, and added no-model M5/M2 parent-to-child markers. The preflight `20260820-184109` passed rendered M5/M2 source facts, normalized geometry-only diff, canonical `sys.prefix` and runtime metadata (mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`), and both marker paths with `model_loaded=false` and `target_compute_executed=false`.

Fresh ABBA `M5 -> M2 -> M2 -> M5` completed at `results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix3/20260820-184128/summary.json`: all four constituents were exact, accepted ten tokens, retained H36/full persistence/single cleanup, and passed resources. Scientific result: `SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS`. M5 pooled `14.3307127237 tok/s`; M2 `11.8349427869 tok/s`; M2/M5 `0.8258446747`; wall/token `0.06978020` vs `0.08449555`; median block `0.3487060 s` vs `0.1672135 s`; cleanup/token `0.0091132 s` vs `0.0169262 s`; minimum free memory `18%` vs `24%`; peak swap `2068.12` vs `2083.69 MB`.

Decision: M5 wins and remains canonical geometry. M2 is not rescued and no optimum claim is made. Fix2 failure `20260820-183232` remains harness-only evidence; all prior failed attempts remain unused. Files/result: `research/stretch/single-pass-m2-m5-geometry-comparison-031-fix3-amendment.md` and `research/stretch/single-pass-m2-m5-geometry-comparison-031-result.md`. Next exact step: do not rerun geometry; prepare a separately preregistered independent compute-factor experiment.

## Stretch 032 candidate — M5 row-chunked quantized matmul feasibility — NO-GO

Diagnostic only; no Stretch 032 plan, source transform, preflight, or ABBA was created. The real layer-0 Qwen3-8B 3-bit affine weights were measured under the canonical venv with M5 BF16 inputs. CONTROL was one M5 `mx.quantized_matmul`; TREATMENT was `2+2+1` qmatmuls plus concatenate. Each projection had 40 excluded warmups and 120 synchronized samples per side interleaved `CONTROL -> CHUNKED -> CHUNKED -> CONTROL`, with no deliberate cache purge.

All q/k/v/o/gate/up/down outputs were bit-exact (`max_abs_diff=mean_abs_diff=0`) and shapes matched, but chunked/monolithic median ratios were all slower: q `1.062675`, k `1.178569`, v `1.186259`, o `1.091189`, gate `1.061970`, up `1.068221`, down `1.061597`. Applying only the matching Stretch 028 MLP component telemetry estimates a `-0.0185683 s/block` loss, `-5.3249%` of the valid Stretch 031 M5 median block wall. Even the explicitly optimistic attention-inclusive bound is negative (`-8.9908%`).

Classification: `STRETCH_032_ROW_CHUNKED_FEASIBILITY_NO_GO`. M5 monolithic qmatmul remains canonical. Do not retry this measurement, do not try `1+1+...` or `3+2`, and do not launch an ABBA; each alternative is a separate factor. Artifact: `research/stretch/m5-row-chunked-quantized-matmul-032-feasibility.md`; evidence: `results-local/stretch/m5-row-chunked-quantized-matmul-032-feasibility/20260820-185103/summary.json`. Next exact step: select and separately preregister a new independent compute factor.

## Stretch 033 candidate — outer `mx.compile` MLP feasibility — NO-GO

Diagnostic only; no Stretch 033 plan, scientific source transform, preflight, or ABBA was created. Under the literal canonical venv and real 3-bit/group64 layer-0 payloads, the pure Qwen3 MLP expression was compared as eager outer graph versus `mx.compile(..., inputs=layer0)` with immutable weight trees captured. M5 BF16 input, monolithic qmatmuls and no cache purge were retained. The installed mlx-lm `swiglu` is itself `@partial(mx.compile, shapeless=True)`; the factor is only the proposed outer MLP compile.

First compiled invocation plus eval was `0.2991603 s` (factory call `0.0000068 s`); excluded warmup median was `0.0056032 s`. The 120-side interleaved steady benchmark was exact (`max_abs=mean_abs=0`): eager `5.9251 ms`, compiled `5.9132 ms`, ratio `0.9979923`. A three-real-MLP sequence was also exact and flat: `16.7317` vs `16.7314 ms`, ratio `0.9999800`. Fixed callable/input/weight identity and no second compile-scale timed outlier are the available MLX 0.31.2 reuse evidence; no public compilation counter exists.

Stretch-028-weighted diagnostic saving is only `0.0006557 s/block`, `0.1880%` of the valid Stretch-031 M5 median block wall, far below 5%. Classification: `STRETCH_033_COMPILED_MLP_FEASIBILITY_NO_GO`. Keep canonical outer eager MLP / monolithic M5 qmatmul; do not create an ABBA or rescue this factor. Artifact: `research/stretch/m5-compiled-mlp-033-feasibility.md`; evidence: `results-local/stretch/m5-compiled-mlp-033-feasibility/20260820-190058/summary.json`. Next exact step: select a different independently preregistered compute factor.

## Stretch 034 candidate — fused residual add + RMSNorm feasibility — NO-GO

Diagnostic only; no Stretch 034 scientific runner, preregistration, source transform, preflight, or ABBA was created. Under the literal canonical MLX 0.31.2 venv, actual Qwen3 BF16 layer-0 `input_layernorm` and `post_attention_layernorm` weights and final model norm all confirmed shape `[4096]`, dtype BF16. The control was the already canonical `h = x + r; n = mx.fast.rms_norm(h, weight, 1e-6)` with both outputs evaluated. The treatment was one custom `mx.fast.metal_kernel`, specialized to BF16 `[1,5,4096]`, producing both raw `h` and normalized `n`; it used FP32 accumulation, a 256-thread row reduction and `metal::rsqrt` with unchanged `1e-6`.

Three controlled random BF16 seeds with both actual layer norm vectors produced bit-exact `h`; normalized output was reduction-order non-bit-exact but diagnostically compatible (worst max/mean absolute difference `0.00390625 / 0.0001372101`, within predeclared `0.03125 / 0.0009765625`). One custom kernel object/fixed BF16 template was reused; factory cost was `0.0430 ms`, first dispatch plus eval `101.4082 ms`, and excluded fused warmup median `270.854 µs`.

The 120-sample-per-side synchronized mirrored benchmark found control pair `245.31 µs` and fused pair `276.10 µs`: fused/control `1.1255195`, a `30.7915 µs` loss per pair. Add alone was `212.52 µs`; canonical `mx.fast.rms_norm` alone was `231.69 µs`. Active/peak diagnostic memory was `516,112 / 663,568 B`. The conditional two-pair layer pattern was also slower: control `240.10 µs`, fused `265.79 µs`, ratio `1.1069828`.

There are 36 simple intra-layer opportunities, 35 cross-layer scheduling opportunities and one potential final pair; layer-0 input norm remains standalone. Applying the measured loss to Stretch 031’s `0.3487060 s` M5 median block gives intra-only `-1.10849 ms/block` (`-0.31789%`), intra+cross `-2.18620 ms/block` (`-0.62695%`), and optimistic +final `-2.21699 ms/block` (`-0.63578%`). Cross-layer use would require exposing each final raw residual and restructuring `Qwen3Model` scheduling; it was not implemented and the measured loss does not justify it.

Decision: `STRETCH_034_FUSED_RESIDUAL_RMSNORM_FEASIBILITY_NO_GO`. Keep separate residual add + canonical `mx.fast.rms_norm`; do not create an ABBA or rescue variant. Artifact: `research/stretch/fused-residual-rmsnorm-034-feasibility.md`; evidence: `results-local/stretch/fused-residual-rmsnorm-034-feasibility/20260820-201000/summary.json`.

## Stretch 035 — M5 quantized kernel-path investigation — INVESTIGATION_ONLY

No scientific ABBA, source transform, MLX patch, venv modification, or runtime comparison was created. Exact upstream MLX `v0.31.2` source (`68cf2fddd8de5edd8ab3d926391772b2e2cedad8`) plus `mx.device_info()` establishes the canonical M1 as `applegpu_g13g`: generation 13, size `g`. At affine BF16/group64/3-bit M5, all layer-0 q/k/v/o/gate/up/down projections follow `QuantizedMatmul::eval_gpu -> dispatch_qmv -> qmv`; all satisfy the fast predicate `N % 8 == 0 && K % 512 == 0` and dispatch concrete `affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0`. The gen13/size-g vector limit is 10 for q/k/v/o and 6 for gate/up/down, so M5 remains qmv_fast; qmv_quad, qmm and split-K do not apply at M5.

The 100-sample-per-shape real-payload BF16 M1–M8 map confirms source-predicted M6 discontinuities only for gate/up (qmm) and down (split-K). M5 medians were q `1533.38 µs`, k `675.31`, v `731.48`, o `1527.06`, gate `2197.58`, up `2195.92`, down `2145.69`. The installed 0.31.2 metallib contains the exact qmv_fast plus fallback qmm/split-K symbols; MLX exposes no public per-dispatch symbol log.

MLX `v0.32.0` adds qmv_wide, but its literal affine gate is `architecture_gen >= 15`; M1 gen13 cannot select it and would continue to select old qmv/qmv_fast at M5. Thus source does not explain Stretch 030’s `0.94393` end-to-end 0.32/0.31 ratio: qmv_wide is unreachable, while other runtime changes exist. PR #3764 reports no M1/3-bit case; its affine M2-Pro row remains qmv. Issues #3553/#3839/#3852 supply M4/M3/M1-Pro mixed 4-bit/2-bit or group-size-different motivation only, not transfer proof.

No isolated prototype was justified or benchmarked. Upstream explicitly says affine qmv_wide only beats qmv on gen15+, but that does not disprove every theoretical M1-specific future kernel. Therefore `STRETCH_035_KERNEL_PATH_INVESTIGATION_ONLY`: no numerical/timing treatment or defensible weighted >=5% estimate exists. Keep monolithic canonical M5 `mx.quantized_matmul`; any custom M1 kernel needs fresh explicit authorization and a separately preregistered correctness-first feasibility factor. Artifact: `research/stretch/m5-quantized-kernel-path-035-investigation.md`; evidence: `results-local/stretch/m5-quantized-kernel-path-035/20260820-202259/summary.json`.

## Stretch 036 — persistent dequantized BF16 projection feasibility — NO-GO

Diagnostic only; no scientific plan, source transform, 36-layer cache, or full-model ABBA was created. Under the literal canonical MLX 0.31.2 venv, real layer-0 Qwen3 3-bit/group64 affine packed tensors were dequantized only with `mx.dequantize(packed, scales, biases, group_size=64, bits=3)`, materialized/persisted BF16 one projection at a time, and compared to canonical M5 `mx.quantized_matmul`. No original floating-point weights, requantization, scale/bias change, cache purge, or full-model cache was used.

All seven BF16 dense outputs had matching shapes but were non-bit-exact for all three deterministic BF16 probes; no compatibility threshold was invented. Median BF16/quantized ratios were q `0.979333`, k `1.034484`, v `1.035620`, o `0.933584`, gate `1.869357`, up `1.867642`, down `1.273514`. Direct x36 arithmetic gives Q `+0.2688%`, O `+1.0677%`, Q+O `+1.3365%`; K/V and all MLP classes are slower. Conservative BOTH-resident BF16 cache cost is Q/O `1,152 MiB` each, K/V `288 MiB` each, MLP `3,456 MiB` each. Linear diagnostic use of the observed Stretch-031 18% minimum free memory projects Q/O to `3.94%`, below the historical 5% abort; Q+O projects `-10.12%`. The largest positive arithmetic candidate is therefore both below the 5% upside gate and memory-risky.

Classification: `STRETCH_036_PERSISTENT_DEQUANTIZED_PROJECTION_FEASIBILITY_NO_GO`. Retain canonical monolithic M5 affine quantized matmul. Do not create a Stretch-036 scientific preregistration or ABBA. Artifact: `research/stretch/persistent-dequantized-projection-036-feasibility.md`; evidence: `results-local/stretch/persistent-dequantized-projection-036-feasibility/20260820-205800/summary.json`.

## Exact next step

Do not retry or rescue persistent dequantized BF16 caches from this feasibility result. Select a new independently authorized compute factor while preserving the canonical M5 monolithic 3-bit/group64 affine `mx.quantized_matmul`, H36, full raw-weight persistence, single final cleanup, MLX/mlx-metal 0.31.2, and BF16 KV.

### Historical Stretch 031 rationale

The old Stretch 018 M4/M5 result predates H36 full persistence and the large cleanup-frequency reductions. Therefore the throughput-optimal block geometry must be rechecked on the current schedule.

Upstream MLX performance reports indicate nonlinear quantized-matmul cost in the small-M range, including a low-cost M2 region before a higher-cost M3+ region. This is motivation only; the M1 result must be measured locally.

### Scientific question

At identical 10-token oracle continuation depth, is M2 faster per accepted token than M5 on the preferred MLX 0.31.2 architecture?

### Common frozen depth

Oracle prefix in both variants:
`[1,374,264,4647,1483,304,279,1809,315,5994]`

CONTROL:
- M5
- 2 target blocks
- 10 accepted oracle tokens.

TREATMENT:
- M2
- 5 target blocks
- 10 accepted oracle tokens.

Frozen besides block size:
- Qwen3-8B 3-bit/group64
- MLX 0.31.2 + mlx-metal 0.31.2
- mlx-lm 0.31.3
- H36
- full raw-weight persistence
- one final cleanup/pass
- BF16 KV
- exactness/top-1/acceptance/resource/I-O gates
- no cache purge.

Geometry callback is applied only after inherited Stretch 017/H36 source-provenance checks pass.

M5 helper:
`scripts/stretch_single_pass_m5_ten_token_control_031.py`
blob `5f047b9e5f42bed959ced59e9329a8c8d7e3fc25`.

M2 helper:
`scripts/stretch_single_pass_m2_ten_token_variant_031.py`
blob `6005ff3a285760457d3255bc6505f2987c1fa4e8`.

Balanced runner:
`scripts/stretch_single_pass_m2_m5_geometry_comparison_031.py`
blob `bc3b21ff504c65d0852aad68a566cba924888d90`.

Plan:
`research/stretch/single-pass-m2-m5-geometry-comparison-031-plan.md`

Balanced order:
`M5 -> M2 -> M2 -> M5`.

Primary metric:
pooled accepted oracle tokens / total target-block wall seconds.

Outcome policy:
- first genuine M2 numerical/top-1/oracle failure => `M2_SINGLE_PASS_GEOMETRY_EXACTNESS_FAIL`, valid scientific FAIL, stop/no rescue;
- complete exact ABBA => `SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS`;
- harness/resource/provenance failure => `SINGLE_PASS_M2_M5_GEOMETRY_COMPARISON_INCOMPLETE`.

If M2 wins, do not declare global optimum; separately compare M2 vs M3 at common depth. If M5 wins, retain M5 and move to another compute factor.

## Exact next step

Do **not** rerun Stretch 031 geometry, Stretch 032 row chunking, Stretch 033 outer MLP compile, Stretch 034 fused residual/RMSNorm, Stretch 036 persistent dequantized BF16 projection caching, or a 0.32 full-runtime comparison. Preserve M5 monolithic qmv_fast affine quantized matmul and canonical separate residual add + `mx.fast.rms_norm`; select a different independently authorized compute factor before any scientific run, retaining the venv-launcher regression guard.

## Other track

Amplify remains queued behind Stretch:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`.
