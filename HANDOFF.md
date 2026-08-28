# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Output Validator v0 remains GO. Validator-Guided Selective Rescue 001 was mechanically valid but scientific NO_GO: final quality improved from RAW8 `2/8` CORRECT to `5/8`, zero false accepts and 4/8 DEEP calls avoided, but frozen gate required `>=6/8`. Current checkpoint isolates one cheap validator-guided 8B repair before any further DEEP escalation.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_VALIDATOR_GUIDED_REPAIR_001`
Pi context: `/AGENTS.md` v3.63.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective expensive tier, not assumed to solve every residual failure;
- FAST — concept retained; legacy 4B parked;
- LOOM AUTO — validator-first for mechanically verifiable tasks: `8B -> validate -> safe deterministic repair -> cheap guided repair -> DEEP only if still unresolved`.

Open-ended semantic uncertainty and automatic validator selection remain separate future tracks.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional after initial runtime/capability optimization, with frozen refusal/steerability and capability-preservation gates.

## Runtime evidence

8B BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, roughly 13 tok/s real generation.
30B DEEP: roughly 1.4 tok/s compact generation, very high TTFT/wall cost.
Historical 8B 4-bit remains closed by resource evidence; legacy 4B FAST remains parked.

## Output Validator v0 — GO

Result:
`research/architecture/loom-8b-output-validator-v0-001-result.md`
Evidence:
`results-local/research/8b-output-validator-v0-001/20260828T174056Z/`

Key result:
- false PASS `0`;
- deterministic verifiable classes fail closed;
- open-ended tasks abstain `UNCERTAIN`;
- validator p95 <1 ms.

## Selective Rescue 001 — NO_GO

Result:
`research/architecture/loom-validator-guided-selective-rescue-001-result.md`
Evidence:
`results-local/research/validator-guided-selective-rescue-001/20260828T175816Z/`
Classification: `LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_NO_GO`.

Observed:
- RAW8 C/P/I `2/3/3`;
- final C/P/I `5/0/3`;
- improvement `+3 CORRECT`;
- false acceptance `0`;
- safe fence repairs `2/2` successful;
- 30B calls `4/8`, avoided `4/8`;
- only one of four DEEP calls produced a validator-PASS/CORRECT rescue;
- 8B wall `38.656 s`; added DEEP wall `246.346 s`.

Why gate failed:
- final CORRECT `5/8` < frozen `6/8`.

Unresolved residuals were genuine under the frozen contracts: one exact boolean-format failure and two incomplete verification-rule answers. Do not rescore, relax gate, or retry these exposed tasks.

## Exact next action — 8B Validator-Guided Repair 001

Preregistration:
`research/architecture/loom-8b-validator-guided-repair-001-preregistration.md`.

Fresh eight-task mechanically verifiable suite.

Per task:
1. RAW8 once;
2. frozen validator;
3. if PASS: accept;
4. if FAIL and frozen outer-fence safe repair succeeds: accept repaired payload;
5. residual FAIL triggers exactly one additional 8B repair call using original prompt + raw failed answer + exact deterministic validator failure report;
6. revalidate;
7. remaining FAIL becomes UNRESOLVED; no retry and no 30B.

Create only:
`scripts/loom_8b_validator_guided_repair_001.py`.

Frozen GO:
- all required calls valid;
- zero false accepts;
- final CORRECT >=6/8 and >=RAW8 +2;
- guided repair fixes at least 2 residual FAIL tasks to validator PASS + ground-truth CORRECT;
- no repair after initial PASS/successful safe repair;
- exact repair prompt/template unchanged;
- validator/deterministic repair p95 <5 ms;
- no network/package/model/runtime mutation.

If GO: integrate this cheap stage into a later selective-DEEP graph on a new fresh suite. If NO_GO: do not tune on exposed repair tasks; move to a different mechanism/semantic verifier track.
