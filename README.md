# LOOM

**Status: CLOSED / ARCHIVED — 2026-09-06**

LOOM was a research project focused on making capable local AI practical on constrained consumer hardware, with an Apple Silicon M1 Mac with 8 GB unified memory as the reference platform.

The project is now concluded. The final decision is not a runtime failure: the 30B UNLOCKED model was made materially more usable, but its practical capability remained below the level required for the intended real workloads. Further speed work therefore no longer justified additional engineering effort.

## Final retained product

The last stable local product is the **UNLOCKED UOPT-003 S40** profile:

- source GGUF SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- expert-major sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- matched S40 decode: `7.557 tok/s`
- matched 1,155-token cold TTFT: `102.242 s`
- frozen behavior/capability gates: refusal `0/6`, degeneration `0/6`, benign `8/8`

Operator commands remain documented in `docs/LOOM_OPERATIONS.md` for historical/recovery use.

## Final optimization outcome

- UOPT-001: PARTIAL_GO
- UOPT-002: GO
- UOPT-003: GO — final retained S40 profile
- UOPT-004: NO_GO — Q2 expert quality loss
- UOPT-005: NO_GO — selective IQ3 quality frontier exhausted
- UOPT-006: NO_GO — draftless n-gram speculative decoding produced 0 drafted / 0 accepted tokens and no useful speedup

See `HANDOFF.md`, `ROADMAP.md`, `research/integration/loom-unlocked-speed-optimization-006-result.md`, and `research/integration/loom-project-closure-20260906.md`.

## Archive rule

There is no active LOOM roadmap. No agent or automation should resume experiments, modify the production profile, or begin a new optimization work package unless the project is explicitly reopened by the owner.
