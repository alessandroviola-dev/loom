# LOOM 30B Acceleration Prompt Cache R2 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**

## Summary

Prompt Cache R2 completed validly and passed all 14 frozen gates.

This establishes explicit `llama-completion --prompt-cache` reuse as a canonical DEEP prefill/end-to-end optimization for the preregistered stable-prefix workload on canonical Apple S24.

It does **not** establish a decode-throughput increase over the canonical ~4.39–4.40 tok/s decode baseline. Decode remained a preservation metric in this experiment.

Evidence root:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`

## Frozen provenance

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion -no-cnv`

Frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Profile: S24.

## Wrapper preflight

Frozen Prompt Cache 001 parent wrapper:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/prompt_cache_runner.py`

Required/observed parent SHA256:
`1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`

The parent was verified and preserved unchanged.

Derived R2 wrapper SHA256, frozen before inference:
`3550d56e0fee1adcf08ae95fcb1ae8fcf50c740147bae036745ab28f0db68ccd`

Synthetic preflight:
- 13 validator/harness checks passed;
- no GGUF access occurred during synthetic testing;
- no wrapper mutation occurred after inference began.

## Measurements

| Round | B prompt eval | B E2E | B gen tok/s | W prompt eval | W E2E | W gen tok/s | C prompt eval | C E2E | C gen tok/s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 71.220 s | 76.747 s | 3.52 | 71.088 s | 75.741 s | 3.34 | 2.858 s | 7.823 s | 3.55 |
| 2 | 71.394 s | 76.442 s | 3.47 | 71.694 s | 76.443 s | 3.35 | 2.878 s | 8.357 s | 3.47 |
| 3 | 73.331 s | 78.476 s | 3.49 | 72.952 s | 77.602 s | 3.31 | 2.952 s | 8.437 s | 3.38 |

All nine cleaned outputs passed the frozen semantic validator.

## Primary metric

Per-round `C_prompt_eval_wall / B_prompt_eval_wall`:
- round 1: `0.04013`;
- round 2: `0.04031`;
- round 3: `0.04025`.

Median:
**`0.04025`**.

Frozen GO threshold:
`<= 0.70`.

Result:
**PASS**.

Equivalent observed reduction in target prompt-evaluation wall under this workload is approximately 95.98% relative to cache-disabled B, based on the frozen median ratio.

## Secondary metrics

Per-round target E2E C/B:
- `0.10193`;
- `0.10932`;
- `0.10751`.

Median E2E C/B:
**`0.10751`**.

Median B/C generation throughput:
- B: `3.49 tok/s`;
- C: `3.47 tok/s`.

Decode preservation:
**`99.43%`**.

Frozen preservation threshold:
`>= 90%`.

Result:
**PASS**.

## Cache evidence

Each W created a fresh per-round cache and each corresponding C reused that cache.

Cache size:
`26,449,272` bytes.

Cache SHA256:
`f96f9fb61f6e2302fb206932a4ca497c8a1ccbe7346c22b20bc0678094dd5a99`.

C runtime evidence:
- loaded 269-token session;
- matched 262/269 prompt tokens.

This directly supports actual cache reuse rather than a timing-only inference.

## Resource safety

Peak RSS:
`2948.83 MiB`.

Peak swap:
`1267.56 MiB`.

No critical memory pressure, OOM, corruption or output runaway was observed.

Frozen swap ceiling:
`3.5 GiB`.

Result:
**PASS**.

## Gate evaluation

All 14 preregistered gates passed:
1. model/source/frontend provenance — PASS;
2. parent wrapper SHA and preservation — PASS;
3. derived wrapper authorization/synthetic test/freeze — PASS;
4. 9/9 functionally valid invocations — PASS;
5. cache creation/reuse — PASS;
6. direct prompt-eval timing — PASS;
7. median prompt ratio <=0.70 — PASS (`0.04025`);
8. median E2E ratio <1.00 — PASS (`0.10751`);
9. decode preservation >=90% — PASS (`99.43%`);
10. no critical pressure/OOM/corruption/runaway — PASS;
11. every invocation swap <=3.5 GiB — PASS;
12. complete durable evidence — PASS;
13. zero model/source/runtime/package mutation — PASS;
14. no post-inference derived-wrapper mutation — PASS.

Final classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**.

## Scientific interpretation

Validated claim:

> Under the frozen stable-prefix workload, canonical S24 can reuse an explicit prompt cache across fresh `llama-completion` processes and reduce target prompt-evaluation wall time to a median 4.025% of the cache-disabled baseline while preserving decode throughput above the preregistered 90% floor.

Boundary:
- this is a prompt/prefill and end-to-end optimization;
- it is not direct decode acceleration;
- it does not imply the same ratio for short prompts, changing prefixes, unrelated workloads, or persistent-server execution.

## Exact next step

Proceed to paging/I/O attribution for canonical S24 before any source-level expert prefetch/overlap intervention.

The next research objective is to determine how much decode time is attributable to expert-residency misses and synchronous expert reads, and whether there is sufficient I/O/compute overlap headroom to justify a separately preregistered intervention.
