# LOOM — Pi Agent Protocol

Version: 3.63
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
9. Integration Readiness Protocol v1 before production integration/model forward;
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
- **DEEP / 30B** — selective expensive tier, not assumed to repair every failure;
- **FAST** — architecturally retained, legacy 4B path parked;
- **LOOM AUTO** — validator-first: `8B -> validate -> semantics-preserving deterministic repair -> validator-guided cheap repair -> DEEP only if still unresolved` for mechanically verifiable tasks.

Open-ended semantic uncertainty and automatic validator selection remain separate unresolved tracks. Do not freeze general 30B escalation thresholds yet.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains a core final-project track. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Runtime baselines

### 8B BALANCED
`mlx-community/Qwen3-8B-3bit@619ded3`; weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`; 3-bit/group64; Direct MLX; M1 built-in `qmv_fast`; BF16 KV; greedy; thinking OFF.
Historical REALGEN ~`13.18 tok/s`.

### 30B DEEP
Canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Compact-suite pooled generation ~`1.402 tok/s`; median TTFT ~`50.671 s`.

### Closed/parked
- historical 8B 4-bit continuous branch: CLOSED by resource evidence; no valid quality result justifies reopening;
- legacy 4B FAST recovery: PARKED.

## Key prior capability evidence

- compact 8B-vs-30B: 8B utility `4/10`, 30B `7/10`, +`433.541 s` waiting for +3 utility;
- calculator flow REJECTED;
- strict-output / verification-first accepted only at branch level;
- Capability Candidate v1 NO_GO;
- selector v0 isolated GO but end-to-end selector-first dispatch FIX1 NO_GO; do not tune on exposed prompts.

## Output Validator v0 — COMPLETE / GO

Result: `research/architecture/loom-8b-output-validator-v0-001-result.md`.
Evidence: `results-local/research/8b-output-validator-v0-001/20260828T174056Z/`.
Classification: **`LOOM_8B_OUTPUT_VALIDATOR_V0_GO`**.

Observed:
- synthetic `11/11` PASS;
- 12/12 valid records;
- false PASS `0`;
- T10–T12 open-ended `UNCERTAIN 3/3`;
- validator p95 `0.758321 ms`.

Supported: deterministic/task-specific post-generation validation can fail closed when validator kind/spec is known.

## Validator-Guided Selective Rescue 001 — COMPLETE / SCIENTIFIC NO_GO

Result: `research/architecture/loom-validator-guided-selective-rescue-001-result.md`.
Evidence: `results-local/research/validator-guided-selective-rescue-001/20260828T175816Z/`.
Classification: **`LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_NO_GO`**.

Frozen gate:
- valid model calls: PASS;
- false acceptance `0`: PASS;
- safe fence-only repair `2/2`: PASS;
- final CORRECT `5/8` vs required `>=6/8`: **FAIL**;
- RAW8 `2/8` -> final `5/8` (`+3`): PASS;
- 30B calls avoided `4/8`: PASS;
- no unnecessary DEEP calls: PASS.

Cost:
- 8B wall `38.656 s`;
- added 30B wall `246.346 s`;
- 30B calls `4/8`, but only one residual failure became `30B_PASS`;
- validator/repair overhead sub-ms.

Unresolved:
- exact boolean contract failure persisted through DEEP (`enabled=no` vs required `enabled=false`);
- two verification-rule tasks remained incomplete under frozen required components.

Supported conclusion: validator-first and fence-only repair remain useful, but raw one-shot DEEP is not a sufficient universal repair mechanism. Do not relax the `6/8` gate or rescore exposed tasks.

## Current checkpoint — 8B Validator-Guided Repair 001

Preregistration:
`research/architecture/loom-8b-validator-guided-repair-001-preregistration.md`.

Question: before paying DEEP, can one cheap 8B repair use the deterministic validator report to fix a failed mechanically-verifiable answer?

Frozen graph:
`RAW8 -> validator -> PASS accept; FAIL -> existing safe fence-only repair if eligible -> revalidate -> residual FAIL -> exactly one validator-guided 8B repair -> revalidate`.

No 30B inference in this checkpoint.

Repair receives only:
- original request;
- raw failed answer;
- exact deterministic validator failure report.

Create only:
`scripts/loom_8b_validator_guided_repair_001.py`.

Frozen GO requires:
- all required 8B conditions valid;
- zero false acceptance;
- final CORRECT >=6/8 and >=RAW8 +2;
- at least 2 residual FAIL tasks converted by guided 8B repair to validator PASS + ground-truth CORRECT;
- no repair call after initial PASS/successful safe fence repair;
- validator/repair p95 <5 ms;
- exact repair prompt/template frozen;
- zero network/download/package/model/runtime mutation.

No 30B, 4B, selector, calculator, memory/RAG, tools, fine-tuning, Heretic, provider/UI or production integration.

If GO, next checkpoint may insert the validated cheap repair before selective DEEP and then separately address semantic/open-ended validation. If NO_GO, do not tune on the exposed repair set; move to a different mechanism.
