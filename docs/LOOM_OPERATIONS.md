# LOOM DEEP local operation

LOOM has two local, selectable 30B profiles. They use one loopback-only endpoint and only one profile is served at a time.

| Selection | Pi model label | Purpose |
| --- | --- | --- |
| `fast` (default) | `loom-local/loom-deep-30b-s32` | Canonical S32 FAST profile. Use this normally. |
| `unlocked` | `loom-local/loom-deep-30b-unlocked` | Validated abliterated profile. It is materially slower, uses more swap, and has intentionally different safety/disposition behavior. |

## Normal commands

Run these from the repository root:

```bash
# Select a profile. `use` always stops the currently managed LOOM server first.
scripts/loom-deep use fast
scripts/loom-deep use unlocked

# Start the selected profile, or stop/check it.
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

If no local selection state exists, `fast` is selected. Normal serving is always:

- WebUI: <http://127.0.0.1:18080/>
- OpenAI-compatible API base: `http://127.0.0.1:18080/v1`
- Health: `http://127.0.0.1:18080/health`

The server is started with `--offline --host 127.0.0.1` and never intentionally binds publicly. Do not start both profiles manually; the unified manager prevents two managed 30B servers from being resident.

## Pi and Context Intelligence

Both labels are installed under the `loom-local` provider and point at the same endpoint. Select one in Pi without changing endpoint configuration:

```bash
pi --model loom-local/loom-deep-30b-s32
pi --model loom-local/loom-deep-30b-unlocked
```

The global Pi2 Context Intelligence implementation is enabled by default and serves `loom-local` without a LOOM-specific project extension. Historical WP2 Caveman+Cavemem provenance remains available through `scripts/loom-context`. Its independent rollback leaves serving intact:

```bash
PI2_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-s32
```

The local Pi model entries pin deterministic `max_tokens=256`, `temperature=0`, and `top_p=1` request parameters for this llama.cpp path.

## Rollback to the default

```bash
scripts/loom-deep use fast
scripts/loom-deep start
scripts/loom-deep health
```

This stops UNLOCKED, restores the FAST alias at the same endpoint, and requires no Pi rewiring.

## Local artifact provenance

Model data is local-only and ignored by Git. Stable paths are hard links to their previously verified local artifacts, so no multi-GB copy was made:

| Path | SHA256 |
| --- | --- |
| `models/loom-deep-30b-fast.gguf` | `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251` |
| `models/loom-deep-30b-unlocked.gguf` | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` |

The pinned local server binary is `.loom/runtime/loom-llama-server`, SHA256 `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

UNLOCKED reproduced its frozen WP3-R2 result (0/6 explicit refusals and 8/8 benign controls), but that behavioral openness is not a safety improvement. On the 8 GiB M1 it has lower throughput and materially higher swap/memory pressure; choose FAST unless that explicit trade-off is wanted.
