# LOOM 30B Interactive Runtime v1 001 — Result

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Final classification: `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`

## Question

Can the frozen canonical Qwen3-30B-A3B Q4 LOOM runtime be converted into a real terminal chat runtime with exact model semantics, live token streaming, multi-turn state reuse and stable end-to-end generation on Apple M1/8GB?

## Frozen reference

- canonical backend: `scripts/loom_30b_moe_expert_major_backend_001.py`;
- production baseline commit: `96958de`;
- accepted exact-Q4/top-8 research median: `1.229233 tok/s`;
- no model/weight/quantization/routing changes.

## Reconciled execution environment

- Python: `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python version: `3.13.0`;
- MLX: `0.32.0`;
- mlx-lm: `0.31.3`;
- model/tokenizer: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`;
- canonical PACKED bank/runtime contract verified.

This resolves the earlier metadata-probe environment discrepancy: accepted model-forward work uses the above project venv.

## Candidate CLI

Local untracked candidate:
`scripts/loom_30b_interactive_v1_001.py`

Reported behavior:
- PACKED-only greedy terminal chat;
- canonical chat-template semantics;
- token-by-token stdout streaming;
- multi-turn KV/state reuse;
- `/reset` and `/exit`;
- clean teardown;
- deterministic persistent PACKED descriptor close;
- zero SOURCE fallback;
- no persistent expert-payload cache.

The candidate file is NOT canonical until exact local code review and Git persistence.

## Semantic parity

PASS.

For the frozen first 16 positions:
- chat-template/tokenization parity PASS;
- greedy token IDs identical;
- routed expert identities/order identical;
- raw float32 final-logit SHA identical;
- finite logits;
- stop behavior compatible;
- zero fallback/cache violation.

## Streaming / state reuse

Streaming: PASS.

Measured stdout flush p95:
`0.000075 s`.

State reuse: PASS.

The runtime retains generated token IDs and KV/recurrent state, then appends only the pending assistant token plus canonical assistant-close/user/generation boundary for the next turn. Prior transcript is not fully re-prefilled.

## Fixed three-turn memory smoke

PASS.

Transcript outputs:
1. `PRONTO`
2. `MEMORIZZATO`
3. `7319`

Conversation state remained available across turns without model reload.

## Long-form real generation

Prompt: frozen Italian MoE explanation from preregistration.

Generated text:

> Un modello **Mixture-of-Experts (MoE)** è una architettura in cui diversi “esperti” (sotto-modelli specializzati) vengono combinati in base al contesto. Ogni esperto è addestrato per gestire specifici tipi di input o compiti. Durante l'inferenza, un **gate** decide quale esperto utilizzare in base all'input, attivando solo i modelli rilevanti. Questo permette di ridurre il consumo di risorse, poiché non tutti gli esperti sono attivi contemporaneamente.
>
> La **riduzione della RAM** è un vantaggio principale: solo gli esperti necessari vengono caricati in memoria, permettendo l'uso di modelli molto grandi su hardware con limitata capacità. Questo è particolarmente utile in scenari di produzione o dispositivi con risorse limitate. Il MoE è quindi una soluzione efficiente per bilanciare **accuratezza** e **efficienza**, rendendolo ideale per applicazioni in tempo reale o su dispositivi a basso costo.

Measured:
- TTFT: `47.832 s`;
- decode-only throughput: `1.116 tok/s`;
- end-to-end output throughput: `0.921 tok/s`;
- per-token p50: `0.869 s`;
- per-token p95: `1.276 s`.

The output is coherent and generation completed safely. Decode throughput passes the frozen `>=1.00 tok/s` requirement, but TTFT exceeds the frozen `<=30 s` READY gate.

## Five-turn stability session

PASS.

Frozen turn-2 fact `ALFA-482` was correctly recovered on turn 5.

Per-turn measurements:
- T1: TTFT `29.013 s`, decode `0.789 tok/s`, context `25`;
- T2: TTFT `48.049 s`, decode `1.226 tok/s`, context `68`;
- T3: TTFT `21.830 s`, decode `1.426 tok/s`, context `99`;
- T4: TTFT `20.699 s`, decode `1.305 tok/s`, context `132`;
- T5: TTFT `26.003 s`, decode `1.331 tok/s`, context `174`.

All five turns completed without crash/hang/model reload and retained the required context fact.

## Memory / safety

Peak RSS:
`1,447,067,648 B` (~1.35 GiB).

Swap:
- long-form delta `-48 MiB`;
- three-turn session `0 MiB`;
- five-turn session `0 MiB`.

Safety PASS.

Fallback/cache state:
- backend `PACKED`;
- SOURCE fallback `0`;
- persistent expert payload cache `false`.

## Decision

Final classification:
`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

All correctness, semantic parity, streaming, state-reuse, conversation-memory, stability, memory and safety gates PASS.

The sole frozen READY-gate miss is long-form TTFT:
`47.832 s > 30 s`.

Therefore LOOM 30B is now proven to be a functioning end-to-end local interactive runtime, but it is not yet classified as fully user-ready under the preregistered latency target.

Production/user-facing code must not be called canonical until `scripts/loom_30b_interactive_v1_001.py` is reviewed and committed.

## Evidence

`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`

## Next action

1. review the exact local interactive CLI source and SHA;
2. if review PASS, commit/push only that intended file;
3. run a manual real user conversation from Terminal;
4. then freeze LOOM 30B v1 as the large-model practical comparator;
5. execute the matched 30B vs 8B vs 4B practical bake-off.

Do not hide the TTFT result with post-hoc threshold changes. A later dedicated TTFT/prefill optimization may be opened only as a separate hypothesis if practical use shows it is worth prioritizing.