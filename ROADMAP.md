# LOOM Roadmap

Last updated: 2026-08-30
Current: accelerated macro-work-package mode. Prompt Cache R2 is validated GO. Current work package is `LOOM_RUNTIME_PRODUCTIZATION_WP1`; later packages are Context Intelligence (Caveman + Cavemem only), Behavioral Transform, and Final Integration.
Canonical context: `/AGENTS.md` v3.80.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
WP1 contract: `research/integration/loom-runtime-productization-wp1.md`.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional lighter tier.
- `loom-deep`: Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24.
- historical custom MLX ~1.4 tok/s: historical comparison/fallback only.
- `loom-fast`: later clean-runtime tier.

Goal of current push: a practical local LOOM stack on the M1 8 GiB host, not a sequence of isolated research checkpoints.

## 2. Canonical DEEP baseline

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Profile S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## 3. Validated prompt cache

`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix result:
- median prompt-eval C/B `0.04025`;
- median E2E C/B `0.10751`;
- decode preservation `99.43%`.

Prompt cache is accepted for reusable stable-prefix prefill/E2E acceleration.

## 4. Paging/I/O observation context

External non-mutating tracing preflight completed valid `NO_GO`: current unprivileged tools did not expose a validated high-value per-process read observable.

Pinned source inspection confirms internal LRU hit/miss counters and the `pread_pool(...)` expert-read path. Minimal isolated source-level instrumentation is allowed inside WP1 without another user-facing checkpoint.

## 5. WP1 — Runtime + Product Serving

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Authoritative contract:
`research/integration/loom-runtime-productization-wp1.md`

Deliver in one Pi macro task:
- fastest reliable validated 30B runtime practical on the host;
- bounded source-level paging/decode attribution and acceleration;
- target >=5 tok/s first;
- retain S24 rollback baseline;
- persistent localhost serving/API, preferably OpenAI-compatible;
- directly verified serving-path prompt/prefix caching where applicable;
- **existing** privacy-respecting browser UI only;
- prefer native `llama-server` WebUI;
- do not build a custom LOOM frontend from scratch;
- if native UI is unsuitable, select an existing open-source local UI only after verifying no required cloud inference/conversation-data egress and no mandatory telemetry in the selected configuration;
- Pi connected/tested against local LOOM;
- lightweight operational tracing/health/logs;
- simple start/stop workflow;
- final decode/prefill/E2E/RAM/swap evidence.

Do not stop for individual internal NO_GO results. Record/revert and continue.

Runtime stopping rule:
after three materially different evidence-backed decode interventions fail to beat the best validated runtime, stop micro-optimization and finish product serving. Reaching >=5 tok/s is a target, not a condition for productization GO if the stopping rule is legitimately exhausted.

## 6. WP2 — Context Intelligence

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Permanent mechanisms selected for implementation:
- **Caveman** — deterministic typed compression, context packing, token-budget selection and recovery handles;
- **Cavemem** — progressive local project memory, compact searchable observations and exact retrieval on demand.

Cavemem selects relevant prior information; Caveman decides what enters the active prompt and how compactly.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems. Borrow only small implementation ideas if necessary for Caveman/Cavemem with negligible overhead.

WP2 requires measured net token/task benefit.

## 7. WP3 — Behavioral Transform

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Goal:
actual model/adapter-level behavioral transform with provenance, behavior evidence, capability preservation and runtime-loadable artifact.

Search/implementation priority:
1. Abliterix-derived MoE-aware methodology adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent when upstream implementations are incompatible with the actual host/runtime.

Select by technical fit to canonical GGUF/llama.cpp/Apple Silicon, not project popularity. Prefer a small reversible/runtime-loadable adapter over a second full model copy when technically valid.

Prompt-only behavior does not count as WP3 completion.

## 8. WP4 — Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble best validated outputs from WP1–WP3.

Required:
- reliable clean startup;
- API/web/Pi all operational;
- selected runtime acceleration active;
- serving-path prompt/prefix cache active where directly verified;
- Caveman + Cavemem enabled only in validated net-positive form;
- behavioral-transform profile loaded/validated or exact physical/toolchain blocker documented;
- representative capability smoke tests;
- final performance/memory evidence;
- exact hashes/provenance;
- concise operational documentation.

## 9. Current research inputs

Use mechanisms selectively from:
- mini-SGLang — KV/prefix reuse and scheduling/prefetch/overlap for WP1;
- Caveman + Cavemem for WP2;
- Abliterix/Heretic/Senbonzakura concepts for WP3.

Other repository papers remain available research references but are not current permanent integration requirements.
