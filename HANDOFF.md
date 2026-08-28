# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — 4B legacy path parked after final mechanical abort. Current active product comparison is LOOM 8B BALANCED vs LOOM 30B DEEP using a compact five-task suite designed to measure quality gain per waiting/resource cost.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_30B_COMPACT_PRACTICAL_SUITE_001`
Pi context: `/AGENTS.md` v3.55.

## Product direction

Current active tiers:
- 8B BALANCED — candidate default/primary tier;
- 30B DEEP — candidate escalation tier;
- FAST tier — architecturally retained, but legacy 4B llama.cpp implementation parked for this phase;
- LOOM AUTO — later evidence-based router/escalator.

Do not freeze routing thresholds before current compact evidence is reviewed.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional. After tier selection/initial optimization, execute the Heretic-inspired refusal/steerability editing track with frozen capability-preservation gates.

## 30B DEEP baseline

Canonical production runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form TTFT `47.832 s`, decode `1.116 tok/s`, end-to-end `0.921 tok/s`.
LRUCache at 384 tokens: correct O(1) architecture and `get()->-1`, but INCOMPLETE during `put()`; practical waiting time minutes.

## 8B BALANCED matched result

Qwen3-8B 3-bit/group64 Direct MLX, M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF.
Matched LRUCache result: `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`.
Output strategy correct but unfinished; not coding-quality PASS.

## 4B FAST — parked

Historical Qwen3-4B Q4_K_M runtime existed and measured `22.33 tok/s ±0.02`, but current legacy llama.cpp recovery consumed disproportionate engineering effort.

Final result:
`research/architecture/loom-4b-final-bakeoff-attempt-001-result.md`.
Classification: `LOOM_4B_FINAL_ATTEMPT_ABORTED`.
Evidence: `results-local/research/4b-final-bakeoff-attempt-001/20260828T151352Z/`.

Final attempt executed no inference because the frozen runner-resolved `llama-server` path was absent. Model SHA remained verified; no network/build/model mutation occurred. This is not evidence about 4B capability.

No more legacy 4B recovery/debug/rebuild work in this phase. A future FAST tier may be created through a clean new runtime such as MLX after 8B/30B architecture work.

## Exact next action — compact 8B vs 30B suite

Preregistration:
`research/architecture/loom-8b-30b-compact-practical-suite-001-preregistration.md`.

Run five concise frozen tasks on both validated tiers, fresh state per task:
1. deterministic arithmetic/capacity reasoning;
2. Python debugging;
3. exact JSON instruction following;
4. supplied-context reasoning;
5. concise verification-driven model-escalation design.

Fixed output caps are 80–140 tokens to prevent verbosity from dominating 30B wall time. No skills/tools/memory/RAG/Heretic/retries/runtime optimization.

For every task/model record correctness (`CORRECT/PARTIAL/INCORRECT`), instruction-following, completion, TTFT, throughput, wall and resources. Aggregate a descriptive utility score /10 plus time per correct task.

Primary question:
**Does 30B produce a material correctness advantage over 8B that justifies its extra waiting time and memory cost, and on which task types?**

After result/review, choose initial BALANCED/DEEP roles. Then optimize with skills/protocols/memory/tools/verification, build LOOM AUTO, provider/UI integration, and mandatory Heretic track.
