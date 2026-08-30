# LOOM 30B Acceleration Prompt Cache 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_ACCEL_PROMPT_CACHE_MECHANICAL_NO_GO`**

## Summary

The frozen prompt-cache experiment produced strong direct evidence that `llama-completion --prompt-cache` can reuse the stable prefix and dramatically reduce prompt-evaluation time, but the preregistered functional-validity gate failed in all nine invocations. Therefore the experiment is mechanically invalid for a scientific GO claim.

The failure was caused by the experiment contract rather than cache compatibility: the frozen `-n 8` generation budget truncated the target answer before `4317` completed, while the warm answer was semantically correct (`ambra`) but violated the overly strict exact-string validator by adding explanatory text.

No post-hoc relaxation is applied. The timing/cache observations are retained as diagnostic evidence only and must be confirmed by a fresh preregistered recovery run.

## Evidence

Evidence root:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`

## Measured observations

| Round | Condition | Prompt eval | E2E | Generation tok/s | Peak RSS | Peak swap |
|---|---|---:|---:|---:|---:|---:|
| 1 | B | 71.256 s | 75.285 s | 3.68 | 2914.5 MiB | 1353.3 MiB |
| 1 | W | 70.702 s | 74.713 s | 3.37 | 2917.4 MiB | 1329.3 MiB |
| 1 | C | 2.974 s | 6.766 s | 3.53 | 2916.5 MiB | 1313.3 MiB |
| 2 | B | 73.509 s | 77.364 s | 3.64 | 2910.9 MiB | 1328.1 MiB |
| 2 | W | 73.213 s | 77.471 s | 3.27 | 2911.1 MiB | 1330.1 MiB |
| 2 | C | 3.070 s | 6.942 s | 3.47 | 2912.5 MiB | 1339.6 MiB |
| 3 | B | 73.264 s | 77.216 s | 3.64 | 2910.6 MiB | 1339.6 MiB |
| 3 | W | 73.441 s | 78.163 s | 3.33 | 2913.2 MiB | 1331.6 MiB |
| 3 | C | 2.949 s | 6.886 s | 3.54 | 2916.5 MiB | 1323.6 MiB |

Observed diagnostic ratios:
- C/B prompt-eval: `0.04174`, `0.04177`, `0.04026`; median **0.04174**;
- C/B E2E: `0.08988`, `0.08973`, `0.08918`; median **0.08973**;
- median B/C generation: `3.64 / 3.53 tok/s`; preservation **96.98%**.

These numbers are not promoted to a canonical acceleration GO because functional validity failed.

## Cache evidence

- Each W created a fresh `26,449,272` byte cache file.
- All three cache files had SHA256 `f96f9fb61f6e2302fb206932a4ca497c8a1ccbe7346c22b20bc0678094dd5a99`.
- Each C pre-launch cache hash matched its corresponding W post-run hash.
- Runtime reported loading 269-token sessions, matching `262 / 269` prompt tokens, and replaying the last token.

Therefore cache creation/reuse itself was mechanically demonstrated.

## Functional failure

Frozen expected outputs:
- B/C: exact `4317`;
- W: exact `ambra`.

Observed:
- B/C: `Il nodo Vega usa la porta 4` — truncated before `4317` completed under `-n 8`;
- W: `Il colore del nodo Atlas è ambra` — semantically correct but not exact-string equal.

All nine invocations therefore failed the preregistered functional-validity rule.

## Gate evaluation

- provenance — PASS;
- all 9 functionally valid — **FAIL**;
- cache created/reused — PASS;
- direct prompt timing — PASS;
- median prompt ratio <=0.70 — diagnostic PASS only;
- median E2E ratio <1.00 — diagnostic PASS only;
- decode preservation >=90% — diagnostic PASS only;
- no critical pressure/OOM/corruption/runaway — PASS;
- every swap <=3.5 GiB — PASS;
- durable evidence — PASS;
- no mutation — PASS.

Final classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_MECHANICAL_NO_GO`**.

## Exact next step

Preregister a recovery run that changes only the mechanical output-validation conditions:
- increase generation budget enough to avoid truncation;
- validate semantic correctness rather than exact surface form;
- retain the same model, runtime, S24 profile, stable prefix, B/W/C ordering, cache factor and primary prompt-eval metric.

No reuse of the invalid run as a scientific GO is allowed.
