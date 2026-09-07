# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-001 INFRASTRUCTURE GO / REALISTIC CODING GATE PENDING**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-001`

## Scope

LOOM is reopened only for the Context Engine research direction: keep the retained local 30B UNLOCKED model and physical `n_ctx=4096`, while giving Forge long-session continuity through an external host-side working-memory governor.

This is not a restart of UOPT speed/model optimization. Do not fork or modify Forge.

Operator modes remain:

```text
pi         -> vanilla Pi
Forge      -> normal Forge, unchanged
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM UNLOCKED model
```

`ForgeLoom` sets `FORGE_CONTEXT_INTELLIGENCE=0`; LOOM Context Engine is therefore the only owner of Pi's request-local `context` transformation.

## Current checkpoint

CE-001 has passed both the real one-shot Mac/30B smoke and the calibrated multi-turn synthetic stress. The sliding-window infrastructure is **GO**.

Do **not** proceed to CE-002 yet. The remaining CE-001 acceptance gate is the frozen realistic coding benchmark in one persistent ForgeLoom session.

### Real one-shot smoke — PASS

```text
Pi                         0.85.1
one-shot ForgeLoom         PASS
live gateway               PASS
model marker               PASS
final input                926
input ceiling              2800
output reserve             256
projected total            1214
safe total                 3600
headroom to safe           2386
headroom to physical 4096  2882
gateway prep               128.767 ms
governor estimate          28 -> 28
Pi threshold compactions   0
Pi overflow compactions    0
```

The smoke exposed roughly 900 provider-visible fixed/template/tool tokens not represented in the governor's message-only estimate. Working thresholds were therefore recalibrated from `2200/1700` to `1600/1200`.

### Multi-turn RPC stress — PASS

Real retained Mac/30B result on 2026-09-07:

```text
RPC turns completed        12
persistent message count   24
raw user payload chars     16296
max raw history estimate   5777
max visible estimate       1430
governor compactions       9
max exact final input      2343
max projected total        2631
min headroom to 4096       1465
hard-guard blocks          0
Pi threshold compactions   0
Pi overflow compactions    0
```

This is the first direct proof of the target invariant: the persistent session exceeded the physical 4096-equivalent working history while the model-visible window stayed bounded and the session continued normally.

## Core invariant

**4096 is a forbidden physical ceiling, not an operating target.**

Current calibrated envelope:

```text
physical context       4096
forbidden reserve       496
safe total             3600
final input ceiling    2800
maximum output          800
working high-water     1600   message-only conservative estimate
working target         1200   after governor compaction
measured fixed overhead ~900  smoke observation
legacy count margin      32
```

Final gateway invariant:

```text
final counted input + reserved output <= 3600 < 4096
```

Layer A must normally compact before Layer B is needed. A gateway hard-guard block during the frozen workload counts as CE-001 failure even though the physical limit remains protected.

## Architecture

```text
persistent Pi/Forge session
          |
          v
LOOM Context Engine
(request-local governor)
          |
          v
bounded working history
          |
          v
Pi provider assembly
(system + Forge tool schemas)
          |
          v
LOOM gateway hard guard
          |
          v
30B / n_ctx=4096
```

Pi's original session is not rewritten by the governor; `context` transforms apply only to the imminent model request.

The governor:

1. estimates message-only history;
2. triggers before the calibrated high-water;
3. evicts oldest complete user turns first;
4. preserves tool-call/tool-result coherence;
5. compacts oversized active-turn tool output only when whole-turn eviction is insufficient;
6. targets the low-water working set;
7. records JSONL accounting.

ForgeLoom also replaces Pi's large assembled coding/project system prompt with a minimal profile-only prompt. Project files remain available on disk and are read on demand.

## Exact counting compatibility

The retained patched llama.cpp does not expose `/v1/chat/completions/input_tokens`.

CE-001 counting order:

1. use `/v1/chat/completions/input_tokens` when available;
2. otherwise use retained-runtime `/apply-template`;
3. tokenize the rendered model input with `/tokenize`;
4. verify that tool schemas affect the rendered template when tools are present;
5. add a conservative 32-token legacy margin;
6. fail closed if counting cannot be demonstrated safely.

The legacy-safe path passed both the real smoke and the 12-turn stress.

## Pi native compaction

ForgeLoom cancels Pi automatic `threshold` compaction because the persistent transcript is intentionally retained outside the model-visible window.

Manual `/compact` remains available. Overflow compaction remains only as an emergency fallback.

Acceptance requires zero actual Pi threshold/overflow compactions. If Pi overflow recovery is invoked, CE-001 has failed its primary governor objective.

## Frozen retained product

Do not mutate during Context Engine work:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- default profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- expert-major sidecar: `models/unlocked-expert-major-v1.bin`
- sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime: `.loom/runtime/loom-uopt002/llama-server`
- runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical context: `4096`

Historical retained UOPT-003 baseline:

- decode `7.557 tok/s`
- 1,155-token cold prefill `11.306 tok/s`
- 1,155-token cold TTFT `102.242 s`
- refusal `0/6`, degeneration `0/6`, benign `8/8`

## CE-001 files

- `src/loom-context-engine/core.mjs` — request-local governor
- `src/loom-context-engine/index.ts` — Pi extension hooks
- `scripts/install-forge-loom.sh` — isolated installer / `ForgeLoom`
- `scripts/loom-context-webui-gateway.mjs` — final exact/legacy-safe hard guard
- `scripts/verify-context-engine.sh` — static/invariant verification
- `scripts/smoke-context-engine.sh` — one-shot real runtime smoke
- `scripts/stress-context-engine.sh` — 12-turn single-session synthetic stress
- `scripts/realistic-context-engine-benchmark.py` — frozen coding benchmark RPC harness
- `scripts/realistic-context-engine-benchmark.sh` — operator launcher
- `test/context-engine-core.test.mjs` — governor unit tests

## Next gate — frozen realistic coding benchmark

Use LOOM Coding Benchmark 01 v1.0.1 in `agentic` mode. The harness creates an isolated benchmark copy and one stable staging workspace, keeps **one ForgeLoom RPC session** alive for all six tasks, and sends every canonical `prompt.md` unchanged.

Between tasks the host replaces workspace files with the next frozen fixture while the ForgeLoom session remains alive. Only task-authorized outputs are copied back into the isolated benchmark tree. Out-of-scope edits are detected and fail the harness.

The official v1.0.1 runner then produces the objective 0–100 score.

Operator command:

```bash
git switch research/context-engine-001
git pull --ff-only origin research/context-engine-001
bash scripts/realistic-context-engine-benchmark.sh
```

Record:

- objective benchmark score and per-task tests;
- persistent message count;
- governor calls/compactions and visible estimates;
- exact final request input/projected totals;
- gateway hard-guard blocks;
- Pi actual compactions / overflow events;
- out-of-scope edits;
- sampled llama-server and agent RSS;
- swap before/after;
- client-observed first-text latency per task;
- backend prompt-eval/decode tok/s when present in llama-server logs.

CE-001 final GO requires infrastructure safety and session survival with the benchmark completing under the frozen rules. Model-quality mistakes must be reported separately from context-engine failures; they must not be hidden by changing benchmark prompts/tests.

Do not begin CE-002 archive/task-state/retrieval work until this result is reviewed.

## Later phases — not implemented

CE-002+ may add durable compact task state, external evidence archive, exact recovery and lightweight lexical retrieval. Do not add a second LLM, embeddings, vector DB or new model-facing memory tools unless later evidence demonstrates a need.

## Historical closure

Previous UOPT/model-runtime closure remains valid as historical evidence and rollback reference. The only explicitly reopened work on this branch is the Context Engine.