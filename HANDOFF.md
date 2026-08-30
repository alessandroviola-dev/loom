# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — user-directed acceleration mode. Micro-checkpoints are now internal gates inside one autonomous full-capability integration sprint. Goal is a usable end-to-end LOOM system today: canonical 30B DEEP runtime, local API, web UI, Pi integration, best validated acceleration, lightweight context/memory/observability improvements, and an actual validated behavioral-freedom transform where technically feasible on the reference M1 8 GiB host.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_001`
Pi context: `/AGENTS.md` v3.78.

## Canonical starting point

DEEP model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime baseline:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Validated `llama-completion -no-cnv` SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile: S24.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## Validated acceleration already retained

Prompt Cache R2:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

Validated stable-prefix result:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`;
- all frozen gates passed.

Prompt cache is canonical for reusable stable-prefix prefill/E2E acceleration.

## Paging attribution context

External non-mutating tracing preflight completed:
`LOOM_30B_ACCEL_PAGING_IO_ATTRIBUTION_PREFLIGHT_NO_GO`.

Evidence:
`results-local/research/30b-accel-paging-io-attribution-preflight-001/20260830T111709Z/`

Meaning:
tested native tracing did not expose a validated high-value per-process read observable under the current session constraints. This says nothing about whether paging is a decode bottleneck.

Pinned source inspection already established:
- per-layer LRU hit/miss counters exist internally;
- misses schedule expert-pool reads;
- `pread_pool(...)` performs the read loop;
- pool-read tasks may run concurrently;
- sidecar completion follows `resolve(...)`.

The previously preregistered instrumentation-design checkpoint remains useful research material but is now an internal phase of the full sprint rather than a user-facing stop.

## Current — Full Capability Integration Sprint 001

Authoritative sprint contract:
`research/integration/loom-full-capability-integration-sprint-001.md`

Operating-mode change:
- Pi works end-to-end;
- internal tests/gates remain evidence-based;
- a failed sub-experiment is recorded/reverted and Pi continues;
- no return to the user for routine GO/NO_GO substeps;
- stop only on final acceptance or a genuine hard blocker requiring user action/credentials/destructive or security-sensitive host changes.

Final target:
1. reliable local 30B DEEP serving;
2. stable local API, preferably OpenAI-compatible;
3. usable local browser chat;
4. Pi configured and verified against LOOM;
5. best validated prompt/cache/runtime acceleration enabled;
6. source-level paging attribution/optimization performed internally when justified;
7. lightweight local observability;
8. Caveman/Cavemem/LoopX-style context and durable-memory mechanisms integrated only when measured useful;
9. bounded workflow/orchestration ideas used only when beneficial;
10. actual behavioral-freedom transform attempted using Heretic or a technically valid LOOM-native equivalent, with preservation/resource validation;
11. one/few-command start/stop and durable operational documentation.

## Research inputs

Project repository-paper priority:
- mini-SGLang — inference/cache/scheduling concepts;
- Caveman — deterministic context compression/packing;
- Cavemem — progressive local memory;
- LoopX — durable state/re-entry;
- pi-dynamic-workflows — bounded opt-in orchestration;
- Observal — local measurement/replay philosophy;
- Heretic — contrastive residual-direction behavioral editing.

These are sources of mechanisms, not mandatory wholesale dependencies.

## Final classification

`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_GO` only when runtime + API + web + Pi + final behavior-edit profile are genuinely operational and validated.

If the entire product stack works but an evidenced physical/toolchain limit prevents an actual model-level behavioral transform on M1 8 GiB, use:
`LOOM_FULL_CAPABILITY_INTEGRATION_SPRINT_PRODUCT_GO_BEHAVIOR_BLOCKED`.

Do not label prompt-only jailbreak behavior as Heretic/decensoring.

Pi must not commit/push. ChatGPT remains responsible for canonical Git persistence after the final sprint report.
