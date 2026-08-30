# LOOM Roadmap

Last updated: 2026-08-30
Current: accelerated macro-work-package mode. Prompt Cache R2 is validated GO. Current work package is `LOOM_RUNTIME_PRODUCTIZATION_WP1`; later packages cover agent capability, Heretic/behavioral transform, and final integration.
Canonical context: `/AGENTS.md` v3.79.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

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

Pinned source inspection confirms internal LRU hit/miss counters and the `pread_pool(...)` expert-read path. Minimal isolated source-level instrumentation is therefore allowed inside WP1 without another user-facing checkpoint.

## 5. WP1 — Runtime + Product Serving

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Deliver in one Pi macro task:
- fastest reliable validated 30B runtime practical on the host;
- bounded source-level paging/decode attribution and acceleration;
- target >=5 tok/s first;
- retain S24 rollback baseline;
- persistent localhost serving/API, preferably OpenAI-compatible;
- validated prompt cache in the serving path where applicable;
- usable browser chat;
- Pi connected/tested against local LOOM;
- lightweight operational tracing/health/logs;
- simple start/stop workflow;
- final decode/prefill/E2E/RAM/swap evidence.

Do not stop for individual internal NO_GO results. Record/revert and continue.

Runtime stopping rule:
after three materially different evidence-backed decode interventions fail to beat the best validated runtime, stop micro-optimization and finish product serving.

## 6. WP2 — Agent Capability Layer

Checkpoint:
`LOOM_AGENT_CAPABILITY_WP2`

Integrate selectively and measure net benefit:
- Caveman deterministic typed compression/context packing/recovery handles;
- LoopX durable state/re-entry;
- Cavemem progressive local memory;
- Observal lightweight local trace/accounting/replay concepts;
- pi-dynamic-workflows bounded optional workflows/resume.

Prefer small LOOM-native implementations over wholesale upstream installs.

## 7. WP3 — Behavioral Transform / Heretic

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Separate macro task because canonical DEEP is GGUF while upstream Heretic is Transformers/PEFT-oriented.

Goal:
actual model/adapter-level behavioral transform with provenance, behavior evidence, capability preservation and runtime-loadable artifact.

Preferred routes:
1. compatible Heretic representation + exportable low-rank artifact;
2. valid llama.cpp-compatible adapter/export route;
3. clean LOOM-native contrastive residual-direction low-rank equivalent.

Prompt-only behavior does not count as WP3 completion.

## 8. WP4 — Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble best validated outputs from WP1–WP3.

Required:
- reliable clean startup;
- API/web/Pi all operational;
- selected runtime acceleration active;
- prompt cache active where applicable;
- agent capability layer enabled only where net-positive;
- behavioral-transform profile loaded/validated or exact physical/toolchain blocker documented;
- representative capability smoke tests;
- final performance/memory evidence;
- exact hashes/provenance;
- concise operational documentation.

## 9. Research sources

Use mechanisms selectively from:
- mini-SGLang — KV/prefix reuse, chunked prefill, scheduling/prefetch/overlap;
- Caveman — context compression/packing;
- Cavemem — progressive memory;
- LoopX — durable state;
- pi-dynamic-workflows — bounded orchestration;
- Observal — measurement/replay;
- Heretic — contrastive residual-direction low-rank editing.

These are research/engineering inputs, not mandatory dependencies.
