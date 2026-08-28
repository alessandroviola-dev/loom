# LOOM 8B Capability Amplification Funnel 001 — Result

Date: 2026-08-28
Status: **COMPLETE / PASS**
Classification: **`LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_PASS`**

## Purpose

Test whether cheap system-layer capabilities materially improve the validated LOOM 8B BALANCED tier before escalating to LOOM 30B DEEP.

Preregistration:
`research/architecture/loom-8b-capability-amplification-funnel-001-preregistration.md`

Evidence:
`results-local/research/8b-capability-amplification-funnel-001/20260828T154910Z/`

Harness:
`scripts/loom_8b_capability_amplification_funnel_001.py`
SHA-256: `59df633b4c9bdbd0000cc1673af4e166a2c5a8e9914343a28ff2ea2d9977ad21`

No Git commit/push was performed by Pi. A no-inference mechanical rescore applied the unchanged frozen rubrics to retained outputs; no model condition was rerun.

## Frozen 8B provenance

- model: `mlx-community/Qwen3-8B-3bit@619ded3`;
- weight SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- quantization: 3-bit/group64;
- MLX/mlx-metal `0.31.2`;
- mlx-lm `0.31.3`;
- transformers `5.12.1`;
- Apple M1 built-in MLX QuantizedLinear / `qmv_fast`;
- BF16 KV;
- greedy;
- thinking OFF.

## Branch results

### A — deterministic calculator tool

**REJECTED**.

Paired outcomes:
- A1 RAW `INCORRECT/FAIL` -> TOOL `INCORRECT/FAIL`: no improvement;
- A2 RAW `INCORRECT/FAIL` -> TOOL `PARTIAL/PASS`: improved;
- A3 RAW `PARTIAL/FAIL` -> TOOL `CORRECT/PASS`: improved.

Acceptance failed because only 1/3 treatment items was fully CORRECT.

Key failure mode: the calculator correctly evaluates the expression it receives, but the model may choose the wrong expression/semantic formulation first. A1 produced `ceil(920 / 37)=25`, which is mechanically correct for that expression but does not solve the intended capacity-margin reasoning. A2 obtained the correct numeric total `395.28` but omitted requested explanatory/format requirements. Therefore this calculator flow is not yet an accepted LOOM capability.

Observed tool-flow wall:
- A1: `7.922 s` total two-stage flow;
- A2: `6.038 s`;
- A3: `8.226 s`.

### B — reusable strict-output protocol

**ACCEPTED**.

Paired outcomes:
- B1 RAW `PARTIAL/FAIL` -> PROTOCOL `CORRECT/PASS`;
- B2 RAW `PARTIAL/FAIL` -> PROTOCOL `CORRECT/PASS`;
- B3 RAW `CORRECT/PASS` -> PROTOCOL `CORRECT/PASS`.

Treatment achieved 3/3 CORRECT with two improvements and no regressions.

The treatment removed markdown fences/extra formatting while preserving the requested machine-readable semantic content. This directly addresses the strict-output failure observed in the prior 8B-vs-30B compact suite.

### C — reusable verification-first protocol

**ACCEPTED**.

Paired outcomes:
- C1 RAW `PARTIAL/PASS` -> SKILL `PARTIAL/PASS`;
- C2 RAW `PARTIAL/PASS` -> SKILL `CORRECT/PASS`;
- C3 RAW `INCORRECT/PASS` -> SKILL `CORRECT/PASS`.

Treatment achieved 2/3 CORRECT with two improvements and no regressions.

The accepted protocol materially improves verification-driven escalation reasoning by centering observable/deterministic success criteria rather than prompt length or generic task complexity.

## Performance/resource interpretation

Treatments retained approximately the same 8B generation regime (~11–13 tok/s). The strict-output protocol imposed only small wall/TTFT overhead on these short tasks. Verification-first responses were somewhat longer/slower (~7.9–8.8 s wall in the treated cases) but remained dramatically cheaper than the canonical 30B DEEP latency regime.

MLX peak remained roughly `3.78–3.88 GB`; observed swap remained in the same host-pressure range with no treatment-specific safety regression.

## Scientific interpretation

The funnel supports two candidate LOOM capabilities:
1. **strict-output protocol** for machine-readable/contract-bound outputs;
2. **verification-first protocol** for validation/escalation reasoning.

The current calculator flow is rejected. A deterministic arithmetic engine alone is insufficient when semantic expression construction is wrong; future arithmetic capability work must address expression/task formulation or deterministic extraction/planning rather than merely evaluating model-selected arithmetic.

No branch regressed under the frozen acceptance criteria.

## Product consequence

Do not route immediately to 30B for every 8B failure class.

Current capability-first direction:
`task -> applicable accepted protocol/capability -> 8B -> validator -> 30B only if unresolved/uncertain`.

Next checkpoint should validate an integrated 8B capability candidate using only accepted B/C mechanisms on fresh prompts, while keeping calculator A excluded. Automatic capability selection/router thresholds remain separate and unfrozen.
