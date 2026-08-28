# LOOM Roadmap

Last updated: 2026-08-28
Current: 30B DEEP and 8B BALANCED have matched LRUCache evidence. First 4B FAST attempt did not execute because historical pinned llama.cpp/Metal runtime/server was absent; exact model artifact is verified.
Immediate next: restore the historical pinned 4B llama.cpp/Metal runtime only, then rerun the unchanged 4B matched condition.
Canonical context: `/AGENTS.md` v3.53.

## 1. Product direction — LOOM AUTO

Target one adaptive system:
- `loom-fast` -> optimized ~4B;
- `loom-balanced` -> optimized ~8B;
- `loom-deep` -> optimized 30B;
- `loom-auto` -> cheapest likely-successful tier plus verification-driven escalation 4B -> 8B -> 30B.

Do not freeze routing thresholds before matched multi-task evidence.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional. Execute after runtime roles are selected and initially optimized. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Local-root discipline

Active clone:
`<repository-root>`.
Archive/second clone:
`<external-archive>`.
GitHub is canonical. Do not mix relative artifacts across roots.

## 4. LOOM 30B DEEP

Canonical runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
LRUCache at 384 output tokens: correct O(1) design but task INCOMPLETE; latency minutes.

## 5. LOOM 8B BALANCED

Matched classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`.
Output strategy correct but unfinished during `put()`; not a coding-quality PASS.

## 6. LOOM 4B FAST recovered baseline

Historical Qwen3-4B Q4_K_M on pinned llama.cpp/Metal:
- model SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- historical text generation `22.33 tok/s ±0.02`;
- Metal/max offload validated.

Current exact model artifact verified at:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

First matched attempt result:
`research/architecture/loom-4b-practical-bakeoff-runner-001-result.md`.
Classification `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`; no inference. Missing pinned source/build/server is mechanical only and supports no performance/capability claim.

## 7. Current — pinned llama.cpp runtime restoration

Preregistration:
`research/architecture/loom-4b-llama-runtime-restoration-001-preregistration.md`.

Use tracked `scripts/llama_cpp_setup_probe.py` unchanged to reconstruct exact pinned source/configuration. Official llama.cpp source clone/fetch is authorized. No model network operation is authorized.

After exact setup PASS, build only the missing `llama-server` target in the already configured pinned build. Verify source HEAD, CMake flags, cli/bench/server and Apple M1 Metal device. No model load/inference and no tracked-source modification.

Stop after restoration GO/NO_GO.

## 8. 4B matched rerun

Only after restoration GO, rerun the unchanged local experimental `scripts/loom_4b_practical_bakeoff_runner_001.py` with the same frozen system message, LRUCache prompt, greedy semantics and 384-token cap. Do not change the model/runtime condition between NOT_READY and rerun except restoring the missing historical runtime.

## 9. Broader matched suite

After a valid 4B result, freeze a compact practical 4B/8B/30B suite covering coding, debugging, reasoning/math, structured instruction following, Italian technical explanation, supplied-context reasoning and planning/tool-use decisions.

Score correctness/completion plus TTFT, wall, decode throughput, memory/swap and time-to-correct-task.

## 10. Tier optimization and LOOM AUTO

Only after matched evidence, optimize 4B/8B/30B individually with skills/protocols, memory, tools and verification. Then implement evidence-based routing/escalation and expose `loom-fast`, `loom-balanced`, `loom-deep`, `loom-auto`.

## 11. Provider/UI

After roles are selected, expose LOOM via a local OpenAI-compatible provider usable by Pi and a proper chat UI instead of expanding temporary CLIs.

## 12. Mandatory Heretic integration

After tier selection/initial optimization, execute the separate Heretic-inspired behavioral/steerability track with preservation gates.

## 13. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block tiered product progress.