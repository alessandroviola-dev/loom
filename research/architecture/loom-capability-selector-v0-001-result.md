# LOOM Capability Selector v0 001 — Result

Date: 2026-08-28
Status: **COMPLETE / GO**
Classification: **`LOOM_CAPABILITY_SELECTOR_V0_GO`**

## Evidence

`results-local/research/capability-selector-v0-001/20260828T163136Z/evidence.json`

Harness:
`scripts/loom_capability_selector_v0_001.py`

Harness SHA-256:
`5ccaae77862ceb60700115487ea4db5e5bdcae330d8dcb7583d3186e6521887d`

Only attributable changed file: the new experimental selector harness. No Git commit/push by Pi.

## Frozen selector result

All 15 preregistered unseen mixed/adversarial prompts were classified correctly.

- overall accuracy: **15/15 = 1.0000**;
- NORMAL: precision/recall/F1 **1.0000 / 1.0000 / 1.0000**;
- STRICT_OUTPUT: precision/recall/F1 **1.0000 / 1.0000 / 1.0000**;
- VERIFY_FIRST: precision/recall/F1 **1.0000 / 1.0000 / 1.0000**;
- expected-NORMAL false activations: **0/7**;
- selector wall p50: **8 us**;
- selector wall p95: **218 us**;
- misclassifications: **none**.

Confusion matrix, expected x predicted:

| expected | NORMAL | STRICT_OUTPUT | VERIFY_FIRST |
|---|---:|---:|---:|
| NORMAL | 7 | 0 | 0 |
| STRICT_OUTPUT | 0 | 4 | 0 |
| VERIFY_FIRST | 0 | 0 | 4 |

## Provenance / isolation

The checkpoint executed with `python3 -I`, standard library only. No model inference, network call/client, external package, package mutation, calculator, embeddings, learned classifier or runtime/model action occurred.

The frozen selector rules were not altered after scoring began.

## Interpretation

The preregistered selector v0 gate passed completely. This authorizes a separate end-to-end 8B conditional-dispatch experiment using the exact frozen selector plus the already accepted targeted capabilities:
- STRICT_OUTPUT protocol;
- VERIFY_FIRST protocol;
- otherwise NORMAL baseline.

This GO does **not** promote Capability Candidate v1, does not prove general semantic task classification, and does not authorize 30B escalation thresholds. The next checkpoint must measure actual answer quality and regressions when the selector controls 8B behavior on fresh mixed tasks.
