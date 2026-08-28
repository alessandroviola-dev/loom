# LOOM — Pi Agent Protocol

Version: 3.57
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
Compact-suite pooled generation `1.402 tok/s`, median TTFT `50.671 s`.

## 8B BALANCED

Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Historical REALGEN ~`13.18 tok/s` real generation.
Compact-suite pooled generation `12.931 tok/s`, median TTFT `2.006 s`.

## 4B FAST — PARKED

Final closure: `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference in final attempt. Mechanical availability only, not a capability result. Do not reopen legacy 4B recovery in current phase.

## Compact 8B vs 30B suite — COMPLETE

Result: `research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`.
Classification `LOOM_8B_30B_COMPACT_SUITE_PASS`.

8B utility `4/10`, total task wall `35.325 s`.
30B utility `7/10`, total task wall `468.867 s`.
30B gained +3 utility/+2 correct tasks at +`433.541 s` waiting cost (~`12.27x`).

Key decomposition:
- arithmetic: both wrong -> model escalation alone insufficient;
- strict JSON: 8B semantics right but output contract failed;
- supplied-context reasoning: 8B matched 30B;
- verification-driven design: 30B materially better.

Initial role: 8B default candidate; 30B selective escalation. No final router thresholds/general intelligence claims.

## 8B capability amplification funnel — COMPLETE

Result: `research/architecture/loom-8b-capability-amplification-funnel-001-result.md`.
Evidence: `results-local/research/8b-capability-amplification-funnel-001/20260828T154910Z/`.
Classification: **`LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_PASS`**.

Frozen 8B provenance unchanged.

Branch A — calculator tool: **REJECTED**.
- improved 2/3 pairs but treatment only 1/3 CORRECT;
- key failure: calculator can evaluate a wrong model-selected expression perfectly, so arithmetic semantics/formulation remain unresolved;
- do not integrate current calculator flow.

Branch B — strict-output protocol: **ACCEPTED**.
- treatment 3/3 CORRECT;
- 2 improvements, 0 regressions;
- solves fenced/extra-format failures while preserving semantics.

Branch C — verification-first protocol: **ACCEPTED**.
- treatment 2/3 CORRECT;
- 2 improvements, 0 regressions;
- improves observable/deterministic validation and escalation reasoning.

Accepted B/C remain candidate system-layer capabilities, not yet production behavior. Calculator A is excluded from current integration.

## Current checkpoint — 8B Capability Candidate v1

Preregistration:
`research/architecture/loom-8b-capability-candidate-v1-001-preregistration.md`.

Goal: validate accepted strict-output + verification-first mechanisms together as a capability library on fresh tasks and compare RAW 8B, CAPABILITY 8B and canonical 30B.

Important boundary: capability applicability is frozen by benchmark task label. **Automatic capability recognition/dispatch is NOT tested here.**

Create only:
`scripts/loom_8b_capability_candidate_v1_001.py`.

Four fresh tasks:
- 2 strict-output;
- 2 verification-first.

Every task runs RAW8, CAP8, 30B with fresh state and counterbalanced order.

Promotion gate for CAP8:
- >=`6/8` utility;
- >=`+2` utility vs RAW8;
- zero per-task utility regressions;
- >=`3/4` CORRECT;
- valid provenance/evidence.

No calculator, automatic router selection, 4B, downloads, runtime optimization, retries, tools, memory/RAG, fine-tuning, Heretic, provider/UI or router thresholds.

After candidate review: if GO, validate automatic capability selection/dispatch separately; then build capability-first LOOM execution graph. Heretic remains mandatory after initial runtime/capability optimization.
