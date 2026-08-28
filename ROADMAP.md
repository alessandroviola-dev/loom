# LOOM Roadmap

Last updated: 2026-08-28
Current: 30B DEEP and 8B BALANCED matched evidence exist. 4B model/runtime artifacts are mechanically present, but restoration protocol closed NO_GO due an unexpected UI-asset network fetch. One final no-rebuild/no-network 4B inference attempt remains; otherwise park 4B.
Immediate next: execute `LOOM_4B_FINAL_BAKEOFF_ATTEMPT_001`, then move on regardless of outcome.
Canonical context: `/AGENTS.md` v3.54.

## 1. Product direction — LOOM AUTO

Target one adaptive system:
- `loom-fast` -> optimized ~4B when/if retained;
- `loom-balanced` -> optimized ~8B;
- `loom-deep` -> optimized 30B;
- `loom-auto` -> cheapest likely-successful tier plus verification-driven escalation.

Do not freeze routing thresholds before matched multi-task evidence.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional. Execute after runtime roles are selected and initially optimized. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. LOOM 30B DEEP

Canonical runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
LRUCache / 384 tokens: correct O(1) design but task INCOMPLETE; latency minutes.

## 4. LOOM 8B BALANCED

Matched classification `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`.

## 5. LOOM 4B FAST

Historical Qwen3-4B Q4_K_M on pinned llama.cpp/Metal:
- model SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- historical text generation `22.33 tok/s ±0.02`.

First matched attempt: `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`; no inference.
Restoration: `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` because the server-target build unexpectedly fetched a UI asset outside authorization. Classification remains closed.

Mechanically, exact pinned binaries now exist and pass diagnostics. Therefore one separate final attempt is allowed without rebuilding/network/model mutation.

## 6. Final 4B attempt

Preregistration:
`research/architecture/loom-4b-final-bakeoff-attempt-001-preregistration.md`.

Use existing restored runtime and existing experimental runner unchanged. Exactly one frozen LRUCache inference, max 384 tokens.

- valid inference -> record 4B result and continue;
- any new mechanical blocker -> `LOOM_4B_FINAL_ATTEMPT_ABORTED`, park 4B for current phase.

No more 4B recovery/debug work in this phase.

## 7. Broader practical evaluation

After the final 4B attempt, proceed regardless of outcome. If 4B is retained, include it in the compact multi-task suite. If parked, compare/optimize 8B BALANCED and 30B DEEP and revisit a lightweight fast tier later from a cleaner runtime path.

Task suite should cover coding, debugging, reasoning/math, structured instruction following, Italian technical explanation, supplied-context reasoning and planning/tool-use decisions.

Score correctness/completion plus TTFT, wall, decode throughput, memory/swap and time-to-correct-task.

## 8. Tier optimization and LOOM AUTO

Optimize selected tiers with skills/protocols, memory, tools and verification, then implement evidence-based routing/escalation. Do not let unavailable 4B infrastructure block 8B/30B progress.

## 9. Provider/UI

Expose selected LOOM tiers through a local OpenAI-compatible provider usable by Pi and a proper chat UI instead of expanding temporary CLIs.

## 10. Mandatory Heretic integration

After tier selection/initial optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates.

## 11. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block tiered product progress.