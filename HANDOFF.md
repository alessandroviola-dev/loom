# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — compact 8B-vs-30B suite completed; 8B capability amplification funnel completed. Strict-output and verification-first mechanisms are accepted candidate capabilities; current calculator flow is rejected. Current checkpoint validates an integrated 8B capability candidate on fresh tasks against RAW 8B and canonical 30B.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_CAPABILITY_CANDIDATE_V1_001`
Pi context: `/AGENTS.md` v3.57.

## Provisional product architecture

- 8B BALANCED — default/primary candidate;
- 30B DEEP — selective escalation when measured gain justifies latency;
- FAST — retained conceptually, legacy 4B implementation parked;
- LOOM AUTO — capability-first execution and verification-driven escalation.

Do not freeze routing thresholds yet.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional. Execute after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Compact 8B vs 30B result

Result: `research/architecture/loom-8b-30b-compact-practical-suite-001-result.md`.
Classification `LOOM_8B_30B_COMPACT_SUITE_PASS`.

8B: utility `4/10`, total wall `35.325 s`, median TTFT `2.006 s`, pooled generation `12.931 tok/s`.
30B: utility `7/10`, total wall `468.867 s`, median TTFT `50.671 s`, pooled generation `1.402 tok/s`.
30B gained +3 utility/+2 correct tasks for +`433.541 s` waiting (~`12.27x`).

Interpretation:
- arithmetic both failed -> 30B escalation is not a universal correctness rescue;
- strict machine-readable output exposed an 8B protocol failure;
- supplied-context reasoning showed 8B parity;
- verification-driven design showed a real 30B advantage.

## 8B capability amplification funnel result

Result:
`research/architecture/loom-8b-capability-amplification-funnel-001-result.md`
Evidence:
`results-local/research/8b-capability-amplification-funnel-001/20260828T154910Z/`
Classification: `LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_PASS`.

Frozen 8B remains `mlx-community/Qwen3-8B-3bit@619ded3`, 3-bit/group64, MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1, M1 `qmv_fast`, BF16 KV, greedy, thinking OFF.

### A calculator tool — REJECTED

- A1 no improvement, A2 improved to PARTIAL, A3 improved to CORRECT;
- only 1/3 treatment items fully CORRECT;
- calculator arithmetic was mechanically correct but model-selected expression/semantics could be wrong;
- do not integrate current calculator flow.

### B strict-output protocol — ACCEPTED

- 2 paired improvements;
- treatment 3/3 CORRECT;
- zero regressions;
- removes markdown/extra-format failures for strict machine-readable contracts.

### C verification-first protocol — ACCEPTED

- 2 paired improvements;
- treatment 2/3 CORRECT;
- zero regressions;
- improves deterministic/observable validation and escalation reasoning.

Treatments kept generation in roughly the same 8B regime (~11–13 tok/s). Strict-output overhead was small; verification-first responses were somewhat longer but still far cheaper than 30B latency.

## Exact next action — 8B Capability Candidate v1

Preregistration:
`research/architecture/loom-8b-capability-candidate-v1-001-preregistration.md`.

Create only:
`scripts/loom_8b_capability_candidate_v1_001.py`.

Run four fresh tasks under all three conditions:
1. RAW 8B;
2. CAPABILITY 8B using only the already-accepted frozen protocol for the preregistered task label;
3. canonical 30B DEEP.

Tasks:
- 2 strict-output;
- 2 verification-first.

Automatic task/capability recognition is explicitly NOT part of this checkpoint. Applicability is supplied by frozen task label to isolate capability value.

CAP8 promotion gate:
- >=`6/8` utility;
- >=`+2` vs RAW8;
- zero task regressions;
- >=`3/4` CORRECT;
- valid provenance/evidence.

30B does not control GO/NO_GO; it is a practical comparator to measure residual quality gap and waiting cost.

No calculator, auto dispatcher, 4B, downloads, runtime changes, retries, tools, memory/RAG, fine-tuning, Heretic, provider/UI or router thresholds.

## After candidate result

If CAP8 GO: next validate automatic capability selection/dispatch on unseen mixed tasks, then build the first capability-first LOOM execution graph.
If CAP8 NO_GO: diagnose accepted mechanism integration without changing frozen evidence before deciding whether to retain them separately.

Provider/UI follows validated execution architecture. Mandatory Heretic track remains after initial runtime/capability optimization.
