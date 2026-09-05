# LOOM Roadmap

Last updated: 2026-09-04
Current: LOOM final product GO/fully persisted; UOPT-001 PARTIAL_GO/persisted; UOPT-002 GO/persisted; **UOPT-003 GO locally promoted as normal UNLOCKED S40; UOPT-004 NO_GO; UOPT-005 COMPLETE / NO_GO**.
Canonical context: `/AGENTS.md` v3.96.
Latest optimization commit: `07223f99e75a44f559270af976ab2d8b52b5edb4`.

## 1. Current product profiles

### FAST / archived
- archive `archived-models/loom-deep-30b-fast.gguf` on `<external-archive>`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical matched decode `5.596 tok/s`, WP4 snapshot `6.209 tok/s`, and `-ub 1` remain provenance only;
- unavailable locally and not a rollback profile.

### UNLOCKED / UOPT-003 S40
- label `loom-deep-30b-unlocked`;
- source/rollback GGUF `models/loom-deep-30b-unlocked.gguf`;
- source SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- lossless expert-major sidecar `models/unlocked-expert-major-v1.bin`;
- sidecar SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
- isolated patched runtime `.loom/runtime/loom-uopt002/llama-server`;
- runtime SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`;
- default `unlocked`: S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`, with UOPT-002 sidecar/runtime/LRU/async resolver unchanged;
- managed S32 rollback: `scripts/loom-deep use unlocked-s32`;
- frozen refusal `0/6`, held-out degeneration `0/6`, benign `8/8`;
- matched S32 -> S40 decode `6.660 -> 7.557 tok/s` (+13.46%);
- matched 1,155-token cold TTFT `161.676 -> 102.242 s` (-36.76%).

UOPT-002 UNLOCKED is the sole locally runnable 30B profile.

## 2. Operator interface

```text
scripts/loom-deep use unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable normal endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

`LOOM_CONTEXT_WEBUI_001` is locally validated and pending persistence. Default serving places the UOPT-002 backend on private `127.0.0.1:18081` behind a loopback-only `18080` gateway that imports canonical global Pi2 Context Intelligence. `LOOM_CONTEXT_WEBUI_CI=0` bypasses CI; `LOOM_CONTEXT_WEBUI_GATEWAY=0` restores direct backend serving.

The external backup volume is not required for runtime operation.

## 3. Completed work

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted. Caveman deterministic context packing/recovery + Cavemem SQLite/FTS5 memory.

WP3 Behavioral Transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace routes.

WP3-R2 Behavioral Unlock: GO / persisted.

WP4 Final Integration + Acceptance: GO / persisted in `98949e77863c93a7d9dba266204a911ab85db09c`.

### UOPT-001 — PARTIAL_GO / PERSISTED

Persistence commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained rollback product change: UNLOCKED `-ub 2` while FAST remains `-ub 1`.

Matched metrics:
- decode `2.579 -> 3.161 tok/s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- warm long-prefix TTFT `0.195 -> 0.190 s`.

All frozen gates and product integration passed, but current-runtime tuning did not reach the full targets.

### UOPT-002 — GO / PERSISTED

Persistence commit:
`07223f99e75a44f559270af976ab2d8b52b5edb4`.

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Result:
`research/integration/loom-unlocked-speed-optimization-002-result.md`

Promoted architecture:
- unchanged source GGUF + local lossless expert-major routed-expert sidecar;
- isolated patched runtime built from pinned llama.cpp lineage;
- router/top-k/model math unchanged;
- one `preadv` path per expert miss replaces the previous three source-GGUF reads.

Acceptance:
- matched fresh decode >= `5.0 tok/s`: PASS (`6.903 tok/s` final confirmation; `7.359` validated candidate median);
- ~1,155-token cold TTFT <= `184 s`: PASS (`162.726 s` final confirmation; `156.949 s` validated candidate);
- frozen `0/6`, `0/6`, `8/8`: PASS;
- deterministic source-vs-sidecar equivalence: PASS;
- API/WebUI/Pi+WP2/cache/loopback: PASS;
- FAST rollback and UOPT-001 source rollback: PASS;
- no crash/OOM/corruption and no external-drive runtime dependency.

### UOPT-003 — GO / LOCAL PROMOTION PENDING PERSISTENCE

Result:
`research/integration/loom-unlocked-speed-optimization-003-result.md`

S40 is the validated resident-expert frontier winner: hit rate `81.745% -> 89.831%`, misses `90,229 -> 50,260`, and frozen/integration gates passed. S48 failed with Metal GPU timeout; the frequency-aware cache experiment was not promoted. Evidence is local at `results-local/unlocked-speed-uopt-003/20260901T130729Z/`.

### UOPT-004 — NO_GO

Result: `research/integration/loom-unlocked-speed-optimization-004-result.md`.

Expert-only `Q2_K` from BF16 reduced expert footprint `23.636%` and passed frozen gates, but failed functional quality (`3/4`) and arithmetic (`414` vs expected `410`). Temporary artifacts were removed; production S40 is unchanged.

### UOPT-005 — COMPLETE / NO_GO

Result: `research/integration/loom-unlocked-speed-optimization-005-result.md`.

BF16 source verification (`13/13`), HF→BF16 GGUF validation, imatrix construction, and Candidate A expert `IQ3_XXS` construction completed. external archive sidecar placement was the initial smoke bottleneck: storage isolation changed decode `0.69 -> 9.63 tok/s`, prefill `0.24 -> 6.31 tok/s`, and TTFT `148.277 -> 5.605 s`. Candidate A passed frozen refusal `0/6`, degeneration `0/6`, and benign `8/8`, but failed functional (`3/4`) and arithmetic (`400` vs required `410`). B.1 Q3 `40–47` returned `400`; B.2 Q3 `36–47` and B.3 Q3 `32–47` returned `414`. The layer frontier identified 37 and 39 as causal (36/38 noncausal); 11 losslessly validated tensor splices exhausted causal set `{up37, down37, down39}` (nonempty subsets `414`, empty `400`) without reaching `410`. Expert-by-expert selection was not pursued because it needs a new format/runtime (estimated 1–3 days) with unproven benefit. UOPT-005 is closed NO_GO; production S40 is unchanged.

## 4. Current roadmap state

UOPT-005 is closed NO_GO. Do not alter the promoted UOPT-003 S40 production profile.
