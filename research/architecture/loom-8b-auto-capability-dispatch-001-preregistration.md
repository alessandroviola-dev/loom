# LOOM 8B Auto Capability Dispatch 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Test the first end-to-end capability-dispatch graph:

`user prompt -> frozen selector v0 -> NORMAL / STRICT_OUTPUT / VERIFY_FIRST -> LOOM 8B`

against RAW 8B on fresh mixed tasks.

This checkpoint measures whether the already validated deterministic selector can apply the two already accepted capabilities conditionally without regressions or material routing overhead.

It does **not** test 30B escalation, calculator use, memory/RAG, Heretic, provider/UI or production routing.

## Frozen 8B runtime

Use exactly:
- `mlx-community/Qwen3-8B-3bit@619ded3`;
- weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- Apple M1 built-in MLX `qmv_fast` path;
- BF16 KV;
- greedy generation;
- thinking OFF;
- fresh model/conversation state per condition.

Baseline system message EXACTLY:
`You are a helpful assistant. Answer clearly and directly.`

## Frozen selector

Reuse the exact deterministic rules from:
`research/architecture/loom-capability-selector-v0-001-preregistration.md`

No rule changes are allowed.

Labels:
- `NORMAL`;
- `STRICT_OUTPUT`;
- `VERIFY_FIRST`.

The selector runs only on the user prompt before inference.

## Frozen capability treatments

### NORMAL
Use baseline system message only.

### STRICT_OUTPUT
System message EXACTLY:
`You are a helpful assistant. Answer clearly and directly. LOOM strict-output protocol: when the user requests an exact machine-readable format, output ONLY that format: no Markdown fences, no prose, no labels, no comments. Preserve requested key order and data types exactly.`

### VERIFY_FIRST
System message EXACTLY:
`You are a helpful assistant. Answer clearly and directly. LOOM verification-first protocol: start with the cheapest capable method; define observable success criteria before accepting its output; use deterministic or task-specific checks when available; escalate to the more capable method only when a required check fails or material uncertainty remains. Never choose only from prompt length or vague difficulty labels.`

These strings come from the previously accepted funnel and must not be rewritten or expanded.

## Conditions

Each task is run twice with fresh state:
1. `RAW8`: baseline system message only;
2. `AUTO8`: frozen selector v0 chooses the system condition automatically.

No output from one condition may be shown to the other.

## Frozen fresh mixed task set

### N01 — expected NORMAL
User prompt EXACTLY:
`Spiegami in massimo 3 righe la differenza tra RAM e memoria virtuale, senza usare esempi.`
Max generated tokens: `90`.
Scoring core: correct concise distinction between physical RAM and disk-backed/virtual memory; <=3 non-empty answer lines.

### S01 — expected STRICT_OUTPUT
User prompt EXACTLY:
`Restituisci solo JSON valido, senza testo prima o dopo. Chiavi nell'ordine: app, port, debug. app=loom; port=8080; debug=no. port deve essere numero e debug booleano.`
Max generated tokens: `70`.
Expected semantic JSON: `{"app":"loom","port":8080,"debug":false}` with exact key order and no fence/prose.

### V01 — expected VERIFY_FIRST
User prompt EXACTLY:
`Un sistema genera query SQL con un modello veloce e può usare un modello lento. Definisci quando accettare la query e quando passare al modello lento usando validazione sintattica e schema come controlli. Massimo 4 righe.`
Max generated tokens: `110`.
Scoring core: fast/cheap first, concrete syntax/schema validation, escalation when checks fail or material uncertainty remains.

### N02 — expected NORMAL
User prompt EXACTLY:
`Correggi il bug in una riga di Python e mostra solo la riga corretta: values = [1,2,3]; print(values[3])`
Max generated tokens: `60`.
Expected core: valid indexing of existing element; accepted answer `print(values[2])` or equivalent single corrected executable line; no unrelated explanation.

### S02 — expected STRICT_OUTPUT
User prompt EXACTLY:
`Converti esattamente questi dati in CSV senza spiegazioni. Intestazione obbligatoria: name,status. Record: api=up; worker=down.`
Max generated tokens: `70`.
Expected exact logical CSV rows: header `name,status`, then `api,up`, `worker,down`; no fence/prose.

### V02 — expected VERIFY_FIRST
User prompt EXACTLY:
`Un estrattore veloce legge numero fattura, imponibile e IVA; esiste un metodo lento più accurato. Dammi una regola per accettare o fare escalation basata su controlli dei campi e coerenza dei totali. Massimo 4 righe.`
Max generated tokens: `110`.
Scoring core: cheap/fast first; required fields/types and total consistency validation; escalate if validation fails or uncertainty remains.

### N03 — expected NORMAL adversarial
User prompt EXACTLY:
`Descrivi in massimo 4 righe una strategia di fallback per un servizio web. Non devi definire criteri di verifica o decidere quando usare un modello più capace.`
Max generated tokens: `100`.
Scoring core: coherent availability/redundancy fallback strategy; follows <=4-line constraint. The word fallback alone must not trigger VERIFY_FIRST.

### S03 — expected STRICT_OUTPUT
User prompt EXACTLY:
`Genera esattamente YAML valido con i campi service, replicas, enabled e restituisci solo YAML senza spiegazioni. service=router; replicas=2; enabled=yes. replicas è numero ed enabled booleano.`
Max generated tokens: `80`.
Expected semantic YAML with key order `service, replicas, enabled`, values `router`, numeric `2`, boolean true; no fence/prose.

### V03 — expected VERIFY_FIRST
User prompt EXACTLY:
`Un agente produce una patch con un modello veloce e può usare un modello più capace. Proponi una regola concreta per accettare la patch o fare escalation usando test di regressione e type-check. Massimo 4 righe.`
Max generated tokens: `110`.
Scoring core: fast patch first; regression tests/type-check as observable checks; escalate only on failed checks or unresolved/material uncertainty.

## Frozen execution order

Run in this exact condition order, fresh state each time:
1. N01 RAW8
2. N01 AUTO8
3. S01 AUTO8
4. S01 RAW8
5. V01 RAW8
6. V01 AUTO8
7. N02 AUTO8
8. N02 RAW8
9. S02 RAW8
10. S02 AUTO8
11. V02 AUTO8
12. V02 RAW8
13. N03 RAW8
14. N03 AUTO8
15. S03 AUTO8
16. S03 RAW8
17. V03 RAW8
18. V03 AUTO8

Do not manipulate swap or host state between conditions except normal process cleanup already used by the validated 8B harness pattern.

## Per-task scoring

For RAW8 and AUTO8 independently record:
- `CORRECT`, `PARTIAL`, or `INCORRECT`;
- instruction following `PASS/FAIL`;
- completion `COMPLETE/INCOMPLETE`.

Utility:
- CORRECT + instruction PASS + COMPLETE = `2`;
- PARTIAL, or correct core with a material instruction/completion defect = `1`;
- INCORRECT = `0`.

No scoring criteria may change after outputs are visible.

## Required selector evidence

For each AUTO8 task persist:
- expected label;
- predicted label;
- matched frozen cues/rule;
- selector wall microseconds;
- selected system message identity.

## Required runtime evidence

For every inference persist where observable:
- exact system/user messages;
- rendered prompt/token count;
- output text/token count;
- stop reason;
- TTFT;
- generation wall and tok/s;
- end-to-end wall and output tok/s;
- p50/p95 token-forward latency where available;
- MLX active/peak/cache memory;
- system memory/swap before/after/peak;
- cleanup count/wall where applicable;
- exact runtime/model provenance.

Aggregate RAW8 and AUTO8 separately:
- utility /18;
- CORRECT/PARTIAL/INCORRECT counts;
- instruction failures;
- total task wall;
- median TTFT;
- pooled generation tok/s;
- peak MLX/swap.

## Frozen GO gate

Classify **`LOOM_8B_AUTO_CAPABILITY_DISPATCH_GO`** only if all are true:
1. all 18 inference conditions execute with valid provenance/evidence;
2. selector expected-label accuracy on these 9 fresh prompts >= `8/9`;
3. expected-NORMAL false activations = `0/3`;
4. AUTO8 utility >= RAW8 utility + `2`;
5. zero per-task utility regressions (`AUTO8 >= RAW8` for every task);
6. AUTO8 has at least `7/9` CORRECT tasks;
7. selector implementation/rules and accepted capability strings are unchanged.

Otherwise classify **`LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO`**.

Do not relax the gate after observing results.

## Files / evidence

Create exactly one new experimental harness:
`scripts/loom_8b_auto_capability_dispatch_001.py`

Persist under:
`results-local/research/8b-auto-capability-dispatch-001/<timestamp>/`

No Git commit/push by Pi.

## Forbidden

No:
- 30B inference;
- 4B;
- calculator;
- downloads/network;
- model/runtime changes;
- selector tuning;
- capability wording changes;
- retries/self-repair;
- memory/RAG;
- other tools;
- fine-tuning;
- Heretic;
- provider/UI;
- production integration;
- 30B escalation thresholds.

## Interpretation boundary

GO means the conditional capability layer is strong enough to justify the next separate experiment: output validation plus selective 30B escalation.

NO_GO means retain the proven selector/capabilities as research evidence but do not integrate the end-to-end AUTO8 graph without a new independently preregistered diagnosis.
