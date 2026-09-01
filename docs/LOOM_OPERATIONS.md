# LOOM DEEP local operation

The sole locally runnable 30B profile is the promoted UOPT-002 UNLOCKED profile. It serves one loopback-only endpoint.

| Selection | Pi model label | Purpose |
| --- | --- | --- |
| `unlocked` (default) | `loom-local/loom-deep-30b-unlocked` | Promoted UOPT-002 profile, using its lossless expert-major sidecar and isolated runtime. |

## Normal commands

Run these from the repository root:

```bash
scripts/loom-deep use unlocked
scripts/loom-deep start
scripts/loom-deep stop
scripts/loom-deep status
scripts/loom-deep health
scripts/loom-deep current
```

If no local selection state exists, `unlocked` is selected. Serving is always:

- WebUI: <http://127.0.0.1:18080/>
- OpenAI-compatible API base: `http://127.0.0.1:18080/v1`
- Health: `http://127.0.0.1:18080/health`

The server is started with `--offline --host 127.0.0.1` and never intentionally binds publicly.

## Pi and Context Intelligence

Use the local endpoint through Pi:

```bash
pi --model loom-local/loom-deep-30b-unlocked
```

The global Pi2 Context Intelligence implementation is enabled by default and serves `loom-local` without a LOOM-specific project extension. Historical WP2 Caveman+Cavemem provenance remains available through `scripts/loom-context`. Its independent rollback leaves serving intact:

```bash
PI2_CONTEXT_INTELLIGENCE=0 pi --model loom-local/loom-deep-30b-unlocked
```

The local Pi model entry pins deterministic `max_tokens=256`, `temperature=0`, and `top_p=1` request parameters for this llama.cpp path.

## FAST archive

FAST is not available in the local `models/` directory and cannot be selected with `scripts/loom-deep`. Its verified archival copy is:

```text
<external-archive>/archived-models/loom-deep-30b-fast.gguf
```

Its SHA256 is `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`. The external archive is not a runtime dependency; restoring FAST would require a deliberate, verified restoration decision.

## Local artifact provenance

Model data is local-only and ignored by Git:

| Path | SHA256 |
| --- | --- |
| `models/loom-deep-30b-unlocked.gguf` | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` |
| `models/unlocked-expert-major-v1.bin` | `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e` |

The promoted runtime is `.loom/runtime/loom-uopt002/llama-server`, SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`. The pinned `.loom/runtime/loom-llama-server` remains the UOPT-001 rollback runtime.

UNLOCKED reproduced its frozen WP3-R2 result (0/6 explicit refusals and 8/8 benign controls), but that behavioral openness is not a safety improvement.
