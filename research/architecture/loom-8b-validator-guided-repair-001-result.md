# LOOM 8B Validator-Guided Repair 001 — Result

Date: 2026-08-28
Classification: **LOOM_8B_VALIDATOR_GUIDED_REPAIR_MECHANICAL_NO_GO**

## Why this checkpoint is invalid

The executed harness supplied validator task/spec metadata containing hidden expected-payload information inside the guided-repair failure report. That violates the preregistered boundary that repair may receive only the original request, raw failed answer, and deterministic validator failures without hidden expected answer/ground-truth leakage.

Therefore guided-repair outputs and aggregate scientific quality from this run are not valid evidence. No rerun occurred.

## Provenance / execution

- harness: `scripts/loom_8b_validator_guided_repair_001.py`
- executed SHA256: `c03c62eee6829a12d9b4edce7af2e28c3c56324519b65bdfcfbd76c01b55b158`
- model: `mlx-community/Qwen3-8B-3bit@619ded3`
- weight SHA256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; greedy; thinking OFF; BF16 KV
- evidence: `results-local/research/8b-validator-guided-repair-001/20260828T204632Z/`
- no 30B, no network/package/model mutation, no commit/push

## Preflight

- validator fixtures: 10/10 PASS
- fence-repair fixtures: 4/4 PASS
- offline/socket guard active
- immutable artifact hashes unchanged

## Observations retained only as diagnostics

These values must not be used as scientific guided-repair performance claims because of leakage:

- RAW C/P/I: 2/3/3
- final C/P/I: 5/1/2
- guided calls: 3; one apparent correct conversion
- RAW wall: 35.690 s
- guided-added wall: 22.497 s
- total wall: 78.141 s

A separate non-leakage issue was observed before guided repair on T08: `V_VERIFY_RULE` returned PASS while the independent frozen scorer marked the answer PARTIAL. Because this acceptance path occurs before guided repair, the leakage does not explain it. Treat this as a validator-safety diagnostic requiring independent hardening on fresh/adversarial fixtures before another guided-repair experiment.

## Decision

1. Do not repair/reclassify this run.
2. Do not reuse T01–T08 to tune validator or repair behavior.
3. Do not immediately rerun guided repair with only a sanitized report: `V_VERIFY_RULE` first needs an independent fail-closed hardening checkpoint because a false accept was observed.
4. After validator hardening, any future guided-repair checkpoint must use fresh tasks and a sanitized allowlisted failure-report schema that cannot serialize hidden expected payload/spec fields.
