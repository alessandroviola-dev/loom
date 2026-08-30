# LOOM — Pi Agent Protocol

Version: 3.90
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired for the current push.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside an authorized macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Default rule: Pi must not commit/push/PR.

Narrow exception: at a completed macro-work-package boundary, ChatGPT may explicitly authorize one bounded persistence commit/push containing only reviewed package implementation/result/docs. Never include `.loom/`, `results-local/`, personal/home-directory config, secrets, caches, model artifacts, generated databases, or unrelated working-tree changes.

## Core rules

1. evidence over narrative;
2. exact provenance for model/runtime/derived artifacts;
3. no silent gate relaxation or false promotion;
4. deterministic tests before expensive runs where practical;
5. bounded A/B comparisons for performance claims;
6. no public internet exposure by default;
7. do not disable SIP/change host security settings;
8. do not delete unrelated user data;
9. project-local dependencies/environments are allowed when required and recorded;
10. Pi Git persistence only under the explicit bounded exception above.

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

FAST model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Pinned source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Pinned `llama-server` SHA256:
`58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`

Runtime: S32. Historical validated median decode `5.596 tok/s`.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`.

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`.

Canonical layer:
- Caveman-derived deterministic host-side packing/compression/recovery;
- Cavemem-derived SQLite/FTS5 project memory;
- Pi `before_provider_request` integration for `loom-local`;
- heavy-context provider-input reduction `23.24%` median;
- no-op overhead `0%`;
- exact recovery `6/6`, SHA-verified.

Rollback:
`LOOM_CONTEXT_INTELLIGENCE=0`.

## WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were built and served but retained the original frozen held-out refusal result at `6/6`. Those three bounded methods remain rejected.

The still-local historical result `research/integration/loom-behavioral-transform-wp3-result.md` may be included in the final bounded WP4 persistence package; do not sweep unrelated historical scripts.

## WP3-R2 — Behavioral Unlock — COMPLETE / GO / PERSISTED

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Persistence commit:
`1252fcfad73878981a1aa1844a484949a12d5ff4`.

UNLOCKED model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Validated R2 outcome:
- frozen explicit refusals `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- no increased frozen degeneration;
- API/WebUI and real Pi + WP2 passed;
- rollback to FAST + WP2 passed.

## WP4 — Final Integration + Acceptance — COMPLETE LOCALLY / GO — PERSISTENCE PENDING

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Classification:
`LOOM_FINAL_ACCEPTANCE_WP4_GO`.

Contract:
`research/integration/loom-final-acceptance-wp4.md`

Local result:
`research/integration/loom-final-acceptance-wp4-result.md`

Evidence:
`results-local/final-acceptance-wp4/20260830T182958Z/`

### Final operator UX

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Normal serving endpoint for both profiles:
- WebUI `http://127.0.0.1:18080/`;
- API `http://127.0.0.1:18080/v1`.

FAST remains default. Only one 30B profile is resident at a time.

### Stable local artifacts

Ignored local model paths:
- `models/loom-deep-30b-fast.gguf` -> SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- `models/loom-deep-30b-unlocked.gguf` -> SHA256 `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`.

Pinned local runtime link:
- `.loom/runtime/loom-llama-server` -> SHA256 `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Model aliases were created by verified hard-link without redownload/copy. Models and `.loom/` remain excluded from Git.

### Final acceptance

Passed:
- FAST -> UNLOCKED -> FAST switching twice;
- old profile PID stopped before replacement;
- only loopback listener present;
- health, `/v1/models`, API chat and WebUI for both profiles;
- Pi + WP2 for both labels;
- Context Intelligence disable rollback;
- UNLOCKED frozen reproduction: refusal `0/6`, held-out degeneration `0/6`, benign capability `8/8`;
- prompt/KV cache for both: repeated 1,149-token prefix reduced to one evaluated token;
- final rollback to FAST + WP2 with hash/API/health verification.

Final WP4 performance snapshot:
- FAST: decode `6.209 tok/s`, prefill `3.438 tok/s`, E2E `7.131 s`, RSS `4.00->4.01 GiB`, swap `1269->1308 MiB`, free memory `11->10%`;
- UNLOCKED: decode `2.963 tok/s`, prefill `1.673 tok/s`, E2E `9.129 s`, RSS `4.13->4.16 GiB`, swap `1667->1708 MiB`, free memory `8->9%`.

UNLOCKED remains slower and more memory/swap constrained; its disposition drift remains explicit.

Final active state after WP4: FAST + WP2 on `127.0.0.1:18080`.

### Current exact action

Persist one bounded final WP4 package under the macro-boundary exception.

Include only reviewed final product/config/result/docs and, if useful for historical completeness, the original WP3 NO_GO result file.

Expected WP4 product files:
- `config/loom-deep-profiles.env`;
- `config/loom-deep-server.env`;
- `config/loom-deep-r2-abliterated-q3ks.env`;
- `scripts/loom-deep`;
- `scripts/loom_wp4_probe.py`;
- `docs/LOOM_OPERATIONS.md`;
- `research/integration/loom-final-acceptance-wp4-result.md`.

Optional archival inclusion:
- `research/integration/loom-behavioral-transform-wp3-result.md`.

Exclude:
- both GGUFs / `models/`;
- `.loom/`;
- `results-local/`;
- home-directory Pi config;
- caches/secrets;
- unrelated historical untracked scripts.

After persistence, review the exact final commit and classify LOOM final product as fully persisted.
