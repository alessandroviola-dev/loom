# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — DFlash target/drafter components proven; first E2E loop failed with zero acceptance and memory pressure
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`
Next core checkpoint: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and long-lived invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established target/runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone 819,015,680 B; routed bank external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache is rejected: ~80.9% hit but +2.41 GiB swap and severe slowdown.

## DFlash prerequisites already proven

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Target side:
- exact taps `[1,12,23,34,45]` exposed with router/logit/token bitwise parity;
- exact B7 wavefront verifier PASS;
- canonical q_len=1 attention per position;
- unique expert reuse per layer;
- B7 hidden/KV/router/logits/token decisions bitwise exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- zero swap/expert leak.

Drafter side:
- MLX maps all 680,813,824 learned BF16 params;
- 9-state real-tap corpus, 63/63 seven-step proposal decisions match independent NumPy publisher translation;
- deterministic rerun PASS;
- seven-proposal drafter P50 ~0.08437 s;
- standalone memory pressure PASS / swap 0.

## DFLASH-GREEDY-E2E-001 — FAIL GATE

Report: `research/architecture/loom-dflash-greedy-e2e-001-result.md`.
Raw evidence: `results-local/research/dflash-greedy-e2e-001/20260824T124009Z/`.
Runner: `scripts/loom_dflash_greedy_e2e_001.py`.

Correctness of committed target output:
- P1/P2/P3 completed;
- 96 committed tokens;
- ordinary-greedy output token parity PASS;
- target KV/router/logit parity bitwise PASS;
- deterministic rerun PASS;
- zero routed-expert leak.

But proposal acceptance is a complete failure:
- 96 speculative cycles;
- accepted proposals/cycle mean/P50 = **0.0 / 0.0**;
- acceptance rate = **0%**.

Economics:
- verifier calls/output token: 1.96875;
- useful external expert bytes/output token: 3,098,293,248 B;
- control: 0.7735 tok/s;
- DFlash treatment: 0.1544 tok/s;
- relative speed: 0.1996x.

Wall:
- drafter 43.906 s;
- verifier 574.698 s;
- other 3.110 s;
- total 621.713 s.

Memory:
- MLX peak 3,148,206,740 B;
- RSS peak 1,259,044,864 B;
- swap delta +737.43 MiB;
- memory pressure FAIL.

## Scientific interpretation

Do not treat this as `memory only`.

There are **two independent blockers**:
1. zero proposal acceptance — the speculative system currently provides no amortization at all;
2. +737.43 MiB swap — combined target+drafter execution is not memory-clean.

Acceptance is the first priority. Fixing memory while acceptance remains zero would only make a useless path less memory-heavy.

The previous decision-stability checkpoint proved MLX and the NumPy translation make the same proposal decisions. It did not prove that both were aligned correctly to the target's real speculative-generation contract. A shared integration error can therefore explain 63/63 MLX-vs-NumPy parity and 0/96 target acceptance simultaneously.

## Exact next step — `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001`

Use the existing E2E runner/evidence and publisher/source snapshots. Do not optimize memory or performance.

For a small deterministic subset of cycles, reconstruct and compare token-by-token:
1. ordinary target greedy continuation;
2. actual mapped DFlash proposal sequence;
3. target logits used to verify each proposal;
4. proposal seed/input token;
5. target tap position/timing used by the drafter;
6. draft logit index used for proposal 1..7;
7. d2t/t2d mapping location;
8. draft KV initialization, carry and reset semantics;
9. proposal-vs-target-token offset (`k`, `k+1`, etc.);
10. publisher/source generation semantics, including bonus/correction behavior only where relevant.

Required outcome: identify the **first semantic/alignment mismatch** or prove integration alignment correct and show that the drafter truly has zero acceptance against this quantized target.

Do not relax acceptance rules and do not modify the drafter weights in this diagnostic.

If a mechanical off-by-one/seed/tap/KV/mapping bug is proven, repair only that variable and rerun a short acceptance probe before full E2E. If alignment is correct and acceptance remains near zero, investigate target compatibility (e.g. 4-bit target vs the drafter's intended target) as a separate checkpoint.

## Later order

1. acceptance/alignment diagnosis;
2. short repaired acceptance probe if a mechanical cause is found;
3. only after nonzero acceptance, memory remediation of combined target+drafter runtime;
4. rerun full E2E economics;
5. capability/coding benchmark once practical speed improves;
6. context/stability;
7. behavioral decensoring validation before final promotion.
