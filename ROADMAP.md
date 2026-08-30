# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 GO/persisted. WP2 GO/persisted. WP3 original GGUF-LoRA families valid NO_GO. WP3-R2 Behavioral Unlock GO/persisted. **WP4 Final Integration + Acceptance completed locally with GO; final bounded persistence is pending.**
Canonical context: `/AGENTS.md` v3.90.
WP4 contract: `research/integration/loom-final-acceptance-wp4.md`.

## 1. Final product profiles

### FAST / default
- label `loom-deep-30b-s32`;
- stable model `models/loom-deep-30b-fast.gguf`;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- final WP4 decode `6.209 tok/s`;
- WP2 enabled by default.

### UNLOCKED
- label `loom-deep-30b-unlocked`;
- stable model `models/loom-deep-30b-unlocked.gguf`;
- SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- final frozen refusal `0/6`;
- benign capability `8/8`;
- final WP4 decode `2.963 tok/s`;
- slower and more swap-constrained; disposition drift remains documented.

FAST remains default. Only one 30B profile is resident at a time.

## 2. Final operator interface

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable normal endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

## 3. Completed work

### WP1 — Runtime + Product Serving — GO / PERSISTED
S32 serving, API/WebUI/Pi/cache/lifecycle validated.

### WP2 — Context Intelligence — GO / PERSISTED
Caveman deterministic context packing/recovery + Cavemem SQLite/FTS5 memory; `23.24%` median heavy-context input reduction, `0%` no-op overhead, exact recovery `6/6`.

### WP3 — Behavioral Transform — VALID NO_GO
Rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA routes were served but retained refusal `6/6`. Those methods remain rejected.

### WP3-R2 — Behavioral Unlock — GO / PERSISTED
Persistence commit `1252fcfad73878981a1aa1844a484949a12d5ff4`. Huihui exact-lineage Q3_K_S replacement achieved refusal `0/6` with benign `8/8`.

### WP4 — Final Integration + Acceptance — COMPLETE LOCALLY / GO

Classification:
`LOOM_FINAL_ACCEPTANCE_WP4_GO`.

Evidence:
`results-local/final-acceptance-wp4/20260830T182958Z/`.

Passed:
- stable hard-linked local artifacts and exact hashes;
- FAST -> UNLOCKED -> FAST switching twice;
- loopback-only serving;
- API/WebUI/Pi + WP2 for both;
- Context Intelligence rollback;
- prompt/KV reuse for both;
- unchanged frozen UNLOCKED reproduction;
- final rollback to FAST + WP2.

Final performance snapshot:
- FAST decode `6.209 tok/s`, prefill `3.438 tok/s`, E2E `7.131 s`, RSS about `4.01 GiB`, swap up to `1308 MiB`;
- UNLOCKED decode `2.963 tok/s`, prefill `1.673 tok/s`, E2E `9.129 s`, RSS about `4.16 GiB`, swap up to `1708 MiB`.

## 4. Final persistence action

Persist only the reviewed WP4 product/config/result/docs, optionally plus the reviewed original WP3 NO_GO result for archival completeness.

Exclude all GGUF/model artifacts, `.loom/`, `results-local/`, home Pi config, caches/secrets and unrelated historical scripts.

After final commit review, classify LOOM as FINAL / GO / FULLY PERSISTED.
