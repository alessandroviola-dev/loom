# LOOM Roadmap

Last updated: 2026-08-28
Current: legacy 4B FAST runtime is parked after final mechanical abort; active architecture work continues with validated 8B BALANCED and 30B DEEP tiers.
Immediate next: run the preregistered compact five-task 8B-vs-30B practical suite.
Canonical context: `/AGENTS.md` v3.55.

## 1. Product direction — LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, candidate default;
- `loom-deep` -> optimized 30B, candidate escalation tier;
- future `loom-fast` -> lightweight runtime to be reintroduced later through a cleaner implementation;
- `loom-auto` -> verification-driven routing/escalation.

Do not freeze routing thresholds before current multi-task evidence.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional. Execute after runtime roles are selected and initially optimized. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. LOOM 30B DEEP

Canonical runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
LRUCache / 384 tokens: correct O(1) design but task INCOMPLETE; latency minutes.

## 4. LOOM 8B BALANCED

Matched classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`.
Historical REALGEN remains ~`13.18 tok/s` real generation, confirming reproducibility.

## 5. Legacy 4B FAST — parked

Historical Qwen3-4B Q4_K_M on pinned llama.cpp/Metal had `22.33 tok/s ±0.02`, but current recovery path is closed.

Final result:
`research/architecture/loom-4b-final-bakeoff-attempt-001-result.md`.
Classification `LOOM_4B_FINAL_ATTEMPT_ABORTED`; no inference executed because the frozen runner's expected server path was absent.

No capability conclusion is supported. No more legacy 4B recovery/debug/rebuild work in current phase. Revisit FAST later using a cleaner runtime, likely MLX-native or otherwise aligned with the final provider architecture.

## 6. Compact 8B vs 30B practical suite

Preregistration:
`research/architecture/loom-8b-30b-compact-practical-suite-001-preregistration.md`.

Five concise tasks:
- arithmetic/reasoning;
- debugging;
- strict JSON instruction following;
- supplied-context reasoning;
- verification-driven software/model routing judgement.

Each task is independently run on both models with frozen prompts, fresh state and 80–140 token caps. No tools, skills, memory/RAG, Heretic, retries or runtime optimization.

Measure:
- correctness/partial/incorrect;
- instruction following;
- completion;
- TTFT;
- generation/end-to-end speed;
- wall time;
- memory/swap;
- time per correct task.

Primary decision: whether 30B provides enough correctness gain to justify its much larger latency, and on which task types.

## 7. Tier optimization

After suite review:
- make 8B default if it matches 30B on most practical tasks;
- reserve 30B for task categories where it shows a material correctness advantage;
- improve both with skills/protocols, memory, tools and verification;
- later introduce a clean FAST tier if useful.

## 8. LOOM AUTO

Implement routing only after measured tier boundaries exist. Prefer cheap-first execution plus task-specific verification/escalation over prompt-length heuristics.

Expose eventually:
- `loom-fast`;
- `loom-balanced`;
- `loom-deep`;
- `loom-auto`.

## 9. Provider/UI

Expose selected runtimes through a local OpenAI-compatible provider usable by Pi and a proper chat UI rather than extending temporary custom CLIs.

## 10. Mandatory Heretic integration

After tier selection/initial optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates. Determine per-tier application from measured behavior.

## 11. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block tiered product progress.
