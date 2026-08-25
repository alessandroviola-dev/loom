# LOOM — Q4 Baseline Segmentation Replay Repair 001

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`
Classification: `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`

## Purpose

Mechanically align the causal-pilot Q4 baseline producer with the original frozen continuation producer before any BF16/network retry. No model/math changes were permitted.

## Evidence

`results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

## Recovered exact segmentation

- P3 `P3_t01`: `[63,1]`; cached decode token `3889`; frozen KV boundary `63`.
- P1 `P1_t32`: initial `[43]`, then `31 x [1]`, then branch `5 x [1]` with tokens `[1674,52245,9935,11,1187]`; frozen KV boundary `74`.
- P2 `P2_t16`: initial `[57]`, then `15 x [1]`, then branch `2 x [1]` with tokens `[30130,84]`; frozen KV boundary `72`.

Producer segmentation and BF16-KV cache boundary are therefore part of the exact continuation-state provenance contract.

## Exact final-logit commitments

Expected and observed contiguous raw `float32` final-logit SHA-256 values matched exactly:

- P1: `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`
- P2: `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`
- P3: `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`

All three states passed exact token IDs, frozen base taps, BF16-KV boundary/offsets, selector `[0,-1]`, output `float32 [151936]`, final-logit SHA, finite-output and no-expert-leak gates.

## DFlash baseline recovery

Unchanged DFlash with corrected publisher decode recovered the preregistered baselines:

- P1 frozen target `326`: rank `3`; proposal `3100`.
- P2 frozen target `994`: rank `3`; proposal `4057`.
- P3 frozen target `1620`: rank `2`; proposal `5416`.

No target labels, frozen evidence, hashes or tolerances were altered.

## Execution isolation

Verified:
- BF16 target forwards: `0`;
- real network requests: `0`;
- network bytes: `0`;
- downloads: `0`;
- E2E runs: `0`.

## Reproducible source sync

User commit:
`8a74c3a2f039a771b4f1a682cc1754e48c76e50e`

Validated local SHA-256 values immediately before commit/push:

- `scripts/loom_dflash_q4_baseline_replay_shared_001.py` — `6da9e920f24e3c66ac8d37056d13e544dc70194b1d83987a5875db54590e1ea0`
- `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py` — `2882a8168612d1a3b6d0151b1b4511d21a51c0ba90b209f145f2fd3cc64a5e2b`

Remote Git blobs:

- shared Q4 replay: `f75771e99ca8e604521094ed494422409e31e65c`
- causal pilot: `3e3639749078c6ef60b25846a6df8d1ce4a4f48f`

The remote branch was verified identical to commit `8a74c3a2f039a771b4f1a682cc1754e48c76e50e` after push.

## Decision

The Q4 baseline provenance blocker is CLOSED. The first BF16 pilot attempt remains invalid and carries no BF16 scientific conclusion, but its mechanical cause is repaired.

A new checkpoint may re-attempt the same preregistered causal experiment without changing state selection, order, intervention, cost caps or decision criteria:

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

Fixed order remains `P3 -> P1 -> P2`; aggregate limits remain `8 GiB / 1,024 requests` with pre-dispatch `NETWORK_CAP_ABORT` and persistent/resumable cache.