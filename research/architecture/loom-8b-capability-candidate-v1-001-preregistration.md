# LOOM 8B Capability Candidate v1 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Measure whether the two accepted system-layer mechanisms from `LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_001` materially close the practical gap between raw LOOM 8B BALANCED and LOOM 30B DEEP on fresh tasks.

Accepted mechanisms only:
- B: reusable strict-output protocol;
- C: reusable verification-first protocol.

Rejected calculator branch A is explicitly excluded.

This checkpoint does **not** test automatic capability selection. The harness is given a frozen task capability label (`STRICT_OUTPUT` or `VERIFICATION_FIRST`) so capability-effect validation is separated from later dispatcher/router validation.

## Frozen systems

### RAW 8B

- model `mlx-community/Qwen3-8B-3bit@619ded3`;
- local artifact `results-local/mlx/models/Qwen3-8B-3bit`;
- main weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF;
- Qwen3 chat template.

### CAPABILITY 8B

Identical model/runtime to RAW 8B. The only treatment is the already-accepted frozen protocol corresponding to the task's preregistered capability label.

Pi must recover the **exact treatment protocol strings/semantics used in the successful funnel** from:
- `research/architecture/loom-8b-capability-amplification-funnel-001-preregistration.md`;
- `scripts/loom_8b_capability_amplification_funnel_001.py` if needed for exact bytes.

No wording improvements are allowed after this preregistration.

### 30B DEEP comparator

Use canonical production runtime:
- production commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`;
- runtime core SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- interactive/runtime SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`;
- expert backend SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`;
- exact Q4/top-8 packed expert path;
- greedy generation;
- fresh state per task.

30B receives the shared base system message and user prompt only; it does not receive the 8B capability treatment. This is a practical-system comparator, not a one-factor model comparison.

## Shared base system message

EXACTLY:
`You are a helpful assistant. Answer clearly and directly.`

## Fresh task set

### T01 — STRICT_OUTPUT / exact JSON object

User prompt EXACTLY:
`Restituisci ESATTAMENTE un oggetto JSON valido, senza markdown e senza testo extra. Chiavi nell'ordine: service, replicas, healthy, regions. service=loom-api; replicas=3; healthy=yes; regions=rome,milan. healthy deve essere booleano e regions un array di stringhe.`

Maximum generated tokens: `90`.

Expected semantic object:
`{"service":"loom-api","replicas":3,"healthy":true,"regions":["rome","milan"]}`

Instruction PASS requires valid JSON with no surrounding markdown/prose and keys in required order.

### T02 — STRICT_OUTPUT / exact CSV row

User prompt EXACTLY:
`Rispondi con UNA SOLA riga CSV, senza intestazione, senza markdown e senza spiegazioni. Campi nell'ordine: model, tier, tok_s, enabled. Valori: Qwen3-8B, balanced, 13.2, yes. enabled deve essere scritto true.`

Maximum generated tokens: `60`.

Expected exact non-whitespace semantic row:
`Qwen3-8B,balanced,13.2,true`

Spaces surrounding commas are instruction failure. Quoting fields unnecessarily is allowed only if parsed CSV values are exact and no extra output exists; exact expected row is preferred.

### T03 — VERIFICATION_FIRST / extraction escalation

User prompt EXACTLY:
`Un estrattore veloce legge una fattura e produce totale=249.90, valuta=EUR, partita_iva=vuoto. Il contratto richiede tutti e tre i campi e un controllo deterministico verifica presenza e formato. Dammi una regola concreta per decidere se accettare il risultato o passare al metodo lento. Massimo 4 righe.`

Maximum generated tokens: `110`.

Scoring core:
- explicitly run/use deterministic validation of required fields/format;
- current output fails because `partita_iva` is missing/empty;
- therefore escalate to slow method;
- no prompt-length/generic-complexity heuristic.

### T04 — VERIFICATION_FIRST / patch deployment escalation

User prompt EXACTLY:
`Un modello veloce propone una patch. Hai test unitari, type-check e un test di regressione che riproduce il bug. Definisci una regola di escalation: quando accetti la patch del modello veloce e quando chiedi al modello lento. Massimo 5 righe.`

Maximum generated tokens: `120`.

Scoring core:
- run deterministic checks first;
- accept fast-model patch if required checks pass;
- escalate to slow model if one or more required checks fail or result cannot be validated;
- do not escalate merely because prompt/code is long or task seems hard.

## Execution conditions

Each of the four tasks runs under all three conditions:
1. RAW 8B;
2. CAPABILITY 8B;
3. 30B DEEP.

Fresh model/conversation state per condition.

Counterbalanced frozen order:
- T01: RAW8 -> CAP8 -> 30B
- T02: 30B -> CAP8 -> RAW8
- T03: RAW8 -> 30B -> CAP8
- T04: CAP8 -> 30B -> RAW8

Only one model may be loaded in a child process at a time. Do not keep 8B and 30B resident simultaneously.

## Scoring

For each condition/task record:
- `CORRECT`, `PARTIAL`, or `INCORRECT`;
- instruction following `PASS/FAIL`;
- completion `COMPLETE/INCOMPLETE`;
- concise frozen-rubric reason.

Descriptive utility:
- CORRECT + instruction PASS + COMPLETE = 2;
- PARTIAL or correct core with material instruction/completion defect = 1;
- INCORRECT = 0.

Maximum `8` points per condition.

No rubric changes after outputs are visible. Mechanical parsing reconciliation without inference is permitted only when it applies the frozen rubric unchanged and retained raw output is immutable.

## Candidate promotion gate

`LOOM_8B_CAPABILITY_CANDIDATE_V1_GO` only if CAPABILITY 8B simultaneously:
1. scores at least `6/8` utility;
2. improves RAW 8B by at least `+2` utility points;
3. has zero per-task utility regressions versus RAW 8B;
4. has at least `3/4` tasks rated CORRECT;
5. preserves valid runtime/provenance/evidence.

Otherwise classify `LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO` while retaining results.

30B comparison does not control GO/NO_GO. Report separately:
- CAP8 utility gap versus 30B;
- task categories where CAP8 matches/beats 30B;
- categories where 30B still materially wins;
- additional 30B waiting cost.

## Performance evidence

For every condition/task where observable:
- output text/token count/stop reason;
- TTFT;
- generation wall + tok/s;
- end-to-end wall + output tok/s;
- p50/p95 token-forward latency where available;
- runtime-appropriate active/peak memory;
- system memory/swap before/after/peak/min;
- cleanup telemetry where applicable.

Aggregate per condition:
- utility /8;
- CORRECT/PARTIAL/INCORRECT;
- total task wall;
- median TTFT;
- pooled generation throughput when meaningful;
- peak memory/swap;
- time per correct task.

## Forbidden

No:
- calculator branch A;
- automatic capability/router classification;
- 4B;
- model downloads/conversion/requantization;
- runtime optimization;
- protocol wording changes;
- retry/self-repair;
- tools;
- memory/RAG;
- fine-tuning;
- Heretic edits;
- provider/UI integration;
- router thresholds.

## Harness

Create exactly:
`scripts/loom_8b_capability_candidate_v1_001.py`

No existing runtime/runner changes.

Persist evidence under:
`results-local/research/8b-capability-candidate-v1-001/<timestamp>/`

No Git commit/push.

## Interpretation boundary

This checkpoint validates the value of a capability library when applicability is already known. It does not establish that LOOM can automatically recognize when to activate a capability. Automatic dispatcher/selector validation must be a separate checkpoint after candidate review.
