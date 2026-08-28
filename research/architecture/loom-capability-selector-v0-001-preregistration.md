# LOOM Capability Selector v0 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Validate whether a zero-inference deterministic selector can decide when to apply the two already-accepted targeted LOOM capabilities:
- `STRICT_OUTPUT`;
- `VERIFY_FIRST`;
- otherwise `NORMAL`.

This checkpoint tests **capability applicability only**. It does not run 8B or 30B inference and does not test answer quality.

Capability Candidate v1 remains `NO_GO`; this selector is not a rescue or gate relaxation. It is a separate test of conditional use of the two branch-level capabilities already accepted in the earlier funnel.

## Frozen selector v0

Implement exactly these deterministic rules, case-insensitive, over the user prompt text after whitespace normalization.

Priority order:
1. `STRICT_OUTPUT`;
2. `VERIFY_FIRST`;
3. `NORMAL`.

### STRICT_OUTPUT rule

Select `STRICT_OUTPUT` only when BOTH are true:

A. the prompt explicitly requests a machine-readable/rigid output family using one or more of:
`json`, `csv`, `yaml`, `xml`, `array`, `oggetto`, `schema`, `machine-readable`, `formato esatto`, `formato valido`;

AND

B. the prompt contains an explicit exclusivity/contract cue using one or more of:
`solo`, `esattamente`, `senza testo`, `senza spiegazioni`, `nessun testo`, `valid`, `valido`, `chiavi`, `campi`, `ordine`.

Mentions of JSON/CSV/etc. for explanation, discussion, examples or comparison without a rigid-output/exclusivity cue must NOT activate `STRICT_OUTPUT`.

### VERIFY_FIRST rule

If STRICT_OUTPUT did not activate, select `VERIFY_FIRST` only when the prompt explicitly asks for a decision, acceptance/rejection, escalation/fallback or use of a more expensive/slower method/model **based on observable verification**, and contains:

A. at least one decision/escalation cue:
`accetta`, `rifiuta`, `escal`, `fallback`, `modello lento`, `modello più`, `metodo lento`, `passa al`, `quando usare`;

AND

B. at least one verification cue:
`verifica`, `valida`, `test`, `controll`, `criterio`, `check`, `errore`, `corretto`, `completezza`, `sintatt`, `semantic`.

Generic requests to explain testing, verification or fallback concepts without asking for a decision/escalation rule must NOT activate `VERIFY_FIRST`.

### NORMAL rule

Anything not matching the two frozen rules above.

No learned/model classifier, embeddings, network, external packages or post-hoc rule edits are allowed.

## Frozen unseen evaluation set

The selector implementation must be completed from the rules above before scoring the following prompts.

### S01 — STRICT_OUTPUT
`Restituisci solo JSON valido con le chiavi name, enabled, ports in questo ordine. enabled è booleano e ports è un array di interi. name=loom; enabled=yes; ports=8000,8001.`

Expected: `STRICT_OUTPUT`.

### S02 — STRICT_OUTPUT
`Converti esattamente questi record in CSV senza spiegazioni: id=A,status=ok; id=B,status=failed. Intestazione obbligatoria: id,status.`

Expected: `STRICT_OUTPUT`.

### S03 — STRICT_OUTPUT
`Dammi un array JSON valido e nessun testo prima o dopo: alpha,beta,gamma.`

Expected: `STRICT_OUTPUT`.

### S04 — STRICT_OUTPUT
`Genera YAML valido con i campi service, replicas, local e restituisci solo il contenuto YAML.`

Expected: `STRICT_OUTPUT`.

### S05 — STRICT_OUTPUT adversarial
`Spiegami in massimo 4 righe quando è preferibile JSON rispetto a YAML per un file di configurazione.`

Expected: `NORMAL`.

### S06 — VERIFY_FIRST
`Definisci quando accettare la patch del modello veloce e quando passare al modello lento usando test unitari e type-check come criteri osservabili.`

Expected: `VERIFY_FIRST`.

### S07 — VERIFY_FIRST
`Dammi una regola per fare escalation al metodo più lento solo se la validazione dei campi estratti fallisce.`

Expected: `VERIFY_FIRST`.

### S08 — VERIFY_FIRST
`Quando devo rifiutare l'output e usare il fallback? Basa la decisione su controlli sintattici e semantici.`

Expected: `VERIFY_FIRST`.

### S09 — VERIFY_FIRST
`Proponi una regola concreta per accettare o rifiutare una risposta dopo un test automatico di correttezza.`

Expected: `VERIFY_FIRST`.

### S10 — VERIFY_FIRST adversarial
`Spiegami cosa sono i test unitari e perché sono utili nello sviluppo software.`

Expected: `NORMAL`.

### S11 — NORMAL
`Riassumi in tre righe perché la memoria unificata è utile su Apple Silicon.`

Expected: `NORMAL`.

### S12 — NORMAL
`Correggi questo bug Python e mostra il codice corretto: for i in range(3): print(i)`

Expected: `NORMAL`.

### S13 — NORMAL adversarial
`Mostrami un esempio di JSON e poi spiegami riga per riga cosa significa.`

Expected: `NORMAL`.

### S14 — NORMAL adversarial
`Descrivi una strategia di fallback per un servizio web ad alta disponibilità.`

Expected: `NORMAL`.

### S15 — NORMAL adversarial
`Quali controlli useresti per verificare che un database sia sano? Non devi decidere se fare escalation.`

Expected: `NORMAL`.

## Required metrics

Persist per item:
- prompt id;
- expected label;
- predicted label;
- matched rule/cues;
- correct boolean;
- selector wall microseconds.

Aggregate:
- accuracy;
- confusion matrix;
- precision/recall/F1 per label;
- false activations on expected NORMAL;
- selector p50/p95 wall.

## Acceptance gate

`LOOM_CAPABILITY_SELECTOR_V0_GO` only if all are true:
- overall accuracy >= `13/15`;
- `STRICT_OUTPUT` precision >= `0.80` and recall >= `0.80`;
- `VERIFY_FIRST` precision >= `0.80` and recall >= `0.75`;
- expected-NORMAL false activation count <= `1/7`;
- no network/model inference/package mutation;
- exact frozen rules were not changed after scoring begins.

Otherwise `LOOM_CAPABILITY_SELECTOR_V0_NO_GO`.

## Files / evidence

Create only:
`scripts/loom_capability_selector_v0_001.py`

Persist evidence under:
`results-local/research/capability-selector-v0-001/<timestamp>/`

No Git commit/push.

## Interpretation boundary

GO means the deterministic selector is good enough to justify a separate end-to-end dispatcher test with 8B. It does not promote Capability Candidate v1, prove general task understanding, or authorize 30B routing thresholds.

NO_GO means keep B/C as explicitly-invoked capabilities and do not tune the frozen selector on these same prompts.
