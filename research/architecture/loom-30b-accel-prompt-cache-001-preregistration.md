# LOOM 30B Acceleration Prompt Cache 001 — Preregistration

Date: 2026-08-30
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Test the first no-patch acceleration factor identified by `LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`: explicit `llama-completion --prompt-cache` reuse of an exact stable prefix.

This experiment targets prompt/prefill and end-to-end latency. It is **not** expected or required to increase decode tok/s. Decode throughput is a preservation metric.

## Frozen canonical DEEP

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
`llama-completion`

Required SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile:
S24 only.

Common flags:
`-n 8 -c 1024 --temp 0 --moe-n-slots 24 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -ub 1 -no-cnv`

No model/runtime/source/package mutation is authorized.

## Frozen stable prefix

Use the following prefix **byte-for-byte identically** for warm and target prompts:

```text
Contesto stabile per un test di cache di LOOM. Usa soltanto i fatti elencati qui sotto e rispondi esclusivamente alla domanda finale con il valore richiesto, senza spiegazioni. Il progetto Aurora usa Rust. Il progetto Boreale usa Go. Il progetto Cobalto usa Python. Il nodo Atlas ha colore ambra. Il nodo Vega usa la porta 4317. Il backup notturno parte alle 03:30. La retention dei backup è di 14 giorni. Il servizio Orione è gestito da Mara. Il cluster Delta contiene 6 nodi. Il repository principale si chiama LoomCore. Il canale di test si chiama Sigma. La build stabile è la numero 27. Il database locale usa la porta 5544. La regione di prova si chiama Nadir. Il file di configurazione principale è loom.toml. Il worker Echo ha priorità 4. Il task Kappa scade venerdì. Il gruppo Helios contiene 12 elementi. La coda principale si chiama Quarzo. Il profilo di emergenza si chiama Fenice.
```

Warm suffix EXACTLY:

```text
Domanda finale: qual è il colore del nodo Atlas?
```

Expected warm answer for functional validation:
`ambra`

Target suffix EXACTLY:

```text
Domanda finale: quale porta usa il nodo Vega?
```

Expected target answer for functional validation:
`4317`

The full warm prompt is `stable_prefix + warm_suffix` with no extra hidden text.
The full target prompt is `stable_prefix + target_suffix` with no extra hidden text.

## Experiment design

Run three independent rounds. Use a fresh prompt-cache file inside the evidence root for each round.

For each round, in this exact order:

1. **B — cache-disabled target baseline**
   - fresh `llama-completion` process;
   - full target prompt;
   - common frozen flags;
   - **no `--prompt-cache` argument**.

2. **W — cache population**
   - fresh process;
   - full warm prompt;
   - common frozen flags;
   - add `--prompt-cache <fresh-round-cache-file>`;
   - cache file must not exist before this invocation.

3. **C — warm-cache target**
   - fresh process;
   - full target prompt;
   - same common frozen flags;
   - add the exact same `--prompt-cache <fresh-round-cache-file>` used by W.

Do not reuse a cache file across rounds.
Do not retry a scientifically valid invocation.

## Instrumentation

A dedicated local research-only orchestration wrapper is allowed if the existing bounded harness cannot express the experiment without modification.

Before first model invocation:
- complete any wrapper implementation;
- synthetic-test its durable output handling without opening the GGUF;
- freeze and record wrapper SHA256;
- do not edit it after results begin.

The wrapper may orchestrate existing binaries and telemetry only. It may not patch runtime/model/source.

Fresh evidence root:
`results-local/research/30b-accel-prompt-cache-001/<timestamp>/`

Persist before each child launch:
- round and condition B/W/C;
- exact command;
- exact prompt hash and prompt byte length;
- model/source/frontend/wrapper provenance;
- cache-file path and pre-launch existence/size;
- RUNNING state and start timestamp.

Persist after each invocation:
- exit state;
- complete bounded output;
- runtime timing rows;
- prompt token count where observable;
- generated tokens;
- generation tok/s;
- prompt/prefill timing and tok/s where observable;
- model load time where observable;
- E2E wall;
- cache-file post-run existence/size/hash;
- cache reuse/hit evidence exposed by runtime, if any;
- RSS/wired/compressed/swap/memory pressure;
- cleanup proof.

## Functional validity

Normalize surrounding whitespace only.

- every valid B and C target output must equal `4317`;
- every valid W output must equal `ambra`;
- corruption, NaN, repeated-token collapse or wrong target answer invalidates the corresponding scientific condition.

## Primary metric

Primary acceleration metric:
**prompt/prefill wall time for target condition C versus target baseline B**.

For each round compute:
`C_prompt_eval_wall / B_prompt_eval_wall`
where directly observable from runtime timings.

Aggregate by median across three rounds.

If prompt-eval wall is not directly observable in a trustworthy way, the experiment is mechanical/instrumentation NO_GO rather than substituting a post-hoc metric.

## Secondary metrics

- target E2E wall C/B;
- prompt/prefill token count actually evaluated/reused where observable;
- cache file size/load behavior;
- generation tok/s C/B;
- memory/swap cost.

Model load time is reported separately and is not part of the primary cache-effect metric.

## Frozen GO gate

Classification `LOOM_30B_ACCEL_PROMPT_CACHE_GO` only if all are true:

1. exact frozen model/source/frontend provenance verified;
2. 3/3 B, W and C invocations complete validly;
3. cache file is created in each W and reused by corresponding C;
4. direct runtime evidence is sufficient to compute prompt/prefill wall for every B and C;
5. median `C_prompt_eval_wall / B_prompt_eval_wall <= 0.70` (at least 30% faster prompt evaluation);
6. median target E2E C/B is `< 1.00`;
7. median C generation tok/s is at least 90% of median B generation tok/s;
8. no critical memory pressure/OOM/output runaway/corruption;
9. peak swap in every measured invocation <= 3.5 GiB;
10. complete durable evidence retained;
11. zero model/source/runtime/package mutation.

If valid complete measurements exist but the cache acceleration gate fails:
`LOOM_30B_ACCEL_PROMPT_CACHE_NO_GO`.

If cache compatibility, provenance or instrumentation prevents a valid comparison:
`LOOM_30B_ACCEL_PROMPT_CACHE_MECHANICAL_NO_GO`.

## Interpretation

A GO means explicit prompt-cache reuse is useful for canonical DEEP prompt/prefill and E2E latency under a long stable-prefix workload.

It does **not** mean decode throughput exceeded the current ~4.39–4.40 tok/s baseline.

Regardless of GO/NO_GO, the next decode-focused acceleration checkpoint should be paging/I/O attribution, unless a mechanical failure must first be repaired.

## Boundaries

Forbidden:
- model download/copy/requantization;
- source/runtime patch;
- binary build/rebuild;
- package install;
- alternate slot counts;
- changing `-ub 1`;
- prompt changes after first model result;
- retry of valid runs;
- hidden hints/answers in model input;
- mini-SGLang source port;
- expert-prefetch implementation;
- Caveman integration;
- production/provider/UI work;
- Pi Git commit/push.
