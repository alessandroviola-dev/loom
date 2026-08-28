# LOOM — Pi Agent Protocol

Version: 3.52
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

## Local-root clarification

GitHub is canonical. Active local clone with validated 30B and historical 8B `results-local` artifacts:
`<repository-root>`.

Separate archive/clone tree:
`<external-archive>`.

Do not mix relative paths/artifacts across roots in one experiment. External archived model artifacts may be inspected only through explicit absolute paths.

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB where multiple model sizes, tools, memory, skills/protocols and behavioral steering work as one adaptive system.

## Target LOOM architecture — THREE-TIER AUTO ROUTING

- **LOOM FAST / ~4B** — maximize speed, TTFT, low memory and effective capability through skills, protocols, tools and memory; default for easy tasks.
- **LOOM BALANCED / ~8B** — optimized middle tier for tasks where 4B is insufficient but 30B latency is not justified.
- **LOOM DEEP / 30B** — slow large-model tier for difficult tasks where measured capability gain justifies latency.
- **LOOM AUTO** — router chooses the cheapest tier likely to solve the task and may escalate 4B -> 8B -> 30B when confidence/verification is insufficient.

Do not freeze router thresholds before matched evidence exists.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL TRACK

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental design input to final LOOM, not an optional side experiment. Execute after runtime-role selection/initial optimization. Freeze refusal/steerability and capability-preservation gates before edits. Do not claim unmeasured absolute `guardrail-free` status.

## LOOM 30B DEEP baseline

Canonical production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form: TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`.
Manual LRUCache task under 384 output tokens: correct O(1) strategy and `get()->-1`, but output stopped during `put()`; task INCOMPLETE and subjective latency minutes.

## LOOM 8B BALANCED matched result

Historical runtime remains Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF, cleanup every 10 committed tokens.

Matched result:
`research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`
Evidence:
`results-local/research/8b-practical-bakeoff-runner-001/20260828T144423Z/summary.json`

Classification: `LOOM_8B_BAKEOFF_RUNNER_PASS`.
Task status: `INCOMPLETE` because 384-token limit stopped inside `put()` before a complete program/test.

Metrics:
- TTFT `2.992 s`;
- 384 output tokens;
- generation `13.357 tok/s`;
- end-to-end output `12.275 tok/s`;
- end-to-end wall `31.284 s`;
- p50/p95 forward `68.932 / 71.667 ms`;
- MLX active `3,583,928,328 B`, peak `3,912,428,412 B`;
- swap `2363.69 -> 2498.62 MB`, observed peak `2498.62 MB`;
- 38 cleanups, `2.140 s` total cleanup.

Visible partial output chose the correct dictionary + doubly-linked-list O(1) architecture and correct `get()->-1`, but contains an unnecessary `self.key_to` assignment and is visibly unfinished. Do not call this a coding-quality PASS.

Historical REALGEN remains `13.184615 tok/s` generation / `12.046861 tok/s` end-to-end. Current performance is close/slightly higher, confirming the old runtime remains reproducible. Longer prompt TTFT is not by itself a runtime regression claim.

The one-shot 8B runner is local experimental source and not canonical production code unless separately reviewed/persisted.

## Current checkpoint — LOOM 4B FAST matched condition

Next recover/port the existing 4B artifact into the same LOOM-style matched one-shot protocol before adding skills, memory, tools, RAG, prompt optimization or behavioral editing.

Use the same exact LRUCache prompt and 384-token output budget, with comparable measurements: completion, TTFT, generation/end-to-end throughput, wall, p50/p95, cleanup, memory/swap and provenance.

Do not use bare Ollama output as the primary matched result. If the available 4B artifact is only GGUF or Ollama-hosted, first determine the closest LOOM runtime path and preserve a clear runtime-factor distinction.

After the 4B matched result, expand to a compact multi-task 4B/8B/30B bake-off before freezing routing thresholds. Heretic remains mandatory after tier role selection.