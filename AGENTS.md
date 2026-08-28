# LOOM — Pi Agent Protocol

Version: 3.53
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.
After every significant checkpoint, ChatGPT updates canonical GitHub state and user pulls before next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. invalid comparison if more than intended treatment factor changes;
4. expensive/network work requires retained artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. required gate instrumentation must persist;
8. failed frozen methods are not silently rerun under same checkpoint;
9. Integration Readiness Protocol v1 before integration coding/model forward;
10. production code canonical only after exact review + Git persistence;
11. production/user-facing Python must not depend on untracked research helpers;
12. stateful tokenizer-compatible streaming; stop/control tokens not emitted;
13. user-facing runtime claims require real end-to-end evidence.

## Local roots

GitHub is canonical.
Active clone:
`<repository-root>`.
Separate archive/clone:
`<external-archive>`.
Do not mix relative artifacts across roots. Archive artifacts require explicit absolute paths.

## Mission / target architecture

**Big models. Small machines.** Target one adaptive LOOM system:
- **4B FAST** — easy/cheap tasks, optimized latency/memory + skills/protocols/tools/memory later;
- **8B BALANCED** — middle tier;
- **30B DEEP** — hard tasks where quality gain justifies latency;
- **LOOM AUTO** — cheapest likely-successful tier with verification-driven escalation 4B -> 8B -> 30B.

Do not freeze router thresholds before matched multi-task evidence.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core final-project track. Execute after runtime-role selection/initial optimization with frozen refusal/steerability and capability-preservation gates. Do not claim unmeasured absolute guardrail-free status.

## LOOM 30B DEEP baseline

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`.
Matched/manual LRUCache under 384 output tokens: correct O(1) design and `get()->-1`, but task INCOMPLETE during `put()`; latency minutes.

## LOOM 8B BALANCED matched result

Result: `research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`.
Evidence: `results-local/research/8b-practical-bakeoff-runner-001/20260828T144423Z/summary.json`.

Runtime: Qwen3-8B 3-bit/group64 Direct MLX, real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF, cleanup every 10 committed tokens.

Classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task `INCOMPLETE` at 384 tokens.
Metrics: TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`; p50/p95 `68.932/71.667 ms`; MLX peak `3,912,428,412 B`; swap peak `2498.62 MB`; 38 cleanups / `2.140 s`.
Output chose correct O(1) architecture but stopped in `put()` and contained an unnecessary `self.key_to` assignment. Not a coding-quality PASS.

## LOOM 4B FAST — recovered historical condition

Historical canonical runtime control:
`research/runtime/llama-cpp-4b-control-001.md`.

Historical model/runtime:
- `Qwen/Qwen3-4B-GGUF`;
- `Qwen3-4B-Q4_K_M.gguf`;
- Q4_K_M;
- SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- Metal, `-ngl -1`, Flash Attention auto;
- historical text generation `22.33 tok/s ± 0.02`.

Exact model artifact is currently verified in archive:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

## 4B matched attempt — MECHANICAL NOT READY

Result:
`research/architecture/loom-4b-practical-bakeoff-runner-001-result.md`.
Evidence:
`results-local/research/4b-practical-bakeoff-runner-001/20260828T145853Z/`.

Classification: `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`.
No inference occurred. Model SHA passed; task `NOT_ASSESSED`. Historical pinned llama.cpp source/build/server was unavailable in active clone, so Pi correctly stopped. This supports no 4B capability/performance claim.

Local experimental runner exists:
`scripts/loom_4b_practical_bakeoff_runner_001.py`.
Do not modify/rerun it until restoration GO.

## Current checkpoint — 4B llama.cpp runtime restoration

Preregistration:
`research/architecture/loom-4b-llama-runtime-restoration-001-preregistration.md`.

Historical setup probe:
`scripts/llama_cpp_setup_probe.py`, tracked SHA `f7a49cc9e31a3754fcb7d5b0a912f93e2eadbd22`.
Historical valid setup probe 003 proved the pinned source, Release + Metal, server ON, UI OFF.

Restoration is mechanical only:
1. run tracked setup probe exactly; source-network fetch/clone of official ggml-org/llama.cpp is authorized if needed;
2. if exact setup PASS, build only the `llama-server` target additionally because the tracked probe explicitly builds only `llama-cli`/`llama-bench`;
3. verify exact source HEAD, CMake flags, cli/bench/server diagnostics and Metal device;
4. no model acquisition/copy/load/inference;
5. no tracked-file modification.

Classification only `LOOM_4B_LLAMA_RUNTIME_RESTORATION_GO` or `...NO_GO`.
After GO stop; unchanged 4B bake-off rerun is separate.

After valid 4B matched result, freeze broader compact 4B/8B/30B practical suite before role/router thresholds. Heretic remains mandatory after tier selection.