# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — accelerated macro-work-package mode. Current work is `LOOM_RUNTIME_PRODUCTIZATION_WP1`. Later packages are Context Intelligence (Caveman + Cavemem only), Behavioral Transform, and Final Acceptance.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.80.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
Current WP1 contract: `research/integration/loom-runtime-productization-wp1.md`.

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

Pinned source inspection established internal hit/miss counters and the `pread_pool(...)` read path. Minimal isolated source-level measurement is authorized inside WP1.

## Current — WP1 Runtime + Product Serving

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Authoritative contract:
`research/integration/loom-runtime-productization-wp1.md`

Pi works autonomously across internal substeps and returns only when WP1 is complete or a genuine user-action blocker exists.

WP1 deliverables:
1. best validated practical 30B runtime;
2. bounded source-level paging/decode attribution and evidence-backed acceleration attempts handled internally;
3. target >=5 tok/s decode first, with canonical S24 preserved as rollback;
4. persistent localhost serving/API, preferably OpenAI-compatible;
5. validated serving-path prompt/prefix caching where directly supported and verified;
6. **existing** privacy-respecting local WebUI — prefer native `llama-server` WebUI; no custom LOOM frontend from scratch;
7. fallback WebUI only if existing/open-source/local and verified to require no conversation/model-data egress or mandatory telemetry in selected configuration;
8. Pi configured and tested against the same final local model path;
9. operational health/start/stop/logging/tracing;
10. final decode/prefill/E2E/RAM/swap evidence.

Runtime micro-optimization stopping rule:
after three materially different evidence-backed interventions fail to beat the best validated runtime, stop optimization and finish serving/integration. A final result below 5 tok/s does not invalidate WP1 if this stopping rule is legitimately exhausted and the product stack is complete.

Do not return after routine internal NO_GO results; record/revert and continue.

## Approved later macro packages

### WP2 — Context Intelligence
Checkpoint: `LOOM_CONTEXT_INTELLIGENCE_WP2`.

Permanent mechanisms only:
- Caveman — deterministic context compression/packing/recovery handles;
- Cavemem — progressive local project memory and relevant retrieval.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems. Borrow only small ideas if required to support Caveman/Cavemem with negligible overhead.

### WP3 — Behavioral Transform
Checkpoint: `LOOM_BEHAVIORAL_TRANSFORM_WP3`.

Technical priority:
1. Abliterix-derived MoE-aware method adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent when upstream stacks are incompatible.

Criterion: best technically valid route for canonical GGUF/llama.cpp/Apple Silicon. Prefer a small runtime-loadable adapter when technically valid. Prompt-only behavior does not count.

### WP4 — Final Integration + Acceptance
Checkpoint: `LOOM_FINAL_ACCEPTANCE_WP4`.

Assemble best validated outputs from WP1–WP3 and perform final end-to-end acceptance with exact hashes, provenance, resource evidence and operational documentation.

Pi must not commit/push. ChatGPT persists canonical Git state at macro-work-package boundaries.
