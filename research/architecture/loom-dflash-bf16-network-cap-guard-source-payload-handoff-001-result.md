# LOOM DFlash BF16 Network-Cap Guard Source Payload Handoff 001 — Result

Date: 2026-08-25

Checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

Classification: `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`

## Purpose

Close the final reproducibility gate between the locally validated BF16 network-cap guard and the GitHub branch by transferring and verifying the exact validated source bytes.

## Payload received

Archive: `dflash-bf16-network-cap-guard-source-payload-001.tar.gz`

- bytes: `30,095`
- SHA-256: `0c8fc52938c1be5642b8ca4abc1ba25944e8d44ff78fe038048ede19f433be2e`
- members: exactly the three preregistered `scripts/*.py` files; no extras.

Payload verification reproduced the preregistered file identities:

| Path | Bytes | SHA-256 | Git blob SHA |
|---|---:|---|---|
| `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` | 74,261 | `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376` | `00287bc793fce8b552c55b8706a2d7f4d69be08e` |
| `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` | 26,443 | `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f` | `b2366c1c78b960e0bba224a3eb2da8efe92e7bfc` |
| `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` | 11,741 | `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae` | `8ded2333d8007abec857d20b82e891b961add69b` |

## Git synchronization

The user committed only the three validated files and pushed commit:

`01a5f9b` — `Add validated BF16 network cap guard`

Direct remote reads on `research/stretch-015-divergence-attribution` returned the exact Git blob SHAs above. Those blob SHAs are identical to `git hash-object` computed from the received payload bytes.

Therefore the branch/fresh-clone source now contains the exact source state that previously passed:

- synthetic guard tests `6/6`;
- compile PASS;
- pre-dispatch byte/request rejection;
- deterministic `NETWORK_CAP_ABORT`;
- explicit bounded retry accounting;
- cache-hit zero network cost;
- partial/complete cache preservation and resumability;
- zero real network dispatch during validation.

No source reconstruction or behavioral modification was introduced during synchronization.

## Decision

The local-only reproducibility blocker is CLOSED.

The preregistered representable-state BF16 causal pilot may now be authorized under the validated hard ceilings:

- network: `8 GiB` cumulative;
- requests: `1,024` cumulative, retries included;
- abort before dispatch if the next request would exceed either cap;
- persistent/resumable cache.

Next checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`.
