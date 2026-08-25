# LOOM — Pi Agent Protocol

Version: 3.18
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this persistent context. WP prompts carry only the active delta.

## Role / rules

Pi: local inspection, minimum authorized mechanical change, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git/push/PR/edit project docs unless explicitly authorized.

Rules:
1. one-factor experiments; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
3. continuation provenance includes IDs, producer segmentation, KV boundary, selector and DFlash continuation row;
4. treatment comparison is invalid if precision/quantization is not the only material changed factor;
5. expensive/network work requires retained/resumable artifacts and pre-dispatch hard caps;
6. STOP on ambiguity/missing provenance.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Stable LOOM / DFlash facts

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`
Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`
Correct mapping: `target_id = draft_row + d2t[draft_row]`
Support: `50/63` representable, `13/63` unsupported; corrected DFlash exact top1 `0/63`.
Representable ranks min/median/mean/max: `2 / 93.5 / 438.82 / 3510`; top5/top10/top50/top100 `8/11/19/26`.

Closed explanations: temporal shift, MLX drafter implementation, static verifier/tap interface, tap transport dtype. Do not reopen without new evidence.

Pinned BF16 verifier revision: `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.
Network guard: PASS + remote source parity PASS.
Per valid pilot attempt cap: `8 GiB`, `1024` requests including retries, abort before dispatch.

Frozen causal order:
1. P3 `P3_t01:2` target `1620`, exact Q4 rank `2`, proposal `5416`;
2. P1 `P1_t32:6` target `326`, rank `3`, proposal `3100`;
3. P2 `P2_t16:3` target `994`, rank `3`, proposal `4057`.
No substitution/reordering.

## Exact Q4 baseline — PASS

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.
Evidence: `results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

Segmentation:
- P3 `[63,1]`, token `3889`, KV boundary `63`;
- P1 `[43] + 31x[1]`, branch `[1674,52245,9935,11,1187]`, boundary `74`;
- P2 `[57] + 15x[1]`, branch `[30130,84]`, boundary `72`.

Final-logit raw float32 SHA:
- P1 `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`;
- P2 `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`;
- P3 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

## Pilot 002 — operational cap abort; causal score invalid

Pilot evidence: `results-local/research/dflash-representable-bf16-target-causal-pilot-002/20260825T134150Z/`
Operational facts:
- P3 BF16 completed;
- P1 Q4 passed then BF16 cap-aborted; P2 unexecuted;
- network `8,583,061,312 B`, `1007` requests, `7` retries;
- next `9,437,184 B` request blocked before dispatch.

Audit:
`LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001` = `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`.
Evidence: `results-local/research/dflash-bf16-pilot-002-causal-validity-audit-001/20260825T154402Z/audit.json`
Executed `_002.py` SHA-256: `2c1bfdcfbca1da39d867432570037867f25bea65e5b9407ba6e5eaacb8b6352f`.

Audit result:
- full-taps hazard: NO;
- BF16 fresh-full-prefix hazard: NO;
- BF16 P3 producer is frozen-equivalent `[63,1]`, KV boundary `63`;
- scoring-row hazard: YES. P3 used DFlash row `2`; correct sliced continuation row is `1`;
- offline exact Q4 rescore with correct row restores rank `2`, proposal `5416`.

Therefore reported P3 `rank 5 -> 13` / `4330 -> 2790` is invalid. Do not interpret it.
Underlying P3 BF16 taps/arrays are potentially reusable because producer provenance is valid; they must be rescored offline with the predetermined correct row before being treated as causal evidence.
Reusable cache after pilot 002: 744 completed P3 experts + 153 completed P1 experts, subject to pinned manifest/hash validation.

## Next checkpoint

`LOOM_DFLASH_PILOT_002_SCORING_ROW_REPAIR_OFFLINE_001`

Strictly OFFLINE. No BF16 model forward, no network/downloads.

Goal:
mechanically repair continuation-row selection and recover P3 Q4-vs-BF16 DFlash scoring from already-existing valid arrays.

Required:
1. repair scoring selector to use each state's preregistered continuation position (`row = continuation_position - 1` in sliced continuation logits), not a hardcoded/faulty row;
2. use existing P3 Q4 and BF16 tap arrays only;
3. exact Q4 side must reproduce target 1620 rank `2`, proposal `5416`;
4. score existing BF16 P3 taps at the same correct row and report proposal plus target-1620 rank/top5/top10/top50/top100/top1;
5. BF16 verifier top1 remains `1620`; verify representability/mapping roundtrip;
6. report full 32k Q4-vs-BF16 drift at the corrected row;
7. validate row logic for P1 position 6 -> row 5 and P2 position 3 -> row 2 without executing treatment;
8. save repaired runner/source or minimal patch plus offline tests; no scientific treatment changes.

Classifications:
- `PILOT_SCORING_ROW_REPAIR_PASS`
- `PILOT_SCORING_ROW_REPAIR_FAIL`
- `PILOT_SCORING_ROW_REPAIR_AMBIGUOUS`

If PASS, P3 existing BF16 treatment may be scientifically interpreted from the corrected offline rescore; any later P1/P2 treatment requires this repaired runner to be source-synced and validated before network use.

Restrictions: no BF16 forward, network, E2E, retraining/remapping, state changes, tolerance relaxation, Git/docs edits.
