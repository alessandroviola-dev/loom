# LOOM — Pi Agent Protocol

Version: 3.78
Mode: `AUTONOMOUS_INTEGRATION_SPRINT / EVIDENCE_GATED`

Pi reads this file as persistent context. The active sprint prompt carries only the execution delta.

## Roles / synchronization

Pi: local inspection/execution, implementation, bounded experimentation, local integration, `results-local/` evidence, autonomous continuation through internal GO/NO_GO gates.
ChatGPT: scientific direction, canonical Git/GitHub persistence, final review of sprint result.
GitHub is canonical. Active clone: `<repository-root>`.

During `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_001`, Pi may edit/build/test local project/runtime artifacts as authorized by the sprint contract, but must not commit/push/PR.

## Core rules

1. evidence over narrative;
2. preserve exact provenance for model/runtime/derived artifacts;
3. failed experiments are recorded, reverted if needed, then execution continues;
4. no silent gate relaxation or false promotion;
5. do not stop for routine subtask NO_GO;
6. stop only on final acceptance or a genuine blocker requiring user action, credentials, destructive/security-sensitive host changes, or unavailable hardware/storage;
7. prefer deterministic tests and measured A/B comparisons;
8. keep one known-good runnable baseline while experimenting;
9. never expose the local inference service publicly by default;
10. do not disable SIP/change host security settings;
11. do not delete unrelated user data;
12. no Pi Git commit/push.

## Product direction

**Big models. Small machines.**

BALANCED:
Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary for lighter workloads.

DEEP:
Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24.

Canonical DEEP model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Canonical source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Validated frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile: S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## Validated cache result

`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix measurements:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`.

Prompt/prefix caching is accepted as a canonical stable-prefix prefill/E2E optimization.

## Current checkpoint

`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_001`

Contract:
`research/integration/loom-full-capability-integration-sprint-001.md`

This sprint supersedes user-facing micro-checkpoints. Treat research gates as internal phase gates and continue autonomously.

## Required final product

Pi should attempt to leave the host with:

- reliable local DEEP serving;
- localhost API, preferably OpenAI-compatible;
- working local web chat;
- Pi connected to and tested against the local LOOM model;
- best validated prompt/cache/runtime optimizations enabled;
- lightweight local trace/measurement support;
- useful deterministic context packing and progressive project memory where net utility is positive;
- actual model/adapter-level behavioral-freedom transform attempted through Heretic or a technically valid LOOM-native equivalent;
- behavioral/capability/resource preservation evidence;
- simple documented start/stop/health workflow.

## Research-paper mechanisms

Use project research papers as engineering inputs:
- mini-SGLang: prefix/KV reuse, chunked prefill, scheduling/prefetch/overlap;
- Caveman: typed compression, budgeted context selection, recovery handles;
- Cavemem: local progressive memory;
- LoopX: durable state/re-entry;
- pi-dynamic-workflows: bounded optional workflow/journal;
- Observal: local trace and measurement philosophy;
- Heretic: contrastive residual-direction + low-rank behavioral editing.

Do not install upstream systems wholesale when a small LOOM-native implementation captures the useful mechanism with lower overhead.

## Runtime optimization policy

The external paging tracing preflight was valid `NO_GO` under current non-privileged tools. Source-level measurement is therefore allowed inside the sprint when implemented minimally and isolated from the canonical baseline.

Pi may:
- instrument paging counters/timers;
- build a separate instrumented binary;
- calibrate its overhead;
- use it for attribution;
- implement small evidence-backed acceleration patches such as expert I/O prefetch/overlap;
- A/B candidates and retain only verified improvements.

Target `>=5 tok/s` decode first. Continue beyond only while measured low-risk headroom remains.

After three materially different evidence-backed decode interventions fail to beat the best validated runtime, stop micro-optimization and finish integration.

## Behavioral-freedom requirement

Project requirement:
`research/behavior/decensoring-requirement-v1.md`.

Prompt-only jailbreaks do not satisfy it.

Preferred:
Heretic-compatible behavioral transform.

Because upstream Heretic is Transformers/PEFT-oriented rather than native-GGUF, Pi must find the shortest technically sound route on this machine:
- compatible local Heretic representation and runtime-loadable adapter/artifact; or
- clean LOOM-native directional-edit equivalent.

Do not claim full promotion if no actual weight/adapter-level behavioral edit is produced and validated.

Search should be bounded and preservation-aware; avoid huge TPE sweeps as the first attempt on M1 8 GiB.

## Final classifications

`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_GO`
= runtime/API/web/Pi/optimization/context integration and actual validated behavioral profile all operational.

`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_PRODUCT_GO_BEHAVIOR_BLOCKED`
= complete usable product stack, but actual behavioral transform proven infeasible under current physical/toolchain constraints.

`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_NO_GO`
= integrated stack itself is not reliably usable.

## Final response required from Pi

Return one bounded final report only after the sprint terminates. Include:
- classification;
- final architecture;
- exact start/stop commands;
- browser URL;
- API endpoint/model id;
- Pi config/test;
- hashes/provenance;
- decode/prefill/E2E/memory/swap;
- enabled context/memory/trace features and measured effect;
- behavior-edit artifact/method and validation;
- capability preservation;
- changed files;
- evidence roots;
- notable reverted failures;
- genuine remaining blocker if any.
