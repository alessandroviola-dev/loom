# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — pilot 002 BF16 producer for P3 was valid, but DFlash scored the wrong continuation row. P3 can likely be recovered offline without another BF16 run.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001_PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`
Next: `LOOM_DFLASH_PILOT_002_SCORING_ROW_REPAIR_OFFLINE_001`
Pi context: `/AGENTS.md` v3.18.

## Stable

Frozen order: P3 -> P1 -> P2.
Exact Q4 baselines:
- P3 target 1620, rank 2, proposal 5416, segmentation `[63,1]`, KV boundary 63;
- P1 target 326, rank 3, proposal 3100;
- P2 target 994, rank 3, proposal 4057.

Pinned BF16 revision: `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Network guard/cap: PASS; `8 GiB / 1024 requests`, abort before dispatch.

## Pilot 002

Operational cap abort after P3 completion and partial P1:
- `8,583,061,312 B`, `1007` requests, `7` retries;
- P3 BF16 complete; P1 partial; P2 unexecuted;
- reusable cache: 744 completed P3 experts + 153 completed P1 experts, subject to pinned validation.

Causal audit:
- `_002.py` SHA-256 `2c1bfdcfbca1da39d867432570037867f25bea65e5b9407ba6e5eaacb8b6352f`;
- full-taps hazard absent;
- BF16 P3 producer valid/frozen-equivalent `[63,1]`, KV boundary 63;
- sole confirmed causal bug: wrong DFlash row. P3 used row 2; correct row is 1;
- offline Q4 recompute at correct row restores rank 2 / proposal 5416.

Therefore original P3 `rank 5 -> 13` and `4330 -> 2790` are invalid. Do not interpret them.

## Exact next step

Strictly offline scoring-row repair using existing P3 arrays. Require Q4 rank 2/proposal 5416, then rescore the existing valid BF16 taps at the same correct row and report target-1620 rank/top-k/proposal plus full 32k drift. Validate generic selector logic P1 row5 and P2 row2. No BF16 forward/network.
