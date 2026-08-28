# LOOM Validator-Guided Selective Rescue 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Test the first bounded validator-first rescue graph on fresh mechanically verifiable tasks:

`RAW8 -> validator -> PASS accept; FAIL -> safe deterministic format repair when eligible -> revalidate -> residual FAIL -> one 30B DEEP call -> revalidate`.

This checkpoint measures whether LOOM can avoid unnecessary 30B calls while improving final correctness. It does not address open-ended semantic uncertainty.

## Frozen runtimes

### 8B BALANCED
- `mlx-community/Qwen3-8B-3bit@619ded3`
- weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit/group64
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; transformers 5.12.1
- M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF
- baseline system: `You are a helpful assistant. Answer clearly and directly.`

### 30B DEEP
Use the exact canonical production runtime/provenance already frozen in AGENTS.md. No runtime/model modification.

Only one model may be resident at a time.

## Fresh task set

Eight fresh mechanically verifiable tasks, not used in prior capability/validator suites.

### T01 — V_JSON_OBJECT
`Restituisci solo JSON valido, senza Markdown o testo aggiuntivo. Chiavi nell'ordine: host, port, tls. Valori: host=localhost; port=9000; tls=yes. port deve essere numero e tls booleano.`
Expected semantic payload: `{"host":"localhost","port":9000,"tls":true}`.
Max output 80.

### T02 — V_JSON_ARRAY
`Restituisci solo un array JSON valido, senza Markdown: tre oggetti nell'ordine dato, chiavi name e enabled. alpha=yes; beta=no; gamma=yes. enabled deve essere booleano.`
Expected: `[{"name":"alpha","enabled":true},{"name":"beta","enabled":false},{"name":"gamma","enabled":true}]`.
Max output 100.

### T03 — V_CSV
`Restituisci solo CSV, nessun fence o spiegazione. Intestazione esatta: node,status. Righe: edge-a=ready; edge-b=failed; edge-c=ready.`
Expected exact rows/columns and order.
Max output 80.

### T04 — V_KV
`Restituisci solo tre righe chiave=valore in questo ordine: service,workers,enabled. service=loom; workers=3; enabled=no. workers deve essere intero ed enabled booleano true/false.`
Expected exact contract with `enabled=false`.
Max output 80.

### T05 — V_JSON_OBJECT
`Restituisci solo JSON valido e nessun testo extra. Chiavi nell'ordine: model, context, local. model=balanced; context=8192; local=yes. context numero, local booleano.`
Expected semantic payload with correct types/order.
Max output 80.

### T06 — V_VERIFY_RULE
`Un sistema genera una migrazione SQL con il metodo veloce e può usare il modello lento. In massimo 4 righe dai una regola operativa: prova prima il metodo veloce, verifica sintassi e compatibilità con lo schema, passa al modello lento solo se una verifica fallisce o resta incertezza materiale.`
Required components: cheap-first; syntax/schema validation; escalation only on failed check/material uncertainty. Max 120.

### T07 — V_VERIFY_RULE
`Un agente produce una patch Python col modello veloce. In massimo 4 righe definisci quando accettarla e quando usare il modello lento usando test automatici e type-check, non la lunghezza del prompt.`
Required: fast first; tests/type-check; accept on passed checks; escalate on failed checks/material uncertainty; no prompt-length heuristic. Max 120.

### T08 — V_VERIFY_RULE
`Un estrattore veloce legge ordini e un metodo lento è più accurato. In massimo 4 righe definisci una regola di escalation basata su campi obbligatori, tipi e coerenza dei totali.`
Required: fast first; listed deterministic checks; escalation on failed checks/material uncertainty. Max 120.

## Frozen validation

Reuse Output Validator v0 definitions/semantics exactly for the six validator kinds already accepted. This checkpoint uses only V_JSON_OBJECT, V_JSON_ARRAY, V_CSV, V_KV and V_VERIFY_RULE.

Validator kind/spec is task metadata; automatic validator selection is outside scope.

Ground-truth scorer independently records CORRECT/PARTIAL/INCORRECT so false-PASS can be measured.

## Safe deterministic repair v0

Repair is allowed only after an 8B `FAIL`, and only if **all** are true:
1. failure is attributable solely to one outer Markdown fenced-code wrapper around the complete payload;
2. removing exactly the opening/closing fence plus immediately adjacent fence newlines leaves the interior payload bytes unchanged;
3. no token/value/type/order/content coercion is performed;
4. the repaired payload passes the same frozen validator.

No yes/no coercion, JSON repair, CSV repair, key reordering, truncation repair, prose deletion or semantic rewriting.

If repair succeeds, accept repaired output and do not call 30B.
If ineligible or repair still FAILs, call 30B exactly once on the **original user prompt** with canonical DEEP baseline semantics.

## 30B escalation

- only residual FAIL after validator/eligible repair;
- one call maximum per task;
- same user prompt and max-output cap as 8B;
- no capability prompt, retry, self-repair, tool, RAG or context from the failed 8B answer;
- validate 30B response with the same validator;
- if 30B still FAILs, task remains unresolved; do not retry.

No 30B call is permitted for an 8B PASS or successful deterministic repair.

## Required evidence

Create exactly:
`scripts/loom_validator_guided_selective_rescue_001.py`

Persist under:
`results-local/research/validator-guided-selective-rescue-001/<timestamp>/`

For each task record:
- exact prompt/spec/max tokens;
- 8B output, metrics and ground-truth score;
- first validator decision/checks/wall;
- repair eligibility, exact byte-level transformation if any, repaired output and revalidation;
- whether 30B was called and why;
- 30B output/metrics/revalidation when called;
- final output source: `8B_PASS`, `SAFE_REPAIR`, `30B_PASS`, or `UNRESOLVED`;
- final quality score;
- memory/swap/cleanup telemetry;
- exact provenance.

Aggregate:
- raw8 CORRECT/PARTIAL/INCORRECT;
- final CORRECT/PARTIAL/INCORRECT;
- false-PASS count at every acceptance stage;
- safe-repair attempts/successes;
- 30B calls /8 and calls avoided /8;
- final mechanically accepted count;
- 8B wall, 30B added wall, total pipeline wall;
- measured time per final-CORRECT task;
- validator/repair overhead.

## Frozen GO gate

`LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_GO` only if all are true:
1. all 8 initial 8B conditions and every triggered 30B condition are valid;
2. zero false acceptance: every `8B_PASS`, `SAFE_REPAIR`, and `30B_PASS` is ground-truth CORRECT;
3. safe repair performs only the frozen fence-removal transformation;
4. final CORRECT count >= `6/8`;
5. final CORRECT count >= RAW8 CORRECT + `2`;
6. at least `2/8` 30B calls are avoided by 8B PASS or safe repair;
7. no 30B call occurs after 8B PASS/successful repair;
8. validator p95 <5 ms and deterministic repair p95 <5 ms;
9. zero network/download/package/model/runtime mutation outside the already-local canonical runtimes.

Otherwise `LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_NO_GO`.
Mechanical/instrumentation failure preventing valid evidence: `LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_MECHANICAL_NO_GO`.

## Boundaries

No open-ended `UNCERTAIN` tasks in this checkpoint. They require a separate semantic-verifier experiment.

No selector tuning, capability injection, calculator, 4B, memory/RAG, fine-tuning, Heretic, provider/UI or production integration.

No router threshold is frozen by this experiment. GO would validate a bounded mechanically-verifiable rescue path, not general LOOM AUTO.
