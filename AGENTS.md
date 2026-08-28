# LOOM — Pi Agent Protocol

Version: 3.54
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
Active clone: `<repository-root>`.
Archive/second clone: `<external-archive>`.
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

## 30B DEEP

Production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`.
Matched/manual LRUCache under 384 output tokens: correct O(1) design and `get()->-1`, task INCOMPLETE during `put()`, latency minutes.

## 8B BALANCED

Result: `research/architecture/loom-8b-practical-bakeoff-runner-001-result.md`.
Classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`; p50/p95 `68.932/71.667 ms`; MLX peak `3,912,428,412 B`; swap peak `2498.62 MB`.
Output chose correct O(1) architecture but remained unfinished. Not a coding-quality PASS.

## 4B FAST — recovered condition

Historical canonical control: Qwen3-4B Q4_K_M on pinned llama.cpp/Metal.
- model SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- historical text generation `22.33 tok/s ±0.02`;
- exact model artifact verified at `<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

First matched attempt: `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`; no inference.

Runtime restoration result:
`research/architecture/loom-4b-llama-runtime-restoration-001-result.md`.
Classification remains `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` because the server-target build unexpectedly downloaded a UI asset outside the preregistered network boundary. Do not retroactively relax this gate.

Mechanically, the restored runtime now exists and passed diagnostics:
- exact llama.cpp source HEAD `60addddf...`;
- `llama-cli`, `llama-bench`, `llama-server` all exist;
- Apple M1 Metal visible;
- model was not downloaded/loaded/modified during restoration;
- tracked LOOM files stayed clean.

## Current checkpoint — FINAL 4B attempt

Preregistration:
`research/architecture/loom-4b-final-bakeoff-attempt-001-preregistration.md`.

This is the final 4B recovery attempt for current tier selection.
- NO rebuild/setup probe/network/package/model mutation;
- use existing restored pinned binaries only;
- use existing `scripts/loom_4b_practical_bakeoff_runner_001.py` unchanged;
- verify runner SHA/source HEAD/server/Metal/model SHA;
- execute exactly one frozen 384-token LRUCache inference;
- no retries or repairs.

If valid inference runs: `LOOM_4B_FINAL_BAKEOFF_PASS`.
If any further mechanical blocker occurs: `LOOM_4B_FINAL_ATTEMPT_ABORTED`; park 4B for current phase and continue with 8B BALANCED + 30B DEEP. Do not open another 4B recovery checkpoint unless separately reactivated later.

Do not claim 4B is intrinsically less intelligent than 8B from parameter count alone. Current product decision may still park it on engineering cost.

After this final attempt, proceed to broader practical tier/product work without allowing 4B recovery to block progress. Heretic remains mandatory after tier selection/initial optimization.