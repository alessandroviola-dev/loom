# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE

## Purpose

Replace user-facing micro-checkpoints with a small number of substantial Pi work packages.

Scientific gates are retained as internal decision gates. Pi should record failed experiments, revert regressions, and continue inside the same work package rather than returning after every GO/NO_GO.

A work package ends only when its substantial deliverable is complete or a genuine blocker requires user action, credentials, destructive/security-sensitive host changes, unavailable storage/hardware, or a project-direction choice not resolvable from existing goals/evidence.

This is not one monolithic task. The current push is divided into four coherent macro work packages.

## WP1 — Runtime + Product Serving

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Goal:
Leave the canonical 30B DEEP model reliably usable through a persistent local serving path, browser UI, and Pi, while retaining the best validated runtime acceleration reachable under bounded evidence-based iteration.

Internal scope:
- audit existing builds/runtime/scripts;
- turn the current paging/I/O instrumentation design into a minimal source-level measurement path if needed;
- build an isolated instrumented runtime when required;
- perform paging/decode attribution;
- test up to three materially different evidence-backed decode interventions, including expert prefetch/overlap or scheduling/residency changes when justified;
- keep only improvements that survive repeated bounded A/B tests;
- retain canonical S24 as rollback baseline;
- build/use `llama-server` from provenance-controlled source if compatible with Apple MoE paging, otherwise create the smallest reliable local service wrapper;
- localhost-only API, preferably OpenAI-compatible;
- enable validated stable-prefix prompt-cache behavior where applicable;
- provide health/start/stop/logging;
- provide a minimal usable local web chat;
- configure and test Pi against the local model/provider;
- record decode, prompt/prefill, E2E, RAM and swap;
- add lightweight local tracing sufficient for operational diagnosis.

Acceleration stopping rule:
- target >=5 tok/s decode first;
- continue only while evidence shows low-risk headroom;
- after three materially different evidence-backed interventions fail to beat the best validated runtime, stop micro-optimization and finish serving/integration.

WP1 completion means the 30B stack is practically usable even if later capability layers are not yet installed.

## WP2 — Agent Capability Layer

Checkpoint:
`LOOM_AGENT_CAPABILITY_WP2`

Goal:
Improve real Pi/LOOM task efficiency and continuity using the mechanisms already researched in the project papers without turning Pi into a heavy generic agent framework.

Engineering inputs:
- Caveman: typed deterministic compression, budgeted context selection, recovery handles;
- LoopX: durable state outside transcript, compact re-entry packet;
- Cavemem: local progressive memory and exact retrieval on demand;
- Observal: local trace/accounting/replay philosophy;
- pi-dynamic-workflows: bounded optional workflow/journal only for genuinely decomposable tasks.

Internal scope:
- implement a lightweight LOOM-native trace schema (JSONL/SQLite first);
- durable project goal/frontier/evidence/blocker state;
- deterministic context selection under a token budget;
- preserve chronology after selection;
- exact recovery references for omitted evidence;
- progressive local searchable memory where useful;
- optional bounded subtask workflow/resume only when it lowers net cost;
- measure permanent overhead, tokens before/after, retries/recovery and task quality;
- keep features optional/off by default when net utility is negative.

WP2 completion requires measured net benefit on representative LOOM/Pi work, not mere feature presence.

## WP3 — Behavioral Transform / Heretic

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Goal:
Produce and validate an actual model/adapter-level behavioral-freedom transform for the final LOOM profile. Prompt-only behavior does not satisfy this work package.

Primary research basis:
`LOOM_HERETIC_TECHNICAL_PAPER.md` and project behavioral requirement.

Important constraint:
The canonical DEEP artifact is GGUF, while upstream Heretic is Transformers/PEFT-oriented. Therefore this work package is intentionally separate from WP1/WP2.

Allowed technical routes, ordered by preference:
1. compatible local Heretic representation and exportable/runtime-loadable low-rank artifact;
2. technically valid conversion/export route to llama.cpp-compatible adapter/artifact;
3. clean LOOM-native implementation of the documented contrastive residual-direction + low-rank edit principle;
4. if local physical/toolchain constraints make an actual transform impossible, produce exact evidence of the blocker rather than relabeling prompt instructions as a model edit.

Execution policy:
- freeze provenance/datasets/evaluation before expensive search;
- prefer streaming residual statistics and low-memory methods;
- prefer searchless/small-search baselines before wide TPE sweeps;
- preserve quality/capability/resource metrics;
- retain exact hashes and rollback baseline;
- final serving path must be able to load/use the resulting profile for WP3 GO.

## WP4 — Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Goal:
Assemble the best validated outputs of WP1–WP3 into the final practical LOOM system.

Required acceptance:
- reliable clean startup;
- localhost serving/API healthy;
- browser chat works;
- Pi works against local LOOM;
- selected runtime acceleration active;
- validated prompt cache active where applicable;
- agent capability layer enabled only where net-positive;
- behavioral-transform profile loaded and validated, or explicitly classified blocked by evidenced physical/toolchain constraints;
- representative capability smoke tests pass;
- final decode/prefill/E2E/RAM/swap recorded;
- simple documented start/stop/health flow;
- exact artifact/config/source hashes and evidence roots retained.

## Global execution rules

1. Do not return after routine internal NO_GO results.
2. Record and revert regressions, then continue.
3. Never relax a frozen scientific gate after seeing its result.
4. Keep a known-good runnable baseline throughout.
5. Prefer small LOOM-native implementations over installing whole upstream systems.
6. No public internet exposure by default.
7. No SIP/security disabling, destructive system actions, unrelated user-data deletion, or paid-cloud/credential requirements without returning to the user.
8. Pi does not commit/push; ChatGPT persists canonical Git state at macro-work-package boundaries.
9. Intermediate evidence remains under `results-local/`.
10. A macro work package should return one bounded end report with deliverables, measurements, failed/reverted attempts, changed files, commands and evidence roots.

## Current work package

`LOOM_RUNTIME_PRODUCTIZATION_WP1`
