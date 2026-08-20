# Stretch 031 — Harness defect 20260820-180652

Status: preserved harness-only failure; scientific result **NONE**.

## Evidence inspected

Failed parent run:
`results-local/stretch/single-pass-m2-m5-geometry-comparison-031/20260820-180652/`

The complete artifact set contains only:

- `summary.json` — parent classification `SINGLE_PASS_M2_M5_GEOMETRY_COMPARISON_INCOMPLETE`;
- `attempt-1-m5-stdout.txt` — outer provenance lines only;
- `attempt-1-m5-stderr.txt` — Python traceback.

No child state, final JSON, child stdout/stderr, or constituent summary exists. The parent records return code 1, wrapper wall `0.2171166671 s`, and `child_summary_path: null`.

## Exact root cause

The original M5 helper blob `5f047b9e5f42bed959ced59e9329a8c8d7e3fc25` reached its Stretch 031 geometry callback, then raised:

```text
RuntimeError: Stretch 031 M5 transform failed for summary title: source text missing
```

The failed `add_geometry()` searched the generated final source for:

```text
Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant
```

as a summary-title literal. This literal is not present in the final runtime source. The transform chain changes the terminal title to Stretch 027, but the inherited `summary["experiment"]` string still is:

```text
Stretch 013 — Four-Token Oracle Block Verification
```

Therefore the failure occurred during source-to-source transformation, before the generated parent could create its child paths or invoke the canonical MLX child interpreter.

## Classification rationale

This is harness-only, not a scientific result:

- no model child was launched;
- no resident or target pass ran;
- no numerical/top-1/oracle/resource gate was reached;
- no M5 constituent summary exists;
- no measurement from this run may be reused.

## Fix1

Original 031 files remain preserved. Fix1 adds:

- `scripts/stretch_single_pass_geometry_harness_031_fix1.py` — exact final-source renderer, phase checks, invariant checks and `--preflight` support;
- `scripts/stretch_single_pass_m5_ten_token_control_031_fix1.py`;
- `scripts/stretch_single_pass_m2_ten_token_variant_031_fix1.py`;
- `scripts/stretch_single_pass_m2_m5_geometry_comparison_031_fix1.py`.

Fix1 changes the summary-title anchor to the literal actually present in the final generated source and adds only variant identity, M5/M2 block geometry, common 10-token depth and run-directory naming changes. Its normal runner performs the no-model preflight before creating a fresh ABBA run.

## Required evidence before a new ABBA

Run:

```bash
python3 scripts/stretch_single_pass_m2_m5_geometry_comparison_031_fix1.py --preflight
```

The preflight must render both final runtime sources, compile them, check the final-source facts and prove normalized M5 == M2. Only then may one fresh `M5 -> M2 -> M2 -> M5` run begin. The failed constituent must never be used.
