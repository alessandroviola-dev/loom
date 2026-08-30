# LOOM Full Capability Integration Sprint 001

Date: 2026-08-30
Status: **AUTHORIZED INTEGRATION SPRINT / NOT YET EXECUTED**

## User-directed change of operating mode

This sprint supersedes the prior sequence of user-facing micro-checkpoints for the remainder of the current push toward a usable LOOM system.

The research rules remain valid, but gates are now **internal execution gates inside one long Pi task**. Pi should continue autonomously after a failed experiment by recording evidence, reverting invalid/regressive changes, and advancing to the next justified action.

Do not stop merely because one sub-experiment is NO_GO.

Stop and return to the user only when:
1. the final acceptance contract is satisfied; or
2. a genuine hard blocker requires credentials, destructive/security-sensitive host changes, unavailable storage/hardware, or a choice that cannot be resolved from the frozen project goals and evidence.

## Primary goal

Produce the strongest practical LOOM local-AI stack achievable on the reference Apple M1 8 GiB machine, with the current 30B MoE DEEP model as the main large-model target, and leave it **usable rather than merely researched**.

Final system goal:

- local model starts reliably;
- callable from Pi as a local model/provider;
- callable through a local OpenAI-compatible HTTP API or equivalent stable API;
- usable through a local web chat UI;
- best validated runtime acceleration enabled;
- stable-prefix/prompt caching enabled where applicable;
- useful context compression and progressive memory mechanisms integrated where they improve measured utility;
- local observability/tracing present;
- behavioral-freedom/decensoring stage attempted as an actual model-behavior transform, with preservation checks;
- startup, shutdown and verification documented and preferably reduced to one or a few commands.

## Canonical starting point

Repository:
`Ilcoach/loom`

Branch:
`research/stretch-015-divergence-attribution`

Reference host:
Apple M1 / 8 GiB unified memory.

Canonical DEEP model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Canonical source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Current canonical execution profile:
S24.

Validated fresh-process decode baseline:
approximately `4.39–4.40 tok/s`.

Validated prompt-cache result:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix cache measured median ratios:
- prompt-eval C/B `0.04025`;
- E2E C/B `0.10751`;
- decode preservation `99.43%`.

## Repository research inputs

Treat the project repository papers as engineering inputs, not as mandatory dependencies to install wholesale.

### mini-SGLang

Use concepts where applicable:
- stable prefix/KV reuse;
- cache ownership/liveness;
- chunked prefill;
- scheduling overlap;
- preparation/prefetch of next-step work.

Prompt-cache reuse is already validated. Investigate additional runtime ideas only when they are implementable on the pinned Apple/Metal path and measurable.

### Caveman

Use concepts where useful:
- deterministic type-aware compression;
- context packing under a token budget;
- relevance + recency + error/priority scoring;
- exact recovery handles;
- preserve chronology after selection.

Do not add permanent prompt overhead that costs more than it saves.

### Cavemem

Use concepts where useful:
- project-scoped local memory;
- compact searchable observations;
- progressive retrieval;
- exact body retrieval only on demand;
- local SQLite/FTS-first design.

### LoopX

Use concepts immediately for the long sprint:
- durable state outside model context;
- current goal/frontier/evidence/blocker ledger;
- compact re-entry packet;
- evidence-backed state transitions.

### pi-dynamic-workflows

Use only if Pi can benefit from bounded decomposition:
- intermediate results outside parent context;
- resume/journal;
- bounded fan-out;
- deterministic verification before model review.

Do not introduce large uncontrolled fan-out.

### Observal

Adopt the measurement philosophy immediately:
- local session/run trace;
- model request/response timing;
- token/cache usage where exposed;
- tool calls and failures;
- context packing accounting;
- benchmark results;
- replay/evidence references.

Prefer lightweight local JSONL/SQLite over deploying the full upstream stack.

### Heretic / LOOM behavioral editing

Behavioral freedom is a final promotion requirement.

Preferred route:
- Heretic-compatible or Heretic-derived contrastive residual-direction editing;
- reversible low-rank transform where possible;
- measure target behavior change and capability/resource preservation.

Important runtime reality:
- upstream Heretic is Transformers/PEFT-oriented and does not directly consume GGUF;
- Apple MPS support exists upstream, but the canonical GGUF cannot simply be passed to Heretic;
- therefore Pi must investigate the shortest technically sound route for the current machine and artifact.

Allowed routes, in priority order:
1. direct Heretic on a compatible source/quantized Transformers representation if feasible within local hardware/storage;
2. export/use the resulting low-rank edit in a llama.cpp-compatible form if technically valid;
3. a clean LOOM-native implementation of the same documented directional-edit principle targeting a runtime-compatible adapter/artifact;
4. if physical hardware/storage constraints make an actual behavior edit impossible, document the exact blocker and do not falsely label a prompt-only jailbreak as Heretic/decensoring.

A prompt-only system instruction does not satisfy the behavioral-edit acceptance gate.

## Sprint execution policy

Pi is authorized to operate autonomously inside this sprint.

### Authorized

- inspect all project files and local evidence;
- inspect upstream source/repositories and documentation;
- create/edit project code and configs locally;
- create isolated worktrees/copies for experiments;
- patch the Apple MoE runtime for measurement or acceleration when justified;
- build/rebuild required local binaries;
- build `llama-server` or another minimal serving frontend from a provenance-controlled source;
- create lightweight local API/web/Pi adapters;
- create project-local Python virtual environments / Node environments where necessary;
- install project-local dependencies when required and record them;
- run bounded benchmarks and capability tests;
- use deterministic synthetic tests before expensive model runs;
- revert unsuccessful/regressive experiments and continue;
- add local tracing/context/memory components;
- modify Pi local configuration needed to call LOOM, preserving backups;
- use the validated prompt-cache mechanism;
- perform source-level paging instrumentation and acceleration experiments;
- implement and test expert prefetch/overlap if attribution or direct controlled A/B evidence supports it;
- compare multiple runtime variants and keep the best validated one.

### Not authorized without returning to the user

- disabling SIP or other host security mechanisms;
- destructive disk/system operations;
- deleting user data outside project/evidence/temp artifacts;
- exposing the inference server to the public internet by default;
- requiring paid cloud/GPU services or new credentials;
- changing unrelated personal/system configuration;
- claiming success without evidence;
- committing/pushing to GitHub from Pi.

Prefer localhost-only networking by default.

## Internal phase plan

These are internal phases, not separate user tasks. Continue automatically from one to the next.

### Phase A — Fast integration audit

Determine what already exists and reuse it.

Inspect:
- current runtime/builds;
- current scripts/benchmarks;
- existing Pi provider hooks/config;
- existing UI/server code;
- model artifacts and disk headroom;
- current Python/Node/tooling;
- current source worktrees.

Create a durable sprint state file under `results-local/` recording goal, current phase, evidence and decisions.

### Phase B — Production serving path

Produce a persistent local serving path for DEEP.

Preferred first candidate:
build/use `llama-server` from the same pinned Apple MoE source if that target supports the required MoE paging flags and provides stable HTTP serving.

Otherwise implement the smallest reliable local service wrapper around the validated runtime.

Requirements:
- localhost-only by default;
- health check;
- streaming generation if available;
- stable model identifier;
- prompt/prefix cache or persistent KV reuse where supported;
- clean start/stop;
- logs and telemetry;
- no duplicate full model copies unless required.

### Phase C — Web interface

Deliver a usable browser chat interface.

Prefer the runtime's existing web UI if it is adequate and adds negligible overhead.

Otherwise build a minimal local UI consuming the API.

Required:
- send/stream messages;
- clear/new conversation;
- model/status display;
- visible generation state/error;
- no cloud dependency.

Do not spend sprint time on visual polish beyond usability.

### Phase D — Pi integration

Configure/test Pi against the local LOOM API/model.

Preserve any previous Pi config before mutation.

Acceptance test:
Pi must successfully issue at least one real local model request through the final serving path and receive a coherent response.

Prefer OpenAI-compatible local provider configuration if supported by Pi.

### Phase E — Runtime acceleration sprint

Goal:
maximize practical DEEP decode without sacrificing reliability/capability.

Prompt cache is already accepted for stable-prefix prefill/E2E.

For decode:
1. instrument the current paging path minimally;
2. measure expert hit/miss/read activity or another direct source-level statistic;
3. identify the largest likely wait source;
4. test the smallest evidence-backed optimization;
5. A/B against canonical S24;
6. keep only improvements that survive repeated bounded runs.

Candidate ideas include:
- expert read/prefetch overlap;
- scheduling overlap;
- reduced synchronization where source correctness proves it safe;
- cache/residency policy improvements;
- hot-expert retention/prefetch;
- chunking/prefill changes when product-relevant.

Do not port mini-SGLang wholesale.

Time/effort stopping rule:
- target `>=5 tok/s` decode first;
- continue toward higher throughput only while evidence suggests remaining low-risk headroom;
- after three materially different evidence-backed runtime interventions fail to improve the best validated candidate, stop runtime micro-optimization and finish the product stack.

Never keep an optimization whose speed gain is explained by broken output, changed model semantics, truncated generation, unsafe memory pressure or unbounded swap.

### Phase F — Context packing + progressive memory

Implement the smallest useful LOOM-native layer inspired by Caveman/Cavemem/LoopX.

Minimum desired behavior:
- project-scoped durable state outside prompt history;
- compact current-state/re-entry packet;
- deterministic context selection under a budget;
- exact recovery references for omitted tool/file evidence;
- local searchable memory for prior decisions/evidence if useful;
- token/accounting metrics before/after packing.

This layer should improve Pi/local-model usability, not merely exist.

If measured permanent overhead outweighs savings on the real LOOM workload, keep the feature optional/off by default.

### Phase G — Behavioral-freedom transform

Attempt the actual Heretic/LOOM-equivalent behavioral-edit stage.

Use project requirement:
`research/behavior/decensoring-requirement-v1.md`.

Minimum evidence before calling it complete:
- exact source/model/adapter provenance;
- actual weight/adapter-level behavior transform, not prompt-only behavior;
- frozen contrast prompts/evaluation prompts;
- measurable reduction in target refusal/alignment behavior;
- preservation test using existing LOOM capability benchmark or a bounded representative successor;
- throughput/memory delta;
- exact artifact hashes;
- final runtime can load the transformed profile.

Search should be bounded. Prefer deterministic/searchless or small-trial baselines before expensive large TPE sweeps on M1 8 GiB.

If a full Heretic run on this 30B cannot physically fit or complete using valid local representations, investigate a clean runtime-compatible low-rank equivalent before declaring a blocker.

### Phase H — Final end-to-end acceptance

Run the final system as a user would.

Required final checks:
1. one documented startup command or minimal command sequence;
2. model/server starts from a clean state;
3. health/API request succeeds;
4. browser UI can complete a conversation;
5. Pi can complete a local-model request;
6. stable-prefix caching works in the serving path where supported;
7. final decode speed, prompt/prefill, memory and swap are recorded;
8. representative capability smoke tests pass;
9. context/memory layer works or is explicitly disabled because evidence showed negative utility;
10. behavioral-edit profile is loaded and validated, or final status is explicitly `NOT_FULLY_PROMOTED` with the single hard blocker documented;
11. no critical crash/OOM/corruption;
12. startup/shutdown instructions and artifact hashes are durable.

## Final acceptance classifications

### `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_GO`

Use only if all user-facing requirements are genuinely operational, including an actual validated behavioral-edit profile.

### `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_PRODUCT_GO_BEHAVIOR_BLOCKED`

Use only if runtime/API/web/Pi/integration are production-usable but an evidenced physical/toolchain constraint prevents the required actual behavioral transform on the current machine.

This is not a fully promoted LOOM model.

### `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_NO_GO`

Use when the integrated stack itself is not reliably usable.

## Final return to ChatGPT/user

Return one bounded final report containing:
- classification;
- final architecture;
- exact start/stop commands;
- browser URL;
- API endpoint/model id;
- Pi integration/config location and test result;
- final selected runtime source/binary/model/adapter hashes;
- final decode/prefill/E2E/memory/swap results;
- prompt-cache state;
- context/memory components enabled/disabled and measured effect;
- behavioral-edit method/result;
- benchmark/capability preservation result;
- all code/config files changed;
- local evidence root(s);
- failed/reverted optimization attempts worth retaining as research evidence;
- remaining blockers only if they prevent full GO.

Do not return after every phase. Continue automatically.
