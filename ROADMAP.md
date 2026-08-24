# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001_IDENTITY_MATCH_EXCEPT_QUANTIZATION`
Strategic next: `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, full intended model capacity, reproducible correctness and later behavioral-freedom validation.

Canonical target values and stable invariants live in `/AGENTS.md`.

## Proven target/runtime

- full Qwen3-30B-A3B external-expert execution across all 48 layers;
- exact final logits and real greedy generation;
- complete ~819-MB shared-backbone residency;
- expert-major disk access gives a real decode win;
- real routing reuse exists;
- 4-GiB resident raw cache rejected for memory pressure;
- exact DFlash target taps `[1,12,23,34,45]`;
- exact B7 wavefront target verification with expert reuse;
- MLX DFlash drafter component runs and fits.

## DFlash drafter — publisher semantics PASS

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`:
- repaired MLX drafter matches an independently implemented masked publisher reference;
- explicit independent 8×13 mask assertion PASS;
- 9 frozen real target-tap states;
- 63/63 mapped proposal-token decisions match;
- deterministic rerun PASS;
- no NaN/Inf.

The corrected MLX mask/port path is no longer the leading explanation for zero acceptance.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- target committed behavior exact;
- acceptance 0/96;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Frozen target continuation — PASS

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`:
- independent-oracle historical overlap 45/45;
- complete 63/63 reference;
- 18 new decisions marked `REBASELINED_REFERENCE`;
- deterministic rerun PASS;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

## Target/drafter compatibility — structural incompatibility

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`:
- target replay 63/63 PASS;
- scoring control 63/63 PASS;
- drafter/target top1 parity 0/63;
- top5/top10/top50 hits all 0/63;
- target rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- proposal logprob P50/mean -37.3015 / -35.7567;
- target top1/top2 margin P50/mean 8.8752 / 9.0658;
- accepted prefixes `[0,0,0,0,0,0,0,0,0]`.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`

This is not a near-boundary greedy mismatch.

## Target identity — MATCH EXCEPT QUANTIZATION

`LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001` classified:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Publisher target:
`Qwen/Qwen3-30B-A3B`

Local target:
`Qwen/Qwen3-30B-A3B-MLX-4bit`, revision `4e2776a4…`

Checks:
- DFlash-relevant config/architecture parity PASS;
- tokenizer parity PASS;
- special-token parity PASS;
- vocab parity PASS;
- `d2t`/`t2d` audit PASS;
- first material non-quantization mismatch: none.

Conversion delta:
- MLX affine 4-bit;
- group size 128;
- 386 weight/scales/biases triplets.

Unresolved provenance:
- exact original unquantized revision unavailable locally;
- publisher tokenizer byte snapshot unavailable locally.

Conclusion:
- static architecture/token semantics do not explain the incompatibility;
- target hidden-state / precision drift is now the leading hypothesis;
- quantization causality is still unproven.

Report:
`research/architecture/loom-dflash-target-identity-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-identity-audit-001/20260824T155624Z/`

## Next — unquantized control preflight

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`

Before downloading or running the large unquantized target, establish the minimum valid isolated control.

Preflight questions:
1. Which exact upstream unquantized model revision/artifacts should be used?
2. What download and temporary disk footprint is required?
3. Can the existing LOOM external-expert path consume unquantized weights without full-model residency?
4. What is the smallest frozen prefix/state subset that can decisively test hidden-state drift?
5. Which quantities must be compared at taps `[1,12,23,34,45]` and final logits?
6. What numerical gates distinguish small expected precision noise from a DFlash-breaking distributional shift?
7. What temporary artifacts are produced and how are they cleaned up?

Preflight restrictions:
- do not download the full unquantized model;
- do not run the full unquantized target yet;
- no target/drafter/mapping changes;
- no full E2E;
- no memory/performance remediation;
- no causal claim against quantization.

Decision after preflight:
- feasible bounded control -> preregister and execute isolated unquantized hidden-state/logit comparison;
- infeasible on M1/storage/runtime -> identify the minimum alternative independent control rather than silently weakening the experiment;
- only a successful isolated control may promote or reject 4-bit hidden-state drift as the cause.

## Later order

1. unquantized-control preflight;
2. isolated unquantized target hidden-state/logit control;
3. decide whether the existing DFlash drafter is salvageable for LOOM;
4. only after nonzero useful acceptance, combined-runtime memory remediation;
5. full E2E rerun and economics;
6. capability/coding benchmark;
7. context/stability;
8. if DFlash remains nonviable, return to the next highest-leverage LOOM architecture/I/O branch;
9. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only active delta, exact inputs, gates, evidence and concise return fields. Pi performs local execution/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
