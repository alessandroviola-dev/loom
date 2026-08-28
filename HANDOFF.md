# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — canonical Qwen3-30B-A3B interactive runtime is persisted and manually exercised. The runtime works, but a small real coding task exposed materially poor practical latency and an incomplete response at the configured output budget. Current checkpoint moves to the matched 30B/8B/4B practical bake-off and the target architecture is now a three-tier routed LOOM system.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_TIERED_30B_8B_4B_PRACTICAL_BAKEOFF_PREP`
Pi context: `/AGENTS.md` v3.50.

## Target product architecture — frozen direction

LOOM should operate as one adaptive system with:
- **4B FAST** — aggressively optimized for easy/cheap tasks; speed, TTFT, low memory, skills/protocols/tools/memory;
- **8B BALANCED** — optimized middle tier for harder work where 4B is insufficient;
- **30B DEEP** — slow tier reserved for difficult tasks where measured capability gain justifies latency;
- **LOOM AUTO** — automatic routing and later escalation 4B -> 8B -> 30B based on task difficulty and verification/confidence.

Do not choose router thresholds by intuition. Use matched task evidence first.

## LOOM Heretic — fundamental track

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental/non-optional design input for final LOOM, not a side experiment.

Execution remains intentionally after runtime-role selection so behavioral edits can target the tiers that matter. The Heretic checkpoint must freeze refusal/steerability metrics and capability-preservation gates before edits. Use measured refusal suppression/steerability language rather than absolute unmeasured `guardrail-free` claims.

## Frozen 30B comparator

Canonical expert backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Backend commit `96958de`.
Backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact Q4/top-8 3x32 median: `1.229233 tok/s`.

Closed speed paths: routing sparsity no acceptable gain; Q2/Q3 fidelity fail; DFlash closed; perfect-oracle K=4 verifier ceiling `1.792925 tok/s`, so real drafter is not justified.

Qwen3.8-27B and Flash-Next remain parked until after practical size comparison.

## Canonical LOOM 30B v1 — FUNCTIONAL_SLOW

Production commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c`.

Files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Historical long-form metrics:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Historical classification remains `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW` because the frozen READY TTFT gate failed.

Canonical properties include exact token/routing/logit parity, incremental KV reuse, Unicode streaming, EOS suppression/finalization, robust special-token boundary handling, zero SOURCE fallback/cache and deterministic fd close.

## Manual-use findings

1. Terminal CLI uses one-line `input()`. Pasting multiline prompts causes pasted lines to become separate turns. This is a temporary harness/UI limitation; do not spend product effort extending the CLI before model-size comparison. Final integration should expose LOOM through a standard provider/API layer consumable by Pi and a proper chat UI.

2. First single-line real coding task requested an O(1) Python `LRUCache`.
   - 30B correctly chose dictionary + doubly linked list;
   - `get()` behavior and O(1) strategy were correct;
   - generation reached its configured output budget while implementing `put()`, so the requested executable solution was incomplete;
   - user reported the small task taking minutes and being difficult to use at this speed.

Interpretation: partial reasoning quality is encouraging, but completion/latency are already material disadvantages. This is exactly what the practical bake-off must quantify.

## Immediate next action

Do not optimize the temporary 30B CLI now.

1. Identify exact already-downloaded local 4B and 8B model artifacts and their runnable environments.
2. Freeze a compact fair 30B/8B/4B evaluation set with identical prompts/output budgets where possible.
3. Include coding, debugging, reasoning, instruction following, Italian technical explanation, supplied-context reasoning and planning/tool decisions.
4. Record correctness/completion, TTFT, total wall time, decode throughput, RAM/swap and practical usability.
5. Select initial FAST/BALANCED/DEEP roles from measured utility.
6. Optimize each selected tier with memory, skills/protocols, tools and verification.
7. Build LOOM AUTO router/escalation after measured tier boundaries exist.
8. Then open the mandatory Heretic behavioral/steerability integration checkpoint.

Separate materially new 30B speed R&D remains allowed but must not block the tiered product path.