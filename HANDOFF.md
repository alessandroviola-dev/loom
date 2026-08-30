# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — accelerated macro-work-package mode. WP1 Runtime + Product Serving completed GO. Canonical DEEP runtime is S32 at 5.596 tok/s median decode on persistent localhost `llama-server`; S24 is rollback. WP2 Context Intelligence is now authorized and active, limited to Caveman-derived context packing/compression and Cavemem-derived progressive local project memory.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.82.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
Current WP2 contract: `research/integration/loom-context-intelligence-wp2.md`.

## Canonical DEEP after WP1

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical server binary:
`llama-server`
SHA256 `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Canonical runtime profile: **S32**.
Rollback: S24.

Matched deterministic S24/S32 3x96-token A/B with byte-identical outputs:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode `5.596 tok/s`, E2E `23.849 s`;
- decode ratio `1.2768x`;
- E2E ratio `0.8172`.

S32 resources:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- minimum sampled free memory `10%`;
- no crash/OOM/corruption/critical pressure indication.

Final flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

## WP1 — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Canonical result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Operational commands:
```bash
scripts/loom-deep-server start
scripts/loom-deep-server status
scripts/loom-deep-server health
scripts/loom-deep-server stop
```

WebUI:
`http://127.0.0.1:18080/`

API:
`http://127.0.0.1:18080/v1/chat/completions`

Health:
`http://127.0.0.1:18080/health`

Selected UI is the existing embedded `llama-server` WebUI. No custom LOOM frontend was built. Final server is offline/local-only and loopback-bound.

Serving-path prompt/KV reuse is directly validated with `--cache-ram 512`:
- cold: 136 prompt tokens, 27.809 s;
- reuse: 134 cached / 2 evaluated tokens, 280.389 ms;
- reuse E2E: 0.332 s.

Pi local integration is operational through `http://127.0.0.1:18080/v1`; final offline Pi request completed coherently.

Current provider/model label `loom-local/loom-deep-30b-s24` is stale naming only. WP2 may safely rename it to `loom-local/loom-deep-30b-s32` after preserving config backup/compatibility or retain an alias if required.

## Current — WP2 Context Intelligence

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Status: **AUTHORIZED / ACTIVE**.

Authoritative contract:
`research/integration/loom-context-intelligence-wp2.md`

User-approved permanent mechanisms only:

### Caveman-derived layer
- deterministic local context scoring/selection under a token budget;
- typed compression for logs/search/JSON/code/diffs where net-positive;
- exact preservation of machine-critical values;
- errors/warnings prioritized;
- relevance determines membership, chronology determines final presentation order;
- omitted evidence remains exactly recoverable through stable local handles;
- small/already concise inputs bypass compression when overhead would exceed savings.

### Cavemem-derived layer
- project-scoped local memory outside the prompt;
- SQLite/FTS5/BM25-first compact observations;
- progressive disclosure: cheap compact candidates first, exact source/body only on demand;
- persist decisions, results, failed approaches, constraints and checkpoints rather than every transcript turn;
- source/evidence provenance retained;
- privacy/redaction before durable writes;
- no mandatory embeddings in v0.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## WP2 benchmark / promotion

Final frozen comparison arms:
- A: current WP1 baseline;
- B: Caveman only;
- C: Caveman + Cavemem.

Benchmark must contain both context-heavy real LOOM/Pi workload classes and small/no-op negative cases.

GO requires all contract gates, including:
- objective task quality non-inferior to baseline;
- exact recovery/provenance;
- safe privacy/project-memory behavior;
- target >=20% median provider-input reduction on context-heavy cases;
- target <=5% provider-input overhead on small/no-op cases with no correctness regression;
- host packing/retrieval overhead small relative to saved prefill/E2E;
- safe RAM/swap with S32;
- no accepted wrong answer caused by stale/incorrect memory;
- one real Pi task through combined WP2 path;
- easy disable/rollback to WP1 baseline.

Pi must continue autonomously through internal compressor/retrieval NO_GO outcomes: record/revert or disable net-negative subfeatures and continue until WP2 completion or a genuine user-action blocker.

## Later

WP3 — Behavioral Transform:
priority Abliterix-derived MoE-aware approach -> Heretic -> Senbonzakura-style methods -> clean LOOM-native equivalent, chosen by technical fit to GGUF/llama.cpp/Apple Silicon.

WP4 — Final Integration + Acceptance:
assemble best validated outputs and perform final end-to-end acceptance.

Pi must not begin WP3 or commit/push. ChatGPT persists canonical Git state at macro-work-package boundaries.
