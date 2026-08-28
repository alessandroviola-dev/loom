# LOOM — Pi Agent Protocol

Version: 3.55
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

## Mission / architecture

**Big models. Small machines.** Target one adaptive LOOM system:
- **FAST** — lightweight tier for easy/cheap tasks;
- **BALANCED / 8B** — default candidate for most work;
- **DEEP / 30B** — expensive tier for tasks where measured quality gain justifies latency;
- **LOOM AUTO** — cheapest likely-successful tier with verification-driven escalation.

The original ~4B FAST concept remains architecturally useful, but the legacy llama.cpp 4B path is parked for current tier selection. A future FAST tier may be reintroduced through a cleaner runtime such as MLX after higher-value 8B/30B work.

Do not freeze router thresholds before matched multi-task evidence.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core final-project track. Execute after runtime-role selection/initial optimization with frozen refusal/steerability and capability-preservation gates. Do not claim unmeasured absolute guardrail-free status.

## 30B DEEP

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`.
Manual LRUCache under 384 output tokens: correct O(1) design and `get()->-1`, task INCOMPLETE during `put()`, latency minutes.

## 8B BALANCED

Matched result: `research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`.
Classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`; p50/p95 `68.932/71.667 ms`; MLX peak `3,912,428,412 B`; swap peak `2498.62 MB`.
Output chose correct O(1) architecture but remained unfinished. Not a coding-quality PASS.

Runtime remains Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.

## 4B FAST — PARKED FOR CURRENT PHASE

Historical condition existed: Qwen3-4B Q4_K_M on pinned llama.cpp/Metal, historical text generation `22.33 tok/s ±0.02`.

Final closure:
`research/architecture/loom-4b-final-bakeoff-attempt-001-result.md`.
Classification: **`LOOM_4B_FINAL_ATTEMPT_ABORTED`**.
Evidence: `results-local/research/4b-final-bakeoff-attempt-001/20260828T151352Z/`.

No inference occurred in final attempt because frozen runner-resolved `llama-server` path was absent. Model SHA remained verified. This is mechanical availability only, not a capability result.

Do not open another legacy 4B recovery/debug/rebuild checkpoint in this phase. Continue with 8B + 30B. Future FAST reintroduction requires a new clean runtime checkpoint.

## Current checkpoint — compact 8B vs 30B practical suite

Preregistration:
`research/architecture/loom-8b-30b-compact-practical-suite-001-preregistration.md`.

Purpose: determine where 30B produces enough correctness gain over 8B to justify much higher latency.

Frozen suite: five concise tasks, each run independently on both tiers with fixed prompts/output caps and no tools/skills/memory/RAG/Heretic/retries.

Tasks cover:
- arithmetic/reasoning;
- debugging;
- strict structured instruction following;
- supplied-context reasoning;
- concise software-design/escalation judgement.

Primary product quantity: quality/correctness gain of 30B versus additional waiting time and resource cost.

Do not optimize either tier before this result. Do not reactivate 4B. Do not implement routing thresholds before review.

After the compact result:
1. decide whether 8B should be default/primary and identify any proven 30B escalation categories;
2. optimize selected tiers with skills/protocols, memory, tools and verification;
3. build LOOM AUTO;
4. expose via local OpenAI-compatible provider/Pi/chat UI;
5. execute mandatory LOOM Heretic behavioral/steerability integration with preservation gates.
