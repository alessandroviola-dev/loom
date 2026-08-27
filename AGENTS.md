# LOOM — Pi Agent Protocol

Version: 3.33
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, quantitative gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. Integration Readiness Protocol v1 is mandatory before integration coding/model forward: `research/architecture/loom-integration-readiness-protocol-v1.md`;
12. producer/consumer compatibility must be proven mechanically before adapter coding: `consumer_required_coverage ⊆ provider_available_coverage`;
13. static adapter dry-run with zero unresolved accesses and zero forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts must not be promoted implicitly to general runtime artifacts;
15. metadata/coverage/provenance checks should use deterministic scripts/JSON rather than broad Pi reasoning;
16. once a mechanism is accepted by causal + runtime funnels, do not reopen settled validation during productionization unless a canonicalization regression appears.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable 30B target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- routed identities `48 × 128 = 6144`;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- raw 4-GiB global LRU rejected.

## DFlash — CLOSED

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`. Do not reopen absent a new independent mechanism.

## Expert-major physical-I/O — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.

Valid first-touch PACKED/SOURCE ratios: `0.602456`, `0.595950`, `0.581170`; median `0.595950` = `40.405%` lower expert-access wall.

All payload/hash, physical-byte, read-structure, memory and swap gates PASS. Raw expert-major physical-I/O causality is settled.

## Runtime Funnel 001 — readiness failure only

`LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001 = EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.

A 384-expert trace/position-scoped pack could not cover the selected runtime workload. No model forward ran. This produced Integration Readiness Protocol v1; it is not evidence against expert-major.

## Full-Bank Runtime Funnel 002 — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Result:
`research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-result.md`

Evidence:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

Accepted evidence:
- Stage 0 readiness PASS: source `6144/6144`, disk gate PASS;
- Stage 1 full bank PASS: `6144` entries, `15,401,484,288 B`, full hash/provenance PASS;
- Stage 2 static dry-run PASS: `18,048` accesses, `0` unresolved/fallback/cache;
- Stage 3 exactness PASS: 3 full 48-layer decode positions, identical routing and raw final-logit float32 SHA;
- Stage 4 A/B PASS: runtime ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS gate PASS;
- swap delta `0 MiB`;
- no unsafe pressure, fallback or persistent expert cache.

Decision: the full-bank expert-major backend is the accepted runtime direction for the current M1/8GB 30B path. Do not re-run full physical-I/O or runtime acceptance testing absent a regression or materially different target/runtime.

## Current checkpoint — CANONICALIZATION 001

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001`

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-001-preregistration.md`

Purpose: productionize the already accepted experimental full-bank backend into reusable canonical repo code without reopening settled science.

Stages:
1. recover exact accepted builder/manifest/backend implementation and validate retained artifact integrity;
2. integrate minimal reusable SOURCE/PACKED backend code into working tree, preserving SOURCE and all non-I/O semantics;
3. static production gate: compile/syntax, `6144/6144` manifest, `18,048`-access replay, zero unresolved/fallback/cache;
4. exactness regression gate: same 3 accepted decode positions, identical routing + raw float32 final-logit SHA;
5. one bounded process-level SOURCE->PACKED performance/safety smoke only.

Canonicalization GO requires all gates PASS and smoke PACKED/SOURCE decode wall `<=0.95`, RSS <= SOURCE +128 MiB, swap <= SOURCE +64 MiB, no fallback/cache/unsafe pressure.

Pi may edit runtime/source code in the local working tree during this checkpoint but must not commit/push or edit project decision docs.

Final outcomes:
- `EXPERT_MAJOR_CANONICALIZATION_GO`
- `EXPERT_MAJOR_CANONICALIZATION_NO_GO`
- `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`
