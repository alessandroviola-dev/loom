# LOOM Roadmap

Last updated: 2026-08-28
Current: compact 8B-vs-30B suite and 8B capability-amplification funnel are complete. Strict-output and verification-first capabilities are accepted; current calculator flow is rejected. Immediate next is validation of an integrated 8B capability candidate on fresh tasks.
Canonical context: `/AGENTS.md` v3.57.

## 1. Product direction — capability-first LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> optimized 30B, selective escalation;
- future `loom-fast` -> reintroduce later via clean runtime;
- `loom-auto` -> applicable capability/protocol first, then 8B, validation, and 30B only when unresolved.

Do not freeze routing thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## 3. Compact 8B vs 30B evidence

Result: `research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`.
Classification `LOOM_8B_30B_COMPACT_SUITE_PASS`.

8B: utility `4/10`, wall `35.325 s`, median TTFT `2.006 s`, generation `12.931 tok/s`.
30B: utility `7/10`, wall `468.867 s`, median TTFT `50.671 s`, generation `1.402 tok/s`.
30B gained +3 utility at +`433.541 s` waiting cost (~`12.27x`).

Observed classes:
- arithmetic: both fail -> model escalation alone insufficient;
- strict machine-readable contract: 8B semantic content right but output contract fails;
- supplied-context reasoning: 8B matches 30B;
- verification-driven design: 30B materially better.

## 4. 8B capability amplification funnel — COMPLETE

Result: `research/architecture/loom-8b-capability-amplification-funnel-001-result.md`.
Classification `LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_PASS`.

### Accepted

**Strict-output protocol**
- 2 improvements;
- treatment 3/3 CORRECT;
- zero regressions.

**Verification-first protocol**
- 2 improvements;
- treatment 2/3 CORRECT;
- zero regressions.

### Rejected

**Calculator tool flow**
- improved 2 pairs but only 1/3 treatment tasks fully CORRECT;
- failure is semantic formulation/expression selection, not arithmetic evaluation;
- do not integrate current calculator flow.

Accepted mechanisms retain roughly the normal 8B throughput regime and remain much cheaper than 30B latency.

## 5. Current — LOOM 8B Capability Candidate v1

Preregistration:
`research/architecture/loom-8b-capability-candidate-v1-001-preregistration.md`.

Validate accepted B/C mechanisms as a capability library on four fresh tasks:
- two strict-output;
- two verification-first.

Compare three conditions on every task:
- RAW 8B;
- CAPABILITY 8B;
- canonical 30B DEEP.

Capability applicability is supplied by frozen task label. Automatic recognition/dispatch is explicitly excluded to isolate mechanism value.

CAP8 GO gate:
- >=`6/8` utility;
- >=`+2` utility vs RAW8;
- zero per-task regressions;
- >=`3/4` CORRECT;
- valid evidence/provenance.

30B comparison measures residual quality gap and added waiting cost; it does not control CAP8 GO/NO_GO.

## 6. Next — capability dispatcher validation

Only if Capability Candidate v1 GO:
- test automatic recognition of when strict-output or verification-first capability applies;
- use unseen mixed task set including tasks where no special capability should activate;
- measure false activations, missed activations, quality impact and routing overhead;
- do not involve 30B escalation thresholds until selector behavior is validated.

## 7. Capability-first execution graph

After dispatcher validation, build first experimental graph:
`task -> capability selector -> accepted capability/protocol -> 8B -> validator -> 30B only if unresolved/uncertain`.

Calculator remains absent until semantic arithmetic formulation is solved with a separately preregistered mechanism.

## 8. Further 8B intelligence amplification

After B/C integration/dispatch:
- memory/RAG;
- skills/protocol retrieval rather than static prompt stuffing;
- tools with deterministic validators;
- planner/executor/verifier when evidence justifies it;
- domain-specific adaptation/distillation only after system-layer gains are measured.

## 9. 30B DEEP

Retain for proven hard-task advantages and separate speed R&D. Do not make 30B the generic fallback for deterministic/protocol failures that cheap LOOM mechanisms can solve.

## 10. FAST tier

Legacy 4B llama.cpp path remains parked. Reintroduce only later through a clean runtime aligned with final architecture.

## 11. Provider/UI

After capability execution graph is validated, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 12. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and determine per-tier application from evidence.

## 13. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block capability-first product progress.
