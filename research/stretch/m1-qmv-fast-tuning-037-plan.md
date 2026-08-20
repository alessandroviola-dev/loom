# Stretch 037 — M1-specific qmv_fast treatment — PREREGISTRATION

Date: 2026-08-20
Status: **READY FOR HUMAN REVIEW — no treatment integration or ABBA has run.**

## Scientific question

On the frozen M1 `applegpu_g13g` architecture, can replacing only eligible canonical M5 affine BF16/3-bit/group64 qmv_fast projection execution with the Stretch-037 `s1_r8` isolated Metal implementation preserve every inherited oracle gate and improve target-verification throughput?

## Motivation and single-factor evidence

Stretch-037 feasibility used the exact MLX v0.31.2 source specialization and real layer-0 Qwen3 payloads. Its canonical clone was bit-exact in all 21 direct comparisons and had worst clone/canonical median `1.006870`. The predeclared `s1_r8` treatment (one SIMD group/threadgroup, eight output rows/SIMD) was bit-exact in all 21 direct comparisons and improved gate/up/down medians by `6.52%`, `5.96%`, and `6.32%`. Matched Stretch-028 MLP telemetry projects `5.2120%` of the valid Stretch-031 M5 median block wall; the optional attention-inclusive bound is `6.0239%`.

This is admission evidence only. Full-model performance, oracle parity, resource behavior and scheduling additivity remain unproven.

## Frozen architecture

Both sides retain without exception:

- Qwen3-8B 3-bit affine/group64 checkpoint and its existing packed weights/scales/biases;
- M5 geometry, H36, full raw-weight persistence, one final cleanup/pass and ordinary BF16 KV;
- mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`, literal canonical launcher;
- canonical prompt/oracle workload, exact numerical/top-1/acceptance/resource/I-O gates and abort rules;
- no cache purge, runtime upgrade, model download, weight conversion, requantization or persistent BF16 cache.

## CONTROL

The current canonical source path with monolithic `mx.quantized_matmul`, which selects:

```text
affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0
```

for all eligible M5 q/k/v/o/gate/up/down projections.

## TREATMENT

One factor only: route eligible non-batched, transpose-true M5 BF16 affine/group64/3-bit projection calls through the process-local, fixed `s1_r8` Metal source derived from MLX v0.31.2 qmv_fast.

The kernel must preserve exactly:

- the existing U32 packed payload and BF16 scales/biases;
- 3-bit decode layout, group64 affine correction and float operation/reduction order;
- 16 values/lane, 512-K loop and SIMD reduction;
- BF16 output layout and all non-eligible/canonical fallback paths.

Only output-row execution ownership changes: one 32-lane SIMD group owns eight independent output rows; grid Y maps one such eight-row tile. No installed MLX package or metallib may be modified. The integration must be reversible and isolated to the experimental child source; it must not alter `main` or canonical runtime files.

## Required preflight before model load

1. Literal venv-launcher / `sys.prefix` and package-version provenance PASS.
2. Verify Apple M1 `applegpu_g13g`, M5, non-batched projection inputs and all fixed qmv_fast eligibility predicates.
3. Render and compile CONTROL/TREATMENT source; prove normalized source diff is only the projection dispatch factor.
4. Run real layer-0 payload direct parity for all seven projections and the three frozen deterministic BF16 probes: strict bit equality required.
5. Establish no-model parent/child dispatch markers for both constituents.
6. Verify no runtime package, raw checkpoint tensor, quantization metadata, M, residency, cleanup or KV policy changed.

Any preflight/provenance/render failure is `M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE`; no scientific constituent begins.

## Balanced order and stopping rules

Balanced order: `CONTROL → TREATMENT → TREATMENT → CONTROL`.

- First genuine TREATMENT numerical/top-1/oracle/acceptance failure: `M1_QMV_FAST_TUNING_NUMERICAL_PARITY_FAIL`, valid scientific FAIL; stop, no rescue configuration.
- Complete exact/resource-valid ABBA: `M1_QMV_FAST_TUNING_BALANCED_COMPARISON_PASS`.
- Harness, provenance, resource or incomplete sequence failure: `M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE`.

No alternate geometry, additional tuning configuration, fused projection, runtime version, or kernel precision change may be introduced after this preregistration.

## Metrics and interpretation

Primary metric after four valid constituents: pooled accepted oracle tokens / total target-block wall seconds, treatment/control ratio.

Secondary: median block wall, MLP projection telemetry where non-perturbing, minimum free memory, peak swap, and isolated treatment-kernel active/peak allocation telemetry.

Promotion requires inherited exactness/resource gates plus a robust positive balanced throughput result. A result below the projected 5% admission estimate is still valid evidence; it simply does not promote the treatment. No result here proves a broader MLX, non-M1, non-M5, different quantization, or other geometry claim.
