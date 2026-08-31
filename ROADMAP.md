# LOOM Roadmap

Last updated: 2026-08-31
Current: LOOM final product GO/fully persisted; UOPT-001 PARTIAL_GO/persisted; **UOPT-002 GO/persisted and promoted**.
Canonical context: `/AGENTS.md` v3.94.
Latest optimization commit: `07223f99e75a44f559270af976ab2d8b52b5edb4`.

## 1. Current product profiles

### FAST / default
- label `loom-deep-30b-s32`;
- stable model `models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- historical matched decode `5.596 tok/s`;
- WP4 operational snapshot `6.209 tok/s`;
- FAST `-ub 1`;
- WP2 enabled by default.

### UNLOCKED / UOPT-002
- label `loom-deep-30b-unlocked`;
- source/rollback GGUF `models/loom-deep-30b-unlocked.gguf`;
- source SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- lossless expert-major sidecar `models/unlocked-expert-major-v1.bin`;
- sidecar SHA256 `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`;
- isolated patched runtime `.loom/runtime/loom-uopt002/llama-server`;
- runtime SHA256 `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`;
- UNLOCKED `-ub 4`;
- frozen refusal `0/6`, held-out degeneration `0/6`, benign `8/8`;
- final promoted matched decode `6.903 tok/s` (validated candidate median `7.359`);
- final 1,155-token cold TTFT `162.726 s` (validated candidate `156.949 s`).

FAST remains default. Only one 30B profile is resident at a time.

## 2. Operator interface

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable normal endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

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

## 4. Current roadmap state

The UOPT speed branch is complete. There is no active optimization macro.

Any future work should be opened as a new explicit package. Possible future directions, only if separately authorized, include further cold-TTFT reduction below the UOPT-002 ~157–163 s range, packaging/rebuild automation hardening, or later archival of FAST if rollback policy is intentionally changed.
