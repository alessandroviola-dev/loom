# LOOM — llama.cpp 8B Q3 Auto-Fit Server Smoke 001 — Diagnostic

Date: 2026-08-19
Source run: `20260819-111648`
Status: **CLOSED — DEFAULT SERVER PARALLELISM IDENTIFIED; NP1 RESCUE JUSTIFIED**

## Purpose

Interpret the saved Q3 auto-fit server run without rerunning inference and select the next single-variable memory intervention.

## Frozen run result

The source experiment remains a valid failure:
- Qwen3-8B Q3_K_M, 3.841 GiB;
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- context 4096;
- automatic fit enabled;
- default KV-cache types;
- minimum observed free memory **4%**;
- peak process RSS **2121.859375 MB**;
- peak swap **2263.31 MB**;
- frozen 5% free-memory guardrail triggered;
- `server_ready=False` in the runner because the guardrail fired before the next successful health poll;
- no API request was authorized.

## Health timeline

Observed `/health` history:
- ~0.002 s: connection refused while process starts;
- ~1.035–6.163 s: HTTP 503 `Loading model`;
- no runner-observed HTTP 200 before the safety abort.

## Memory timeline

Saved samples:
- 0.002 s: RSS 0.80 MB, swap 1381.19 MB, free 58%;
- 1.035 s: RSS 880.16 MB, swap 1381.19 MB, free 58%;
- 2.053 s: RSS 2040.36 MB, swap 1381.19 MB, free 58%;
- 3.109 s: RSS 2121.86 MB, swap 1381.19 MB, free 59%;
- 4.121 s: RSS 1343.06 MB, swap 1381.19 MB, free 42%;
- 5.137 s: RSS 408.03 MB, swap 1381.19 MB, free 22%;
- 6.163 s: RSS 9.94 MB, swap 1636.88 MB, free 8%;
- 7.228 s: RSS 586.05 MB, swap 2263.31 MB, free **4%** -> guardrail.

The process RSS values are not a complete unified-memory accounting signal. The system-wide memory-pressure metric remains the safety authority.

## Critical server log evidence

The stderr tail contains:

```text
0.07.342.019 I srv    load_model: initializing, n_slots = 4, n_ctx_slot = 4096, kv_unified = 'true'
0.07.414.811 I srv  llama_server: model loaded
0.07.414.829 I srv  llama_server: listening on http://127.0.0.1:18083
0.07.512.566 I srv    operator(): operator(): cleaning up before exit...
```

Thus the server did finish model/context initialization and began listening, but the runner had already observed 4% free memory and correctly initiated shutdown according to the frozen guardrail.

## Why four slots appeared

At the pinned llama.cpp commit, `llama-server` sets server `n_parallel` to auto by default. In single-model mode, an unresolved auto value is explicitly converted to:

```text
n_parallel = 4
kv_unified = true
```

The context conversion passes `params.n_parallel` into `cparams.n_seq_max`, and server context initialization creates one server slot for each parallel sequence. The observed `n_slots = 4` is therefore expected default server behavior, not a LOOM-requested workload requirement.

LOOM's current experiments send one request at a time. Four-way server concurrency is unnecessary for this research question.

## Interpretation boundary

This diagnostic does **not** prove that four slots alone caused the full memory shortfall, nor does it quantify how much memory `-np 1` will save. It does establish that:
- the failure happened during the load/context initialization window rather than during user-token generation;
- the server instantiated four 4096-token slots under its automatic default;
- parallelism is an unfrozen server variable that is unnecessary for the single-request LOOM workload;
- reducing it is a smaller and more directly motivated intervention than changing KV precision.

## Next experiment

Preregister one variable only:

**Q3 Auto-Fit NP1 Server Smoke 001**

Keep unchanged:
- Q3_K_M model and SHA;
- context 4096;
- automatic fit and fit target;
- Flash Attention auto;
- default KV-cache types;
- localhost/offline/no Web UI;
- same 5% free-memory / 5600 MB swap guardrails;
- same one-request API smoke.

Change only:
- explicit `-np 1` / `--parallel 1`.

The new run must require log evidence `n_slots = 1` before being classified as a technical pass.

Do not introduce Q8_0 KV compression unless the NP1 condition still fails.