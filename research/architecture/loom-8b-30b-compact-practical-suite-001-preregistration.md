# LOOM 8B vs 30B Compact Practical Suite 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Measure whether LOOM 30B DEEP provides enough practical quality gain over LOOM 8B BALANCED to justify its much higher latency on representative tasks. This is a practical system comparison, not a one-factor parameter-count experiment.

The 4B FAST legacy llama.cpp path is parked for this phase after `LOOM_4B_FINAL_ATTEMPT_ABORTED` and is excluded from this suite.

## Frozen systems

### LOOM 8B BALANCED

Use the already validated local Qwen3-8B 3-bit/group64 Direct MLX condition:
- model: `mlx-community/Qwen3-8B-3bit@619ded3`;
- local artifact: `results-local/mlx/models/Qwen3-8B-3bit`;
- main weight SHA: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF;
- Qwen3 chat template;
- no S1_R8/oracle/speculation;
- preserve the existing LOOM cleanup policy unless a task ends before a cleanup boundary.

### LOOM 30B DEEP

Use the canonical Git-persisted Qwen3-30B-A3B Q4 interactive/runtime core:
- production runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`;
- `scripts/loom_30b_runtime_core_v1_001.py` SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`;
- canonical expert backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`;
- exact Q4/top-8 packed expert path;
- deterministic greedy generation;
- existing incremental state/runtime semantics;
- no new speed mechanism in this suite.

## Experimental source scope

Create exactly one new experimental harness:

`scripts/loom_8b_30b_compact_practical_suite_001.py`

No existing tracked runtime/runner may be modified.

The harness must support isolated child execution so only one model is loaded at a time. A permitted design is for the parent process to invoke the same script in child mode with explicit `--model {8b,30b}` and `--task Txx` arguments. Model state must not be shared across tasks/models. The parent may orchestrate the frozen AB/BA order and aggregate evidence.

Do not create additional helper scripts unless a deterministic mechanical limitation makes the single-file design impossible; in that case stop `INCOMPLETE` before model execution rather than broadening source scope.

## Shared boundary

No skills, tools, memory/RAG, Heretic editing, prompt optimization, self-repair, retries, agent loops or verifier feedback. We want raw tier behavior before intelligence amplification.

System message for every task EXACTLY:
`You are a helpful assistant. Answer clearly and directly.`

Each model receives each task independently with a fresh conversation/state. No output from one model/task is shown to another.

## Task set

The suite intentionally requires concise outputs so 30B latency is spent on reasoning rather than verbosity.

### T01 — deterministic arithmetic/reasoning

User prompt EXACTLY:
`Un server riceve 1375 richieste al minuto. Ogni worker gestisce al massimo 48 richieste al minuto. Devi mantenere almeno il 20% di capacità libera rispetto al traffico previsto. Dimmi solo: numero minimo di worker e calcolo essenziale in una riga.`

Maximum generated tokens: `80`.

Expected core answer: capacity target `1650 req/min`; minimum workers `ceil(1650/48)=35`.

### T02 — debugging

User prompt EXACTLY:
`Trova il bug e proponi la correzione minima. Rispondi in massimo 8 righe. Codice Python: def remove_user(users, user_id):\n    for i, user in enumerate(users):\n        if user["id"] == user_id:\n            users.pop(i)\n    return users\nIl requisito è rimuovere tutti gli elementi con quell'id, anche se sono consecutivi.`

Maximum generated tokens: `140`.

Scoring core: must identify mutation-during-forward-iteration / skipped consecutive matches and propose a correct minimal solution (e.g. filtering/list comprehension, reverse iteration, or index-safe loop).

### T03 — instruction following / structured transform

User prompt EXACTLY:
`Converti ESATTAMENTE questi dati in JSON valido, senza testo prima o dopo. Chiavi obbligatorie nell'ordine: project, priority, blocked, tags. project=LOOM; priority=high; blocked=no; tags=mlx,router,local-ai. blocked deve essere booleano e tags un array di stringhe.`

Maximum generated tokens: `80`.

Expected exact semantic object:
`{"project":"LOOM","priority":"high","blocked":false,"tags":["mlx","router","local-ai"]}`
Formatting whitespace is irrelevant; extra prose is a failure of the strict-output requirement.

### T04 — supplied-context reasoning

User prompt EXACTLY:
`Usa solo questi fatti: A) il runtime X produce 20 token/s e usa 2.5 GB; B) il runtime Y produce 8 token/s e usa 4.0 GB; C) il task richiede circa 160 token; D) entrambi risolvono correttamente il task. Quale runtime sceglieresti per questo task e perché? Rispondi in massimo 3 righe e non aggiungere informazioni esterne.`

Maximum generated tokens: `100`.

Expected core: X, because under equal correctness it is faster and lower-memory; ~8 s vs ~20 s for 160 tokens if timing is computed.

### T05 — concise software design judgement

User prompt EXACTLY:
`Stai progettando un'app locale che deve scegliere tra un modello veloce e uno lento ma più capace. Dammi una regola di escalation concreta basata su verifica dell'output, non sulla sola lunghezza del prompt. Massimo 5 righe.`

Maximum generated tokens: `140`.

Scoring core: must propose a concrete verification-driven route/escalation rule: try cheaper model, validate against task-specific/deterministic checks or confidence evidence, escalate on failure/uncertainty. Generic “use the big model for hard prompts” is insufficient.

## Execution order

To reduce systematic host-state/order bias, use an AB/BA task grouping without cross-model shared state:
- T01: 8B then 30B
- T02: 30B then 8B
- T03: 8B then 30B
- T04: 30B then 8B
- T05: 8B then 30B

Host readiness and provenance must be checked before each model child launch. Do not purge/manipulate swap to make a gate pass.

## Task scoring

For each model/task persist:
- `CORRECT`, `PARTIAL`, or `INCORRECT`;
- instruction-following `PASS/FAIL`;
- completion `COMPLETE/INCOMPLETE`;
- concise reason tied to frozen expected criteria.

Numerical utility score for descriptive aggregation only:
- CORRECT + instruction PASS + COMPLETE = 2 points;
- PARTIAL or correct core with material instruction/completion defect = 1 point;
- INCORRECT = 0 points.

Maximum = 10 points/model.

Do not alter scoring criteria after outputs are visible.

## Required performance evidence

For every task/model where observable:
- rendered prompt/token count;
- output text and output token count;
- stop reason;
- TTFT;
- generation wall + tok/s;
- end-to-end wall + output tok/s;
- p50/p95 token-forward latency where runtime exposes it;
- peak/active memory appropriate to runtime;
- system memory/swap before/after/peak/min;
- cleanup wall/count where applicable.

Also aggregate per model:
- task utility score /10;
- number CORRECT/PARTIAL/INCORRECT;
- total task wall;
- median TTFT;
- pooled generation tok/s when meaningful;
- time per correct task;
- peak memory/swap.

Primary practical decision quantity:
**quality/correctness gain of 30B versus additional waiting time and resource cost.**

## Evidence root

Persist under:
`results-local/research/8b-30b-compact-practical-suite-001/<timestamp>/`

Preserve one child evidence record per model/task plus aggregate summary and exact source SHA/diff.

## Interpretation

This suite may support an initial product rule such as “8B default, 30B escalation for categories where it produces a material correctness gain,” but five tasks are not enough to claim general model intelligence rankings.

Do not infer parameter-count causality because model families/quantization/runtime paths differ.

If 8B matches or beats 30B on most/all tasks while being dramatically faster, use that as evidence to make 8B the primary/default tier and reserve 30B only for separately demonstrated hard-task advantages.

If 30B materially beats 8B on specific tasks, preserve those task features as candidate routing signals for `LOOM AUTO`.

## Forbidden

No:
- 4B reactivation;
- model downloads/conversions/requantization;
- runtime optimization;
- prompt changes;
- retries/self-repair;
- tool use;
- skills/RAG/memory;
- Heretic edits;
- speculative decoding;
- UI/provider integration;
- router implementation before result review.

## Result classification

`LOOM_8B_30B_COMPACT_SUITE_PASS` only if all ten frozen model-task conditions execute with valid provenance and evidence.

If one model/task cannot execute for a mechanical reason, classify `LOOM_8B_30B_COMPACT_SUITE_INCOMPLETE` and preserve completed conditions; do not silently substitute or rerun under changed conditions.
