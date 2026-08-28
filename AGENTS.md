# LOOM — Pi Agent Protocol

Version: 3.50
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. required gate instrumentation must persist before evidence is accepted;
8. failed frozen methods are not silently modified/rerun under the same checkpoint;
9. Integration Readiness Protocol v1 is mandatory before integration coding/model forward;
10. production code is canonical only after exact review and Git persistence;
11. production/user-facing Python must not depend on untracked research helper modules;
12. token streaming must use tokenizer-compatible stateful detokenization and stop/control tokens must not be emitted;
13. user-facing runtime claims require real end-to-end generation evidence.

External root: `<external-archive>/`

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB where multiple model sizes, tools, memory, skills/protocols and behavioral steering work as one adaptive system.

## Target LOOM architecture — THREE-TIER AUTO ROUTING

LOOM is not a single-model runtime. Target product architecture:

- **LOOM FAST / ~4B** — maximize speed, TTFT, low memory and effective capability through skills, protocols, tools and memory; default for easy tasks.
- **LOOM BALANCED / ~8B** — optimized middle tier for tasks where 4B is insufficient but 30B latency is not justified.
- **LOOM DEEP / 30B** — slow large-model tier for difficult tasks where measured capability gain justifies latency.
- **LOOM AUTO** — router chooses the cheapest tier likely to solve the task and may escalate 4B -> 8B -> 30B when confidence/verification is insufficient.

All tiers should eventually share the same higher-level LOOM services where compatible: memory/retrieval, skills/protocols, tools, verification, context handling and provider/API layer.

Do not freeze router thresholds before matched 4B/8B/30B evidence exists. Routing policy must be based on measured task success, latency and resource cost rather than nominal parameter count.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL TRACK

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental design input to the project, not an optional side experiment.

The implementation checkpoint remains scheduled after runtime-role selection so edits can be applied to the tiers that actually matter, but the final LOOM architecture must include a measured Heretic-inspired behavioral/steerability layer unless evidence proves the mechanism unsuitable.

Scientific language remains refusal suppression / steerability. Freeze behavioral and capability-preservation gates before edits; do not claim unmeasured absolute `guardrail-free` status.

## Frozen Qwen3-30B-A3B research comparator

Canonical expert backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Backend commit: `96958de`.
Backend SHA-256: `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact-Q4/top-8 sustained 3x32: `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Closed current-verifier speed paths:
- expert-major accepted/canonical;
- routing sparsity no acceptable gain;
- Q2/Q3 from deployed Q4 fidelity fail;
- DFlash closed;
- exact K=4 oracle verifier ceiling `1.792925 tok/s`, not promising for a real drafter.

## Qwen3.8 readiness — BOTH PORTABLE, EXECUTION PARKED

`QWEN38_BOTH_PORTABLE` from metadata-only readiness.
Qwen3.8-27B projected dense-streamed external traffic: `13,702,468,608 B/token`.
Qwen3.8-Flash-Next projected external baseline: `3,858,155,864 B/token`.
Both large executions remain parked until after practical 30B/8B/4B comparison unless explicitly reactivated.

## LOOM 30B Interactive Runtime v1 — CANONICAL / FUNCTIONAL_SLOW

Historical functional classification:
`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Result:
`research/architecture/loom-30b-interactive-runtime-v1-001-result.md`
Evidence:
`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`

Validated environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Historical long-form metrics:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Only frozen READY miss: TTFT >30 s. Do not relax this threshold post hoc.

Canonicalization repair: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`.
EOS-finalize micro-repair: `LOOM_30B_INTERACTIVE_V1_EOS_FINALIZE_GO`.

Canonical production runtime commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c` — `feat: add canonical LOOM 30B interactive runtime`.

Canonical files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA-256 `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA-256 `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Canonical guarantees:
- 16-position token/routing/float32-logit SHA parity PASS;
- exact incremental KV/recurrent reuse PASS;
- no full transcript re-prefill;
- stateful Unicode streaming equivalence PASS;
- EOS/control marker never emitted;
- detokenizer finalized on EOS and length termination;
- literal `<|im_end|>` user-content boundary smoke PASS;
- `7319` conversation smoke PASS;
- PACKED-only; SOURCE fallback 0; no persistent expert payload cache; deterministic packed fd close.

## Manual-use finding 2026-08-28

The canonical CLI accepts one terminal line per `input()` call; pasting a multi-line prompt causes subsequent pasted lines to be consumed as separate turns. Treat this as a UI/harness limitation, not a model-semantic failure. Final product should use a proper provider/API/UI (e.g. OpenAI-compatible service consumed by Pi/WebUI) rather than extending this validation CLI indefinitely.

First real coding task, single-line LRUCache prompt:
- 30B selected the correct O(1) design: dictionary + doubly linked list;
- `get()` correctly returned `-1` and refreshed recency;
- generation hit the configured output-length limit while implementing `put()`, leaving the program incomplete;
- manual user observation: latency for this small task was already measured subjectively in minutes and is difficult to tolerate.

This is evidence for the practical bake-off: incomplete output under the configured token budget counts against end-to-end task utility even when partial reasoning is sound.

## Current checkpoint — PRACTICAL 30B / 8B / 4B BAKE-OFF PREPARATION

Manual 30B use has established that the runtime works and that latency is a material usability problem. Do not spend more work polishing the temporary CLI before model-size comparison.

Next:
1. identify the already-downloaded 4B and 8B local models/runtime artifacts;
2. freeze a compact matched practical evaluation set and output budgets;
3. run 30B/8B/4B on identical prompts where possible;
4. measure correctness/completion, TTFT, total time, decode rate, memory/swap and subjective usability;
5. choose initial FAST/BALANCED/DEEP roles from evidence;
6. only then optimize each tier and design `LOOM AUTO` routing/escalation.

After role selection, open the mandatory LOOM Heretic behavioral/steerability integration track with frozen preservation gates.

Separate R&D may continue on materially new 30B speed mechanisms, but must not block tiered-system product work.