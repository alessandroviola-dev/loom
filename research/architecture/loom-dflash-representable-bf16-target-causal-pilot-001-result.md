# LOOM DFlash representable BF16 target causal pilot 001 — invalid Q4 baseline

Date: 2026-08-25

Checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Administrative outcome: `INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`

This is **not** one of the preregistered BF16 scientific outcome classifications because no BF16 verifier state was executed.

## Evidence

Local evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/`

## Pre-dispatch gates

- all three pinned BF16 network-cap guard source SHA-256 values matched `AGENTS.md`;
- network-cap synthetic tests: `6/6 PASS`;
- external storage/cache available;
- reported free external disk: `1,152.25 GiB`;
- aggregate network ledger initialized at `0 B / 0 requests / 0 retries`.

## Q4 baseline stop

The first fixed-order state was P3 `P3_t01:2`, frozen Q4 verifier target token `1620`.

The replayed Q4 verifier top1 remained `1620`, but the final-logit provenance SHA gate failed.

Reported hashes in the Pi return were abbreviated:
- observed: `97cde5dd...297cd52e`;
- expected: `58d20d90...185432`.

The exact full hashes remain in the local evidence directory and must be recovered during the reconciliation checkpoint rather than inferred from the abbreviated return.

## Cost / isolation

- completed BF16 states: `0`;
- network bytes: `0`;
- requests: `0`;
- retries: `0`;
- no BF16 dispatch occurred.

## Scientific interpretation

The STOP is valid. The pilot cannot support `BF16_TARGET_RECOVERY_SIGNAL`, `NO_USEFUL_BF16_TARGET_RECOVERY`, `BF16_TARGET_EFFECT_AMBIGUOUS`, or `BF16_TARGET_PILOT_NETWORK_CAP_ABORT` because the BF16 intervention never occurred.

Matching verifier top1 is insufficient to waive the preregistered Q4 provenance gate. The logit-hash mismatch may represent hash/serialization semantics, a mechanically different replay path, or real numerical drift. Those possibilities must be isolated before any BF16 network/compute is authorized.

No post-hoc tolerance relaxation or state substitution is allowed.

## Next checkpoint

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

P3-only, Q4-only diagnostic. Recover the exact expected/observed artifacts and hash semantics, compare original frozen producer versus current pilot replay, quantify full-vector/tap/router drift, and locate the earliest divergence. No BF16 target execution and no network.
