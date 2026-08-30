# LOOM Final Integration + Acceptance — WP4 Result

Date: 2026-08-30
Checkpoint: `LOOM_FINAL_ACCEPTANCE_WP4`
Classification: **`LOOM_FINAL_ACCEPTANCE_WP4_GO`**

## Product decision

WP4 productized the two already-validated DEEP profiles without replacing the canonical default:

| Selection | Served alias / Pi label | Product role |
| --- | --- | --- |
| `fast` | `loom-deep-30b-s32` / `loom-local/loom-deep-30b-s32` | Default canonical S32 FAST profile |
| `unlocked` | `loom-deep-30b-unlocked` / `loom-local/loom-deep-30b-unlocked` | Explicit opt-in behavioral-unlock profile |

The unified operator interface is:

```bash
scripts/loom-deep use fast
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

`use` cleanly stops the currently managed LOOM server before changing selection; `start` refuses an occupied product port. The default when no selection state exists is `fast`. Both profiles use only `127.0.0.1:18080`, including the embedded WebUI and `/v1` API.

## Stable artifacts and provenance

No model was redownloaded or copied. Source GGUFs and the pinned server were SHA256-verified before placement, then hard-linked on the same APFS filesystem and rehashed after placement and at final rollback. Stable links and sources have matching inode/device identifiers and link count 2.

| Final artifact | SHA256 | Size |
| --- | --- | ---: |
| `models/loom-deep-30b-fast.gguf` | `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251` | 12,424,439,872 bytes |
| `models/loom-deep-30b-unlocked.gguf` | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` | 13,292,468,896 bytes |
| `.loom/runtime/loom-llama-server` | `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506` | 49,984 bytes |

The runtime remains `kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892` with S32-style flags: `--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

## Acceptance sequence and interfaces

A clean final-manager sequence ran FAST → UNLOCKED → FAST. The original FAST PID `37316` was confirmed stopped before UNLOCKED PID `37510`; that UNLOCKED PID was confirmed stopped before FAST rollback PID `37814`. A post-Pi-correction repeat also ran FAST PID `38099` through UNLOCKED PID `37983` and back to FAST, with no concurrent listener. The final state is FAST on `127.0.0.1:18080` with health `{"status":"ok"}`.

For each profile, `/health`, `/v1/models`, a deterministic OpenAI-compatible chat request, and WebUI HTML returned successfully. `lsof` recorded only a `127.0.0.1:18080` listener. The active `/v1/models` alias changed correctly between `loom-deep-30b-s32` and `loom-deep-30b-unlocked`.

Both Pi labels were added to the local `loom-local` provider at the stable endpoint. Real Pi requests loaded the WP2 extension and produced a new packing record for each profile. An initial multi-token Pi marker check exposed a one-token completion cap; the deterministic local Pi entries were corrected with model `samplingParams` (`max_tokens=256`, `temperature=0`, `top_p=1`). Retests returned exactly `alpha beta gamma delta` through Pi + WP2 for both FAST and UNLOCKED. This was a bounded integration correction, not a model change.

`LOOM_CONTEXT_INTELLIGENCE=0` was then exercised through Pi on final FAST: it returned the expected exact response and left the packing-record count unchanged (`8 -> 8`). `scripts/test_loom_context.py` also passed its deterministic privacy, compression, recovery, no-op, and packing invariants.

## Frozen UNLOCKED reproduction

The unchanged frozen files were hashed before execution:

- `benchmarks/behavioral-transform-wp3/frozen-v1.json`: `c6d3785d3c4b840c9549dbb42623291df02aa93650f77da8bb994e95179159de`
- `benchmarks/behavioral-unlock-wp3-r2/r2-controls-v1.json`: `72266046a461f28707ef164f5fdce13f9c9281d9590f0be07773844c8cd8c571`

Using the existing deterministic evaluator against the final UNLOCKED alias:

| Frozen set | Result |
| --- | ---: |
| Held-out explicit refusals | **0/6** |
| Held-out degeneration | **0/6** |
| Benign capability | **8/8** |
| Benign degeneration proxy | 1/8 (the existing short exact-number control) |

This reproduces the selected WP3-R2 behavior/capability result. The abliterated model's disposition/safety drift remains an explicit product caveat; its openness must not be described as a safety or general capability improvement.

## Performance, resources, and cache

The following are deterministic representative API probes. The three performance requests are cache-warm after the first request and output lengths differ by profile, so they are operational health measurements, not a matched quality claim.

| Profile | Median decode | Median prefill | Median E2E | RSS before → after | Swap used before → after | Memory free % before → after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FAST | 6.209 tok/s | 3.438 tok/s | 7.131 s | 3,999,696 → 4,014,752 KiB | 1269.31 → 1307.75 MiB | 11% → 10% |
| UNLOCKED | 2.963 tok/s | 1.673 tok/s | 9.129 s | 4,133,664 → 4,157,392 KiB | 1667.00 → 1708.00 MiB | 8% → 9% |

FAST decode is within ordinary run-to-run tolerance of the WP1 S32 5.596 tok/s matched median. UNLOCKED completed the complete 14-case frozen run and probe without crash, OOM, corruption, or failed rollback, but its low free-memory percentage and higher swap remain material operator caveats.

The inherited `--cache-ram 512` prompt/KV mechanism was directly observed for both final profiles with an identical 1,149-token prefix:

| Profile | Cold prompt evaluation | Reuse prompt evaluation | Cached/evaluated on reuse | Reuse E2E |
| --- | ---: | ---: | ---: | ---: |
| FAST | 1,135 tokens / 184.269 s | 1 token / 56.991 ms | 1,148 / 1 | 0.221 s |
| UNLOCKED | 1,135 tokens / 373.774 s | 1 token / 61.773 ms | 1,148 / 1 | 0.242 s |

Thus both final profile paths are compatible with the same validated persistent prompt/KV cache; no new cache layer was added.

## Rollback and final state

Final rollback was exercised with:

```bash
scripts/loom-deep use fast
scripts/loom-deep start
scripts/loom-deep health
```

It restored FAST alias `loom-deep-30b-s32`, passed health, `/v1/models`, and `FAST_ROLLBACK_OK` API checks, and reverified both model hashes plus the server hash. The machine is left in this documented default state with WP2 enabled.

## Evidence and changed files

Evidence root: `results-local/final-acceptance-wp4/20260830T182958Z/`.

It contains pre/post placement hashes and hard-link metadata, lifecycle/API/WebUI captures, Pi/WP2 transcripts and packing deltas, frozen evaluation JSON, API/cache/resource probes, Pi configuration backups/hashes, final product hashes, Context Intelligence rollback evidence, and final Git status.

WP4-created or updated repository files:

- `config/loom-deep-profiles.env`
- `config/loom-deep-server.env` (stable compatibility paths)
- `config/loom-deep-r2-abliterated-q3ks.env` (stable compatibility paths)
- `scripts/loom-deep`
- `scripts/loom_wp4_probe.py`
- `docs/LOOM_OPERATIONS.md`
- `research/integration/loom-final-acceptance-wp4-result.md`

Local-only changes excluded from Git: ignored `models/` hard links, `.loom/` state/runtime link, `results-local/` evidence, and `~/.pi/agent/models.json` (backed up in evidence). No commit or push was performed.
