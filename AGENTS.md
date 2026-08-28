# LOOM — Pi Agent Protocol

Version: 3.56
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.
After every significant checkpoint, ChatGPT updates canonical GitHub state and user pulls before next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. invalid comparison if more than intended treatment factor changes;
4. expensive/network work requires retained artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. required gate instrumentation must persist;
8. failed frozen methods are not silently rerun under same checkpoint;
9. Integration Readiness Protocol v1 before integration coding/model forward;
10. production code canonical only after exact review + Git persistence;
11. production/user-facing Python must not depend on untracked research helpers;
12. stateful tokenizer-compatible streaming; stop/control tokens not emitted;
13. user-facing runtime claims require real end-to-end evidence.

## Local roots

GitHub is canonical.
Active clone: `<repository-root>`.
Archive/second clone: `<external-archive>`.
Do not mix relative artifacts across roots. Archive artifacts require explicit absolute paths.

## Mission / provisional architecture

**Big models. Small machines.** Current evidence supports:
- **BALANCED / 8B** — provisional default/primary tier;
- **DEEP / 30B** — selective escalation tier where measured quality gain justifies latency;
- **FAST** — architecturally retained but legacy 4B llama.cpp path is parked; reintroduce later only through a clean runtime;
- **LOOM AUTO** — capability-first execution plus verification-driven escalation, not prompt-length routing.

Do not freeze router thresholds yet.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core final-project track. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates. Do not claim unmeasured absolute guardrail-free status.

## 30B DEEP

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`.

## 8B BALANCED

Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Historical REALGEN ~`13.18 tok/s` real generation.

## 4B FAST — PARKED

Final closure: `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference in final attempt. This is mechanical availability only, not a capability result. Do not reopen legacy 4B recovery in current phase.

## Compact 8B vs 30B suite — COMPLETE

Result:
`research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`
Evidence:
`results-local/research/8b-30b-compact-practical-suite-001/20260828T152617Z/`
Classification: **`LOOM_8B_30B_COMPACT_SUITE_PASS`**.

Aggregates:
- 8B utility **4/10**, correct/partial/incorrect `2/1/2`, total task wall `35.325 s`, median TTFT `2.006 s`, pooled generation `12.931 tok/s`;
- 30B utility **7/10**, correct/partial/incorrect `4/0/1`, total task wall `468.867 s`, median TTFT `50.671 s`, pooled generation `1.402 tok/s`;
- 30B gained +3 utility points/+2 correct tasks at +`433.541 s` waiting cost (~`12.27x` task wall).

Per-task interpretation:
- T01 arithmetic: both tiers INCORRECT -> model escalation alone is not a reliable calculator;
- T02 debugging: 8B PARTIAL, 30B core CORRECT but strict-line instruction FAIL;
- T03 strict JSON: 8B semantic JSON correct but output-contract FAIL; 30B PASS;
- T04 supplied context: both CORRECT/PASS;
- T05 verification-driven design: 8B INCORRECT, 30B CORRECT/PASS.

Initial product role: 8B default candidate; 30B selective escalation. No final router thresholds/general intelligence claims.

## Current checkpoint — 8B capability amplification funnel

Preregistration:
`research/architecture/loom-8b-capability-amplification-funnel-001-preregistration.md`.

Purpose: test whether cheap LOOM capabilities close raw-8B gaps before 30B escalation, using fresh prompts and paired one-factor controls.

Branches:
A. deterministic calculator tool capability for arithmetic;
B. reusable strict-output protocol skill for exact machine-readable contracts;
C. reusable verification-first protocol skill for decision/escalation reasoning.

Create only:
`scripts/loom_8b_capability_amplification_funnel_001.py`.

No 30B/4B inference, downloads, runtime optimization, memory/RAG, Heretic, fine-tuning or unregistered retries.

If a branch passes its frozen acceptance signal, it becomes a candidate LOOM capability. Production/router integration remains separate.

After funnel review: design capability-first LOOM AUTO architecture from accepted mechanisms, then provider/UI and mandatory Heretic integration after initial optimization.