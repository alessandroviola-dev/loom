# LOOM — Pi Agent Protocol

Version: 3.61
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
- **LOOM AUTO** — move toward `8B -> post-generation validator -> accept / repair / 30B escalation`, rather than trusting a pre-inference prompt classifier.

Do not freeze 30B escalation thresholds yet.

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
Historical Direct MLX 4-bit continuous profile resource-failed even after controlled 72–74% free-memory launch. The later KV8 rescue branch has no canonical quality classification. Do not reopen from current evidence; there is no valid quality result showing 4-bit solves the present correctness issue.

### 4B FAST — PARKED
Final closure `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference in final attempt. Mechanical availability only, not capability evidence. Do not reopen legacy 4B recovery in current phase.

## Key capability evidence

Compact 8B-vs-30B suite:
- 8B utility `4/10`, wall `35.325 s`;
- 30B utility `7/10`, wall `468.867 s`;
- +3 utility cost +`433.541 s` (~12.27x wall).

8B capability funnel:
- calculator: **REJECTED**;
- strict-output: **ACCEPTED branch-level**;
- verification-first: **ACCEPTED branch-level**.

Capability Candidate v1:
- `LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO` because CAP8 improved only `+1` vs frozen required `+2`;
- CAP8 nevertheless matched 30B `7/8` on that fresh set with `26.311 s` vs `284.591 s` wall;
- do not promote an always-on bundle.

Capability Selector v0 isolated test:
- `LOOM_CAPABILITY_SELECTOR_V0_GO` on its 15-item selector-only set;
- 15/15, zero NORMAL false activations, microsecond overhead.

This isolated GO did not generalize sufficiently in the end-to-end mixed suite.

## Auto Capability Dispatch 001 — original mechanical invalid

Original result:
`research/architecture/loom-8b-auto-capability-dispatch-001-result.md`.
Classification `LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO` because post-inference cleanup-evidence instrumentation failed; valid scientific conditions `0/18`.
Original remains permanently closed.

## Auto Capability Dispatch 001 FIX1 — COMPLETE / SCIENTIFIC NO_GO

Result:
`research/architecture/loom-8b-auto-capability-dispatch-001-fix1-result.md`.
Evidence:
`results-local/research/8b-auto-capability-dispatch-001-fix1/20260828T165528Z/`.
Classification: **`LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_NO_GO`**.

All 18 frozen conditions valid after the separately preregistered cleanup-only FIX1.

Frozen gate:
- all 18 valid: PASS;
- selector >=8/9: FAIL — `7/9`;
- NORMAL false activations 0/3: FAIL — `1/3`;
- AUTO8 >=RAW8 +2 utility: PASS — `8 vs 6`;
- zero per-task utility regressions: PASS;
- AUTO8 >=7/9 CORRECT: FAIL — `2/9`.

RAW8 aggregate: utility `6`, C/P/I `1/4/4`, median TTFT `1.517422 s`, pooled generation `12.865656 tok/s`, E2E wall `45.979878 s`.
AUTO8 aggregate: utility `8`, C/P/I `2/4/3`, median TTFT `2.091046 s`, pooled generation `13.167506 tok/s`, E2E wall `58.924179 s`.

Material selector errors:
- T03 VERIFY_FIRST -> STRICT_OUTPUT;
- T07 expected NORMAL -> VERIFY_FIRST false activation.

Interpretation:
- targeted protocol dispatch can rescue some formatting failures;
- pre-inference deterministic selector v0 does not generalize enough to mixed cues;
- static capability prompts do not solve semantic/incomplete answers; AUTO8 only 2/9 CORRECT;
- do not tune selector/protocols on the exposed T01–T09 set;
- do not build 30B escalation on this selector-first graph.

## Current checkpoint — 8B Output Validator v0 001

Preregistration:
`research/architecture/loom-8b-output-validator-v0-001-preregistration.md`.

Goal: validate a cheap fail-closed post-generation layer:
`prompt -> RAW8 -> PASS / FAIL / UNCERTAIN`.

Validator kind/spec is benchmark-supplied in v0 to isolate validation fidelity. It does not infer task class and does not use a model judge.

Fresh 12-task set:
- exact JSON/CSV/restricted key-value contracts;
- three verification-rule tasks;
- three deliberately open-ended tasks that must return `UNCERTAIN`.

Create only:
`scripts/loom_8b_output_validator_v0_001.py`.

Before model inference run synthetic no-model PASS/FAIL/UNCERTAIN fixtures for every validator kind.

Frozen GO requires:
- 12/12 valid inference/evidence records;
- all synthetic fixtures pass;
- zero false PASS on mechanically invalid T01–T09 outputs;
- T10–T12 all `UNCERTAIN`;
- validator p95 <5 ms;
- exact frozen validator definitions and zero network/package/model/runtime mutation.

No 30B, selector tuning, capability injection, calculator, 4B, retries/repair, memory/RAG, fine-tuning, Heretic, provider/UI or production integration.

If validator v0 GO, next checkpoint may test selective repair and/or 30B escalation only on FAIL/UNCERTAIN results. Heretic remains mandatory after initial runtime/capability optimization.
