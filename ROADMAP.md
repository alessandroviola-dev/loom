# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`
Strategic next: `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`

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

This removes the corrected MLX mask/port path as the leading explanation for zero acceptance.

## First end-to-end DFlash — FAIL

`LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`:
- target committed-token parity PASS;
- target KV/router/logit correctness PASS;
- acceptance 0/96;
- useful external expert bytes/output token 3,098,293,248 B;
- control 0.7735 tok/s vs treatment 0.1544 tok/s;
- swap +737.43 MiB.

Do not optimize memory while acceptance remains zero.

## Target continuation reference — PASS

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`:
- 45/45 historical overlap through an independent target oracle;
- complete 63/63 reference;
- 18 new decisions marked `REBASELINED_REFERENCE`;
- deterministic rerun PASS;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

## Target/drafter compatibility — INCOMPATIBLE on frozen prefixes

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`.

Validation:
- frozen reference hash PASS;
- current-target replay 63/63 PASS;
- scoring-path frozen-target control 63/63 PASS;
- deterministic rerun PASS;
- no NaN/Inf.

Compatibility:
- 63 decisions scored;
- drafter/target top1 parity 0/63;
- top5/top10/top50 hits all 0/63;
- proposal target rank min/P50/mean/max = 987 / 14,195 / 28,621.08 / 146,487;
- proposal target logprob P50/mean = -37.3015 / -35.7567;
- target top1/top2 margin P50/mean = 8.8752 / 9.0658;
- accepted prefixes `[0,0,0,0,0,0,0,0,0]`.

Verdict:
`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`

This is structural incompatibility, not a near-boundary greedy mismatch. The cause is not yet identified. No causal attribution to 4-bit quantization is supported yet.

Report:
`research/architecture/loom-dflash-target-compatibility-audit-001-result.md`

Evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T151134Z/`

## Next — target identity audit

Checkpoint:
`LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`

The DFlash publisher identifies the intended target as `Qwen/Qwen3-30B-A3B`. Before building an expensive unquantized target control, prove whether the local target is the same static/token semantic model modulo conversion/quantization.

Audit:
1. local source model lineage and revision metadata where recoverable;
2. architecture/config fields relevant to taps/logits/routing;
3. tokenizer, vocabulary and special-token identity;
4. d2t/t2d mapping semantics against the actual local target tokenizer;
5. conversion/quantization metadata and provenance.

Decision:
- any material non-quantization identity mismatch -> localize and stop before precision testing;
- static identity compatible except quantization/conversion -> promote target hidden-state/precision drift to the leading hypothesis and design a separate isolated unquantized control;
- do not call quantization causal until that control passes.

Restrictions:
- no full E2E rerun;
- no target/drafter/weight/mapping changes;
- no threshold or acceptance tuning;
- no memory/performance remediation.

## After identity audit

1. isolated target precision/hidden-state control if required;
2. determine whether the existing DFlash drafter is salvageable for LOOM;
3. only after nonzero useful acceptance, combined-runtime memory remediation;
4. full E2E rerun and economics;
5. capability/coding benchmark;
6. context/stability;
7. if DFlash remains nonviable, return to the next highest-leverage LOOM I/O/architecture branch;
8. behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts contain only active delta, exact inputs, gates, evidence and concise return fields. Pi performs local execution/tests/evidence; ChatGPT owns Git/HANDOFF/ROADMAP.
