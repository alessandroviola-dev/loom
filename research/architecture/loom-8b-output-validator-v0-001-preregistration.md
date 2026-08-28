# LOOM 8B Output Validator v0 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED / NOT YET RUN

## Purpose

Test a cheap post-generation validation layer:
`prompt -> RAW 8B -> validator -> PASS / FAIL / UNCERTAIN`.

No 30B, retry, repair, selector tuning or capability injection. Validator v0 verifies only explicit contracts/structures and must abstain on open-ended semantic tasks.

## Frozen 8B

- `mlx-community/Qwen3-8B-3bit@619ded3`
- weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit/group64
- MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1
- M1 built-in qmv_fast, BF16 KV, greedy, thinking OFF
- fresh state per task
- system exactly: `You are a helpful assistant. Answer clearly and directly.`

## Validator kinds

Benchmark supplies validator kind/spec; v0 does not infer task class. Standard library only.

`V_JSON_OBJECT`: exact single JSON object; no prose/fence; exact key order, values and types.

`V_JSON_ARRAY`: exact top-level JSON array; no prose/fence; exact ordered semantic content.

`V_CSV`: exact header/order, row count/order/content; no prose/fence.

`V_KV`: restricted one `key: value` per line; exact order/values/types; no prose/fence/comments; booleans only lowercase `true`/`false`.

`V_VERIFY_RULE`: PASS only if response contains all of:
1. cheap/first attempt cue (`prima`, `veloce`, `metodo rapido`, `modello veloce`, `prima prova`);
2. observable validation cue (`test`, `type-check`, `schema`, `sintatt`, `campo`, `totale`, `checksum`, `controll`, `valida`, `verifica`);
3. escalation cue (`escal`, `modello lento`, `metodo lento`, `passa al`, `fallback`);
4. failure/uncertainty cue (`fall`, `non passa`, `non valido`, `non conforme`, `incert`, `errore`, `manca`, `mancante`);
5. no prompt-length/vague-difficulty-only routing. `lunghezza`, `prompt lungo`, `query lunga`, `più lungo` cause FAIL; bare `complesso/complessa` without observable validation also fails.

`V_UNVERIFIABLE`: always `UNCERTAIN`.

Validator output exactly `PASS`, `FAIL`, or `UNCERTAIN`.

## No-model preflight

Before inference, test each validator kind on frozen synthetic PASS/FAIL fixtures; V_UNVERIFIABLE must return UNCERTAIN. Any fixture failure -> MECHANICAL_NO_GO before model load.

## Fresh tasks

T01 V_JSON_OBJECT, max 90:
`Restituisci soltanto un oggetto JSON valido, senza Markdown o testo extra. Chiavi in questo ordine: node, active, ports. node=edge-1; active=yes; ports=7001,7002. active deve essere booleano e ports un array di interi.`
Expected `{"node":"edge-1","active":true,"ports":[7001,7002]}`.

T02 V_CSV, max 90:
`Restituisci soltanto CSV, nessuna spiegazione. Header esatto: service,status. Righe nell'ordine: api=ok; worker=failed; cache=ok.`
Expected header/rows exactly: service,status / api,ok / worker,failed / cache,ok.

T03 V_JSON_ARRAY, max 100:
`Restituisci soltanto un array JSON valido senza testo extra: tre oggetti nell'ordine A,B,C con chiavi id e retries. Valori: A=0; B=2; C=1. retries deve essere numero intero.`
Expected `[{"id":"A","retries":0},{"id":"B","retries":2},{"id":"C","retries":1}]`.

T04 V_KV, max 80:
`Restituisci soltanto questo formato key: value, una riga per campo, senza Markdown. Campi nell'ordine: service, replicas, enabled. service=loom-router; replicas=2; enabled=yes. replicas deve essere intero e enabled booleano.`
Expected lines: `service: loom-router`, `replicas: 2`, `enabled: true`.

T05 V_JSON_OBJECT, max 80:
`Converti i dati in un solo JSON valido e non aggiungere altro. Chiavi nell'ordine: model, context, local. model=balanced; context=4096; local=yes. context è intero, local è booleano.`
Expected `{"model":"balanced","context":4096,"local":true}`.

T06 V_CSV, max 90:
`Produci solo CSV valido. Header obbligatorio nell'ordine: id,latency_ms,ok. Record: A,12,true; B,35,false. Nessun testo prima o dopo.`
Expected exact header and two rows.

T07 V_VERIFY_RULE, max 110:
`Un modello veloce genera query SQL e un modello lento può intervenire. Definisci in massimo 4 righe quando accettare la query veloce e quando fare escalation, usando controlli osservabili sulla query e sullo schema.`

T08 V_VERIFY_RULE, max 110:
`Un estrattore veloce legge ordini e un metodo lento è più accurato. In massimo 4 righe dai una regola: prima prova economica, controlli su campi obbligatori e totale, escalation solo quando i controlli non bastano.`

T09 V_VERIFY_RULE, max 110:
`Un agente propone una patch con il modello veloce. In massimo 4 righe indica quando tenerla e quando chiamare il modello lento, usando test e type-check come verifiche dell'output.`

T10 V_UNVERIFIABLE, max 100:
`Spiega in massimo 4 righe perché la memoria unificata può aiutare un carico AI locale su Apple Silicon.`

T11 V_UNVERIFIABLE, max 100:
`In massimo 4 righe confronta BFS e DFS e indica un caso d'uso tipico per ciascuno.`

T12 V_UNVERIFIABLE, max 100:
`Spiega in massimo 4 righe perché una cache può ridurre la latenza di un servizio locale.`

## Execution/evidence

Run T01->T12 once each, fresh state, no retry. Persist prompt/output/token IDs/stop reason, validator kind/spec/decision/checks/wall, TTFT, generation rate, E2E wall, memory/swap/cleanup and exact provenance.

Score T01-T09 separately as CORRECT/PARTIAL/INCORRECT from their frozen contract/rubric. T10-T12 are NOT_SCORED_SEMANTICALLY; validator must remain UNCERTAIN.

Aggregate validator decision counts, false PASS count, T10-T12 abstention correctness, model C/P/I for T01-T09, validator p50/p95, and 8B performance/resources.

## GO gate

`LOOM_8B_OUTPUT_VALIDATOR_V0_GO` only if:
1. 12/12 inference/evidence records valid;
2. all synthetic fixtures pass;
3. zero false PASS on a mechanically invalid T01-T09 output;
4. T10-T12 = UNCERTAIN 3/3;
5. implementation matches frozen rules;
6. validator p95 <5 ms;
7. no network/package/model/runtime mutation.

Harness defect -> `LOOM_8B_OUTPUT_VALIDATOR_V0_MECHANICAL_NO_GO`.
Valid evidence but failed gate -> `LOOM_8B_OUTPUT_VALIDATOR_V0_NO_GO`.

GO authorizes a separate selective repair/30B-escalation test. It does not claim factual verification, revive selector v0, freeze 30B thresholds, or restore calculator/4B.

Create only `scripts/loom_8b_output_validator_v0_001.py`.
Evidence under `results-local/research/8b-output-validator-v0-001/<timestamp>/`.
No Git commit/push.
