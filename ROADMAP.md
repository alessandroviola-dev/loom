# LOOM Roadmap

Last updated: 2026-08-25
Current: `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`
Strategic next: `LOOM_DFLASH_PILOT_002_SCORING_ROW_REPAIR_OFFLINE_001`
Canonical context: `/AGENTS.md` v3.18.

## Stable chain

DFlash/verifier/taps/mapping remain frozen. Q4 baseline repair is PASS for P3/P1/P2. Closed hypotheses remain closed.

Pinned BF16 revision: `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Hard network cap remains `8 GiB / 1024 requests`, pre-dispatch abort.

## Pilot 002 audit

Pilot 002 hit the cap after valid BF16 P3 production and partial P1 caching. The expensive P3 producer path itself was frozen-equivalent (`[63,1]`, KV boundary 63).

The scientific score is invalid for one confirmed mechanical reason: DFlash used P3 row 2 instead of the predetermined row 1. Correct offline Q4 scoring restores rank 2/proposal 5416.

Thus the retained P3 BF16 arrays can be rescored offline; no repeat P3 BF16 treatment is justified at this point.

## Next

Repair generic continuation-row selection (`continuation_position - 1`) and validate strictly offline on existing P3 Q4/BF16 arrays. Recover corrected P3 causal score, validate P1/P2 row logic, and source-sync the repaired runner before any further network treatment.

Only after this PASS decide whether remaining P1/P2 BF16 execution is needed. Reuse the existing validated cache; do not repeat P3.
