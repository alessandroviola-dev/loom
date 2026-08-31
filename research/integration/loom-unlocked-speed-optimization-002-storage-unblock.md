# LOOM UOPT-002 — Storage Unblock Checkpoint

Date: 2026-08-31
Branch: `research/unlocked-speed-001`
Checkpoint: `LOOM_UNLOCKED_SPEED_UOPT_002_STORAGE_UNBLOCKED`
Status: RESUME AUTHORIZED

## Why this checkpoint exists

UOPT-002 returned a genuine storage blocker after isolating cold latency to routed-expert paging. A separate authorized LOOM-only reclamation/archive pass has now removed that blocker without changing the persisted product or resuming UOPT-002 experiments.

## UOPT-002 measured state before the blocker

Persisted UOPT-001 UNLOCKED S32/ub2 was reproduced at:
- fresh decode: `3.192 tok/s`;
- ~1,155-token cold TTFT: `401.5 s`.

Exact runtime telemetry attributed the cold path to routed-expert paging:
- expert misses: `90,312`;
- `pread` calls: `270,936`;
- logical bytes requested: `183.1 GB`;
- aggregate sidecar resolution: `393.96 s`.

S24 residency regressed to `2.308 tok/s`; S32 remains the best safe profile.

The exact GGUF layout has three physical expert ranges per miss. A lossless one-layer expert-major probe reduced read calls `3 -> 1` while remaining cache-neutral. A full non-destructive compatible relayout was storage-blocked at that point.

Frozen checks at the blocker passed:
- explicit refusals `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`;
- WP2/API/WebUI/cache/loopback passed;
- FAST restored healthy;
- persisted UOPT-001 UNLOCKED unchanged.

## Storage reclamation result

LOOM-only cleanup/archive completed without resuming UOPT-002 and without Git persistence.

Internal free space:
- before cleanup: `3.850 GiB`;
- after cleanup: `58.416 GiB`;
- allocator-visible reclaim: `54.566 GiB`.

External archive root used exclusively for archival recovery:
`<external-archive>/reclamation-uopt-002-20260901/`

Approximately `79 GiB` was archived there. Deterministic source/archive manifests matched across `70,042` entries with relative path, size and SHA256 records.

Archived/removed local historical material included the incompatible ~`15.107 GiB` MLX-4bit fullbank, expert fullbank, obsolete GGUF candidates, DFlash caches, build/source trees and prior evidence. LOOM-only `.ruff_cache` and `scripts/__pycache__` were deleted as regenerable caches.

The external disk remains **archive/backup only**. Normal inference, expert paging, model loading and promoted UOPT-002 operation must not depend on `external archive`.

## Local artifacts verified after cleanup

FAST:
- SHA256 verified against canonical value;
- allocated bytes `12,424,441,856`;
- link count now `1`;
- retain locally during UOPT-002 as rollback;
- status `ARCHIVE_AFTER_UOPT002` only after a later explicit authorization.

UNLOCKED:
- SHA256 verified against canonical value;
- allocated bytes `13,292,470,272`;
- link count now `1`.

Production runtime SHA256 was reverified. A required ~21 MiB runtime dylib directory was initially archived, then restored after discovering the pinned binary's absolute local `LC_RPATH`; restored files were manifest-verified. Runtime has no external-drive file descriptors.

Post-cleanup validation passed:
- FAST start / health / stop;
- UOPT-001 UNLOCKED start / health / stop;
- WP2 deterministic test;
- final state FAST running healthy on `127.0.0.1:18080`;
- no `external archive` runtime file descriptors.

## Resume instruction

The UOPT-002 storage blocker is cleared. Resume the existing UOPT-002 macro from the architectural relayout/paging checkpoint; do **not** redo completed storage audit, reclamation, broad UOPT-001 flag tuning, or already-completed UOPT-002 attribution unless a narrow verification is necessary for experimental validity.

Priority next experiment:
1. build a **non-destructive full lossless expert-major/compatible relayout** on the internal SSD using the verified UNLOCKED source;
2. preserve the source GGUF unchanged and separately hash/provenance the derived candidate;
3. verify exact tensor/model semantics before performance promotion;
4. benchmark matched fresh decode and true cold TTFT against persisted UOPT-001 and the reproduced UOPT-002 baseline;
5. inspect whether `pread` count, logical bytes requested, pager time and page amplification fall as predicted;
6. if the relayout is not sufficient, continue the remaining authorized UOPT-002 architectural ladder (residency/prefetch/cache overlap and only then justified exact-output speculation).

Disk safety guardrail:
- construction may use the reclaimed internal SSD space;
- do not intentionally depend on the external archive for inference;
- keep enough headroom to preserve FAST + UOPT-001 rollback and avoid destructive storage pressure;
- if free internal space falls below `20 GiB` during candidate construction, stop creating additional large artifacts, remove only clearly temporary UOPT-002 construction artifacts, and reassess before proceeding.

All original UOPT-002 full-GO gates remain unchanged:
- fresh decode median `>=5.0 tok/s`;
- ~1,150-token cold TTFT `<=184 s` (stretch `<120 s`);
- frozen `0/6`, `0/6`, `8/8`;
- exact routed top-k semantics;
- API/WebUI/Pi+WP2/cache/loopback;
- exact hashes/provenance;
- no crash/OOM/corruption;
- rollback to FAST and persisted UOPT-001 UNLOCKED.

Pi still must not commit/push during UOPT-002 execution. Return only at final GO, justified PARTIAL_GO, or a new genuine contract-defined blocker.
