# LOOM 8B Capability Amplification Funnel 001 — Preregistration

Date: 2026-08-28
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Test whether low-cost LOOM system capabilities can close specific raw-8B failure modes observed in Compact Practical Suite 001 before escalating to 30B.

This is an 8B-only paired-control experiment. No 30B and no 4B inference.

Frozen 8B runtime remains exactly:
- `mlx-community/Qwen3-8B-3bit@619ded3`;
- weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit/group64;
- MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1;
- real M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF;
- Qwen3 chat template;
- fresh state per condition.

Baseline system message EXACTLY:
`You are a helpful assistant. Answer clearly and directly.`

No downloads, model/runtime changes, memory/RAG, Heretic, fine-tuning, retries/self-repair outside explicitly frozen tool flow, or 30B escalation.

## Experimental design

Three independent branches. Each branch has three fresh prompts not used in the preceding 8B/30B suite.

For each prompt, run RAW 8B control and exactly one treatment condition. Do not use treatment outputs to modify later prompts or scoring.

Execution order alternates treatment/control within each branch to reduce order effects:
- item 1 RAW -> TREATMENT;
- item 2 TREATMENT -> RAW;
- item 3 RAW -> TREATMENT.

Run branches in order A -> B -> C. Each model process/state must be fresh per condition.

---

## Branch A — deterministic calculator capability

Question: can a simple calculator tool remove arithmetic errors that are not solved reliably by model escalation?

### RAW condition

Normal one-shot 8B response with baseline system message.

### TOOL condition

Use the same 8B runtime with a frozen two-stage calculator protocol.

Stage 1 system message:
`You are a helpful assistant with a calculator tool. For arithmetic that affects the final answer, output ONLY one JSON object {"expression":"..."}. Use only numbers, +, -, *, /, parentheses, ceil(...), floor(...), round(...,n). Do not calculate mentally.`

Harness parses exactly one JSON object and safely evaluates only the allowed AST/operators/functions. No Python `eval`, shell, network or arbitrary code.

If Stage 1 is invalid or requests unsupported syntax, TOOL condition is INCORRECT; no repair/retry.

Stage 2 receives baseline system message plus user prompt plus tool result in a deterministic tool-result message:
`Calculator result: <value>. Use this result and answer the user's original request exactly. Do not recompute it.`

Stage 2 max output tokens 70. Stage 1 max 45.

### A1
User prompt EXACTLY:
`Un cluster riceve 920 job al minuto. La capacità totale deve essere almeno 1,15 volte il traffico previsto. Ogni worker gestisce 37 job al minuto. Dimmi solo il numero minimo di worker e il calcolo essenziale in una riga.`
Expected: `29`; core calculation `ceil(920*1.15/37)=29`.
RAW max tokens: 70.

### A2
User prompt EXACTLY:
`Un componente costa 2,40 euro. Ne compri 135 e poi applichi IVA del 22%. Qual è il totale finale? Rispondi solo con importo in euro e calcolo essenziale, arrotondato a due decimali.`
Expected: `395.28` euro; `round(135*2.40*1.22,2)`.
RAW max tokens: 70.

### A3
User prompt EXACTLY:
`Devi trasferire 7,5 GB a 240 MB/s. Usa 1 GB = 1000 MB. Ignora overhead. Dimmi solo il tempo in secondi e il calcolo essenziale.`
Expected: `31.25 s`; `7500/240`.
RAW max tokens: 70.

Branch-A scoring per item:
- CORRECT only if final numeric answer and requested concise format are correct;
- PARTIAL if numeric core correct but material format/instruction defect;
- INCORRECT otherwise.

Branch-A acceptance signal: TOOL improves at least 2/3 items over RAW, yields at least 2/3 CORRECT, and introduces no new wrong numeric answer where RAW was correct.

---

## Branch B — strict-output protocol skill

Question: can a cheap generic protocol close 8B contract-following failures without using 30B?

### RAW condition
Baseline system message only.

### PROTOCOL condition
System message EXACTLY:
`You are a helpful assistant. Answer clearly and directly. LOOM strict-output protocol: when the user requests an exact machine-readable format, output ONLY that format: no Markdown fences, no prose, no labels, no comments. Preserve requested key order and data types exactly.`

No post-processing, parser repair or second inference. The treatment factor is only this reusable protocol instruction.

### B1
User prompt EXACTLY:
`Restituisci ESATTAMENTE un JSON valido senza testo aggiuntivo. Chiavi nell'ordine: device, ram_gb, local. Valori: device=MacBook Pro; ram_gb=8; local=yes. ram_gb deve essere numero e local booleano.`
Expected semantic JSON: `{"device":"MacBook Pro","ram_gb":8,"local":true}` with no surrounding prose/fence.
Max tokens: 70.

### B2
User prompt EXACTLY:
`Restituisci ESATTAMENTE un JSON valido senza testo aggiuntivo. Chiavi nell'ordine: model, speed, enabled. model=balanced; speed=13.2; enabled=no. speed deve essere numero e enabled booleano.`
Expected semantic JSON: `{"model":"balanced","speed":13.2,"enabled":false}` with no surrounding prose/fence.
Max tokens: 70.

### B3
User prompt EXACTLY:
`Restituisci ESATTAMENTE un array JSON valido, senza testo aggiuntivo e senza Markdown: tre oggetti nell'ordine dato con chiavi id e ok: id=A ok=yes; id=B ok=no; id=C ok=yes. ok deve essere booleano.`
Expected semantic array: `[{"id":"A","ok":true},{"id":"B","ok":false},{"id":"C","ok":true}]` with no surrounding prose/fence.
Max tokens: 90.

Branch-B scoring:
- CORRECT only if machine-parseable JSON, semantically exact, correct types/order, and no extra text/fence;
- PARTIAL if semantic object is correct but strict-output contract fails;
- INCORRECT for wrong/unparseable semantic content.

Branch-B acceptance signal: PROTOCOL improves at least 2/3 items over RAW, gets at least 2/3 CORRECT, and causes no semantic regression.

---

## Branch C — verification-first reusable skill

Question: can a generic reusable LOOM decision protocol improve 8B reasoning about cheap-first execution and escalation?

### RAW condition
Baseline system message only.

### SKILL condition
System message EXACTLY:
`You are a helpful assistant. Answer clearly and directly. LOOM verification-first protocol: start with the cheapest capable method; define observable success criteria before accepting its output; use deterministic or task-specific checks when available; escalate to the more capable method only when a required check fails or material uncertainty remains. Never choose only from prompt length or vague difficulty labels.`

No task-specific answer hints beyond this reusable protocol.

### C1
User prompt EXACTLY:
`Un'app genera SQL con un modello veloce e può usare un modello lento più capace. Dammi una regola concreta per decidere quando passare al modello lento usando verifiche sull'output. Massimo 4 righe.`
Max tokens: 110.
Expected core: try fast; validate syntax/schema/allowed tables or executable deterministic checks; escalate on failed checks/material uncertainty.

### C2
User prompt EXACTLY:
`Un sistema estrae campi da fatture con un metodo veloce e ha un metodo lento più accurato. Proponi una regola di escalation basata su controlli dei campi estratti, non sulla lunghezza del documento. Massimo 4 righe.`
Max tokens: 110.
Expected core: fast first; validate required fields/types/totals/consistency; escalate if validation fails/uncertain.

### C3
User prompt EXACTLY:
`Un agente modifica codice usando un modello veloce e può chiamare un modello lento. Come dovrebbe decidere se escalare dopo la prima patch? Dammi una regola concreta basata sulla verifica, massimo 4 righe.`
Max tokens: 110.
Expected core: fast patch first; run tests/static checks/spec verification; escalate only if checks fail or unresolved ambiguity remains.

Branch-C scoring:
- CORRECT: explicit cheap-first attempt + concrete output validation + escalation on validation failure/uncertainty;
- PARTIAL: mentions validation/escalation but misses one required component or is vague;
- INCORRECT: difficulty/prompt-length heuristic, incoherent loop, or no verification-driven rule.
Instruction following scored separately.

Branch-C acceptance signal: SKILL improves at least 2/3 items over RAW, yields at least 2/3 CORRECT, and causes no correctness regression.

---

## Required evidence

Create exactly one new experimental harness:
`scripts/loom_8b_capability_amplification_funnel_001.py`

Persist under:
`results-local/research/8b-capability-amplification-funnel-001/<timestamp>/`

For every condition record:
- branch/item/condition;
- exact system/user/tool messages;
- output text and token count;
- stop reason;
- correctness/partial/incorrect + reason;
- instruction PASS/FAIL;
- TTFT;
- generation/end-to-end wall and tok/s;
- memory/swap telemetry;
- exact runtime/model provenance.

For TOOL conditions additionally persist:
- raw Stage-1 tool request;
- parsed expression;
- safe evaluator validation;
- calculator result;
- Stage-1 and Stage-2 timing separately;
- total tool-flow wall.

Aggregate each branch separately. Do not merge the three treatment mechanisms into one synthetic overall score.

## Interpretation boundary

This funnel tests system-level capability amplification, not intrinsic model intelligence.

If accepted:
- calculator capability becomes a candidate deterministic pre/escalation path for arithmetic;
- strict-output protocol becomes a candidate reusable skill for machine-readable contracts;
- verification-first protocol becomes a candidate reusable skill before 30B escalation.

No router thresholds or production integration are authorized by this experiment alone.

## Classification

`LOOM_8B_CAPABILITY_AMPLIFICATION_FUNNEL_PASS` if all paired conditions execute validly with frozen provenance/evidence. Individual branches may be ACCEPTED or REJECTED according to their frozen signals.

Mechanical failure of one branch yields `...INCOMPLETE`; preserve completed evidence and do not silently modify/rerun.
