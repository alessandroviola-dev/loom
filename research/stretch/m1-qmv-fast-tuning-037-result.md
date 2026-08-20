# Stretch 037 — M1-specific custom qmv_fast full-model result

Date: 2026-08-20
Status: **`M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE` — scientific result NONE.**

## Frozen preregistration and prepared-source provenance

Before this result attempt:

1. feasibility/preregistration commit `41397e94857f4a4ebd394dd1681078310cc60002` was pushed and remote-verified;
2. the methodological amendment freezing the factor as **built-in MLX qmv implementation → custom M1 S1_R8 qmv implementation**, not geometry alone, was committed/pushed as `5f3ff4417c9b8fea70bcd6575f1049760592d13c`;
3. the prepared runtime/harness source was committed/pushed as `3a517ab93055e9ad8111a4216fb835fc5e57c358`.

A standalone no-model preflight before the prepared-source commit passed source rendering/normalization, literal venv dispatch and four-specialization JIT/parity. The final scientific harness nonetheless must rerun its complete mandatory preflight inside its own evidence directory immediately before ABBA. That run is the decisive launch gate.

## Preflight failure

Fresh scientific harness run directory:

`results-local/stretch/m1-qmv-fast-tuning-037/20260820-212659/`

The harness created its top-level run directory, then invoked `render_preflight(repo, root / "preflight")` without first creating that `preflight/` directory. The first render artifact write therefore raised:

```text
FileNotFoundError: [Errno 2] No such file or directory:
.../m1-qmv-fast-tuning-037/20260820-212659/preflight/control-final.py
```

The outer summary was written with:

```text
classification: M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE
scientific_result: NONE
```

No CONTROL or S1_R8 constituent was launched. Consequently there are no full-model logits/top-1/oracle outcomes, accepted tokens, target-block timings, cleanup metrics, resource metrics, or treatment JIT observations attributable to a scientific constituent.

## Required interpretation

This is a harness-only preflight failure, not a numerical FAIL and not a performance result. It does not alter the approved scientific factor, feasibility evidence, frozen runtime, or canonical built-in qmv path.

Per the preregistered stop rule, no retry, rescue geometry, fallback, threshold change, source integration correction followed by rerun, or partial ABBA was performed. The existing prepared harness remains preserved as evidence of the defect; any dispatch/preflight revision and fresh ABBA require new explicit authorization.

## Evidence

- Failure summary: `results-local/stretch/m1-qmv-fast-tuning-037/20260820-212659/summary.json`
- Preregistration amendment: `research/stretch/m1-qmv-fast-tuning-037-preregistration-amendment.md`
- Frozen plan: `research/stretch/m1-qmv-fast-tuning-037-plan.md`
- Prepared runtime/harness: `scripts/stretch_m1_qmv_fast_runtime_037.py`, `scripts/stretch_m1_qmv_fast_comparison_037.py`
