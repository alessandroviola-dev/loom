# LOOM 8B Capability Candidate v1 001 — Result

Date: 2026-08-28
Status: **COMPLETE / NO_GO**
Classification: **LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO**

Evidence:
`results-local/research/8b-capability-candidate-v1-001/20260828T161543Z/`

Harness:
`scripts/loom_8b_capability_candidate_v1_001.py`
SHA-256: `f4bdbef225af0dc7a76874e4f5e18e78385d3dc7486f94b304302b588a50a970`

## Frozen conditions

All 12 child conditions completed with valid provenance:
- RAW 8B;
- CAPABILITY 8B using only the previously accepted strict-output or verification-first treatment selected by frozen task label;
- canonical 30B DEEP.

No calculator, automatic dispatch, 4B, downloads, runtime changes, retries, tools, memory/RAG, fine-tuning, Heretic, provider/UI or router threshold work occurred.

## Promotion gate

CAP8 gate result: **4/5 gates passed**.

- utility >= `6/8`: PASS — `7/8`;
- improvement >= `+2` vs RAW8: **FAIL — +1** (`7/8` vs `6/8`);
- zero per-task regressions: PASS;
- >= `3/4` CORRECT: PASS — `3/4`;
- valid provenance/evidence: PASS — 12/12 conditions.

The frozen gate therefore requires **NO_GO**. Do not relax it post hoc.

## Per-task utility

| Task | RAW8 | CAP8 | 30B |
|---|---:|---:|---:|
| T01 strict-output | 2 | 2 | 2 |
| T02 strict-output | 2 | 2 | 2 |
| T03 verification-first | 1 | 1 | 1 |
| T04 verification-first | 1 | 2 | 2 |
| **Total** | **6/8** | **7/8** | **7/8** |

CAP8 had no task-level regression and closed the observed aggregate utility gap to 30B on this set, but the preregistered improvement-over-RAW requirement was not met because RAW8 itself performed strongly on three of four tasks.

## Aggregates

RAW8:
- utility `6/8`;
- correct/partial/incorrect `3/1/0`;
- total wall `22.343 s`;
- median TTFT `1.712 s`;
- pooled generation `12.344 tok/s`;
- peak MLX `3,856,804,524 B`;
- peak swap `2668.44 MB`.

CAP8:
- utility `7/8`;
- correct/partial/incorrect `3/1/0`;
- total wall `26.311 s`;
- median TTFT `2.494 s`;
- pooled generation `12.857 tok/s`;
- peak MLX `3,915,492,224 B`;
- peak swap `2559.19 MB`.

30B:
- utility `7/8`;
- correct/partial/incorrect `3/1/0`;
- total wall `284.591 s`;
- median TTFT `46.894 s`;
- pooled generation `1.363 tok/s`;
- peak MLX process metric `939,823,112 B`;
- peak observed swap `2620.44 MB`.

30B added no utility/correct-task gain over CAP8 in this set while costing `+258.280 s`, `10.82x` CAP8 task wall, and `+44.401 s` median TTFT.

## Interpretation

This result does **not** promote an always-on integrated CAP8 candidate because the frozen +2 improvement gate failed.

It also does **not** overturn the prior branch-level evidence:
- strict-output remains an accepted targeted capability from the frozen funnel;
- verification-first remains an accepted targeted capability from the frozen funnel;
- calculator remains rejected.

There is no evidence here of a B+C integration regression. The main reason the integrated candidate missed promotion is limited headroom: RAW8 already scored `6/8` on this fresh set and CAP8 only had one additional utility point available through T04.

Therefore retain strict-output and verification-first as **targeted, conditional capabilities**, not as an always-on promoted 8B bundle.

## Next action

Do not relax/retry Capability Candidate v1. Validate capability applicability/dispatch separately on unseen mixed prompts before building a full capability-first execution graph.
