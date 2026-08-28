# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — canonical 30B runtime is persisted and manually usable but practically slow. Historical LOOM 8B REALGEN artifacts have been recovered in the active local clone and are ready for a matched one-shot bake-off against the exact 30B LRUCache task.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_PRACTICAL_BAKEOFF_RUNNER_001`
Pi context: `/AGENTS.md` v3.51.

## Local roots

GitHub is canonical.
Active local clone containing validated 30B and historical 8B `results-local` artifacts:
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

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental/non-optional final project track. Execute after runtime-role selection with frozen refusal/steerability and capability-preservation gates.

## Canonical LOOM 30B v1

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
Manual LRUCache prompt: correct O(1) design and `get()->-1`, but the 384-token budget ended during `put()`, leaving the requested complete executable solution unfinished; subjective latency was minutes.

## Recovered LOOM 8B REALGEN baseline

Historical source: `scripts/loom_real_generation_baseline_001.py`.
Local model exists at `results-local/mlx/models/Qwen3-8B-3bit` in active clone; 3.4 GB model snapshot and validated `results-local/mlx/venv-mlx-lm-0.31.3` are present.

Frozen identity:
- `mlx-community/Qwen3-8B-3bit`, revision `619ded3`;
- model weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- Qwen3 non-thinking template;
- real M1 built-in MLX qmv_fast;
- BF16 KV, greedy;
- LOOM cleanup every 10 committed tokens.

REALGEN 001 measured 722 genuine autoregressive generated tokens:
- generation `13.184615 tok/s`;
- end-to-end output `12.046861 tok/s`;
- TTFT ~0.94 s across representative prompts;
- peak MLX `3,826,575,836 B`;
- peak swap `1591.19 MB`.

Stretch-037 S1_R8 is an M5/oracle-path optimization and is ineligible for real M1 chat; do not inject it into this bake-off.

## Exact next step

Preregistration:
`research/architecture/loom-8b-practical-bakeoff-runner-001-preregistration.md`.

Pi creates exactly one new runner:
`scripts/loom_8b_practical_bakeoff_runner_001.py`.

It must preserve the historical REALGEN model/runtime semantics and execute exactly the same single-line LRUCache prompt used manually on 30B with max 384 generated tokens. Persist text, completion reason, TTFT, generation/end-to-end performance, token latency, cleanup, memory/swap and provenance.

No model download, conversion, quantization change, S1_R8 injection, Ollama/llama.cpp, skills/tools/memory, UI work or existing-file modification.

After result/review: run analogous 4B LOOM matched condition, then choose initial tier roles. Provider/UI and Heretic follow after evidence-based tier selection.