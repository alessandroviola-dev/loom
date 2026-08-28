# LOOM Roadmap

Last updated: 2026-08-28
Current: canonical LOOM 30B DEEP exists; recovered LOOM 8B BALANCED reproduced historical performance on the matched LRUCache task but remained incomplete at the 384-token cap.
Immediate next: recover/port LOOM 4B FAST and run the same matched task before broader multi-task comparison.
Canonical context: `/AGENTS.md` v3.52.

## 1. Product direction — LOOM AUTO

LOOM is a multi-tier inference system:
- `loom-fast` -> optimized ~4B;
- `loom-balanced` -> optimized ~8B;
- `loom-deep` -> optimized 30B;
- `loom-auto` -> evidence-based routing plus escalation 4B -> 8B -> 30B when verification/confidence is insufficient.

All selected tiers should later share compatible LOOM memory/retrieval, skills/protocols, tools, verification and provider/API integration.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core, non-optional project track. Execute after runtime roles are selected and initially optimized. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Local-root discipline

GitHub is canonical.
Active clone with validated 30B/8B `results-local` artifacts:
`<repository-root>`.
Separate archive/clone:
`<external-archive>`.
Do not mix relative paths/artifacts across roots in one experiment.

## 4. LOOM 30B DEEP baseline

Qwen3-30B-A3B exact-Q4/top-8 expert-major backend; production runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Manual LRUCache prompt under 384-token budget: correct O(1) architecture and correct `get()->-1`, but incomplete during `put()`; subjective latency minutes.

## 5. LOOM 8B BALANCED matched result

Result:
`research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`.

Classification: `LOOM_8B_BAKEOFF_RUNNER_PASS`; task status `INCOMPLETE` at 384 tokens.

Matched performance:
- TTFT `2.992 s`;
- generation `13.357 tok/s`;
- end-to-end output `12.275 tok/s`;
- end-to-end wall `31.284 s`;
- p50/p95 forward `68.932 / 71.667 ms`;
- MLX active `3,583,928,328 B`, peak `3,912,428,412 B`;
- peak swap `2498.62 MB`;
- 38 cleanups / `2.140 s`.

Visible output selected the correct dictionary + doubly-linked-list O(1) strategy and correct `get()->-1`, but stopped in `put()` before a complete executable program/test. This is not a coding-quality PASS.

Historical REALGEN 001 was `13.184615 tok/s` generation / `12.046861 tok/s` end-to-end, so the recovered 8B runtime remains reproducible. The longer prompt's TTFT must not be interpreted alone as a runtime regression.

## 6. Immediate — LOOM 4B FAST matched recovery/port

Known candidate artifacts:
- Ollama `qwen3.5:4b-mlx` (4.0 GB);
- archived `<external-archive>/models/Qwen3-4B-GGUF` (~2.3 GB).

First search Git history and active local artifacts for an existing LOOM 4B runtime/benchmark. Prefer recovery over rebuilding.

Then run one matched one-shot condition with the exact LRUCache prompt and max 384 generated tokens. Measure:
- complete output + task completion;
- TTFT;
- prefill/generation/end-to-end wall and tok/s;
- p50/p95 token-forward latency;
- cleanup;
- MLX/system memory or equivalent runtime memory telemetry;
- swap;
- exact model/runtime provenance.

Bare Ollama output is not the preferred primary result. If runtime parity with the 8B is impossible from existing artifacts, record the runtime factor explicitly rather than pretending the comparison is one-factor.

## 7. Broader matched 4B/8B/30B bake-off

After the single-task 4B run, freeze a compact practical suite spanning:
- coding from specification;
- debugging;
- reasoning/math;
- structured instruction following;
- Italian technical explanation;
- supplied-context reasoning;
- planning/tool-use decisions.

Score task correctness/completion together with TTFT, total time, decode rate, memory/swap and time-to-correct-task. One LRUCache task is insufficient to freeze tier boundaries.

## 8. Tier optimization

Only after raw matched evidence:
- 4B FAST: optimize latency, memory, skills/protocols, tools and verification;
- 8B BALANCED: optimize quality/latency ratio;
- 30B DEEP: reserve for tasks where measured gain justifies latency and continue separate speed R&D.

## 9. LOOM AUTO router

After tier boundaries are measured, implement deterministic routing + optional small-model classification and verification-driven escalation. Expose `loom-fast`, `loom-balanced`, `loom-deep`, and `loom-auto`.

## 10. Provider/UI integration

After runtime roles are selected, expose LOOM via a standard local OpenAI-compatible provider/service consumable by Pi and a proper chat UI instead of extending temporary custom CLIs.

## 11. Mandatory Heretic integration

After tier selection/initial optimization, open a separate preregistered Heretic-inspired refusal/steerability editing checkpoint with capability-preservation gates. Determine whether edits apply to all tiers or selected tiers from measured behavior.

## 12. Separate R&D

Qwen3.8 and materially new 30B speed hypotheses remain separate and must not block the tiered product path.