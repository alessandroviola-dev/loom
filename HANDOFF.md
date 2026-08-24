# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — validated masked DFlash drafter is structurally incompatible with the current frozen target prefixes; cause isolation next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`
Next core checkpoint: `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable target anatomy and long-lived invariants live in `/AGENTS.md`. Pi uses compact work packages; ChatGPT owns Git/HANDOFF/ROADMAP.

## Established target/runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone 819,015,680 B; routed bank external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache rejected: ~80.9% hit but +2.41 GiB swap and severe slowdown.

## DFlash prerequisites proven

Candidate:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Publisher-intended target:
`Qwen/Qwen3-30B-A3B`

Target side:
- taps `[1,12,23,34,45]` exposed with router/logit/token bitwise parity;
- B7 wavefront verifier exact;
- 431,519,451 B useful expert bytes/verified position;
- 10.8152 s sequential -> 6.5430 s wavefront = 1.653x;
- zero swap/expert leak.

Drafter side:
- all 680,813,824 learned BF16 params mapped;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- 63/63 corrected MLX/reference proposal-token parity;
- deterministic and finite.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- 96 committed output tokens with ordinary-greedy parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96 cycles;
- verifier calls/output token 1.96875;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s vs DFlash 0.1544 tok/s = 0.1996x;
- swap delta +737.43 MiB.

Acceptance remains the first blocker; memory remediation stays deferred.

## Target continuation freeze — PASS

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`:
- historical overlap 45/45;
- complete 63/63 `REBASELINED_REFERENCE` through an independent target oracle;
- 18 missing decisions explicitly marked rebaselined;
- deterministic rerun PASS;
- no NaN/Inf;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

## TARGET-COMPATIBILITY-AUDIT-001 — PASS / INCOMPATIBLE

Classification:
`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`

Report:
`research/architecture/loom-dflash-target-compatibility-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T151134Z/`

Validation gates:
- reference hash PASS;
- current-target replay 63/63 PASS;
- frozen-target scoring-path control 63/63 PASS;
- deterministic rerun PASS;
- no NaN/Inf.

Compatibility measurements:
- decisions: 63;
- drafter/target top1 parity: **0/63**;
- top5/top10/top50 hits: **0/63 / 0/63 / 0/63**;
- target rank min/P50/mean/max: **987 / 14,195 / 28,621.08 / 146,487**;
- proposal logprob P50/mean: **-37.3015 / -35.7567**;
- target top1/top2 margin P50/mean: **8.8752 / 9.0658**;
- accepted prefixes: `[0,0,0,0,0,0,0,0,0]`.

First mismatch:
- `P1_t01`, proposal position 1;
- drafter token 1778 vs target top1 12050;
- target rank 23,235;
- logprob -40.4061.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`

Interpretation:
- this is not a narrow top1-boundary miss;
- validated DFlash proposals are structurally far from the current target distribution;
- the mask/MLX drafter port is already independently validated;
- current target replay/scoring is exact on the frozen reference;
- incompatibility cause is still unresolved;
- **do not blame 4-bit quantization yet**.

## Exact next step — `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`

Before any expensive BF16/unquantized control, establish whether the local target is statically/provenance-compatible with the publisher-intended `Qwen/Qwen3-30B-A3B` except for quantization/conversion.

Audit only:
1. local model source lineage and revision metadata where recoverable;
2. DFlash-relevant architecture/config identity;
3. tokenizer/vocab/special-token identity;
4. d2t/t2d mapping semantics against the actual local target tokenizer;
5. quantization/conversion provenance.

Decision:
- material non-quantization identity mismatch -> localize it and STOP before BF16 control;
- identity compatible except quantization/conversion -> quantization/hidden-state drift becomes the leading hypothesis, not proof; design a separate isolated precision/hidden-state control next.

Restrictions:
- no full E2E;
- no weights/target/drafter/mapping changes;
- no acceptance/threshold tuning;
- no memory/performance remediation.

## Later order

1. target identity audit;
2. isolated target precision/hidden-state control if identity passes;
3. decide whether this DFlash drafter remains viable for LOOM;
4. only after nonzero useful acceptance, combined-runtime memory remediation;
5. rerun full E2E economics;
6. capability/coding benchmark;
7. context/stability;
8. behavioral decensoring validation before final promotion.
