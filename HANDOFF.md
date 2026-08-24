# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — corrected DFlash drafter validated against independent masked publisher reference; frozen-prefix acceptance remains zero; target compatibility audit next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`
Next core checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

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
- publisher anchor/block mask semantics have now been independently revalidated after repair.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- P1/P2/P3 completed;
- 96 committed output tokens with ordinary-greedy parity PASS;
- target KV/router/logit parity bitwise PASS;
- deterministic rerun PASS;
- zero expert leak;
- acceptance 0/96 cycles;
- verifier calls/output token 1.96875;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s;
- DFlash 0.1544 tok/s = 0.1996x;
- swap delta +737.43 MiB.

This remains a dual failure. Acceptance is the first blocker; memory remediation stays deferred.

## Acceptance alignment diagnostic — mask bug repaired

`LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`.

Report: `research/architecture/loom-dflash-acceptance-alignment-diag-001-result.md`.
Raw evidence: `results-local/research/dflash-acceptance-alignment-diag-001/20260824T141239Z/`.

Recovered publisher contract:
- base positions `< anchor`;
- causal same-block synthetic attention;
- slots 1–7 map via `d2t`;
- `sample_from_anchor=False`;
- post-block taps `[1,12,23,34,45]`;
- no draft-KV carry;
- target correction/bonus logic aligned.

Only the missing drafter mask was mechanically repaired. The short repaired probe still accepted 0/21 proposals with prefixes `[0,0,0]`.

## MASKED-REFERENCE-PARITY-001 — PASS

Classification: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`.

Report: `research/architecture/loom-dflash-masked-reference-parity-001-result.md`.
Raw evidence: `results-local/research/dflash-masked-reference-parity-001/20260824T142830Z/`.

Independent publisher-semantics reference:
- implements the corrected anchor/block attention mask independently from MLX;
- explicit 8×13 mask-matrix assertion PASS;
- same 9 frozen P1/P2/P3 states at positions 1/16/32;
- 63/63 mapped proposal-token parity over full seven-step autoregressive rollouts;
- first mismatch none;
- deterministic rerun PASS;
- no NaN/Inf.

Numerics:
- final-logit max-abs distribution max/mean: 0.0166407 / 0.0109135;
- final-logit mean-abs distribution max/mean: 0.00175031 / 0.00120281;
- top1/top2 mean margin MLX/reference: 0.55770 / 0.55726;
- maximum absolute margin error: 0.00708771.

Frozen target continuation observation:
- MLX accepted-prefixes: `[0,0,0,0,0,0,0,0,0]`;
- independent reference accepted-prefixes: `[0,0,0,0,0,0,0,0,0]`.

Interpretation:
- the repaired MLX drafter now matches the independently implemented masked publisher semantics;
- a remaining MLX drafter-port/mask error is no longer the leading explanation for the observed zero frozen-prefix acceptance;
- this does NOT yet prove incompatibility with the current target;
- this does NOT prove 4-bit quantization is causal.

## Exact next step — `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

Do not rerun full E2E and do not optimize memory/performance.

The audit must first validate current-target replay against the frozen target continuation. This is a hard gate: if the current target does not reproduce the frozen continuation deterministically, classify target replay drift and stop before interpreting drafter compatibility.

Only if target replay integrity passes should the validated masked drafter proposals be scored against the target to characterize:
- proposal-vs-target top1 parity;
- target rank of each proposed token;
- proposed-token log-probability;
- top-k inclusion;
- target margins;
- exact accepted-prefix distribution.

A frozen-target continuation control must go through the same validation path to prove the scorer/validator itself recovers target top1 correctly.

Do not change drafter, target, weights, token mapping, acceptance rules, thresholds or memory policy.

## Decision tree after compatibility audit

1. target replay FAIL -> repair/localize target replay drift only; no drafter compatibility claim;
2. target replay PASS + proposals structurally far from target -> drafter/target incompatibility becomes strong evidence;
3. target replay PASS + proposals consistently near target top1 -> characterize whether acceptance failure is caused by narrow decision margins or another interface condition;
4. do not attribute any incompatibility specifically to 4-bit quantization until a later control isolates quantization.

## Later order

1. target/drafter compatibility audit;
2. isolate compatibility cause only if needed;
3. only after nonzero useful acceptance, combined-runtime memory remediation;
4. rerun full E2E economics;
5. capability/coding benchmark once practical speed improves;
6. context/stability;
7. behavioral decensoring validation before final promotion.
