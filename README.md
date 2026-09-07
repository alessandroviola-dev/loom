# LOOM

**Status: ACTIVE — CONTEXT ENGINE RESEARCH ONLY — 2026-09-07**

LOOM is a local-AI research project for constrained consumer hardware. The retained inference product remains the previously frozen **UNLOCKED UOPT-003 S40** 30B profile; model/runtime optimization is still closed.

The project is reopened only for the external **LOOM Context Engine**: a host-side layer that lets Forge run long sessions against the retained physical `n_ctx=4096` model while exposing only a bounded sliding working window to each model request.

## Current branch

`research/context-engine-001`

Current phase: **CE-001 preventive Context Governor**.

Operator modes are intentionally isolated:

```text
pi         -> vanilla Pi
Forge      -> normal Forge, unchanged
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM UNLOCKED model
```

Install/update the LOOM extension and launcher from the repository with:

```bash
bash scripts/install-forge-loom.sh
```

Then use:

```bash
ForgeLoom
```

Static/local verification:

```bash
bash scripts/verify-context-engine.sh
```

## CE-001 safety envelope

Initial conservative values, subject to measured calibration:

```text
physical context       4096
target working view    1700
working high-water     2200
final input ceiling    2800
maximum output          800
safe total             3600
forbidden reserve       496
```

The final gateway invariant is:

```text
exact final input + reserved output <= 3600 < 4096
```

The full Pi/Forge session stays persistent; the model receives a request-local bounded view. Normal Forge is not modified.

## Frozen retained inference product

Do not mutate during Context Engine work:

- source GGUF SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- expert-major sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- UOPT-003 S40 matched decode: `7.557 tok/s`
- physical context: `4096`

Historical UOPT verdicts remain archived and valid: UOPT-001 PARTIAL_GO, UOPT-002 GO, UOPT-003 GO, UOPT-004/005/006 NO_GO.

Read `AGENTS.md` and `HANDOFF.md` for the current rules, implementation state, and CE-001 acceptance gate.