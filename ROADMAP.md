# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001_MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`
Strategic next: `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.3.

## Stable DFlash chain

Still valid:
- target tap interface `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

BF16 branch:
- Q4->BF16 target states drift materially;
- Q4/BF16 target top1 on P1_t01 both `12050`;
- Q4->BF16 taps materially move drafter 32k logits;
- ~33 GiB BF16 cache and exact P1_t01 taps/logits retained externally.

## Resolved — d2t offset semantics

Authoritative semantics:
- draft vocab size `32,000`;
- `d2t` stores `selected_target_id - draft_row`;
- correct decode is `draft_row + d2t[draft_row]`;
- `t2d` marks the 32,000 selected target IDs;
- vLLM reconstructs the same mapping before target-vocab logits expansion.

The old MLX direct-`d2t` decode was a mechanical bug.

## Completed — corrected offset decode repair

Checkpoint:
`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Classification:
`MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`

Report:
`research/architecture/loom-dflash-d2t-offset-decode-repair-001-result.md`

Evidence:
`results-local/research/dflash-d2t-offset-decode-repair-001/20260825T093731Z/`

Repair:
- 8 local decode/analysis paths corrected;
- raw drafter distribution unchanged;
- only row->target-token interpretation changed.

Correct mapping:
- 32,000 rows;
- 32,000 valid unique reconstructed target IDs;
- exact equality with `t2d` TRUE support;
- true effective support `32,000`.

Corrected frozen support:
- representable `50/63` (`79.37%`);
- unsupported `13/63` (`20.63%`);
- P1_t01 target `12050` remains unsupported.

Corrected proposals:
- raw draft-row argmax unchanged `63/63`;
- decoded token changes `63/63` vs old faulty interpretation;
- exact target matches remain `0/63`;
- P1_t01 corrected proposal `8747`.

Therefore:
- old `17,018` effective support is superseded;
- old `30/63 vs 33/63` support split is superseded;
- old numeric proposal IDs are superseded;
- **corrected frozen top1 compatibility is still `0/63`**.

Target-distribution top5/top10/top50 and proposal ranks were unavailable because full target logits were not retained. No target forward was performed.

Historical E2E `0/96` remains contaminated until replayed with corrected decode; no E2E rerun is authorized yet.

## Current strategic interpretation

The mapping bug explained a large part of the apparent support failure but did not explain drafter incompatibility.

Reduced vocabulary remains a secondary blocker (`13/63` unsupported), while all `50/63` representable target tokens are nevertheless wrong at top1. The remaining problem is therefore in drafter alignment / training distribution / target-interface compatibility rather than simple output-ID translation.

## Next — corrected drafter target-rank audit

Checkpoint:
`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Purpose:
Determine whether DFlash is at least directionally aligned with the exact target tokens on the 50 representable frozen states.

Cheap diagnostic only:
1. invert the corrected 32k support to obtain the unique draft row for each representable target token;
2. use retained full drafter logits if present; otherwise rerun only the unchanged drafter on frozen tap evidence;
3. measure exact target-row rank, probability/logit and top-k membership for each of the 50 states;
4. report min/P25/P50/mean/P75/max target-row rank and counts in top1/top5/top10/top50/top100/top1000;
5. keep the 13 unsupported states outside rank statistics;
6. no target-model or BF16 execution.

Decision:
- target rows frequently near top despite 0/63 top1 -> continue diagnosis of calibration/interface sensitivity;
- target rows generally very low -> learned drafter is materially incompatible with these frozen target states and DFlash salvage should be weighed against returning to LOOM's main serving/I/O path.

## Later order

1. `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`;
2. decide whether remaining DFlash alignment is worth further salvage work;
3. only if supported, identify the next one-factor compatibility mechanism;
4. corrected bounded E2E only after useful compatibility evidence exists;
5. memory/performance optimization only after acceptance becomes non-zero/useful;
6. otherwise return to the next high-leverage 30B-on-8GB architecture/I/O branch.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
