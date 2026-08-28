# LOOM — Pi Agent Protocol

Version: 3.59
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
- **LOOM AUTO** — capability selector -> conditional protocol -> 8B -> validation -> 30B only when unresolved.

Do not freeze 30B escalation thresholds yet.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains a core final-project track. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Runtime baselines

### 30B DEEP
Canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Compact-suite pooled generation `1.402 tok/s`, median TTFT `50.671 s`.

### 8B BALANCED
Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Historical REALGEN ~`13.18 tok/s`.
Compact-suite pooled generation `12.931 tok/s`, median TTFT `2.006 s`.

### 4B FAST — PARKED
Final closure `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference in final attempt. Mechanical availability only, not capability evidence. Do not reopen legacy 4B recovery in current phase.

## Key capability evidence

Compact 8B-vs-30B suite:
- 8B utility `4/10`, wall `35.325 s`;
- 30B utility `7/10`, wall `468.867 s`;
- +3 utility cost +`433.541 s` (~12.27x wall).

8B capability funnel:
- calculator: **REJECTED**;
- strict-output: **ACCEPTED**;
- verification-first: **ACCEPTED**.

Capability Candidate v1:
- **`LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO`** because CAP8 improved only `+1` vs required `+2`;
- CAP8 still matched 30B `7/8` on that fresh set with `26.311 s` vs `284.591 s` wall;
- do not relax/retry candidate gate;
- retain strict-output and verification-first as targeted capabilities, not an always-on bundle.

## Capability Selector v0 — COMPLETE / GO

Result: `research/architecture/loom-capability-selector-v0-001-result.md`.
Evidence: `results-local/research/capability-selector-v0-001/20260828T163136Z/evidence.json`.
Classification: **`LOOM_CAPABILITY_SELECTOR_V0_GO`**.

Frozen deterministic selector over `NORMAL`, `STRICT_OUTPUT`, `VERIFY_FIRST`:
- accuracy `15/15`;
- per-label precision/recall/F1 all `1.0000`;
- expected-NORMAL false activations `0/7`;
- selector p50/p95 `8 us / 218 us`;
- zero model inference/network/external packages.

This GO authorizes end-to-end conditional 8B dispatch. It does not prove general semantic classification and does not authorize 30B routing thresholds.

## Current checkpoint — 8B Auto Capability Dispatch 001

Preregistration:
`research/architecture/loom-8b-auto-capability-dispatch-001-preregistration.md`.

Goal: compare RAW8 vs AUTO8 on 9 fresh mixed tasks using the exact frozen selector and exact accepted protocol strings.

AUTO8 graph:
`prompt -> selector v0 -> NORMAL / STRICT_OUTPUT / VERIFY_FIRST -> 8B`.

Task mix:
- 3 NORMAL, including adversarial cue cases;
- 3 STRICT_OUTPUT;
- 3 VERIFY_FIRST.

Create only:
`scripts/loom_8b_auto_capability_dispatch_001.py`.

Frozen GO requires all 18 conditions valid, selector >=8/9, zero NORMAL false activations, AUTO8 >=RAW8 +2 utility, zero per-task regressions, >=7/9 AUTO8 CORRECT, and unchanged selector/protocol definitions.

No 30B inference, calculator, 4B, downloads, runtime changes, selector tuning, protocol changes, retries, memory/RAG, tools, fine-tuning, Heretic, provider/UI or production integration.

If GO, next checkpoint is output validation plus selective 30B escalation. Heretic remains mandatory after initial runtime/capability optimization.
