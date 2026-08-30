# LOOM Roadmap

Last updated: 2026-08-30
Current: WP1 GO/persisted. WP2 GO/persisted. WP3 original GGUF-LoRA families valid NO_GO. WP3-R2 Behavioral Unlock GO/persisted. **WP4 Final Integration + Acceptance is active**.
Canonical context: `/AGENTS.md` v3.89.
WP4 contract: `research/integration/loom-final-acceptance-wp4.md`.

## 1. Final product profiles

### FAST / default
- label `loom-deep-30b-s32`;
- Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw;
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- S32 validated median decode `5.596 tok/s`;
- persistent local llama-server + WP2.

### UNLOCKED
- label `loom-deep-30b-unlocked`;
- `Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`;
- SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- WP3-R2 explicit refusal `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- stable API/WebUI + real Pi/WP2;
- slower and higher-swap than FAST; disposition drift remains documented.

Both profiles are intentionally retained. FAST remains default.

## 2. Completed work

### WP1 — Runtime + Product Serving — GO / PERSISTED
S32 server, WebUI/API/Pi/cache/lifecycle validated.

### WP2 — Context Intelligence — GO / PERSISTED
Caveman deterministic context packing/recovery + Cavemem SQLite/FTS5 progressive project memory. Heavy-context provider-input reduction `23.24%` median, no-op overhead `0%`, exact recovery `6/6`.

### WP3 — Behavioral Transform — VALID NO_GO
Rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were served but retained frozen refusal `6/6`. Those methods remain rejected.

### WP3-R2 — Behavioral Unlock — GO / PERSISTED
Persistence commit `1252fcfad73878981a1aa1844a484949a12d5ff4`. Exact-lineage Huihui abliterated Q3_K_S replacement achieved frozen refusal `0/6` with benign `8/8`.

## 3. WP4 — FINAL INTEGRATION + ACCEPTANCE — ACTIVE

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Goal: convert the validated research stack into a stable practical two-profile LOOM product.

Required:
- stable local model artifact names under ignored `models/`, without unnecessary duplication;
- one 30B resident at a time;
- simple FAST/UNLOCKED profile manager;
- stable loopback serving endpoint where practical;
- FAST -> UNLOCKED -> FAST switching and rollback;
- API/WebUI/Pi + WP2 for both;
- unchanged frozen UNLOCKED behavior/capability recheck;
- FAST performance health;
- UNLOCKED performance/RAM/swap/memory-pressure evidence;
- prompt/KV cache compatibility;
- Context Intelligence disable rollback;
- exact hashes/provenance;
- `docs/LOOM_OPERATIONS.md`;
- `research/integration/loom-final-acceptance-wp4-result.md`.

WP4 should leave FAST + WP2 as the documented default final state unless the final evidence supports a safer stopped state.

Pi must not commit/push during execution. Final bounded persistence follows review.
