# LOOM — SELECT-TIME-GC-DEFER 001 — FROZEN PLAN

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Question

Under the promoted deferred post-forward streamed-layer lifecycle, does removing/defering only the per-streamed-layer select-time `gc.collect()` materially reduce real-M1 marginal streaming cost without causing unacceptable transient memory pressure?

## Baseline

Use exact promoted S1:
- transformer layers 0..34 persistent;
- layer 35 streamed;
- embedding/final norm/LM head persistent;
- embedding/norm/head eval boundaries retained;
- post-embedding/post-norm shared cleanup absent;
- streamed-layer post-forward `gc.collect()/mx.clear_cache()` absent/deferred;
- final post-head cleanup exactly once/token;
- persistent raw weights 3,499,501,056 B;
- logical streamed weight traffic 84,427,264 B/token.

## One factor

CONTROL retains the current select-time lifecycle after `mx.load`/selection: deletion/release of the full loaded weight container plus the inherited select-time `gc.collect()`.

TREATMENT keeps deletion/release at the identical logical point but omits/defer only that select-time `gc.collect()`. No replacement cleanup is inserted. The final canonical post-head cleanup remains unchanged.

Do not change load, tensor selection, reconstruction, rebinding, parameter materialization, streamed forward, eval boundaries, transient deletion/release, post-forward policy, residency, model math, logical I/O, source representation, threading, prefetch, buffering, mmap/pread/range-I/O, KV or decoding.

## Correctness

Separate fresh parity preflight with the first canonical REALGEN001 prompt, at least 16 real greedy unknown tokens or EOS. CONTROL and TREATMENT must match canonical S0 exact token IDs.

## Science

Exact ABBA order:
1. CONTROL
2. TREATMENT
3. TREATMENT
4. CONTROL

Fresh process each constituent; first three canonical REALGEN001 prompts; max 64 generated tokens/EOS; thinking disabled; real greedy M1.

Host admission before each process: free >=60% for two consecutive passive samples and swap <=5600 MB. Passive recovery only. After execution starts abort if free <5% or swap >5600 MB. No rescue/retry.

## Measurements

Per prompt/run:
- generated token IDs/EOS;
- generation wall/tok/s/wall per token;
- E2E tok/s;
- TTFT;
- MLX active/cache after load where natural;
- peak MLX active;
- peak active+cache where naturally available;
- minimum system free;
- peak swap;
- RSS diagnostic;
- logical streamed B/token;
- process-read B/token diagnostic;
- low-overhead counters for select-time GC and final cleanup only.

No profiler, per-stage timers, extra `mx.eval` or `mx.synchronize`.

## Interpretation

`SELECT_TIME_GC_COST_MATERIAL` if generation improves >=5%, exact parity passes and resource behavior remains usable.

`SELECT_TIME_GC_COST_SMALL` if stable positive gain >0 but <5%.

`SELECT_TIME_GC_NO_GO` for no gain/regression/parity failure/unacceptable resource behavior.

If material, remeasure the S0/S1/S2/S4 gradient before choosing a different mechanism. If small/no-go, close cleanup cadence and move to the next evidence-selected per-layer mechanism.

## Evidence

Store under:
`results-local/memory/select-time-gc-defer-001/<run-id>/`

Minimum: `summary.json`, `implementation-audit.json`, `parity.json`, `host-admission.jsonl`, `comparison.json`, `cleanup-counts.json`, `runs/`.
