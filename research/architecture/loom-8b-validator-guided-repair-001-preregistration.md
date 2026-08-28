# LOOM 8B Validator-Guided Repair 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Test one new factor before DEEP escalation: can the validated 8B cheaply repair its own mechanically verifiable failures when given the exact deterministic validator report?

Frozen graph:
`RAW8 -> validator -> PASS accept; FAIL -> existing safe fence-only repair if eligible -> revalidate -> residual FAIL -> one validator-guided 8B repair -> revalidate`.

No 30B inference. This isolates guided repair value and avoids spending DEEP latency before the cheap repair stage is justified.

## Frozen runtime

Use exact BALANCED runtime:
- `mlx-community/Qwen3-8B-3bit@619ded3`;
- weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; transformers 5.12.1;
- Apple M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF;
- baseline system exactly `You are a helpful assistant. Answer clearly and directly.`

Fresh process/state per model call.

## Frozen validator and safe repair

Reuse Output Validator v0 definitions exactly.
Validator kind/spec is task metadata; automatic validator selection remains out of scope.

Before guided model repair, retain the already-validated safe repair stage exactly: remove one complete outer Markdown code fence only when interior payload bytes remain unchanged and the same validator passes afterward. No other deterministic repair.

## Guided repair treatment

Only residual validator FAIL after ineligible/failed safe fence repair triggers one additional 8B call.

Repair system message EXACTLY:
`You repair an answer using deterministic validation feedback. Return only a complete corrected answer to the original request. Satisfy every validator failure exactly. Do not explain the repair. Do not mention the validator.`

Repair user message template EXACTLY:
`ORIGINAL REQUEST:\n<original user prompt>\n\nFAILED ANSWER:\n<raw 8B answer>\n\nVALIDATOR FAILURES:\n<ordered frozen validator failure report>`

Rules:
- one guided repair call maximum per task;
- same max-output cap as the task's RAW8 call;
- no retry after repair;
- repair receives only original prompt, raw failed output and deterministic validator report;
- no scorer label, ground-truth quality label, hidden expected answer, test feedback beyond the validator report, tool/RAG/memory or 30B.

Validator failure reports must be generated deterministically from the frozen validator/spec. Preserve exact ordered check IDs/messages in evidence.

## Fresh eight-task set

### T01 — V_JSON_OBJECT
`Restituisci solo JSON valido, senza Markdown o testo extra. Chiavi nell'ordine: service, timeout_ms, enabled. service=api; timeout_ms=2500; enabled=yes. timeout_ms numero intero, enabled booleano.`
Expected semantic payload: `{"service":"api","timeout_ms":2500,"enabled":true}`.
Max output: 80.

### T02 — V_JSON_ARRAY
`Restituisci solo un array JSON valido senza Markdown. Tre oggetti nell'ordine dato, chiavi id e active: id=x active=yes; id=y active=no; id=z active=yes. active deve essere booleano.`
Expected semantic payload: `[{"id":"x","active":true},{"id":"y","active":false},{"id":"z","active":true}]`.
Max output: 100.

### T03 — V_CSV
`Restituisci solo CSV senza fence o spiegazioni. Intestazione esatta: worker,state. Righe nell'ordine: w1=ready; w2=busy; w3=offline.`
Expected exact header/rows/order.
Max output: 80.

### T04 — V_KV
`Restituisci solo tre righe chiave=valore nell'ordine: engine,threads,enabled. engine=mlx; threads=4; enabled=no. threads deve essere intero ed enabled deve essere booleano true/false.`
Expected exact contract ending `enabled=false`.
Max output: 80.

### T05 — V_JSON_OBJECT
`Restituisci solo JSON valido, nessun testo aggiuntivo. Chiavi nell'ordine: tier, context, local. tier=balanced; context=6144; local=no. context numero intero, local booleano.`
Expected semantic payload: `{"tier":"balanced","context":6144,"local":false}`.
Max output: 80.

### T06 — V_VERIFY_RULE
`Un sistema genera query SQL con un metodo veloce e può usare un metodo lento. In massimo 4 righe definisci una regola: prova prima il metodo veloce, controlla sintassi e compatibilità con lo schema, passa al metodo lento solo se un controllo fallisce o resta incertezza materiale.`
Required: cheap-first; syntax/schema checks; escalation only on failed checks/material uncertainty. Max output: 120.

### T07 — V_VERIFY_RULE
`Un agente propone una patch TypeScript con il modello veloce. In massimo 4 righe definisci quando accettarla e quando usare il modello lento usando test automatici e type-check, non la lunghezza del prompt.`
Required: fast first; tests/type-check; accept on passed checks; escalate on failed checks/material uncertainty; no prompt-length heuristic. Max output: 120.

### T08 — V_VERIFY_RULE
`Un estrattore veloce legge ricevute e un metodo lento è più accurato. In massimo 4 righe definisci una regola di escalation basata su campi obbligatori, tipi e coerenza dei totali.`
Required: fast first; required-fields/types/totals checks; escalation on failed checks/material uncertainty. Max output: 120.

## Scoring

Independent frozen ground-truth scorer records CORRECT/PARTIAL/INCORRECT for RAW8 and final accepted/unresolved answer.

Acceptance stages:
- `8B_PASS`;
- `SAFE_REPAIR`;
- `GUIDED_8B_REPAIR`;
- `UNRESOLVED`.

A final answer may be accepted only if the frozen validator returns PASS. Any validator FAIL after the one guided repair remains UNRESOLVED; do not expose it as accepted.

## Required evidence

Create exactly:
`scripts/loom_8b_validator_guided_repair_001.py`

Persist under:
`results-local/research/8b-validator-guided-repair-001/<timestamp>/`

Before model inference:
- run all frozen synthetic validator fixtures;
- run frozen fence-repair fixtures;
- verify model/runtime provenance;
- verify no network/download/package/model mutation.

Per task persist:
- exact prompt/spec/max tokens;
- RAW8 output/metrics/quality;
- validator decision and exact ordered failure report;
- safe-repair eligibility/transformation/revalidation;
- guided-repair trigger yes/no;
- exact repair system/user messages;
- repair output/metrics/revalidation/quality;
- final source and final quality;
- telemetry.

Aggregate:
- RAW8 and final C/P/I;
- false acceptance count;
- safe-repair attempts/successes;
- guided-repair calls/successes;
- unresolved count;
- initial 8B wall + guided-repair wall + total wall;
- validator/repair overhead;
- time per final-CORRECT task.

## Frozen GO gate

`LOOM_8B_VALIDATOR_GUIDED_REPAIR_GO` only if all are true:
1. all 8 RAW8 and every triggered repair call valid;
2. zero false acceptance at any stage;
3. safe deterministic repair remains exact frozen fence-only transformation;
4. final CORRECT >= `6/8`;
5. final CORRECT >= RAW8 CORRECT + `2`;
6. guided 8B repair converts at least `2` residual FAIL tasks to validator PASS + ground-truth CORRECT;
7. no guided repair call occurs after initial PASS/successful safe repair;
8. validator and deterministic repair p95 <5 ms;
9. exact repair prompt/template unchanged;
10. zero network/download/package/model/runtime mutation.

Otherwise `LOOM_8B_VALIDATOR_GUIDED_REPAIR_NO_GO`.
Mechanical/instrumentation invalidity: `LOOM_8B_VALIDATOR_GUIDED_REPAIR_MECHANICAL_NO_GO`.

## Boundaries

No 30B, 4B, selector, capability protocol injection before RAW8, calculator, memory/RAG, tools, fine-tuning, Heretic, provider/UI or production integration.

GO would justify inserting one cheap validator-guided 8B repair before DEEP escalation on mechanically verifiable tasks. It would not solve open-ended semantic uncertainty or automatic validator selection.
