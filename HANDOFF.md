# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — corrected DFlash drafter validated; target compatibility audit blocked by incomplete frozen continuation corpus
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_ENGINE_OR_DATA_BLOCKED`
Next core checkpoint: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`

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
- publisher anchor/block mask semantics independently revalidated after repair.

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

Acceptance remains the first blocker; memory remediation stays deferred.

## Mask repair and independent reference — PASS

`LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE` found and repaired the missing publisher anchor/block attention mask in `Drafter.propose`.

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS` then independently validated the repaired semantics:
- explicit independent 8×13 mask assertion PASS;
- same 9 frozen P1/P2/P3 states at positions 1/16/32;
- 63/63 mapped proposal decisions match;
- first mismatch none;
- deterministic rerun PASS;
- no NaN/Inf;
- final-logit max-abs distribution max/mean 0.0166407 / 0.0109135;
- final-logit mean-abs distribution max/mean 0.00175031 / 0.00120281;
- mean top1/top2 margin MLX/reference 0.55770 / 0.55726;
- max absolute margin error 0.00708771;
- frozen-prefix acceptance observation `[0,0,0,0,0,0,0,0,0]` in both paths.

Therefore the corrected MLX drafter implementation is no longer the leading explanation for zero acceptance. Target compatibility remains unproven, and 4-bit causality is not established.

## TARGET-COMPATIBILITY-AUDIT-001 — BLOCKED

Classification: `ENGINE_OR_DATA_BLOCKED`.

Report:
`research/architecture/loom-dflash-target-compatibility-audit-001-result.md`

Raw evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T144106Z/`

Files:
- `precondition.json`
- `provenance.json`

Gate A did not run because the immutable frozen continuation corpus contains only 45/63 required target decisions.

Missing:
- `P1_t32`: six continuation tokens;
- `P2_t32`: six continuation tokens;
- `P3_t32`: six continuation tokens.

Consequently no target replay/control, drafter-target parity, ranks, top-k rates, logprobs, margins or accepted-prefix characterization is yet valid.

This is a data/provenance blocker, not evidence for or against target compatibility.

## Exact next step — `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`

Do not fill the 18 missing decisions using the same current compatibility replay/scoring path. That would make Gate A circular.

First inspect only the relevant pre-existing local evidence for any independently captured and provenance-usable continuation artifact.

If none exists, create an explicitly **new rebaselined reference** using an independent already-validated target oracle path:
1. same nine frozen prefixes/states;
2. seven greedy target continuation tokens per state;
3. require exact oracle agreement with all 45 already-available historical frozen decisions (`45/45`);
4. only then accept the 18 missing decisions as new reference data;
5. deterministic rerun PASS;
6. no NaN/Inf;
7. freeze exact model/prefix/oracle provenance;
8. hash the complete 63-token artifact;
9. label newly generated tokens as rebaselined reference data, not historical frozen observations.

Only after this gate passes should `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` be rerun.

## Later order

1. target continuation freeze/recovery;
2. rerun target/drafter compatibility audit;
3. isolate compatibility cause only if needed;
4. only after nonzero useful acceptance, combined-runtime memory remediation;
5. rerun full E2E economics;
6. capability/coding benchmark once practical speed improves;
7. context/stability;
8. behavioral decensoring validation before final promotion.
