# LOOM Runtime + Product Serving — WP1

Date: 2026-08-30
Status: **AUTHORIZED / ACTIVE**
Checkpoint: `LOOM_RUNTIME_PRODUCTIZATION_WP1`

## Goal

Leave the canonical 30B DEEP model practically usable on the reference Apple M1 8 GiB host through the best validated runtime reached in this work package, a persistent localhost serving/API path, an existing privacy-respecting browser UI, and Pi.

WP1 is a macro work package. Scientific and engineering gates are internal. Pi must not return after routine sub-experiment GO/NO_GO outcomes; it should retain bounded evidence, revert regressions, and continue.

WP1 does **not** implement Caveman/Cavemem or the behavioral-transform work package.

## Canonical starting point

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Validated `llama-completion -no-cnv` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile:
S24.

Validated fresh-process decode baseline:
~4.39–4.40 tok/s.

Validated prompt-cache checkpoint:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Stable-prefix result:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`.

External unprivileged paging/I/O tracing preflight completed valid NO_GO. This does not reject paging as a bottleneck; isolated source-level measurement is authorized inside WP1.

## Operating policy

Pi may autonomously:
- inspect current local builds, source worktrees, scripts and evidence;
- create isolated source/build variants;
- minimally instrument the paging path for measurement;
- build/rebuild provenance-controlled local binaries;
- test evidence-backed runtime changes;
- run bounded A/B performance and stability tests;
- revert regressions and continue;
- build/use a persistent local serving frontend;
- create project-local environments/dependencies only when necessary and record them;
- update Pi local configuration after preserving a backup;
- create local operational scripts/configuration needed for start/stop/health.

Pi must not:
- commit/push/PR;
- disable SIP or weaken host security;
- perform destructive disk/system operations;
- delete unrelated user data;
- expose the inference service publicly by default;
- require paid cloud services or new credentials;
- silently relax performance/correctness gates;
- retain an optimization whose apparent speedup is caused by broken/truncated output, semantic changes, unsafe pressure or runaway swap.

Keep the canonical S24 path runnable as rollback until a better candidate is fully validated.

## Phase A — Runtime/decode optimization

Purpose: move direct decode above the current ~4.39–4.40 tok/s baseline when evidence supports a safe improvement.

Internal sequence:
1. audit the current pinned paging implementation and available prior evidence;
2. when needed, add the smallest isolated source-level instrumentation sufficient to observe paging hit/miss/read/wait behavior;
3. calibrate instrumentation overhead before using it for attribution;
4. identify the largest plausible decode wait source;
5. test evidence-backed candidates one at a time;
6. compare each candidate against the best known-good runtime using repeated bounded runs with equivalent prompts/settings;
7. keep only reproducible improvements with acceptable output, memory and swap.

Candidate families may include, when justified by evidence:
- expert read/prefetch overlap;
- hot-expert/residency policy improvements;
- scheduling/synchronization overlap;
- reduced avoidable paging/synchronization overhead;
- other small mini-SGLang-inspired mechanisms that map cleanly to this Apple/Metal MoE runtime.

Do not port mini-SGLang wholesale.

Target:
`>=5 tok/s` decode first.

Stopping rule:
- continue while a measured low-risk improvement path remains;
- after three materially different evidence-backed interventions fail to beat the best validated runtime, stop decode micro-optimization and proceed to serving;
- a WP1 GO does not require >=5 tok/s if the stopping rule is legitimately exhausted; it requires the **best validated practical runtime** plus a complete usable serving stack.

Persist failed/reverted attempts because they remain useful research evidence.

## Phase B — Persistent local serving/API

Preferred path:
build/use `llama-server` from the same provenance-controlled Apple MoE source if the server target supports the required paging/runtime configuration and remains stable on this host.

If that is not technically compatible, use the smallest reliable localhost service layer around the best validated runtime.

Requirements:
- bind to loopback/localhost only by default;
- stable health check;
- stable local model identifier;
- OpenAI-compatible API when practical;
- streaming responses when supported;
- clean startup/shutdown;
- logs and lightweight operational metrics;
- no unnecessary second copy of the full model;
- no cloud dependency.

Prefix/prompt caching:
- preserve the validated prompt-cache mechanism where the serving path can use an equivalent verified mechanism;
- measure/verify reuse in the final serving path rather than assuming completion-mode flags automatically transfer to server mode;
- do not claim serving-path cache acceleration unless it is directly verified.

## Phase C — Existing local WebUI only

**Do not build a LOOM web interface from scratch.**

Preferred UI:
the existing WebUI served by `llama-server`, if available and compatible with the final serving path.

Fallback:
an existing open-source local WebUI that can connect to the final localhost API.

Before selecting any fallback UI, verify that normal local use:
- does not require cloud inference;
- does not require sending conversations/model data to a remote service;
- has no mandatory telemetry/data collection path for the chosen configuration, or allows it to be fully disabled;
- can be kept localhost-only.

Do not spend WP1 time implementing visual polish or a custom frontend.

Acceptance:
- browser opens the local UI;
- one real conversation completes through the final 30B serving path;
- streaming/error state is usable enough for normal operation;
- no required external data egress is observed/configured.

## Phase D — Pi integration

Configure Pi to use the final local LOOM serving path.

Requirements:
- inspect current Pi provider/config mechanism rather than guessing;
- back up any existing Pi configuration before mutation;
- prefer a local OpenAI-compatible provider if Pi supports it;
- no cloud fallback during the acceptance request;
- Pi must issue at least one real request to the final local 30B model and receive a coherent response;
- retain the exact config path/change and a bounded test transcript/evidence.

## Phase E — Operationalization + final acceptance

Leave a simple local operating flow.

Required:
- one documented startup command or minimal sequence;
- one documented shutdown command or minimal sequence;
- health/status command;
- browser URL;
- API endpoint/model id;
- Pi configuration/test evidence;
- final binary/source/model hashes;
- final selected runtime flags/config;
- final decode/prompt/prefill/E2E measurements;
- peak RSS and swap;
- cache state and exact serving-path cache claim;
- lightweight logs/trace locations;
- rollback path to canonical S24;
- no critical crash/OOM/corruption in final smoke test.

## WP1 classification

`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Use when:
- the best validated practical runtime is selected;
- persistent local serving/API works;
- an existing privacy-respecting local WebUI works;
- Pi works against the same final local model path;
- start/stop/health workflow is documented;
- final performance/resource evidence is complete.

`LOOM_RUNTIME_PRODUCTIZATION_WP1_NO_GO`

Use when the integrated runtime/serving/web/Pi stack cannot be made reliably usable under the authorized local constraints.

A decode result below 5 tok/s alone does not make WP1 NO_GO if the internal stopping rule is correctly exhausted and the final stack is otherwise complete.

## Return policy

Do not return after routine internal sub-results.

Return only when:
1. WP1 is complete; or
2. a genuine blocker requires user action, credentials, unavailable hardware/storage, or a destructive/security-sensitive host change.

Final report must contain:
- classification;
- final architecture;
- exact start/stop/health commands;
- browser URL;
- API endpoint/model id;
- Pi config/test result;
- source/binary/model hashes;
- final runtime flags;
- decode/prefill/E2E/RAM/swap;
- serving-path prompt/prefix-cache status;
- selected existing WebUI and privacy/local-only verification;
- changed files/configs;
- evidence roots;
- notable failed/reverted runtime candidates;
- genuine remaining blocker, if any.
