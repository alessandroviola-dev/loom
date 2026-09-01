# LOOM — Active Handoff

Last updated: 2026-09-01
Status: LOOM final product GO/persisted; UOPT-001 PARTIAL_GO/persisted; **UOPT-002 GO/persisted and promoted behind the normal UNLOCKED profile**.
Repository: `Ilcoach/loom`
Branch: `research/unlocked-speed-001`
Pi context: `/AGENTS.md` v3.94.
Latest optimization commit: `07223f99e75a44f559270af976ab2d8b52b5edb4`.

## Current product

Operator UX:
```text
scripts/loom-deep use unlocked
scripts/loom-deep start|stop|status|health|current
```

Loopback endpoint: `127.0.0.1:18080`.

`LOOM_CONTEXT_WEBUI_001` is locally validated and pending persistence: the public WebUI/API endpoint is a loopback-only gateway to UOPT-002 on private `127.0.0.1:18081`, importing the canonical global Pi2 Context Intelligence core. `LOOM_CONTEXT_WEBUI_CI=0` bypasses CI; `LOOM_CONTEXT_WEBUI_GATEWAY=0` restores direct backend serving. Evidence: `results-local/loom-context-webui-001-result.md`.

### FAST / archived
- archived model `<external-archive>/archived-models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical matched decode `5.596 tok/s` and FAST `-ub 1` remain provenance only;
- unavailable locally and not selectable by the profile manager.

### UNLOCKED / optimized UOPT-002
- source/rollback GGUF `models/loom-deep-30b-unlocked.gguf`;
- source SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- lossless expert-major sidecar `models/unlocked-expert-major-v1.bin`;
- sidecar size `12,457,082,880` bytes;
- sidecar SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
- isolated runtime `.loom/runtime/loom-uopt002/llama-server`;
- runtime SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`;
- UNLOCKED product uses `-ub 4`;
- UOPT-001 rollback remains source GGUF + pinned rollback runtime + `-ub 2`.

Frozen behavior/capability remains:
- refusal `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

Final promoted matched confirmation:
- fresh decode median **`6.903 tok/s`**;
- validated candidate median `7.359 tok/s`;
- 1,155-token cold TTFT **`162.726 s`**;
- validated candidate cold TTFT `156.949 s`;
- deterministic source-vs-sidecar A/B exact at identical settings.

The expert-major sidecar is lossless. It changes physical routed-expert I/O layout only; Qwen3 routed top-k, router behavior and model math are unchanged.

## Completed optimization lineage

### UOPT-001 — COMPLETE / PARTIAL_GO / PERSISTED

Commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained rollback: UNLOCKED `-ub 2`, FAST `-ub 1`.

Matched retained metrics:
- decode `2.579 -> 3.161 tok/s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- warm long-prefix TTFT `0.195 -> 0.190 s`.

### UOPT-002 — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Result:
`research/integration/loom-unlocked-speed-optimization-002-result.md`

Key outcome:
- expert-paging telemetry isolated the dominant cold-prefill bottleneck;
- full lossless expert-major sidecar was built and byte-verified against all 18,432 routed-expert source components;
- miss I/O changed from three source-GGUF reads to one sidecar `preadv` path;
- decode full-GO gate >= `5.0 tok/s` passed;
- cold TTFT full-GO gate <= `184 s` passed;
- API/WebUI/Pi+WP2/cache/loopback and frozen gates passed;
- FAST and source UNLOCKED hashes unchanged;
- no external-drive runtime dependency.

## Storage / archive state

Historical LOOM material was archived under:
`<external-archive>/reclamation-uopt-002-20260901/`

The external disk is archive/backup only and is not required for normal inference.

FAST was archived on 2026-09-01 at `archived-models/loom-deep-30b-fast.gguf` after byte-size and SHA256 verification. It is unavailable locally.

## Current exact action

No active research macro. Normal operation uses the promoted UOPT-002 UNLOCKED profile. The UOPT-001 source UNLOCKED runtime remains the local rollback baseline; FAST is externally archived.

Any further optimization should start as a new explicitly authorized macro rather than silently extending UOPT-002.
