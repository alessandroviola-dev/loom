# LOOM — Active Handoff

Last updated: 2026-09-04
Status: LOOM final product GO/persisted; UOPT-001 PARTIAL_GO/persisted; UOPT-002 GO/persisted; **UOPT-003 GO locally promoted as the normal UNLOCKED S40 profile; UOPT-004 NO_GO; UOPT-005 COMPLETE / NO_GO**.
Repository: `Ilcoach/loom`
Branch: `research/unlocked-speed-001`
Pi context: `/AGENTS.md` v3.96.
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

### UNLOCKED / optimized UOPT-003 S40
- source/rollback GGUF `models/loom-deep-30b-unlocked.gguf`;
- source SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- lossless expert-major sidecar `models/unlocked-expert-major-v1.bin`;
- sidecar size `12,457,082,880` bytes;
- sidecar SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
- isolated runtime `.loom/runtime/loom-uopt002/llama-server`;
- runtime SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`;
- normal `unlocked` product uses S40, CPU-MoE/no-mmap, cache RAM 512 and `-ub 4`, retaining UOPT-002 sidecar/runtime/LRU/async resolver;
- `scripts/loom-deep use unlocked-s32` is the managed UOPT-002 S32 same-runtime/sidecar rollback;
- UOPT-001 rollback remains source GGUF + pinned rollback runtime + `-ub 2`.

Frozen behavior/capability remains:
- refusal `0/6`;
- held-out degeneration `0/6`;
- benign capability `8/8`.

UOPT-003 matched promotion confirmation (S32 -> S40):
- fresh short decode median **`6.660 -> 7.557 tok/s`** (+13.46%);
- 1,155-token cold prompt **`7.147 -> 11.306 tok/s`**;
- 1,155-token cold TTFT **`161.676 -> 102.242 s`** (-36.76%);
- expert hit rate `81.745% -> 89.831%`, with misses `90,229 -> 50,260`.
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

### UOPT-003 — COMPLETE / GO / LOCAL PROMOTION PENDING PERSISTENCE

Result:
`research/integration/loom-unlocked-speed-optimization-003-result.md`

Evidence:
`results-local/unlocked-speed-uopt-003/20260901T130729Z/`

S40 was the sole stable residency winner. S48 was rejected after Metal GPU timeout; a frequency-aware cache policy did not show a reproducible net gain; existing route-known async sidecar resolution remains unchanged. Frozen `0/6`, `0/6`, `8/8` and API/WebUI/Pi2 passed. Experimental frequency source/build/runtime were removed after evidence retention.

### UOPT-004 — COMPLETE / NO_GO

Result:
`research/integration/loom-unlocked-speed-optimization-004-result.md`

Expert-only `Q2_K` quantization from BF16 reduced the expert footprint by `23.636%` and passed frozen gates, but failed functional quality (`3/4`) and arithmetic (`414` versus expected `410`). Temporary artifacts were removed. Production S40 is unchanged.

### UOPT-005 — COMPLETE / NO_GO

Result:
`research/integration/loom-unlocked-speed-optimization-005-result.md`

The `13/13` BF16 source verification, HF→BF16 GGUF validation, imatrix build, and Candidate A expert `IQ3_XXS` build completed. Storage isolation identified external archive as the initial smoke bottleneck: decode `0.69 -> 9.63 tok/s`, prefill `0.24 -> 6.31 tok/s`, and TTFT `148.277 -> 5.605 s`. Candidate A passed refusal `0/6`, degeneration `0/6`, and benign capability `8/8`, but failed functional quality (`3/4`) and arithmetic (`400` vs required `410`). B.1 Q3 `40–47` returned `400`; B.2 Q3 `36–47` and B.3 Q3 `32–47` returned `414`. The layer frontier found only 37 and 39 causal; the 11 losslessly validated tensor splices exhausted causal set `{up37, down37, down39}` (all nonempty subsets `414`, empty `400`), never `410`. Expert-by-expert selection was not pursued: it requires a new format/runtime, estimated 1–3 days, with unproven benefit. UOPT-005 is NO_GO; production S40 is unchanged.

## Storage / archive state

Historical LOOM material was archived under:
`<external-archive>/reclamation-uopt-002-20260901/`

The external disk is archive/backup only and is not required for normal inference.

FAST was archived on 2026-09-01 at `archived-models/loom-deep-30b-fast.gguf` after byte-size and SHA256 verification. It is unavailable locally.

## Current exact action

Production operation remains the promoted UOPT-003 S40 UNLOCKED profile. `unlocked-s32` is the managed prior UOPT-002 rollback; the UOPT-001 source runtime remains the deeper local rollback baseline; FAST is externally archived.

UOPT-005 is closed NO_GO. Production operation remains the unchanged promoted UOPT-003 S40 profile.
