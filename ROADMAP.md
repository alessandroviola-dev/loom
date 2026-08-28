# LOOM Roadmap

Last updated: 2026-08-28
Current: canonical LOOM 30B v1 is manually usable but slow; historical LOOM 8B REALGEN baseline has been recovered and is next for matched practical bake-off.
Immediate next: run the exact 30B LRUCache task on recovered LOOM 8B with a frozen 384-token budget and full metrics.
Canonical context: `/AGENTS.md` v3.51.

## 1. Product direction — LOOM AUTO

LOOM is a multi-tier inference system:
- `loom-fast` -> optimized ~4B;
- `loom-balanced` -> optimized ~8B;
- `loom-deep` -> optimized 30B;
- `loom-auto` -> evidence-based routing plus escalation 4B -> 8B -> 30B when verification/confidence is insufficient.

All tiers should later share compatible LOOM memory/retrieval, skills/protocols, tools, verification and provider/API integration.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core, non-optional project track. Execute after runtime roles are selected and initially optimized. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Local-root discipline

GitHub is canonical.
Active local clone with validated 30B/8B `results-local` artifacts:
`<repository-root>`.

Separate archive/clone:
`<external-archive>`.

Do not mix relative paths/artifacts across roots in one experiment.

## 4. LOOM 30B DEEP baseline

Qwen3-30B-A3B exact-Q4/top-8 expert-major backend; production runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Manual LRUCache prompt under 384-token output budget: correct O(1) architecture and correct `get()->-1`, but incomplete during `put()`; subjective latency minutes.

## 5. Recovered LOOM 8B BALANCED baseline

Historical source: `scripts/loom_real_generation_baseline_001.py`.
Model: `mlx-community/Qwen3-8B-3bit`, revision `619ded3`, local 3-bit/group64 artifact and validated MLX venv present.
Runtime: MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`, Qwen3 non-thinking template, greedy real M1 built-in qmv_fast, BF16 KV, cleanup every 10 committed generated tokens.

REALGEN 001:
- 722 real generated tokens;
- generation `13.184615 tok/s`;
- end-to-end output `12.046861 tok/s`;
- TTFT roughly `0.94 s` across representative prompts;
- peak MLX `3,826,575,836 B`;
- peak swap `1591.19 MB`.

Stretch-037 S1_R8 is M5/oracle-only and must not be injected into real M1 generation.

## 6. Current experiment — 8B matched LRUCache bake-off

Preregistration:
`research/architecture/loom-8b-practical-bakeoff-runner-001-preregistration.md`.

Create only `scripts/loom_8b_practical_bakeoff_runner_001.py`, derived from REALGEN with no model/runtime semantic changes.

Frozen task: exact same single-line LRUCache prompt used on 30B, max 384 generated tokens.

Measure:
- full output and task completion;
- EOS vs length stop;
- TTFT;
- prefill/generation/end-to-end wall and tok/s;
- p50/p95 token-forward latency;
- cleanup wall/count;
- MLX/system memory and swap;
- provenance.

No model downloads/conversions, S1_R8, Ollama/llama.cpp, skills/tools/memory or UI changes in this checkpoint.

## 7. Next — LOOM 4B FAST

After 8B result/review, recover or minimally port the existing 4B artifact into an analogous LOOM matched condition. Use the same task/output budget before adding skills/protocols/tools.

## 8. Role selection and optimization

Once matched 4B/8B/30B evidence exists, choose initial FAST/BALANCED/DEEP boundaries from correct/useful work per latency and memory cost. Then optimize each tier and build LOOM AUTO routing/escalation.

## 9. Provider/UI integration

After tier roles are selected, expose LOOM via a standard local OpenAI-compatible provider/service consumable by Pi and a proper chat UI instead of extending the temporary custom CLIs.

## 10. Mandatory Heretic integration

After tier selection/initial optimization, open a separate preregistered Heretic-inspired refusal/steerability editing checkpoint with capability-preservation gates. Determine whether edits should apply to all tiers or selected tiers from measured behavior.

## 11. Separate R&D

Qwen3.8 and materially new 30B speed hypotheses remain separate and must not block the tiered product path.