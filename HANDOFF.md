# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — validated DFlash drafter is structurally incompatible with the current target; static target identity matches except MLX 4-bit conversion; unquantized control preflight next
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001_IDENTITY_MATCH_EXCEPT_QUANTIZATION`
Next core checkpoint: `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while balancing memory, speed, capability and later behavioral-freedom validation.

Stable long-lived invariants live in `/AGENTS.md`. Pi executes compact local work packages; ChatGPT owns Git/HANDOFF/ROADMAP and scientific checkpoint administration.

## Established LOOM target/runtime

- Qwen3-30B-A3B external-expert execution is bitwise exact across all 48 layers.
- Shared resident backbone 819,015,680 B; routed bank external.
- Real greedy generation works on M1 8 GB.
- Expert-major disk layout materially improves decode.
- 4-GiB raw RAM cache rejected: ~80.9% hits but +2.41 GiB swap and severe slowdown.

## DFlash candidate

Drafter:
`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

Publisher-intended target:
`Qwen/Qwen3-30B-A3B`

Proven DFlash prerequisites:
- target taps `[1,12,23,34,45]` exposed with exact target parity;
- exact B7 wavefront verifier PASS;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63;
- deterministic and finite.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- committed target behavior remained exact;
- acceptance 0/96 cycles;
- control 0.7735 tok/s vs DFlash 0.1544 tok/s;
- swap +737.43 MiB.

Acceptance remains the first blocker. Memory/performance remediation is deferred.

## Frozen target reference — PASS

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`:
- historical overlap 45/45;
- complete independent-oracle 63/63 reference;
- 18 missing decisions explicitly labeled `REBASELINED_REFERENCE`;
- deterministic rerun PASS;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

## Target compatibility audit — PASS / INCOMPATIBLE

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`:
- reference hash PASS;
- target replay 63/63 PASS;
- scoring control 63/63 PASS;
- 63 drafter proposals scored;
- target top1 parity 0/63;
- top5/top10/top50 hits all 0/63;
- proposal rank min/P50/mean/max = 987 / 14,195 / 28,621.08 / 146,487;
- proposal logprob P50/mean = -37.3015 / -35.7567;
- target top1/top2 margin P50/mean = 8.8752 / 9.0658;
- accepted prefixes `[0,0,0,0,0,0,0,0,0]`.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`

This is structural incompatibility, not a narrow greedy boundary mismatch.

## TARGET-IDENTITY-AUDIT-001 — MATCH EXCEPT QUANTIZATION

Classification:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`

Report:
`research/architecture/loom-dflash-target-identity-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-identity-audit-001/20260824T155624Z/`

Result:
- intended target `Qwen/Qwen3-30B-A3B`;
- local provenance `Qwen/Qwen3-30B-A3B-MLX-4bit`, revision `4e2776a4…`;
- DFlash-relevant architecture/config parity PASS;
- tokenizer parity PASS;
- special-token parity PASS;
- vocab parity PASS;
- `d2t`/`t2d` audit PASS;
- no material non-quantization identity mismatch found.

Material delta:
- MLX affine 4-bit;
- group size 128;
- 386 weight/scales/biases triplets.

Unresolved provenance:
- original unquantized revision unavailable locally;
- publisher tokenizer byte snapshot unavailable locally.

Interpretation:
- static/token-semantic mismatch is no longer a plausible leading explanation;
- target hidden-state / precision drift is now the leading hypothesis;
- this does **not** prove 4-bit quantization is causal.

## Exact next step — `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`

Before any large download or unquantized execution, design the minimum valid isolated control.

Preflight must establish:
1. exact upstream unquantized model artifact/revision availability and provenance;
2. required download and temporary disk footprint;
3. whether LOOM external-expert execution can consume the unquantized weights without full-model residency;
4. minimum frozen prefixes/states needed for a decisive first comparison;
5. exact comparison points: target taps `[1,12,23,34,45]`, final logits and greedy token where required;
6. numerical metrics/gates for 4-bit vs unquantized hidden-state/logit drift;
7. cleanup plan and safety limits.

Restrictions:
- do not download the full unquantized model in the preflight;
- do not run full unquantized forward yet;
- no full E2E;
- no target/drafter/mapping changes;
- no memory/performance remediation;
- no causal quantization claim yet.

## Later order

1. unquantized-control preflight;
2. isolated unquantized hidden-state/logit control if feasible;
3. determine whether 4-bit hidden-state drift explains DFlash incompatibility and whether the drafter is salvageable;
4. only after nonzero useful acceptance, combined-runtime memory remediation;
5. rerun full E2E economics;
6. capability/coding benchmark;
7. context/stability;
8. if DFlash remains nonviable, return to the next highest-leverage LOOM architecture/I/O branch;
9. behavioral decensoring validation before final promotion.
