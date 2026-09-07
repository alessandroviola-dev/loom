# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-001 REALISTIC TRANSCRIPT REPLAY PASS / LIVE TOOL-HEAVY GATE PENDING**
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

CE-001 passed the real one-shot smoke and 12-turn synthetic long-context stress. The first frozen realistic coding benchmark then exposed one genuine gateway hard-guard block, so CE-001 was correctly held at NO-GO.

That real transcript has now been replayed offline through the updated governor at every reconstructed provider-attempt boundary. The updated governor bounded all 24/24 reconstructed realistic views to the `1200` working target, with zero target or high-water misses.

The active-turn fix is therefore **offline validated against the exact transcript that previously failed**. CE-001 is still not final GO until the corrected extension passes one short live tool-heavy ForgeLoom regression.

Do **not** proceed to CE-002 yet.

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

The smoke exposed substantial provider-visible fixed/template/tool overhead not represented directly by the governor's message-only estimate. Working thresholds were recalibrated from `2200/1700` to `1600/1200`.

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

This proved the basic sliding-window invariant for long inert multi-turn history.

### Frozen realistic coding benchmark — COMPLETED / ORIGINAL CE-001 NO-GO

Recovered from the completed six-task ForgeLoom RPC run after the harness timed out only on final `get_state` telemetry.

Objective coding score:

```text
score  60.0 / 100

T01  6/6 tests   15.00/15
T02  2/7 tests    4.29/15
T03  4/7 tests    8.57/15
T04  4/7 tests    8.57/15
T05  6/7 tests   21.43/25
T06  1/7 tests    2.14/15
```

Context-engine evidence:

```text
RPC accepted tasks         6
RPC agent_end events       6
successful assistant msg   24
provider attempts          24
persistent msg lower bound 48
governor calls             24
governor compactions       20
max raw estimate           8191
max visible estimate       2721
max exact final input      2857
max projected total        3145
min headroom to 4096       951
hard-guard blocks          1
Pi actual compactions      0
Pi overflow events         0
persisted scope issues     0
```

Genuine blocked request:

```text
finalInputTokens       2857
guardInputTokens       2889
outputReserve           256
projectedTotalTokens    3145
requestInputCeiling     2800
safeTotalTokens         3600
tokenCountMargin          32
tokenCountMethod        apply-template+tokenize
```

The physical 4096 ceiling remained protected: Layer B blocked the request before model forwarding. The model-quality score (60/100) is recorded separately from this context-engine failure.

## Root cause and active-turn fix

The original governor compacted old complete user turns and `toolResult` text, but did not sufficiently bound structurally large active coding turns containing many completed tool exchanges and large historical `toolCall.arguments`.

Updated `src/loom-context-engine/core.mjs` now:

1. drops oldest complete user turns first;
2. preserves the current user instruction;
3. compacts oversized tool-result text and assistant narration;
4. compacts large strings nested inside historical `toolCall.arguments`;
5. preserves tool-call IDs, names and matching tool-result IDs;
6. compacts completed call/result exchanges together, oldest first;
7. initially preserves the newest completed tool exchange at higher fidelity;
8. performs a second aggressive completed-exchange pass when needed;
9. as a last resort, evicts the oldest **completed assistant tool-call + matching tool-result group as one coherent unit** until the low-water target is met;
10. never truncates the current user request in this fallback;
11. records tool-argument, emergency-pass and completed-exchange-drop accounting.

Unit tests cover repeated coding-style active-turn exchanges and assert target bounding, call/result coherence, and persistent-session immutability.

### Offline replay of failed realistic transcript — PASS

The exact `rpc.jsonl` from the failed realistic run was replayed through the corrected governor without model inference.

```text
provider attempts           24
max raw estimate            8557
max replay visible          1196
governor reductions         20
tool-arg compactions        59
emergency passes            11
target misses (>1200)       0
high-water misses (>1600)   0
```

Result:

```text
CE-001 REPLAY PASS
```

This is the strongest offline regression evidence available because it uses the same real coding transcript that previously produced the hard-guard block.

## Immediate next gate — short live tool-heavy regression

Do **not** rerun the full six-task benchmark yet.

`scripts/live-tool-heavy-context-engine.sh` creates an isolated workspace and runs one real ForgeLoom turn that requires multiple reads, one edit, bash verification and a final read inside the same user turn. It then verifies only that session's Context Engine accounting and only gateway rows created during the run.

Before running it, reinstall the updated extension so `~/.pi/agent/extensions/loom-context-engine/core.mjs` matches the branch.

Operator commands:

```bash
git switch research/context-engine-001
git pull --ff-only origin research/context-engine-001
bash scripts/install-forge-loom.sh
bash scripts/live-tool-heavy-context-engine.sh
```

Live acceptance:

- real ForgeLoom tool chain completes;
- governor active-turn logic is actually exercised;
- every changed governor view is `<=1200`;
- no `best-effort-active-turn-too-large` result;
- exact final input remains `<=2800`;
- projected total remains `<=3600`;
- zero hard-guard blocks;
- zero Pi actual compactions;
- zero Pi overflow events.

If this passes, review whether the already-completed realistic benchmark plus exact transcript replay and live regression provide sufficient CE-001 closure evidence before spending time on a full six-task rerun.

## Core invariant

**4096 is a forbidden physical ceiling, not an operating target.**

Current envelope remains:

```text
physical context       4096
forbidden reserve       496
safe total             3600
final input ceiling    2800
maximum output          800
working high-water     1600   message-only conservative estimate
working target         1200   after governor compaction
legacy count margin      32
```

Final gateway invariant:

```text
final counted input + reserved output <= 3600 < 4096
```

Additional operational requirement:

```text
Layer A governor should keep ordinary requests below the final-input ceiling;
Layer B hard guard is fail-safe, not normal flow control.
```

A gateway hard-guard block during an acceptance workload counts as CE-001 failure even if the request was successfully prevented from reaching the model.

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

The legacy-safe path passed the real smoke and synthetic long-context stress and correctly blocked the one oversized realistic request before forwarding.

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
- `scripts/recover-realistic-context-engine-benchmark.py` — score/safety recovery after telemetry timeout
- `scripts/replay-context-engine-rpc.mjs` — offline replay of real RPC transcript through current governor
- `scripts/live-tool-heavy-context-engine.sh` — short isolated real ForgeLoom active-turn regression
- `test/context-engine-core.test.mjs` — governor unit tests

## Final CE-001 acceptance sequence

Current order:

1. realistic transcript replay — **PASS**;
2. reinstall updated extension;
3. short live tool-heavy validation with zero hard-guard blocks;
4. review whether a full six-task benchmark rerun is necessary for final closure.

Final CE-001 GO requires:

- zero hard-guard blocks in the final live acceptance workload;
- zero Pi threshold/overflow compactions;
- no context-window termination;
- model-visible input kept safely below physical 4096;
- session survival;
- coding-quality mistakes reported honestly and separately.

Do not begin CE-002 archive/task-state/retrieval work until CE-001 final GO.

## Later phases — not implemented

CE-002+ may add durable compact task state, external evidence archive, exact recovery and lightweight lexical retrieval. Do not add a second LLM, embeddings, vector DB or new model-facing memory tools unless later evidence demonstrates a need.

## Historical closure

Previous UOPT/model-runtime closure remains valid as historical evidence and rollback reference. The only explicitly reopened work on this branch is the Context Engine.