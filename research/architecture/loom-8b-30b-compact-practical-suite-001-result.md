# LOOM 8B vs 30B Compact Practical Suite 001 — Result

Date: 2026-08-28
Classification: **LOOM_8B_30B_COMPACT_SUITE_PASS**
Evidence: `results-local/research/8b-30b-compact-practical-suite-001/20260828T152617Z/`

## Validity

All ten frozen model-task conditions executed with valid provenance and isolated child execution. No 4B, downloads, retries, runtime changes, tools/RAG/Heretic, commit or push occurred.

8B provenance: `mlx-community/Qwen3-8B-3bit@619ded3`, weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`, 3-bit/group64, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.

30B provenance: canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`; runtime/core/backend SHAs matched preregistration; Q4/top-8 PACKED, BF16 KV, greedy; contract SHA `ee43eaa...67657aba`; expert bank `15,401,484,288 B`.

Harness SHA `55cc10...64ac344`. Tracked runtime/runner diff was empty before every child launch.

A post-run no-inference scoring reconciliation changed only rubric parsing for fenced JSON and whitespace-variant reverse iteration; raw outputs were unchanged.

## Per-task result

| Task | 8B | 30B |
|---|---|---|
| T01 arithmetic | INCORRECT / instruction FAIL / COMPLETE | INCORRECT / instruction FAIL / COMPLETE |
| T02 debugging | PARTIAL / PASS / COMPLETE | CORRECT / instruction FAIL / COMPLETE |
| T03 strict JSON | CORRECT semantic content / instruction FAIL / COMPLETE | CORRECT / PASS / COMPLETE |
| T04 supplied context | CORRECT / PASS / COMPLETE | CORRECT / PASS / COMPLETE |
| T05 verification-driven design | INCORRECT / PASS / COMPLETE | CORRECT / PASS / COMPLETE |

### T01

Both tiers failed the frozen arithmetic answer. 8B returned `3`. 30B returned `31` with `(1375 / 48) / 0.8 = 31`; this is numerically wrong and also fails the preregistered expected core answer. This is evidence that simply escalating to 30B does not solve deterministic arithmetic reliably.

### T02

8B proposed a safe list-comprehension fix but did not identify the precise forward-iteration skip mechanism; scored PARTIAL. 30B correctly identified mutation during iteration and used reverse iteration, but exceeded the strict eight-line instruction; core correctness was better but utility score remained limited by instruction failure.

### T03

8B produced semantically correct JSON but wrapped it in a fenced block despite the exact-output requirement. 30B followed the strict output contract. This exposes a protocol/structured-output gap rather than a semantic-data gap.

### T04

Both chose runtime X correctly from supplied facts. No material 30B advantage.

### T05

8B produced an incoherent escalation loop without a concrete verification mechanism. 30B supplied the intended verification-driven rule. This is the clearest raw reasoning/design advantage for 30B in this suite.

## Aggregates

| Metric | 8B | 30B |
|---|---:|---:|
| Utility | **4/10** | **7/10** |
| Correct / Partial / Incorrect | 2 / 1 / 2 | 4 / 0 / 1 |
| Total task wall | 35.325 s | 468.867 s |
| Median TTFT | 2.006 s | 50.671 s |
| Pooled generation | 12.931 tok/s | 1.402 tok/s |
| Time per correct task | 17.663 s | 117.217 s |
| Peak runtime memory metric | 3,861,490,392 B MLX | 946,704,392 B process/runtime metric |
| Peak observed swap | 2839.31 MB | 2791.31 MB |

30B quality delta: **+3 utility points, +2 correct tasks**.
Additional 30B waiting cost: **433.541 s** total, about **12.27x** task wall; median TTFT +48.665 s.

## Product interpretation

Initial role evidence:
- **8B BALANCED should be the default/primary candidate** because its latency is dramatically lower and it matches 30B on supplied-context reasoning while giving usable partial/correct behavior on other tasks.
- **30B DEEP should be selective escalation**, especially for tasks resembling T05 where a material judgement/reasoning gain is measured, and for strict-contract tasks only if cheaper deterministic/protocol mechanisms cannot close the gap.
- **Do not route deterministic arithmetic to 30B as a first-line fix**; both tiers failed T01. This failure class is a strong candidate for a deterministic calculator/tool capability.
- T03 suggests structured-output/protocol enforcement may make 8B sufficient without 30B.

These are provisional product roles, not general intelligence rankings and not final router thresholds.

## Next scientific step

Before implementing LOOM AUTO thresholds, test whether low-cost LOOM capabilities can close raw 8B failure modes:
1. deterministic calculation/tool path for arithmetic;
2. structured-output/protocol enforcement for exact contracts;
3. generic verification-first decision protocol for escalation/design tasks.

Use fresh unseen prompts and one-factor comparisons against raw 8B. If these mechanisms materially raise 8B utility, prefer capability-first execution before 30B escalation.

LOOM Heretic remains a mandatory later track after initial runtime/capability optimization.