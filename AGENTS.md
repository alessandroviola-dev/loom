# LOOM — Pi Agent Protocol

Version: 3.58
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
- **LOOM AUTO** — targeted capability first, then 8B, validation, and 30B only when unresolved.

Do not freeze 30B escalation thresholds yet.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains a core final-project track. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## 30B DEEP

Canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Compact-suite pooled generation `1.402 tok/s`, median TTFT `50.671 s`.

## 8B BALANCED

Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Historical REALGEN ~`13.18 tok/s`.
Compact-suite pooled generation `12.931 tok/s`, median TTFT `2.006 s`.

## 4B FAST — PARKED

Final closure `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference in final attempt. Mechanical availability only, not capability evidence. Do not reopen legacy 4B recovery in current phase.

## Compact 8B vs 30B suite — COMPLETE

Result: `research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`.
8B utility `4/10`, wall `35.325 s`.
30B utility `7/10`, wall `468.867 s`.
30B gained +3 utility at +`433.541 s` waiting (~`12.27x`).

## 8B capability amplification funnel — COMPLETE

Result: `research/architecture/loom-8b-capability-amplification-funnel-001-result.md`.
- calculator flow: **REJECTED**;
- strict-output protocol: **ACCEPTED**;
- verification-first protocol: **ACCEPTED**.

Accepted B/C are targeted conditional capabilities, not automatically always-on behavior.

## 8B Capability Candidate v1 — COMPLETE / NO_GO

Result: `research/architecture/loom-8b-capability-candidate-v1-001-result.md`.
Evidence: `results-local/research/8b-capability-candidate-v1-001/20260828T161543Z/`.
Classification: **`LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO`**.

Frozen promotion gate:
- CAP8 >=6/8: PASS — `7/8`;
- CAP8 >=+2 vs RAW8: **FAIL — +1** (`7/8` vs `6/8`);
- zero regressions: PASS;
- >=3/4 CORRECT: PASS;
- provenance/evidence: PASS.

CAP8 matched 30B at `7/8` on this fresh set while costing `26.311 s` vs `284.591 s` total wall, but the preregistered improvement gate failed because RAW8 already scored `6/8`. Do not relax or retry the frozen candidate gate.

Interpretation:
- no evidence of B/C integration regression;
- do not promote an always-on CAP8 bundle;
- retain strict-output and verification-first separately as targeted capabilities;
- calculator remains excluded.

## Current checkpoint — Capability Selector v0

Preregistration:
`research/architecture/loom-capability-selector-v0-001-preregistration.md`.

Goal: test a zero-inference deterministic selector for `NORMAL`, `STRICT_OUTPUT`, `VERIFY_FIRST` on 15 unseen mixed/adversarial prompts.

This checkpoint performs **no model inference**. The exact selector rules and acceptance gate are frozen in the preregistration. Create only:
`scripts/loom_capability_selector_v0_001.py`.

If GO, next validate end-to-end conditional dispatch with 8B. If NO_GO, keep B/C explicitly invoked and do not tune on the same prompts.

No calculator reactivation, 30B threshold work, memory/RAG, provider/UI, fine-tuning or Heretic in this selector checkpoint.
