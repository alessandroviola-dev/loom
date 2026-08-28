# LOOM Roadmap

Last updated: 2026-08-28
Current: canonical LOOM 30B v1 exists and is manually usable but practically slow; target system architecture is now routed 4B FAST / 8B BALANCED / 30B DEEP.
Immediate next: matched 30B/8B/4B practical bake-off using already-downloaded small models.
Canonical context: `/AGENTS.md` v3.50.

## 1. Product direction — LOOM AUTO

LOOM is a multi-tier inference system, not a single-model runtime.

Target modes:
- `loom-fast` -> optimized ~4B;
- `loom-balanced` -> optimized ~8B;
- `loom-deep` -> optimized 30B;
- `loom-auto` -> router selects the cheapest tier likely to solve the task and may escalate 4B -> 8B -> 30B when verification/confidence is insufficient.

All tiers should share LOOM-level memory/retrieval, skills/protocols, tools, verification and provider/API integration where compatible.

Do not freeze routing thresholds before matched evidence exists.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a core, non-optional project track.

It remains scheduled after runtime role selection so refusal/steerability editing targets the tiers that matter. Freeze behavioral and capability-preservation gates before edits. Report measured refusal suppression/steerability, not absolute unmeasured `guardrail-free` claims.

## 3. Frozen 30B research baseline

Qwen3-30B-A3B exact-Q4/top-8:
- canonical backend commit `96958de`;
- backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`;
- sustained 3x32 median `1.229233 tok/s`.

Closed current-verifier paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 from deployed Q4: fidelity fail;
- DFlash: closed;
- perfect-oracle K=4 verifier ceiling `1.792925 tok/s`, so real speculative drafter is not justified.

## 4. Canonical LOOM 30B v1 — FUNCTIONAL_SLOW

Production commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c`.

Runtime files:
- `scripts/loom_30b_runtime_core_v1_001.py` SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Historical long-form:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Canonicalization GO and EOS-finalize GO are complete. Historical class remains `FUNCTIONAL_SLOW` because frozen TTFT READY gate failed.

## 5. Manual-use evidence

Temporary CLI limitation: one-line `input()` means pasted multiline prompts are consumed as multiple turns. Treat this as harness UX, not a model-semantic defect; final product should use an OpenAI-compatible provider/service consumed by Pi and/or a proper chat UI rather than growing a custom terminal frontend.

First real coding task requested an O(1) LRU cache:
- 30B chose the correct dictionary + doubly-linked-list architecture;
- `get()` behavior was correct;
- the response exhausted the configured output budget during `put()` and remained incomplete;
- user observed the task taking minutes and judged the latency difficult to tolerate.

Practical implication: completion and waiting time must be scored alongside raw reasoning quality.

## 6. Immediate scientific decision — matched 30B vs 8B vs 4B

Use the already-downloaded small-model artifacts before any more 30B product polish.

Freeze a compact matched task set and output budget. Measure:
- task correctness and completion;
- TTFT;
- total wall time;
- sustained decode tok/s;
- RAM/swap;
- disk footprint;
- subjective usability.

Task classes:
- coding from specification;
- debugging;
- reasoning/math;
- structured instruction following;
- Italian technical explanation;
- supplied-context/document reasoning;
- planning/tool-use decisions.

Primary question:
**How much correct/useful work is produced per unit of waiting time and memory?**

## 7. Tier optimization after bake-off

### 4B FAST
Prioritize minimal TTFT, high decode speed and low memory. Add skills/protocol retrieval, memory, tools, verification and domain specialization only when measured gains justify overhead.

### 8B BALANCED
Optimize for best middle-tier quality/latency ratio. It may become the most frequently selected tier if 4B fails too often and 30B is too slow.

### 30B DEEP
Reserve for difficult tasks where measured quality gain justifies latency. Continue separate work on TTFT/prefill and materially new expert-runtime speed mechanisms.

## 8. LOOM AUTO router/escalation

After tier evidence exists:
- deterministic rules handle obvious routing cases;
- small-model classifier/router may handle ambiguous cases;
- verification/confidence can trigger escalation 4B -> 8B -> 30B;
- expose forced modes (`loom-fast`, `loom-balanced`, `loom-deep`) plus `loom-auto`.

Evaluate router by total task success, latency and escalation cost rather than routing-label accuracy alone.

## 9. Provider/UI integration

After runtime roles are selected, expose LOOM through a standard local API/provider layer rather than maintaining a bespoke CLI. Preferred direction: OpenAI-compatible local API usable by Pi and a full chat UI such as Open WebUI or equivalent.

## 10. Heretic behavioral/steerability integration

Mandatory after tier selection/initial optimization. Use the Heretic technical paper as design input for clean-room measured edits with capability-preservation gates. Determine whether editing should apply independently to each tier or only selected tiers based on measured behavior.

## 11. Qwen3.8 later

Qwen3.8-27B and Flash-Next remain statically portable but execution/downloads are parked until the tiered architecture decision or a materially new mechanism makes them compelling.

Final architecture is chosen from measured practical utility, not nominal parameter count.