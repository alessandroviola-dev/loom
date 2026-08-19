# LOOM — Coding Quality Compare 002 Resource Diagnostic

Date: 2026-08-19
Run: `20260819-114848`
Status: **CLOSED — Q3 SMOKE-PASS / WORKLOAD-FAIL AT CONTEXT 4096**

## Scope

This diagnostic reads only persisted artifacts from Coding Quality Compare 002. It does not rerun either model and does not change any frozen benchmark or runtime parameter.

## Qwen3 8B Q3_K_M — exact failure

Frozen runtime:
- Qwen3-8B Q3_K_M, verified existing artifact
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- context 4096
- `-np 1`
- FA auto
- `--fit on --fit-target 1024 --fit-ctx 4096`
- `-ctk q8_0 -ctv q8_0`
- no forced `-ngl -1`
- frozen abort threshold: free memory <5% or swap >5600 MB

Observed profile state:
- classification `PARTIAL_OR_RESOURCE_FAIL`
- server ready: true
- exact abort reason: `memory free 4% < 5%`
- no execution/harness failure
- peak process RSS: 2005.5625 MB
- peak observed swap: 2290.88 MB
- minimum observed free memory: 4%
- attempted tasks: 1
- written tasks: 0

Process RSS remains diagnostic only; system-wide memory pressure and swap are authoritative for the LOOM safety boundary.

## T01 request state

T01 started after server readiness.

Observed:
- adapter status `failed`
- error `memory free 4% < 5%`
- HTTP status: none
- request wall: 28.801 s
- request error: `RemoteDisconnected: Remote end closed connection without response`
- no model response was captured

Interpretation: the runner terminated the local server when the frozen memory guardrail fired. The disconnected request is a consequence of the safety abort, not an independent API defect.

## Memory timeline around T01

Key persisted samples:

```text
7.301 s   free 6%   swap 2174.81 MB
7.379 s   free 6%   swap 2174.81 MB
8.400 s   free 5%   swap 2224.06 MB
9.742 s   free 5%   swap 2241.12 MB
10.882 s  free 6%   swap 2233.12 MB
11.988 s  free 5%   swap 2211.94 MB
13.132 s  free 5%   swap 2195.94 MB
14.257 s  free 5%   swap 2214.44 MB
15.381 s  free 5%   swap 2231.38 MB
16.683 s  free 7%   swap 2273.12 MB
18.268 s  free 5%   swap 2258.81 MB
20.268 s  free 4%   swap 2290.88 MB  -> guardrail
```

The profile therefore spent substantial time exactly on the 5% boundary under the first real coding request and then crossed it. This is not a transient startup-only failure.

## Server/request evidence

Relevant server log sequence:

```text
initializing, n_slots = 1, n_ctx_slot = 4096, kv_unified = 'false'
model loaded
listening on http://127.0.0.1:18086
selected slot by LRU
processing task
```

The model completed server initialization and entered real request processing before the resource abort.

## 4B control behavior

Under the same Compare 002 server policy, Qwen3-4B Q4_K_M:
- classification `COMPLETE`
- no guardrail abort
- minimum free memory 15%
- peak swap 2008.94 MB
- attempted 6/6 tasks
- written 3/6 tasks
- delivery-adjusted 25.72/100

The completed 4B profile confirms that the common benchmark/runtime path itself remained operational. Because Q3 did not complete, Compare 002 still does **not** establish an intrinsic Q3-vs-4B quality ordering.

## Canonical conclusion

> The exact Qwen3-8B Q3_K_M + llama.cpp + NP1 + Q8_0-KV profile is API-smoke viable at context 4096 but is not workload-stable under the frozen LOOM 5% free-memory guardrail. A real coding request drove system-wide free memory from the 6% smoke margin to 5% and then 4%, forcing a valid safety abort before T01 delivery.

This is a profile-level/runtime-level boundary, not a claim that all Qwen3 8B configurations are impossible on 8 GB Apple Silicon.

## Decision

The main research branch moves to **Phase 5 — Direct MLX**.

Do not:
- reinterpret Compare 002's printed `4B_HIGHER` as a quality result;
- expose this Q3 llama.cpp profile to Pi;
- lower the 5% guardrail;
- reduce context inside this already-failed condition;
- add another llama.cpp KV rescue automatically.

A more aggressive llama.cpp KV configuration may be revisited later only as a separately motivated experiment. It is not the next main-branch action.