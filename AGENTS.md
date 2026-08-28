# LOOM — Pi Agent Protocol

Version: 3.62
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.
After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and user pulls before the next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. invalid comparison if more than intended treatment factor changes;
4. expensive/network work requires retained artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from invalid/inconclusive evidence;
7. required gate instrumentation must persist;
8. failed frozen methods are not silently rerun under changed conditions;
9. Integration Readiness Protocol v1 before integration coding/model forward;
10. production code canonical only after exact review + Git persistence;
11. production/user-facing Python must not depend on untracked research helpers;
12. stateful tokenizer-compatible streaming; stop/control tokens not emitted;
13. user-facing runtime claims require real end-to-end evidence.

## Local roots

GitHub is canonical.
Active clone: `<repository-root>`.
Archive/second clone: `<external-archive>`.
Do not mix relative artifacts across roots.

## Product direction

**Big models. Small machines.** Current evidence supports:
- **BALANCED / 8B** — provisional default/primary tier;
- **DEEP / 30B** — selective escalation tier;
- **FAST** — architecturally retained, legacy 4B path parked;
- **LOOM AUTO** — validator-first: `8B -> validate -> safe deterministic repair when provably semantics-preserving -> selective 30B -> validate again` for mechanically verifiable tasks.

Open-ended semantic uncertainty remains a separate unresolved track. Do not freeze general 30B escalation thresholds yet.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains a core final-project track. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Runtime baselines

### 30B DEEP
Canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Compact-suite pooled generation `1.402 tok/s`, median TTFT `50.671 s`.

### 8B BALANCED
`mlx-community/Qwen3-8B-3bit@619ded3`, 3-bit/group64, Direct MLX, M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Historical REALGEN ~`13.18 tok/s`.
Compact-suite pooled generation `12.931 tok/s`, median TTFT `2.006 s`.

### 8B 4-bit — CLOSED HISTORICAL BRANCH
Historical Direct MLX 4-bit continuous profile resource-failed even after controlled 72–74% free-memory launch. KV8 rescue has no canonical quality classification. Do not reopen from current evidence.

### 4B FAST — PARKED
Final closure `LOOM_4B_FINAL_ATTEMPT_ABORTED`. Do not reopen legacy recovery in current phase.

## Prior capability evidence

- compact 8B-vs-30B: 8B utility `4/10`, 30B `7/10`, +`433.541 s` waiting for +3 utility;
- calculator flow: REJECTED;
- strict-output and verification-first: ACCEPTED branch-level only;
- Capability Candidate v1: NO_GO;
- selector v0 isolated: GO `15/15`, but end-to-end dispatch FIX1: scientific NO_GO (`7/9` selector, `1/3` NORMAL false activation, AUTO8 only `2/9` CORRECT).

Do not tune selector/protocols on exposed dispatch tasks and do not use selector-first graph as production basis.

## Output Validator v0 — COMPLETE / GO

Result:
`research/architecture/loom-8b-output-validator-v0-001-result.md`.
Evidence:
`results-local/research/8b-output-validator-v0-001/20260828T174056Z/`.
Classification: **`LOOM_8B_OUTPUT_VALIDATOR_V0_GO`**.

Frozen provenance unchanged. Harness SHA:
`c67aed70998ee2cac23827e486b0cdfeaf3b8c1264bd84a84e4c24e8443fdc25`.

Observed:
- synthetic preflight `11/11` PASS;
- 12/12 valid records;
- validator PASS/FAIL/UNCERTAIN `3/6/3`;
- T01–T09 model C/P/I `3/3/3`;
- **false PASS = 0**;
- T10–T12 `UNCERTAIN = 3/3`;
- validator p50/p95 `0.066355 / 0.758321 ms`;
- median 8B TTFT `1.499425 s`;
- pooled generation `12.986417 tok/s`.

Supported conclusion: benchmark-supplied deterministic validators can fail closed on these mechanically verifiable classes and abstain on open-ended tasks. This does not prove general semantic validation or automatic validator selection.

## Current checkpoint — Validator-Guided Selective Rescue 001

Preregistration:
`research/architecture/loom-validator-guided-selective-rescue-001-preregistration.md`.

Fresh 8-task mechanically verifiable suite.

Frozen graph:
`RAW8 -> validator -> PASS accept; FAIL -> safe fence-only deterministic repair if eligible -> revalidate -> residual FAIL -> one canonical 30B DEEP call -> revalidate`.

Safe repair may only remove one outer Markdown code fence while leaving interior payload bytes unchanged. No coercion or semantic repair.

Open-ended UNCERTAIN tasks are excluded from this checkpoint and require a separate semantic-verifier track.

Create only:
`scripts/loom_validator_guided_selective_rescue_001.py`.

Frozen GO requires:
- all initial 8B and every triggered 30B condition valid;
- zero false acceptance at every stage;
- only frozen fence-removal repair;
- final CORRECT >=6/8 and >=RAW8 +2;
- at least 2/8 30B calls avoided;
- no DEEP call after initial PASS/successful repair;
- validator and repair p95 <5 ms;
- no network/download/package/model/runtime mutation.

No selector tuning, capability injection, calculator, 4B, memory/RAG, fine-tuning, Heretic, provider/UI or production integration.
