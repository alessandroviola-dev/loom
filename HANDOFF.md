# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — DFlash first E2E failed; publisher mask bug repaired; acceptance still zero; masked reference parity next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`
Next core checkpoint: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001`

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
- component memory-safe standalone;
- previous 9-state/63-decision MLX-vs-NumPy stability PASS, but that comparison used the pre-mask semantics and must not be treated as publisher-contract proof after the repair below.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- P1/P2/P3 completed;
- 96 committed output tokens with ordinary-greedy parity PASS;
- target KV/router/logit parity bitwise PASS;
- deterministic rerun PASS;
- zero expert leak.

But:
- acceptance 0/96 cycles;
- verifier calls/output token 1.96875;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s;
- DFlash 0.1544 tok/s = 0.1996x;
- swap delta +737.43 MiB.

This is a dual failure. Acceptance is the first blocker; memory remediation is deferred.

## ACCEPTANCE-ALIGNMENT-DIAG-001 — MASK BUG FOUND, PROBE STILL ZERO

Report: `research/architecture/loom-dflash-acceptance-alignment-diag-001-result.md`.
Raw evidence: `results-local/research/dflash-acceptance-alignment-diag-001/20260824T141239Z/`.

Three deterministic P1 cycles C=43–45 were inspected.

First concrete semantic mismatch:
- publisher anchor/block attention mask was absent in the MLX drafter path;
- old port exposed anchor feature C-1 and future MASK slots incorrectly;
- publisher requires base positions `< anchor` plus causal same-block synthetic attention.

Publisher contract recovered:
- slots 1–7 map via `d2t`;
- `sample_from_anchor=False`;
- post-block taps `[1,12,23,34,45]`;
- no draft-KV carry;
- target correction/bonus logic already aligned.

Repair:
- only `Drafter.propose` mask semantics changed.

Short repaired probe:
- acceptance 0/21;
- prefixes `[0,0,0]`;
- no simple proposal offset: k-1 0/20, k 0/21, k+1 0/21.

Interpretation:
- missing mask was a real integration bug;
- repair alone does not explain/solve zero acceptance;
- drafter/target incompatibility is not yet established because the independent reference has not been revalidated under the corrected publisher mask semantics.

## Exact next step — `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001`

Do not rerun full E2E and do not optimize memory/performance.

Build an independent publisher-semantics reference that implements the anchor/block mask separately from the MLX code. Validate corrected MLX against that reference on real frozen target-tap states and full seven-step rollouts.

Required proof:
1. exact anchor/base/synthetic-slot visibility matrix matches publisher source;
2. MLX/reference fusion and per-layer outputs quantified;
3. proposal-token parity across all seven rollout positions;
4. deterministic rerun;
5. no NaN/Inf;
6. record proposal-vs-target acceptance only as observation, not as compatibility conclusion until masked reference parity passes.

If masked MLX/reference parity fails, fix/localize the first publisher-semantic mismatch. If it passes and target acceptance remains ~0, then open a separate target-compatibility checkpoint, with the local Qwen3-30B-A3B MLX 4-bit target as the leading hypothesis rather than an established cause.

## Later order

1. masked publisher-reference parity;
2. target/drafter compatibility audit only if parity PASS and acceptance still zero;
3. only after nonzero acceptance, combined-runtime memory remediation;
4. rerun full E2E economics;
5. capability/coding benchmark once practical speed improves;
6. context/stability;
7. behavioral decensoring validation before final promotion.
