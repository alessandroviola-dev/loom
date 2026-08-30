# LOOM 30B Stage2 Product-Candidate Validation 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Decide whether the Apple Metal MoE-paging 30B candidate is good enough to replace the historical custom-MLX 30B as canonical `loom-deep` on **product utility** grounds.

The comparability audit classified the candidates as:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Therefore Stage2 is explicitly **not** a same-checkpoint runtime benchmark and must not claim runtime-only quality parity.

## Candidates

### Historical DEEP candidate H — custom MLX

Frozen lineage:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`

Declared upstream base:
`Qwen/Qwen3-30B-A3B`

Representation:
MLX affine Q4/group128.

Use the existing locally verified historical artifact and the existing canonical custom-MLX Q4/top-8 execution path. No model download, conversion, requantization, or engine modification is authorized.

Historical numbers `1.402 tok/s` and `1.229233 tok/s` are context only; Stage2 selection must use fresh matched Stage2 measurements.

### New DEEP candidate N — Apple Metal MoE paging

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Existing verified local artifact:
`results-local/research/30b-apple-moe-paging-stage1-001/20260829T131816Z/model/Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Required size:
`12,424,439,872` bytes

Required SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion -no-cnv`

Required frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Apple profile is frozen to S24:
`--moe-n-slots 24 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`

No alternate slot count is authorized in Stage2.

## Common evaluation policy

- deterministic temperature 0;
- same semantic user prompt for both candidates;
- each candidate may use its own canonical tokenizer/chat template because this is a product-candidate comparison;
- max generated tokens: 96 unless a task has a lower explicit stop condition;
- fresh process per measured task unless a task explicitly belongs to the reproducibility block;
- preserve raw prompt, templated/tokenized counts where observable, full output, timings, provenance and host telemetry;
- no RAG, tools, hidden hints or ground-truth payload may enter model input.

## Block A — S24 reproducibility

Run candidate N only on the exact frozen Stage1R2 prompt, in **three fresh processes**, S24, identical settings.

Exact prompt:
`Spiega in italiano, in circa 120 parole, perché un modello Mixture-of-Experts può avere molti parametri totali ma usarne solo una parte per ogni token. Descrivi anche il ruolo del router e un vantaggio pratico.`

Reproducibility gate:
- 3/3 clean coherent runs;
- median generation throughput >= `4.0 tok/s`;
- no individual run < `3.5 tok/s`;
- no critical memory pressure/OOM/corruption/output-runaway;
- peak swap <= `3.5 GiB` in every run.

If this block fails scientifically, Stage2 is `NO_GO` and matched product testing may stop. Instrumentation/provenance failure is mechanical.

## Block B — fresh matched practical suite

The following prompts are frozen before execution and must be run once on H and once on N, temperature 0, maximum 96 generated tokens. Do not tune prompts after seeing outputs.

### T1 — arithmetic exact JSON

Prompt:
`Rispondi esclusivamente con JSON valido, senza testo aggiuntivo. Un magazzino riceve 17 scatole da 24 pezzi ciascuna e poi spedisce 38 pezzi. Restituisci {"result": NUMERO} con il numero di pezzi rimasti.`

Deterministic PASS: parseable JSON object with exactly `result = 370`.

### T2 — structured extraction

Prompt:
`Usa solo le informazioni nel testo. Rispondi esclusivamente con JSON valido con le chiavi project, language, owner, deadline, budget_eur. Testo: "Il progetto Orione usa Rust. La responsabile è Mara. La scadenza è il 17 ottobre. Il budget approvato è 4200 euro."`

Deterministic PASS: semantic JSON values exactly `Orione`, `Rust`, `Mara`, `17 ottobre`, `4200`.

### T3 — ordered transformation

Prompt:
`Rispondi esclusivamente con JSON valido. Dalla lista [7,2,7,5,2,9], elimina i duplicati mantenendo la prima occorrenza e poi inverti la lista risultante. Restituisci {"result": [...]}.`

Deterministic PASS: `result = [9,5,2,7]`.

### T4 — logical entailment

Prompt:
`Rispondi esclusivamente con NO oppure SI. Tutti i Nori sono Veli. Nessun Velo è Taro. Lia è un Nori. Lia può essere un Taro?`

Deterministic PASS: normalized output exactly `NO`.

### T5 — Python utility

Prompt:
`Scrivi solo codice Python, senza markdown. Implementa def dedupe_keep_order(items): che restituisce una nuova lista eliminando i duplicati e mantenendo l'ordine della prima occorrenza. Non modificare la lista di input e non usare librerie esterne.`

Deterministic PASS requires:
- valid Python after stripping an optional single markdown fence only for validator robustness;
- function `dedupe_keep_order` exists;
- no imports;
- passes frozen tests: `[] -> []`, `[1,1,2,1,3] -> [1,2,3]`, `["b","a","b","c","a"] -> ["b","a","c"]`;
- input list remains unchanged.

Generated code must be tested in an isolated local subprocess with a short timeout and no network. The unit tests/expected outputs are validator-only and must not be shown to either model.

### T6 — constrained factual summary

Prompt:
`Riassumi il testo in esattamente 3 punti elenco, senza aggiungere informazioni. Ogni punto deve contenere al massimo 14 parole. Testo: "Nexa ha spostato il backup notturno dalle 02:00 alle 03:30. Il motivo è evitare la sovrapposizione con l'importazione dati, che termina alle 03:00. Il nuovo orario entra in vigore lunedì. La retention dei backup resta invariata a 14 giorni."`

Frozen rubric, 0–3:
- +1 correctly states backup moved to 03:30;
- +1 correctly states overlap/import reason or that import ends at 03:00;
- +1 correctly states either Monday start or unchanged 14-day retention;
- structural requirement: exactly 3 bullets and <=14 words each; violation caps score at 1;
- unsupported factual addition caps score at 1.

### T7 — concise technical explanation

Prompt:
`In italiano, in massimo 70 parole, spiega la differenza tra RAM e memoria di archiviazione a una persona non tecnica. Devi menzionare che la RAM è temporanea e che l'archiviazione conserva i dati anche dopo lo spegnimento.`

Frozen rubric, 0–3:
- +1 RAM correctly described as temporary/working memory;
- +1 storage correctly described as persistent after shutdown;
- +1 explanation is coherent and <=70 words;
- factual contradiction caps score at 1.

## Metrics

For each candidate/task retain where observable:
- exact semantic prompt;
- exact command/runner and provenance;
- prompt token count;
- generated token count;
- generation tok/s;
- prompt/prefill tok/s;
- load time;
- TTFT if observable;
- E2E wall;
- RSS/wired/compressed;
- swap and memory pressure;
- full output;
- validator result / rubric score.

Aggregate separately for H and N:
- objective PASS count T1–T5;
- rubric total T6–T7 (0–6);
- median and pooled generation tok/s where valid;
- median E2E wall;
- peak swap and worst memory pressure.

## Product-selection gate

Final classification is `LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO` only if **all** are true:

1. exact candidate provenance verified with no unauthorized mutation;
2. candidate N passes the Block A S24 reproducibility gate;
3. all seven matched tasks produce valid retained measurements for both candidates;
4. N objective score T1–T5 is at least `4/5` and is no more than one PASS below H;
5. N rubric total T6–T7 is no more than one point below H;
6. N matched-suite generation throughput is at least `2.0x` H using the frozen aggregate method recorded before interpretation;
7. N median matched-task E2E wall is <= `0.80x` H;
8. N has no critical memory pressure/OOM/output corruption/repeated-token collapse/output-runaway;
9. N peak swap <= `3.5 GiB`;
10. complete durable evidence is retained.

If valid measurements exist but any scientific/product gate fails:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_NO_GO`.

If provenance, instrumentation, runner compatibility or artifact integrity prevents a valid comparison:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_MECHANICAL_NO_GO`.

## Interpretation

A GO means Apple Metal MoE paging is eligible to become canonical `loom-deep` **as the better product candidate** on the tested utility criteria.

A GO does not prove that its runtime alone caused the quality/performance difference because H and N are different checkpoints and quantizations.

A NO_GO does not invalidate Stage1R2's 4.40 tok/s result; it only blocks product promotion under this Stage2 contract.

## Boundaries

Forbidden during Stage2:
- model downloads;
- model conversion/requantization/copy as a substitute artifact;
- source/runtime patching;
- package installs;
- Apple slot tuning or alternate slot counts;
- prompt changes after results begin;
- retry of a scientifically valid task to improve score;
- hidden validator answers/specs in model input;
- validator/guided-repair work;
- Heretic integration;
- mini-SGLang acceleration work;
- production/provider/UI integration;
- Git commit/push by Pi.

Use fresh local evidence root:
`results-local/research/30b-stage2-product-candidate-validation-001/<timestamp>/`
