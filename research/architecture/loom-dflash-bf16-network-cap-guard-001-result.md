# LOOM DFlash BF16 Network Cap Guard 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`
Classification: `BF16_NETWORK_CAP_GUARD_PASS`

## Purpose

Mechanically validate a hard pre-dispatch cumulative network byte/request guard for the on-demand BF16 verifier cache path before any new expensive BF16 target execution.

## Local code delta validated by Pi

Modified in the local working tree:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py`
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py`

Important reproducibility note: these source-file modifications were made locally by Pi and are **not yet represented in the GitHub branch** at the time of this result-document commit. Pi is prohibited from Git operations, and ChatGPT does not have direct access to the local working-tree file contents. A source-sync checkpoint is therefore required before the branch itself can be called guard-ready.

## Validation results

- synthetic/unit tests: `6/6` PASS;
- compile: PASS;
- exact boundary: `10 B / 1 request` allowed under cap `10 B / 1 request`;
- byte-cap rejection occurs before `HTTPSConnection.request`;
- request-cap rejection occurs before `HTTPSConnection.request`;
- deterministic abort marker: `NETWORK_CAP_ABORT`;
- retry accounting: each pre-dispatch reservation charged exactly once; 2 attempts = `10 B / 2 requests`, with 1 bounded retry;
- persistent cache hit: `0 B / 0 requests`;
- abort preserves complete and partial cache files;
- resumed ledger/cache remains usable;
- real network dispatches observed: `0` because HTTPS dispatch was patched to fail.

## Evidence

`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

## Scientific / operational consequence

The guard behavior itself is validated locally and removes the safety blocker for the preregistered representable-state BF16 target pilot on this working tree.

However, reproducibility requires the exact validated source delta to be synchronized to GitHub before authorizing the expensive pilot. Do not reconstruct or rewrite the guard from the summary metrics; capture and persist the exact local implementation.

## Next checkpoint

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

Goal: export the exact local content or deterministic patch for the three validated files, without Git or further code changes, so ChatGPT can apply the already-tested implementation to the branch.

After exact source synchronization and remote verification, authorize the preregistered three-state Q4-vs-BF16 target pilot under hard `8 GiB / 1,024 request` pre-dispatch limits.
