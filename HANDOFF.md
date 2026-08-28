# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — 30B DEEP and 8B BALANCED matched evidence exist. The first 4B FAST matched attempt stopped correctly before inference because the historical pinned llama.cpp/Metal runtime/server was not present. The exact 4B Q4_K_M model artifact is verified. Current checkpoint is mechanical restoration of the historical pinned runtime only.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_4B_LLAMA_RUNTIME_RESTORATION_001`
Pi context: `/AGENTS.md` v3.53.

## Local roots

GitHub is canonical.
Active clone:
`<repository-root>`.
Archive/second clone:
`<external-archive>`.
Do not mix relative artifacts across roots.

## Product architecture direction

- 4B FAST;
- 8B BALANCED;
- 30B DEEP;
- LOOM AUTO with evidence-based routing and escalation 4B -> 8B -> 30B.

Do not freeze router thresholds before broader matched evidence.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional. Execute after tier selection/initial optimization with frozen refusal/steerability and capability-preservation gates.

## 30B matched/manual baseline

Canonical production runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form decode `1.116 tok/s`, TTFT `47.832 s`.
LRUCache with 384-token cap: correct O(1) design but INCOMPLETE during `put()`; waiting time minutes.

## 8B matched result

Result: `research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`.
Classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`; p50/p95 `68.932/71.667 ms`; MLX peak `3,912,428,412 B`; swap peak `2498.62 MB`.

## 4B recovered historical condition

Historical result:
`research/runtime/llama-cpp-4b-control-001.md`.

- Qwen3-4B Q4_K_M;
- model SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- Metal;
- historical text-generation rate `22.33 tok/s ±0.02`.

Verified current model artifact:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

## 4B matched attempt 001 — runtime not ready

Result:
`research/architecture/loom-4b-practical-bakeoff-runner-001-result.md`.
Evidence:
`results-local/research/4b-practical-bakeoff-runner-001/20260828T145853Z/`.

Classification `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`.
No inference, no generated tokens, task NOT_ASSESSED. Model artifact/hash PASS. Missing pinned llama.cpp source/build/`llama-server` was the decisive blocker. No 4B performance/capability comparison is supported.

Local experimental runner:
`scripts/loom_4b_practical_bakeoff_runner_001.py`.
Do not modify/rerun it before restoration GO.

## Exact next action — runtime restoration only

Preregistration:
`research/architecture/loom-4b-llama-runtime-restoration-001-preregistration.md`.

Tracked historical setup probe:
`scripts/llama_cpp_setup_probe.py`, SHA `f7a49cc9e31a3754fcb7d5b0a912f93e2eadbd22`.

Authorized restoration:
1. run setup probe exactly; official llama.cpp source clone/fetch is allowed if needed;
2. require exact pinned source commit and historical Release/Metal CMake flags;
3. after setup PASS, build only missing `llama-server` target in the already-configured build because the tracked probe explicitly builds only cli/bench;
4. verify cli/bench/server diagnostics and Metal device;
5. no model download/copy/load/inference and no tracked-source modification.

Stop after `LOOM_4B_LLAMA_RUNTIME_RESTORATION_GO` or `NO_GO`.

After GO, rerun the unchanged 4B practical bake-off as a separate checkpoint. After valid 4B result, freeze a compact multi-task 4B/8B/30B suite.