# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-001 SMOKE GO / MULTI-TURN STRESS PENDING**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-001`

## Reopen decision

LOOM was explicitly reopened by the owner for a new research direction only: preserve the retained local 30B UNLOCKED model and its physical 4096-token context while giving Forge long-session continuity through an external host-side Context Engine.

This is not a restart of UOPT speed/model optimization.

## Current checkpoint

CE-001 repository implementation and the first real local Mac/30B smoke have passed. **Do not proceed to CE-002 yet.** The next gate is the calibrated multi-turn RPC stress test.

Real smoke result on 2026-09-07:

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

The smoke exposed ~900 tokens of provider-visible fixed/template/tool overhead not represented in the governor's message-only estimate. Therefore the working thresholds were recalibrated from `2200/1700` to **`1600/1200`** before stress testing.

Repository-side pieces:

- `src/loom-context-engine/core.mjs` — request-local governor;
- `src/loom-context-engine/index.ts` — Pi/ForgeLoom extension hooks;
- `scripts/install-forge-loom.sh` — isolated installer + `ForgeLoom` launcher;
- `scripts/loom-context-webui-gateway.mjs` — final token/output hard guard;
- `scripts/verify-context-engine.sh` — static/invariant verification;
- `scripts/smoke-context-engine.sh` — one-shot local runtime calibration/smoke;
- `scripts/stress-context-engine.sh` — single-session multi-turn RPC stress;
- `test/context-engine-core.test.mjs` — governor unit coverage.

Required next operator sequence:

```bash
git switch research/context-engine-001
git pull --ff-only origin research/context-engine-001
bash scripts/install-forge-loom.sh
bash scripts/stress-context-engine.sh
```

Do not proceed to CE-002 until the stress passes and its gateway/governor accounting has been reviewed.

## Frozen retained product

Do not mutate:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- default profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- expert-major sidecar: `models/unlocked-expert-major-v1.bin`
- expert-major sidecar SHA256: `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e`
- patched runtime: `.loom/runtime/loom-uopt002/llama-server`
- patched runtime SHA256: `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`
- physical context: `4096`

Retained measured UOPT-003 result remains historical baseline:

- decode `7.557 tok/s`
- 1,155-token cold prefill `11.306 tok/s`
- 1,155-token cold TTFT `102.242 s`
- frozen gates refusal `0/6`, degeneration `0/6`, benign `8/8`

## Architecture decision

Do **not** fork or modify Forge.

Target operator modes:

```text
pi         -> vanilla Pi
Forge      -> normal Forge, unchanged
ForgeLoom  -> Forge + LOOM Context Engine + retained LOOM UNLOCKED model
```

`ForgeLoom` enables Forge normally but sets `FORGE_CONTEXT_INTELLIGENCE=0` for that process, so LOOM Context Engine is the only owner of Pi's `context` transformation.

The model-visible context is a sliding bounded view over a much larger persistent Pi/Forge session:

```text
full Forge session
       |
       v
LOOM Context Engine
       |
       v
safe working window well below 4096
       |
       v
LOOM 30B / n_ctx=4096
```

The original Pi session remains intact because `context` event transforms are request-local/ephemeral.

## Core invariant

**The model must never be allowed to approach 4096 tokens.**

4096 is the physical hard limit, not an operating target. CE-001 must enforce preventive backpressure before every LLM request and reduce the visible working set before Pi/Forge or llama.cpp reaches an overflow condition.

### Calibrated CE-001 operating envelope

```text
physical context       4096
forbidden reserve       496
safe total             3600
final input ceiling    2800
maximum output          800
working high-water     1600   (message-only conservative estimate)
working target         1200   (after governor compaction)
measured fixed overhead ~900  (smoke observation, includes conservative counting path)
```

The working high-water is intentionally below the final input ceiling by enough room to absorb the measured fixed provider/template/tool overhead before Layer B is needed.

Hard invariant at the final gateway:

```text
final counted input + reserved output <= 3600 < 4096
```

## Exact counting compatibility

The retained patched llama.cpp runtime does **not** expose the newer `/v1/chat/completions/input_tokens` endpoint; the first guarded smoke correctly failed closed with HTTP 503 rather than forwarding an unverifiable request.

CE-001 now uses this order:

1. try `/v1/chat/completions/input_tokens` when available;
2. on the retained legacy runtime, render with `/apply-template` and tokenize the rendered model input with `/tokenize`;
3. verify that provider-visible tool schemas are represented in the rendered template when tools are present;
4. add a conservative `32`-token legacy counting margin;
5. fail closed if safe counting cannot be demonstrated.

The fallback passed the real retained-runtime smoke.

## Fixed-overhead reduction

Pi's normal system prompt, project context and tool instructions can consume a material fraction of a 4096-token window even after conversation pruning.

Therefore, only while `LOOM_CONTEXT_ENGINE=1`, CE-001 replaces the fully assembled per-turn system prompt with a minimal ForgeLoom prompt. Project state is not injected on every request; the agent is instructed to read `AGENTS.md` / `HANDOFF.md` when relevant. Forge's four provider-visible tool schemas remain available.

This does not modify normal Forge behavior.

## CE-001 scope

CE-001 implements only the preventive governor:

1. separate opt-in LOOM extension;
2. Pi `context` interception before each LLM call;
3. conservative message-token estimate for the transform decision;
4. whole-turn eviction of oldest history while retaining the newest active turn;
5. deterministic compaction of oversized tool-result text inside the active turn only when whole-turn eviction is insufficient;
6. minimal ForgeLoom-only system prompt to reduce fixed overhead;
7. final request token count + output-reserve guard in the existing LOOM gateway;
8. local JSONL accounting;
9. dedicated `ForgeLoom` launcher/install path;
10. frozen multi-turn validation workload.

No second LLM, embeddings, vector DB, new model-facing tools, durable task-state intelligence, BM25/FTS, or semantic retrieval in CE-001.

## Safety model

### Layer A — request-local Context Governor

Runs on Pi's `context` event before every LLM call and returns a bounded message list. It evicts whole old turns first; if the active turn itself is oversized it deterministically compacts large tool outputs/assistant narration without mutating the persistent session.

### Layer B — final gateway envelope guard

Runs on the final OpenAI-compatible chat payload after Pi/Forge has assembled provider material. It:

- caps/reserves output;
- counts final model input using the supported exact/legacy-safe tokenizer path;
- verifies the configured safe-total envelope;
- refuses the request rather than forwarding an unsafe/unverifiable payload.

Layer B is a last-resort invariant check, not the normal compaction mechanism. A gateway block during the normal frozen workload is a CE-001 failure even though the physical 4096 invariant was protected.

## Pi native compaction interaction

Pi's stock compaction defaults are designed for much larger context windows and can request automatic threshold compaction independently of CE-001. The LOOM extension cancels **threshold** compaction while active so the full persistent transcript is not replaced by Pi's summary.

Manual `/compact` remains available. Overflow compaction remains enabled only as an emergency fallback; if overflow recovery is actually invoked during the frozen workload, CE-001 has failed its primary safety goal.

A cancelled `session_before_compact(reason="threshold")` attempt is accounting evidence, not an actual compaction. Actual `session_compact` events are the failure signal for the acceptance gate.

## Next gate — automated multi-turn RPC stress

`scripts/stress-context-engine.sh` runs one ForgeLoom process in Pi RPC mode and keeps a single in-memory session alive across multiple turns. Default stress is 12 controlled turns with enough inert payload for the **raw uncompressed session estimate to exceed 4096**, while the model-visible request is repeatedly repacked.

Stress PASS requires:

- all RPC turns complete in the same session;
- persistent message count continues growing;
- raw session estimate exceeds 4096;
- governor performs at least one real request-local compaction and drops old whole turns;
- post-compaction estimate returns to <=1200 except an explicitly detected oversized active-turn case;
- every final request remains <=2800 input and <=3600 projected total;
- hard-guard blocks = 0;
- actual Pi threshold compactions = 0;
- Pi overflow compactions = 0;
- session survives through the final turn.

This test validates the core sliding-window invariant. It does **not** yet validate recovery of facts intentionally evicted from the visible window; that belongs to later archive/task-state/retrieval phases.

## CE-001 final acceptance after stress

After the synthetic stress passes, run a frozen realistic coding workload and record at minimum:

- cumulative session activity;
- visible messages/estimated tokens before and after governor;
- number of governor compactions;
- exact final request input tokens;
- reserved output and projected safe total;
- gateway guard rejections;
- Pi compaction attempts/actual events;
- session survival;
- task completion/correctness;
- RAM/swap;
- TTFT and decode tok/s.

GO requires:

- every forwarded request satisfies the configured safe-total envelope;
- no gateway hard-guard blocks during normal operation;
- zero actual Pi threshold/overflow compactions;
- zero context-window session termination;
- task completes correctly;
- no material RAM/swap or throughput regression.

If CE-001 fails, do not proceed to memory/retrieval phases. Diagnose the governor first.

## Historical closure

The previous project closure and UOPT records remain valid for model/runtime optimization. They are historical evidence and rollback references only; they no longer prohibit the explicitly authorized Context Engine work on this branch.
