# LOOM 30B Acceleration Persistent/Cache Feasibility 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`**

## Summary

The bounded no-inference audit found enough deterministic capability evidence to preregister the first no-patch acceleration experiment for canonical `loom-deep`.

Key finding:
- no built `llama-server` is available in the existing frozen build;
- the canonical built `llama-completion` frontend exposes explicit `--prompt-cache` support;
- the recommended first one-factor experiment is exact stable-prefix warm `--prompt-cache` versus a cache-disabled baseline.

This checkpoint makes no throughput or latency claim because no model inference was performed.

## Evidence

Evidence root:
`results-local/research/30b-accel-persistent-cache-feasibility-001/20260830T101246Z/`

Expected retained artifacts:
- `report.json`
- `source-evidence.txt`
- `capability-matrix.json`

## Boundaries respected

Pi reported:
- no model inference;
- no GGUF open;
- no source patch;
- no build/rebuild;
- no download/package install;
- no Git action.

## Interpretation

A persistent server path cannot be tested immediately without a separate build authorization because no built `llama-server` is present.

The available no-patch mechanism with the lowest implementation risk is `llama-completion --prompt-cache`. This should be tested first as an end-to-end/prefill optimization, not as a claim of direct decode-throughput improvement.

Canonical decode baseline remains approximately 4.39–4.40 tok/s at S24.

## Exact next step

Preregister a bounded `--prompt-cache` experiment using:
- the exact canonical Apple S24 model/runtime;
- a frozen long stable prefix;
- cache-disabled matched target runs;
- warm-cache matched target runs using the same stable prefix and a different suffix during cache population;
- fresh process per measured invocation;
- durable output/timing/telemetry evidence;
- no source/runtime/model mutation.

The experiment should primarily evaluate prompt/prefill and E2E latency. Decode throughput must be treated as a preservation metric.

After the prompt-cache experiment, continue the acceleration funnel with paging/I/O attribution to identify a direct decode-throughput intervention toward 5+ tok/s and later 6–9 tok/s.
