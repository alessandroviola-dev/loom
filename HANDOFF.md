# LOOM — Context Engine Handoff

Last updated: 2026-09-07
Status: **ACTIVE — CE-001 PREVENTIVE CONTEXT GOVERNOR**
Repository: `Ilcoach/loom`
Branch: `research/context-engine-001`

## Reopen decision

LOOM was explicitly reopened by the owner for a new research direction only: preserve the retained local 30B UNLOCKED model and its physical 4096-token context while giving Forge long-session continuity through an external host-side Context Engine.

This is not a restart of UOPT speed/model optimization.

## Frozen retained product

Do not mutate:

- model: `models/loom-deep-30b-unlocked.gguf`
- model SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`
- default profile: UOPT-003 S40 / CPU-MoE / no-mmap / cache RAM 512 / `-ub 4`
- expert-major sidecar: `models/unlocked-expert-major-v1.bin`
- patched runtime: `.loom/runtime/loom-uopt002/llama-server`
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

`ForgeLoom` must enable Forge normally but disable Forge Context Intelligence only for that process, so the LOOM Context Engine is the single owner of the Pi `context` transformation.

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

Exact threshold values are configuration/measurement outputs, not assumptions. Initial implementation should expose:

- physical context = 4096
- safe input ceiling
- high-water compaction trigger
- low-water post-compaction target
- safety reserve

## CE-001 scope

Implement only the preventive governor:

1. separate opt-in LOOM extension;
2. Pi `context` interception before each LLM call;
3. conservative token accounting for the transform decision;
4. whole-turn eviction of oldest history while retaining the newest active turn;
5. deterministic compaction of oversized tool-result text inside the active turn only when whole-turn eviction is insufficient;
6. exact final request token count/guard in the existing LOOM gateway using llama.cpp `/v1/chat/completions/input_tokens`;
7. local JSONL accounting;
8. dedicated `ForgeLoom` launcher/install path;
9. frozen long-session validation workload.

No second LLM, embeddings, vector DB, new model-facing tools, durable task-state intelligence, BM25/FTS, or semantic retrieval in CE-001.

## Safety model

Two layers:

### Layer A — request-local Context Governor

Runs on Pi's `context` event before every LLM call and returns a bounded message list. It should normally keep requests far enough below the physical limit that Pi's own threshold/overflow compaction is never invoked.

### Layer B — gateway hard guard

Runs on the final OpenAI-compatible chat payload after Pi has assembled system/tool/provider material. It obtains the backend's exact token count and refuses an unsafe request rather than forwarding it to the 30B.

Layer B is a last-resort invariant check, not the normal compaction mechanism.

## CE-001 acceptance gate

Use a frozen realistic coding workload that produces substantially more than 4096 cumulative session tokens.

Record at minimum:

- cumulative session activity;
- visible messages/tokens before and after governor;
- number of governor compactions;
- maximum final request input tokens;
- gateway guard rejections;
- Pi `session_before_compact` / `session_compact` events by reason;
- session survival;
- task completion/correctness;
- RAM/swap;
- TTFT and decode tok/s.

GO requires:

- no final request reaches the configured safe ceiling;
- zero Pi threshold/overflow compactions during the frozen workload;
- zero context-window session termination;
- task completes correctly;
- no material RAM/swap or throughput regression.

If CE-001 fails, do not proceed to memory/retrieval phases. Diagnose the governor first.

## Historical closure

The previous project closure and UOPT records remain valid for model/runtime optimization. They are historical evidence and rollback references only; they no longer prohibit the explicitly authorized Context Engine work on this branch.