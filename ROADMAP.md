# LOOM Roadmap

Last updated: 2026-08-28
Current: compact 8B-vs-30B suite completed. 8B BALANCED is provisional default; 30B DEEP is selective escalation; legacy 4B FAST remains parked.
Immediate next: test cheap 8B capability amplification before implementing LOOM AUTO.
Canonical context: `/AGENTS.md` v3.56.

## 1. Product direction — LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> optimized 30B, selective escalation;
- future `loom-fast` -> reintroduce later via clean runtime;
- `loom-auto` -> capability-first path plus validation-driven escalation.

Do not freeze router thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## 3. Compact 8B vs 30B evidence

Result:
`research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`.
Classification: `LOOM_8B_30B_COMPACT_SUITE_PASS`.

8B: utility `4/10`, total task wall `35.325 s`, median TTFT `2.006 s`, pooled generation `12.931 tok/s`.
30B: utility `7/10`, total task wall `468.867 s`, median TTFT `50.671 s`, pooled generation `1.402 tok/s`.

30B gained +3 utility points/+2 correct tasks for +`433.541 s` waiting cost (~`12.27x`).

Observed classes:
- deterministic arithmetic: both fail -> tool path;
- strict machine-readable contract: 8B semantic content right but formatting fails -> protocol path;
- supplied-context reasoning: 8B matches 30B;
- verification-driven design: 30B materially better -> candidate DEEP/escalation class.

## 4. Current — 8B capability amplification funnel

Preregistration:
`research/architecture/loom-8b-capability-amplification-funnel-001-preregistration.md`.

Fresh paired 8B-only branches:
A. calculator tool capability;
B. strict-output reusable protocol;
C. verification-first reusable protocol.

Each branch compares raw 8B against exactly one treatment and has frozen acceptance criteria. No 30B/4B inference, downloads, runtime optimization, memory/RAG, fine-tuning or Heretic.

Purpose: determine how much of the 8B-to-30B raw gap can be closed cheaply at the system layer.

## 5. Capability-first execution graph

After funnel review, accepted mechanisms may support a graph such as:
`task -> deterministic capability/protocol -> 8B -> validator -> 30B only if unresolved`.

Do not implement production routing until these mechanisms are validated.

## 6. Tier optimization

Optimize selected tiers only from evidence:
- 8B: latency already strong; prioritize effective intelligence through protocols/tools/verification and later memory/RAG;
- 30B: reserve for proven hard-task advantages and continue separate speed R&D;
- FAST: revisit only after higher-value architecture work.

## 7. Provider/UI

After capability/routing design is validated, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 8. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 9. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block tiered product progress.