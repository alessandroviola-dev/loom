# LOOM 8B Practical Bake-off Runner 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED

## Question

Can the previously validated LOOM Qwen3-8B Direct-MLX runtime complete the same small coding task used in the manual 30B test with materially better practical latency, without changing the validated 8B model/runtime semantics?

## Frozen source baseline

Canonical REALGEN source:
`scripts/loom_real_generation_baseline_001.py`

Validated model/runtime:
- local model: `results-local/mlx/models/Qwen3-8B-3bit`;
- upstream identity: `mlx-community/Qwen3-8B-3bit`, revision `619ded3`;
- weight SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- quantization: 3-bit affine, group size 64;
- launcher: `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- Qwen3 normal chat template, `enable_thinking=false`;
- greedy argmax, no sampling/speculation/oracle/drafter;
- ordinary real autoregressive M1 built-in MLX `qmv_fast` path;
- BF16 KV;
- cleanup translation retained: `gc.collect() -> mx.clear_cache() -> gc.collect()` after each 10 committed generated tokens.

Historical REALGEN 001 comparator:
- pooled real-generation `13.184615 tok/s`;
- pooled end-to-end output `12.046861 tok/s`;
- typical TTFT ~`0.94 s` across six prompts;
- peak MLX memory `3,826,575,836 B`;
- peak swap `1591.19 MB`.

Stretch-037 `S1_R8` is explicitly NOT injected: it is M5-only/oracle-path evidence and ineligible for this M1 chat runner.

## Frozen task

Exact single-line user prompt:

`Scrivi in Python una classe LRUCache con capacità configurabile. Requisiti: deve avere i metodi get(key) e put(key, value); get deve restituire -1 se la chiave non esiste; ogni get o put deve aggiornare l'ordine di utilizzo; quando la cache supera la capacità deve eliminare l'elemento usato meno recentemente; get e put devono avere complessità O(1); non usare functools.lru_cache; aggiungi alla fine un piccolo test eseguibile. Prima spiegami in massimo 5 righe la strategia scelta, poi scrivi il codice completo.`

Maximum generated tokens: **384**.

System message remains the REALGEN system message:
`You are a helpful assistant. Answer clearly and directly.`

## Allowed implementation delta

Create one new tracked runner:
`scripts/loom_8b_practical_bakeoff_runner_001.py`

It may:
- reuse/copy the minimal REALGEN M1 driver and telemetry helpers;
- load the same local 8B artifact;
- run only the frozen prompt above;
- stream visible text to stdout using tokenizer-compatible detokenization/generation behavior;
- persist a JSON summary under `results-local/research/8b-practical-bakeoff-runner-001/<timestamp>/`.

It must NOT:
- download/convert/requantize a model;
- modify the model/runtime/quantization/KV/template/cleanup policy;
- inject S1_R8 or any M5/oracle mechanism;
- use Ollama/llama.cpp;
- add skills, memory, tools, RAG, system-prompt optimization or behavioral edits;
- change the frozen prompt or 384-token budget;
- modify any existing production/research runner.

## Required gates before generation

1. exact Python prefix and package versions;
2. local model exists and main weight SHA matches;
3. config quantization is 3-bit/group64;
4. tokenizer EOS/template semantics available;
5. host telemetry readable;
6. no network/model acquisition action;
7. source diff contains only the new runner.

Historical >=60% free-memory launch gate is not imposed on this user-facing comparison because current practical use is itself under study. Abort only on unreadable telemetry or critical memory pressure / swap >5600 MB. Record exact pre/post resource state.

## Required outputs

- full generated text;
- completion reason: EOS or 384-token limit;
- output token count;
- TTFT;
- prompt/prefill wall and rate;
- generation wall and tok/s;
- end-to-end wall and output tok/s;
- p50/p95 token-forward latency;
- cleanup count/wall;
- MLX active/peak/cache memory;
- system free-memory percentage and swap before/after/observed peak;
- model/runtime provenance;
- evidence path.

## Classification

`LOOM_8B_BAKEOFF_RUNNER_PASS` only if the exact frozen model/runtime executes the prompt and evidence is complete.

A 384-token length stop is still a valid runner PASS but the task is separately scored `INCOMPLETE` if the requested implementation/test is visibly unfinished.

Any runtime/provenance mismatch or hidden fallback is FAIL CLOSED.

No Git commit/push by Pi.
