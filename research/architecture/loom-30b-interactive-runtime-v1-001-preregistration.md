# LOOM 30B Interactive Runtime v1 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Turn the frozen canonical Qwen3-30B-A3B Q4 LOOM runtime from a benchmark/research engine into a practically usable local text-chat runtime on Apple M1/8GB, without changing model semantics, quantization, routing, weights, or accepted expert-major behavior.

This checkpoint is productization/real-use validation, not a new speed frontier.

Frozen model/runtime comparator:
- canonical backend `scripts/loom_30b_moe_expert_major_backend_001.py`;
- production baseline commit `96958de`;
- exact Q4/top-8 sustained reference median `1.229233 tok/s` from the accepted 3×32 campaign;
- no routing sparsity, Q2/Q3, DFlash, speculative decoding, or model-weight edits.

Final outcomes:
- `LOOM_30B_INTERACTIVE_V1_READY`
- `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`
- `LOOM_30B_INTERACTIVE_V1_NOT_READY`
- `LOOM_30B_INTERACTIVE_V1_INCONCLUSIVE`

## Stage 0 — freeze execution environment and canonical path

Before implementation changes:
- mechanically locate/freeze the exact Python/interpreter environment used by accepted Qwen3-30B model-forward runs;
- record Python executable/version, MLX version, mlx-lm version and directly relevant dependencies;
- prove the canonical backend file SHA-256 is `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`;
- verify canonical model/tokenizer/full-bank artifacts exist and are readable;
- no package install/upgrade if the accepted environment already exists;
- no network/model download.

Read only directly relevant current generation/runtime scripts and canonical backend. Do not broadly reread repository history.

If the accepted execution environment cannot be deterministically recovered: `LOOM_30B_INTERACTIVE_V1_INCONCLUSIVE` and STOP.

## Stage 1 — build minimum interactive CLI/runtime wrapper

Create one local candidate implementation, intended path:
`scripts/loom_30b_interactive_v1_001.py`

Pi may create/edit this tracked file locally but MUST NOT commit/push.

Required user-facing behavior:
- text-only terminal CLI;
- load the canonical Qwen3-30B-A3B Q4 LOOM runtime;
- accept user messages interactively;
- use the model/tokenizer's canonical chat-template semantics already compatible with the deployed model;
- stream decoded text to stdout as tokens become available; do not wait for the full answer before printing;
- greedy generation is the frozen v1 decoding mode;
- configurable `--max-tokens` with a safe default;
- stop on canonical EOS/stop semantics;
- maintain conversation state across turns;
- reuse valid KV/recurrent model state so that previous turns are not fully re-prefilled when the runtime architecture permits exact incremental continuation;
- commands at minimum: `/reset`, `/exit`;
- `/reset` must clear conversation/KV/recurrent state deterministically without reinitializing unrelated immutable artifacts when avoidable;
- clean Ctrl-C/EOF teardown;
- deterministic backend close, including the canonical persistent PACKED file descriptor;
- zero SOURCE fallback;
- zero persistent multi-expert payload cache.

No GUI, web server, API server, RAG, tools, memory database, Heretic/refusal editing, sampling search, or unrelated product features in v1.

## Stage 2 — semantic parity gate

Before usability benchmarking, compare the interactive wrapper against the accepted canonical greedy generation path on one frozen deterministic prompt.

Require for exactly the first 16 generated positions, unless EOS occurs earlier after at least 8 positions:
- identical input/chat-template tokenization;
- identical greedy token IDs;
- identical routed expert identities/order;
- identical raw float32 final-logit SHA at each compared position;
- identical stop behavior;
- finite logits;
- zero SOURCE fallback/cache.

If semantic parity FAILs: `LOOM_30B_INTERACTIVE_V1_NOT_READY` and STOP. Do not rescue by changing model semantics.

## Stage 3 — streaming and state-reuse mechanics

Run a deterministic two-turn mechanical test.

Record:
- wall from user-submit to first decoded token available (TTFT);
- wall from first token available to first token flushed to terminal;
- output-token count;
- decode tok/s excluding prefill;
- number of prompt/history tokens processed on turn 1;
- number of new tokens processed on turn 2;
- whether prior-turn KV/recurrent state was reused;
- peak RSS and swap delta.

Streaming PASS requires:
- text is emitted incrementally before generation completes;
- terminal flush overhead after a decoded token becomes available is <=250 ms p95 in this bounded test.

State-reuse PASS requires:
- turn 2 consumes only newly appended chat tokens plus required minimal boundary/control tokens, not a full re-prefill of the entire previous transcript;
- causal state/KV semantics remain equivalent to canonical continuation.

If exact state reuse is not implementable with the current canonical runtime without architectural work, the runtime may remain functionally multi-turn by deterministic re-prefill, but must be explicitly classified as state-reuse FAIL and cannot receive `READY`; it may still receive `FUNCTIONAL_SLOW` if all other functional gates pass.

## Stage 4 — fixed three-turn conversation-memory test

Use exactly this deterministic conversation with greedy decoding and a bounded max-token setting:

Turn 1 user:
`Rispondi soltanto con: PRONTO`

Turn 2 user:
`Ricorda il numero 7319. Rispondi soltanto con: MEMORIZZATO`

Turn 3 user:
`Quale numero ti ho chiesto di ricordare? Rispondi soltanto con il numero.`

Pass conditions:
- each turn completes without runtime error;
- final turn contains the exact tokenized textual answer `7319` after normal whitespace normalization;
- conversation state is not lost between turns;
- no model reload is required between turns;
- no SOURCE fallback/cache violation;
- peak RSS <= 6.5 GiB;
- swap delta across the whole three-turn session <=512 MiB;
- no unsafe memory pressure.

This is a runtime-state smoke, not an intelligence benchmark.

## Stage 5 — real long-form single-answer usability run

Fresh process.

Prompt:
`Spiega in italiano, in modo chiaro ma tecnico, come funziona un modello Mixture-of-Experts e perché può essere utile su hardware con poca RAM. Scrivi circa 180 parole.`

Frozen generation:
- greedy;
- `max_tokens=256`;
- normal EOS/stop semantics;
- stream output live.

Require at least 96 generated tokens unless canonical EOS occurs earlier after producing a coherent complete answer. If EOS occurs before 96 tokens, record it without forcing continuation.

Record:
- startup/runtime-ready wall;
- prompt token count;
- prefill wall;
- TTFT;
- generated token count;
- total answer wall;
- decode-only tok/s;
- end-to-end output tok/s including TTFT;
- p50/p95 per-token decode wall;
- peak RSS;
- swap delta;
- memory-pressure/safety state;
- exact final generated text in evidence.

No quality scoring is used in this checkpoint beyond basic completion/finite-output validity; intelligence comparison is a later frozen bake-off.

## Stage 6 — bounded real-session stability test

In one fresh process, execute exactly five sequential user turns using short deterministic prompts from distinct topics, with the fifth asking for a fact introduced in turn 2.

The five prompts must be frozen into evidence before generation starts and must not be changed after outputs are observed.

Measure per turn:
- context length;
- new prompt tokens;
- TTFT;
- output tokens;
- decode tok/s;
- RSS after turn;
- swap delta;
- state-reuse status.

Pass requires:
- all five turns complete;
- no crash/hang;
- no model reload between turns;
- fifth turn correctly recovers the frozen fact from turn 2;
- RSS <=6.5 GiB;
- cumulative swap delta <=512 MiB;
- zero SOURCE fallback/persistent expert cache.

## Stage 7 — decision

`LOOM_30B_INTERACTIVE_V1_READY` iff all hold:
- Stage 2 semantic parity PASS;
- streaming PASS;
- exact incremental state/KV/recurrent reuse PASS;
- three-turn state smoke PASS;
- long-form run completes safely;
- five-turn stability PASS;
- long-form decode-only throughput >=`1.00 tok/s`;
- long-form TTFT <=30 s;
- memory/swap gates PASS.

`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW` iff:
- semantic parity and functional/stability/safety gates PASS;
- but either exact state reuse is unavailable, long-form decode throughput <1.00 tok/s, or TTFT >30 s.

`LOOM_30B_INTERACTIVE_V1_NOT_READY` for deterministic implementation/runtime correctness failure, state loss, unsafe memory behavior, fallback/cache violation, or inability to complete the required real sessions.

`LOOM_30B_INTERACTIVE_V1_INCONCLUSIVE` only for genuine environment/instrumentation ambiguity.

## Evidence

Save complete machine-readable evidence under:
`results-local/research/30b-interactive-runtime-v1-001/<UTC>/`

Required summary includes:
- environment/provenance;
- semantic parity result;
- streaming mechanics;
- state-reuse mechanics;
- fixed 3-turn transcript;
- long-form text + performance;
- five-turn stability metrics/transcript;
- peak RSS/swap/safety;
- exact changed tracked-file list and concise diff summary.

## Hard bounds

- no network/model download;
- no package upgrade unless the accepted execution environment genuinely cannot be recovered, in which case STOP rather than install;
- no model/weight/quantization/routing change;
- no Q2/Q3;
- no DFlash/speculative decoding;
- no Qwen3.8 work;
- no Heretic/refusal-direction editing yet;
- no 8B/4B comparison yet;
- no Git commit/push/project decision-doc edits by Pi;
- no threshold rescue;
- do not modify the canonical backend unless a deterministic runtime integration defect requires it; if modification becomes necessary, record it and STOP for review before treating v1 as accepted.

## After this checkpoint

If `READY`, review and persist the interactive runtime as **LOOM 30B v1**, then run the matched practical bake-off against one Qwen-family 8B and one 4B local baseline on the same M1/8GB.

The bake-off decides whether LOOM should prioritize:
1. the 30B as deep/primary mode;
2. an 8B/4B fast primary plus 30B deep mode;
3. a skill/tool/protocol-centric small-model system.

Only after that model-role decision should the project apply the Heretic-inspired behavioral/refusal-editing protocol to the selected runtime(s). A separate R&D branch may then revisit materially new 30B speed mechanisms such as direct-from-higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O, or trace-driven bounded caching.