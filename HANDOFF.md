# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — accelerated macro-work-package mode. User-facing micro-checkpoints are retired. Current work is `LOOM_RUNTIME_PRODUCTIZATION_WP1`; later macro packages cover agent capability, Heretic/behavioral transform, and final acceptance.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.79.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## Canonical starting point

DEEP model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Validated frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile: S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## Validated prompt-cache optimization

`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

Validated stable-prefix measurements:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`.

Prompt cache is canonical for reusable stable-prefix prefill/E2E acceleration.

## Paging/I/O context

External non-mutating tracing preflight:
`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`.

Evidence:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/20260830T111709Z/`

Meaning:
current unprivileged external tracing did not expose validated high-value per-process read measurements. This does not refute paging as a bottleneck.

Pinned source inspection established internal hit/miss counters and the `pread_pool(...)` read path. Minimal isolated source-level measurement is therefore authorized inside WP1.

## Current — WP1 Runtime + Product Serving

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Pi should work autonomously across internal substeps and return only when WP1 is complete or a genuine user-action blocker exists.

WP1 deliverables:
1. best validated practical 30B runtime;
2. persistent localhost serving/API, preferably OpenAI-compatible;
3. usable local browser chat;
4. Pi configured/tested against local LOOM;
5. validated prompt cache enabled where applicable;
6. source-level paging/decode attribution and bounded acceleration attempts handled internally;
7. >=5 tok/s target first, but stop micro-optimization after three materially different evidence-backed failures to beat the best runtime;
8. operational health/start/stop/logging/tracing;
9. final decode/prefill/E2E/RAM/swap evidence;
10. preserve S24 known-good rollback baseline.

Do not return after routine internal NO_GO results; record/revert and continue.

## Next macro packages

WP2 — `LOOM_AGENT_CAPABILITY_WP2`
- Caveman-style deterministic context packing/typed compression;
- LoopX-style durable state/re-entry;
- Cavemem-style progressive local memory;
- Observal-style lightweight local tracing/accounting;
- bounded pi-dynamic-workflows only when net-positive.

WP3 — `LOOM_BEHAVIORAL_TRANSFORM_WP3`
- actual model/adapter-level behavioral transform using Heretic or a technically valid LOOM-native directional low-rank equivalent;
- separate because upstream Heretic is Transformers/PEFT-oriented while canonical DEEP is GGUF;
- prompt-only behavior does not satisfy WP3.

WP4 — `LOOM_FINAL_ACCEPTANCE_WP4`
- assemble best validated outputs;
- final end-to-end acceptance;
- documented start/stop/health;
- exact hashes/provenance/evidence.

## Research inputs

Project papers are engineering sources, not mandatory wholesale dependencies:
- mini-SGLang — inference/cache/scheduling/prefetch concepts;
- Caveman — deterministic context compression/packing;
- Cavemem — progressive local memory;
- LoopX — durable state/re-entry;
- pi-dynamic-workflows — bounded opt-in orchestration;
- Observal — local measurement/replay philosophy;
- Heretic — contrastive residual-direction low-rank editing.

Pi must not commit/push. ChatGPT persists canonical Git state at macro-work-package boundaries.
