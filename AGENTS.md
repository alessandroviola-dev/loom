# LOOM — Pi Agent Protocol

Version: 3.80
Mode: `ACCELERATED_MACRO_WORKPACKAGES / EVIDENCE_GATED`

Pi reads this file as persistent context. User-facing micro-checkpoints are retired for the current push.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, durable `results-local/` evidence, autonomous continuation through internal gates inside the active macro work package.

ChatGPT: scientific direction, macro-package definition/review, canonical Git/GitHub persistence.

GitHub is canonical. Active clone:
`<repository-root>`.

Pi must not commit/push/PR.

## Operating rule

Do not return after routine internal GO/NO_GO results.

Inside the active macro work package:
- record failed experiments;
- revert regressions;
- continue to the next justified action;
- preserve frozen scientific gates;
- keep one known-good runnable baseline.

Return only when:
1. the macro work package deliverable is substantially complete; or
2. a genuine blocker requires user action, credentials, destructive/security-sensitive host changes, unavailable hardware/storage, or a project-direction choice not resolvable from existing goals/evidence.

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
10. Pi does not commit/push.

## Canonical DEEP starting point

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Validated frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile: S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

Validated prompt-cache result:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix result:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`.

Prompt/prefix caching is accepted for stable-prefix prefill/E2E optimization.

## Macro work-package plan

Authoritative plan:
`research/integration/loom-accelerated-macro-workpackages-v1.md`

### WP1 — Runtime + Product Serving

Current checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Authoritative contract:
`research/integration/loom-runtime-productization-wp1.md`

Deliver:
- best validated practical 30B runtime;
- persistent localhost serving/API, preferably OpenAI-compatible;
- an existing privacy-respecting local WebUI;
- Pi connected/tested against local LOOM;
- prompt/prefix cache in the serving path only where directly verified;
- operational trace/health/start/stop;
- decode/prefill/E2E/RAM/swap evidence.

Runtime acceleration is internal to WP1. Source-level instrumentation/builds and evidence-backed runtime patches are authorized in isolated variants.

Target >=5 tok/s decode first. After three materially different evidence-backed decode interventions fail to beat the best validated runtime, stop micro-optimization and finish serving/integration.

**Web UI rule:** do not build a custom LOOM web interface from scratch. Prefer the existing `llama-server` WebUI if compatible. Otherwise use an existing open-source local UI only after verifying no required cloud inference/conversation-data egress and no mandatory telemetry for the selected configuration.

WP1 does not implement Caveman/Cavemem or behavioral editing.

### WP2 — Context Intelligence

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Primary permanent mechanisms only:
- Caveman for deterministic compression/context packing/recovery handles;
- Cavemem for progressive local project memory/retrieval.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems. Small implementation ideas from them may be borrowed only when required to support Caveman/Cavemem with negligible overhead.

### WP3 — Behavioral Transform

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Search priority:
1. Abliterix-derived MoE-aware methodology adapted to LOOM;
2. Heretic;
3. Senbonzakura-style multi-direction methods;
4. clean LOOM-native equivalent when upstream tooling is incompatible.

Select by technical fit to canonical GGUF/llama.cpp/Apple Silicon, not popularity. Prefer a small reversible/runtime-loadable adapter when technically valid. Prompt-only behavior does not satisfy WP3.

### WP4 — Final Integration + Acceptance

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Assemble best validated outputs of WP1–WP3 and run final end-to-end acceptance.

## Repository research inputs

Current priority engineering sources:
- mini-SGLang: prefix/KV reuse and scheduling/prefetch/overlap concepts for WP1;
- Caveman + Cavemem for WP2;
- Abliterix/Heretic/Senbonzakura concepts for WP3.

Other papers remain research references, not current permanent integration requirements.

## Current WP1 internal context

External paging tracing preflight was valid `NO_GO`: available unprivileged native tracing did not expose validated per-process read observables. This does not refute paging as a bottleneck.

Pinned source already shows internal hit/miss counters and `pread_pool(...)`. WP1 may therefore implement minimal isolated source-level measurement, calibrate overhead, attribute decode cost, and test evidence-backed acceleration patches without pausing for each sub-result.

## WP1 final return required

Return one bounded report only at WP1 completion/blocker, including:
- WP1 classification;
- final runtime architecture;
- start/stop/health commands;
- browser URL and selected existing WebUI;
- privacy/local-only verification for that UI;
- API endpoint/model id;
- Pi configuration/test result;
- selected source/binary/model hashes;
- final runtime flags;
- decode/prefill/E2E/RAM/swap;
- serving-path prompt/prefix-cache state;
- tracing/health state;
- changed files/configs;
- evidence roots;
- notable failed/reverted runtime candidates;
- remaining genuine blocker, if any.
