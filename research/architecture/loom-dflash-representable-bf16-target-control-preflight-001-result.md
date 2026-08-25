# LOOM DFlash Representable BF16 Target Control Preflight 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`
Classification: `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`
Gate: `PASS_WITH_MECHANICAL_NETWORK_GUARD_REQUIRED`

## Purpose

Define the smallest informative Q4-target vs BF16-target causal pilot on DFlash-representable frozen states, while quantifying cache/network exposure before any target execution or download.

No target/BF16 forward, download, E2E, retraining, remapping, Git, or project-doc edit was performed by Pi.

## Selected representable states

Deterministic selection rule: lowest corrected baseline target rank within each prompt, tie-break by state ID.

- P1: `P1_t32`, position `6`, corrected target rank `3`, target token `326`, verifier prefix `79` tokens.
- P2: `P2_t16`, position `3`, corrected target rank `3`, target token `994`, verifier prefix `74` tokens.
- P3: `P3_t01`, position `2`, corrected target rank `2`, target token `1620`, verifier prefix `64` tokens.

The three states are on distinct P1/P2/P3 trajectories and require fresh KV state. No verifier computation can be shared across the selected states.

## Persistent BF16 cache audit

Integrity verification:
- dense manifests: `435`;
- cached routed experts: `3,470`;
- expert projections verified: `10,410`;
- SHA-256 failures: `0`.

Sizes:
- dense assets: `3,082,218,423 B`;
- expert cache: `32,755,649,797 B`;
- total retained BF16 cache: `35,837,957,463 B`.

External disk free space at preflight: `1,152.25 GiB`.

Cache is persistent and resumable.

## Q4-routing cache estimate

These counts use retained Q4 routing traces only. They are planning estimates, not predictions of exact BF16 cache use, because BF16 routing may diverge.

| State | Q4-estimated hits | Q4-estimated misses | Estimated missing bytes |
|---|---:|---:|---:|
| P1_t32:6 | 1,942 | 315 | 2,972,712,960 B |
| P2_t16:3 | 1,476 | 507 | 4,784,652,288 B |
| P3_t01:2 | 371 | 13 | 122,683,392 B |

Combined unique estimate:
- hits: `2,325`;
- misses: `703`;
- missing bytes: `6,634,340,352 B`.

The combined estimate is below the proposed 8-GiB pilot ceiling, but BF16 routing can create different misses.

## Network safety finding

Existing on-demand BF16 fetch/cache code provides:
- atomic persistent expert caching;
- resumability;
- retained partial cache after interruption.

However, the current path does **not** pre-check hard network-byte/request limits before dispatch. Therefore the expensive pilot is not yet authorized.

A mechanical pre-dispatch guard is required so a request is rejected before it would exceed either limit.

## Proposed later causal pilot

Selected states:
- `P1_t32:6`;
- `P2_t16:3`;
- `P3_t01:2`.

Scope:
- three frozen Q4 teacher-forced verifier forwards/replays as baseline as needed;
- three BF16 teacher-forced verifier forwards;
- separate fresh KV state per prompt trajectory.

Hard network limits:
- maximum total transferred bytes: `8 GiB`, including relevant transfer overhead/retries in the pilot ledger;
- maximum requests: `1,024`;
- mandatory `NETWORK_CAP_ABORT` before dispatch if the next request would exceed either cap.

Retention:
- selected-state target taps;
- target final logits where produced;
- routed-expert traces;
- DFlash 32k logits;
- corrected target-row ranks/top-k status;
- cache progress and network byte/request ledger;
- partial downloaded expert cache remains persistent/resumable.

Decisive Q4-vs-BF16 comparisons:
- tap drift by layer;
- DFlash full-32k logit movement;
- corrected target-row rank;
- top5/top10/top50/top100 membership;
- exact DFlash target top1.

## Scientific consequence

The representable-state BF16 target pilot is scientifically justified and storage-feasible, but it must not run until the hard pre-dispatch network/request guard is implemented and mechanically validated.

The next checkpoint is therefore a local mechanical safety repair, not the expensive causal pilot itself.

Evidence:
`results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z/`
