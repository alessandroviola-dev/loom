# LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001 — Result

Date: 2026-08-25
Classification: `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`

## Decisive finding

Pilot 002's expensive P3 BF16 producer path was valid, but its DFlash scoring selector was not.

Executed local source SHA-256:
`2c1bfdcfbca1da39d867432570037867f25bea65e5b9407ba6e5eaacb8b6352f`

Evidence:
`results-local/research/dflash-bf16-pilot-002-causal-validity-audit-001/20260825T154402Z/audit.json`

## Hazard audit

- Q4 full-taps hazard: **absent**.
- DFlash continuation-row hazard: **present**. P3 used row `2`; preregistered P3 continuation position `2` requires DFlash row `1` in the sliced continuation logits.
- BF16 fresh-full-prefix hazard: **absent**.

Offline exact Q4 recomputation with the correct selector restores the frozen P3 result:
- target `1620`;
- rank `2`;
- proposal `5416`.

BF16 P3 producer provenance is frozen-equivalent:
- segmentation `[63,1]`;
- KV boundary `63`;
- not a fresh full-prefix producer.

## Reuse decision

The reported pilot-002 P3 DFlash causal numbers are invalid because they score the wrong continuation row.

The underlying P3 BF16 treatment arrays are not discarded: because their producer segmentation is frozen-equivalent, they may be rescored offline with the predetermined correct row without executing a new BF16 treatment.

Reusable cache:
- 744 completed P3 experts;
- 153 completed P1 experts;
- subject to pinned manifest/hash validation.

## Next

Mechanically repair continuation-row selection in the pilot runner and validate it strictly offline using the already-retained P3 Q4/BF16 arrays. The repaired offline P3 score must restore Q4 rank `2` / proposal `5416`; then compute the corresponding BF16-tap DFlash score from the existing BF16 taps. No new BF16 forward/network is authorized until this passes.
