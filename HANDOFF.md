# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — compact 8B-vs-30B suite completed. Evidence supports 8B BALANCED as provisional default and 30B DEEP as selective escalation. Legacy 4B FAST remains parked. Current checkpoint tests whether cheap LOOM capabilities can close observed 8B gaps before 30B escalation.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_001`
Pi context: `/AGENTS.md` v3.56.

## Provisional product architecture

- 8B BALANCED — default/primary candidate;
- 30B DEEP — selective escalation when measured gain justifies latency;
- FAST — retained conceptually, legacy 4B implementation parked;
- LOOM AUTO — capability-first execution and verification-driven escalation.

Do not freeze router thresholds yet.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Compact 8B vs 30B result

Result:
`research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`
Evidence:
`results-local/research/8b-30b-compact-practical-suite-001/20260828T152617Z/`
Classification: `LOOM_8B_30B_COMPACT_SUITE_PASS`.

8B:
- utility `4/10`;
- correct/partial/incorrect `2/1/2`;
- total task wall `35.325 s`;
- median TTFT `2.006 s`;
- pooled generation `12.931 tok/s`;
- time/correct task `17.663 s`.

30B:
- utility `7/10`;
- correct/partial/incorrect `4/0/1`;
- total task wall `468.867 s`;
- median TTFT `50.671 s`;
- pooled generation `1.402 tok/s`;
- time/correct task `117.217 s`.

30B gained +3 utility points and +2 correct tasks, but cost +`433.541 s` waiting time (~`12.27x` task wall).

Failure/win decomposition:
- arithmetic T01: both wrong -> deterministic tool candidate;
- debugging T02: 8B safe fix but partial diagnosis; 30B core better but instruction-length fail;
- strict JSON T03: 8B semantic content right but fenced -> protocol/structured-output candidate;
- supplied context T04: 8B matches 30B;
- verification-driven design T05: clear 30B advantage.

Therefore do not use 30B as a generic correctness rescue for every task. Prefer cheap capability fixes where failure class is deterministic/protocol-level.

## Current checkpoint

Preregistration:
`research/architecture/loom-8b-capability-amplification-funnel-001-preregistration.md`.

Frozen 8B-only paired funnel on fresh prompts:
A. RAW vs deterministic calculator-tool flow;
B. RAW vs reusable strict-output protocol;
C. RAW vs reusable verification-first protocol.

Create only:
`scripts/loom_8b_capability_amplification_funnel_001.py`.

No 30B/4B inference, downloads, model/runtime changes, memory/RAG, Heretic, fine-tuning, production integration or unregistered retries.

Each branch is scored independently against frozen acceptance rules. A successful branch becomes a candidate LOOM capability, not automatically production behavior.

## Next after funnel

Use accepted mechanisms to design the first capability-first LOOM execution graph, likely:
`task -> deterministic capability/protocol when applicable -> 8B -> validation -> 30B only on unresolved failure/uncertainty`.

Then validate architecture before provider/UI integration. Mandatory Heretic track remains after initial runtime/capability optimization.