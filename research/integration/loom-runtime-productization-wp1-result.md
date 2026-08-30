# LOOM Runtime + Product Serving — WP1 Result

Date: 2026-08-30
Classification: **LOOM_RUNTIME_PRODUCTIZATION_WP1_GO**

## Outcome

WP1 completed successfully. The canonical 30B DEEP model is now practically usable through a persistent localhost `llama-server` path, the embedded existing WebUI, an OpenAI-compatible API, and Pi.

The validated runtime profile advanced from S24 to **S32**.

Canonical model artifact remains:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Final `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Canonical rollback `llama-completion` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

## Runtime selection

Matched deterministic 3 x 96-token S24/S32 A/B produced byte-identical outputs.

| Profile | Median decode | Median E2E |
|---|---:|---:|
| S24 | 4.382 tok/s | 29.185 s |
| **S32** | **5.596 tok/s** | **23.849 s** |

Derived ratios:
- S32/S24 decode: **1.2768x**;
- S32/S24 E2E: **0.8172**.

Resource observations for S32:
- peak RSS: **3914.6 MiB**;
- peak sampled swap: **1651.88 MiB**;
- minimum sampled free-memory percentage: **10%**;
- no crash, OOM, corruption, or critical memory-pressure indication.

S32 is therefore promoted to canonical DEEP runtime profile. S24 remains the documented rollback profile.

## Final serving path

Server:
`llama-server`, localhost-only.

Browser UI:
existing embedded `llama-server` WebUI.

URL:
`http://127.0.0.1:18080/`

API:
`http://127.0.0.1:18080/v1/chat/completions`

Health:
`http://127.0.0.1:18080/health`

Current configured model id reported by WP1:
`loom-deep-30b-s24`

Note: this identifier is now semantically stale because the selected runtime profile is S32. It is an operational naming inconsistency only, not a runtime/result failure. Rename during a later authorized integration/configuration pass so the provider/model id reflects S32 or a profile-neutral DEEP name.

## Operations

```bash
scripts/loom-deep-server start
scripts/loom-deep-server status
scripts/loom-deep-server health
scripts/loom-deep-server stop
```

Final flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`

## Serving-path cache

Final S32 server uses bounded:
`--cache-ram 512`

Stable-prefix smoke:
- cold: 136 prompt tokens, 27.809 s;
- reuse: 134 cached / 2 evaluated tokens, 280.389 ms;
- reuse E2E: 0.332 s.

This directly validates persistent-server prompt/KV reuse. It is separate from the earlier completion-mode Prompt Cache R2 result, though both support the same product direction.

## Privacy / WebUI

No custom LOOM UI was built.

Selected UI:
embedded existing `llama.cpp` WebUI.

Final serving configuration:
- `--offline`;
- bind only `127.0.0.1`;
- UI MCP proxy disabled;
- server tools disabled.

Final socket inspection showed only the loopback listener.
Static/source inspection found local relative API use and no configured telemetry, cloud inference, or conversation-data egress for the selected configuration.

## Pi integration

Pi provider configuration:
`~/.pi/agent/models.json`

Configured local provider/model:
`loom-local/loom-deep-30b-s24`

Endpoint:
`http://127.0.0.1:18080/v1`

Backup:
`results-local/runtime-productization-wp1/20260830T124040Z/pi-backup/`

Final offline Pi request succeeded with a coherent streamed answer to `2+2`.

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/pi_final_s32_config_test.jsonl`

## Changed local files

- `config/loom-deep-server.env`
- `scripts/loom-deep-server`
- `~/.pi/agent/models.json`

## Evidence

Root:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Full local report:
`results-local/runtime-productization-wp1/20260830T124040Z/wp1-final-report.md`

## Reverted / failed attempts

- initial server `-b 1` startup asserted during slot initialization; reverted to batch=context;
- no source patch/prefetch implementation retained;
- S24 remains rollback.

## Product interpretation

WP1 achieved the intended runtime/productization milestone:
- direct decode exceeds the initial >=5 tok/s target;
- 30B serving is persistent and localhost-only;
- existing WebUI is usable;
- OpenAI-compatible local API is operational;
- Pi is connected to the same local model path;
- serving-path cache reuse is directly validated;
- operational start/stop/health workflow exists.

WP1 does not include Context Intelligence (Caveman/Cavemem) or Behavioral Transform work.
