# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — canonical 30B runtime is persisted and manually usable but slow. Historical LOOM 8B REALGEN was recovered and successfully reproduced on the exact 30B LRUCache task with matched 384-token budget. The 8B runner passed runtime/provenance gates but the task remained incomplete at the token cap. Current checkpoint moves to LOOM 4B FAST matched recovery/port.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_4B_FAST_MATCHED_BAKEOFF_PREP`
Pi context: `/AGENTS.md` v3.52.

## Local roots

GitHub is canonical.
Active clone with validated 30B and historical 8B runtime artifacts:
`<repository-root>`.
Separate archive/clone tree:
`<external-archive>`.
Do not mix relative artifacts across roots in a single experiment.

## Target product architecture

- 4B FAST;
- 8B BALANCED;
- 30B DEEP;
- LOOM AUTO with evidence-based routing/escalation 4B -> 8B -> 30B.

All selected tiers should later share compatible LOOM memory, skills/protocols, tools, verification and provider/API services.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental/non-optional final project track. Execute after runtime-role selection/initial optimization with frozen refusal/steerability and capability-preservation gates.

## LOOM 30B DEEP

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Manual LRUCache under 384 tokens: correct O(1) strategy and `get()->-1`, but stopped during `put()`; task INCOMPLETE and subjective latency minutes.

## LOOM 8B BALANCED matched result

Result:
`research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`
Evidence:
`results-local/research/8b-practical-bakeoff-runner-001/20260828T144423Z/summary.json`

Runtime provenance:
- `mlx-community/Qwen3-8B-3bit@619ded3`;
- verified main weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF;
- cleanup every 10 committed tokens;
- no S1_R8/oracle/speculation/Ollama/llama.cpp/skills/tools/memory.

Classification: `LOOM_8B_BAKEOFF_RUNNER_PASS`.
Task status: `INCOMPLETE` at `MAX_GENERATED_TOKENS_384`.

Metrics:
- TTFT `2.992 s`;
- generation `13.357 tok/s`;
- end-to-end `12.275 tok/s`;
- end-to-end wall `31.284 s`;
- full runner `35.975 s`;
- p50/p95 `68.932 / 71.667 ms`;
- MLX active `3,583,928,328 B`, peak `3,912,428,412 B`;
- swap `2363.69 -> 2498.62 MB`, peak `2498.62 MB`;
- 38 cleanup events, `2.140 s` total.

Visible output chose the correct O(1) dictionary + doubly-linked-list strategy and correct missing-key `-1`, but stopped inside `put()` and had not produced the required test. Do not call it a coding-quality PASS. It is, however, dramatically more usable in latency than the 30B on this task.

Historical REALGEN 001 was `13.184615 tok/s` generation / `12.046861 tok/s` end-to-end, so the recovered runtime remains reproducible under the matched runner.

## Exact next step — LOOM 4B FAST

Recover the existing 4B artifact/runtime and create an analogous bounded one-shot matched condition using the exact same LRUCache prompt and 384-token cap.

Known artifacts from current user inventory:
- Ollama: `qwen3.5:4b-mlx` (4.0 GB), but bare Ollama is not the desired primary comparator;
- archive root contains `<external-archive>/models/Qwen3-4B-GGUF` (~2.3 GB).

Before execution, determine whether an earlier LOOM 4B runtime/runner already exists in Git history/local results. Prefer recovery over rebuilding. If only GGUF/Ollama artifacts exist, select the closest LOOM runtime path and explicitly record any runtime-factor difference from 8B/30B.

Do not add skills, memory, tools, RAG, prompt optimization or Heretic before the raw matched 4B result.

After 4B, expand to a compact multi-task 4B/8B/30B evaluation before freezing router thresholds.