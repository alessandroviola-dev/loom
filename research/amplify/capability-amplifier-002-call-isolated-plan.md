# LOOM — Capability Amplifier 002 Call-Isolated Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the same `qwen3.5:4b-mlx` validator + maximum-one-repair amplifier complete the frozen six-task coding benchmark on the Apple M1 / 8 GB reference machine if each model call is isolated by explicitly unloading the Ollama model before the next call?

This is a new operational profile, not a rewrite of Capability Amplifier 001.

## Motivation

Capability Amplifier 001 run `20260819-142640` launched from 74% free memory and failed during the T02 repair at 4% free. T01 and T02 initial calls completed. The first call showed ~3.668 s model load duration while the second warm call showed ~0.045 s, confirming reused loaded residency between calls. The diagnostic supports testing residency isolation as the narrowest next factor.

No claim of memory leak or specific allocator/runtime bug is preregistered.

## Frozen provenance

Model/runtime:
- Ollama
- `qwen3.5:4b-mlx`
- context 4096
- `think=false`
- temperature 0
- max 2048 generated tokens/call.

Benchmark:
- Coding Benchmark 01 v1.0.1
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- frozen single-shot adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- frozen scorer blob `754e9a6506968d2b191bff57997710591efe8133`.

Amplifier logic inherited unchanged from Capability Amplifier 001 runner blob:
- `9f472c60b523762276291232f6e8c6ffc1c5fcae`.

## Frozen capability mechanism

For each task:
1. exact baseline initial call;
2. deterministic parser/test validation;
3. if all tests pass, no repair;
4. otherwise exactly one repair with deterministic parser/test feedback;
5. valid repair replaces initial only if it passes strictly more frozen tests;
6. ties retain initial;
7. exact frozen final scorer.

No Pi, retrieval, planner, third call, external model, human repair, web access or fine-tuning.

## One changed factor — model residency policy

Amplifier 001:
- Ollama model remained warm/resident across sequential calls unless the safety monitor stopped it.

Amplifier 002:
- before each model call, ensure the target model is not resident;
- after each completed model call, issue `ollama stop qwen3.5:4b-mlx`;
- poll `ollama ps` until the model is absent or a frozen timeout expires;
- record pre/post-isolation free-memory and swap samples.

There is **no new >=70% recovery threshold between calls**. The >=70% three-sample host-state gate remains only at benchmark launch. This avoids changing both residency policy and inter-call host threshold in the same experiment.

The intended trade-off is explicit: more cold-load latency in exchange for greater memory headroom.

## Initial host gate

Same as Amplifier 001:
- stop model before launch;
- require 3 consecutive memory-pressure samples >=70% free;
- swap <=5600 MB.

If not met:
- `HOST_STATE_NOT_READY`
- no benchmark launch.

## Runtime safety

Same frozen abort rules during model calls:
- free memory <5%;
- swap >5600 MB.

Missing required telemetry:
- `TELEMETRY_FAIL`.

If the model cannot be confirmed unloaded between calls:
- `ISOLATION_FAIL`;
- no aggregate quality conclusion.

A runtime/harness defect must not be called a model-quality failure.

## Metrics

Record:
- disk before/after;
- initial host samples;
- per-call load duration;
- per-call prompt/gen tokens and throughput;
- per-call wall time;
- pre/post-isolation free memory and swap;
- overall min free / peak swap;
- number of initial calls / repairs;
- repairs selected;
- total prompt/gen tokens;
- total model-call wall time;
- total orchestration wall time;
- artifact score;
- delivery-adjusted score;
- delivery count.

## Frozen quality gates

Same reference thresholds as Amplifier 001:

Historical single-shot:
- artifact 40.71
- delivery-adjusted 30.00
- delivery 3/6.

`QUALITY_IMPROVED`:
- `COMPLETE`
- delivery-adjusted >30.00.

`STRONG_AMPLIFICATION`:
- `QUALITY_IMPROVED`
- artifact >40.71
- delivery >3/6.

`PI_REFERENCE_REACHED` descriptive only:
- delivery-adjusted >=77.15.

Because Amplify exposes one hidden-test feedback round while Pi Agentic 001 did not, the Pi reference is not an intrinsic-model comparison.

## Decision

If `COMPLETE`:
- freeze quality + resource + efficiency result;
- compare directly with Amplifier 001 resource trajectory and the frozen single-shot quality baseline;
- decide the next capability factor only after this result.

If `PARTIAL_RESOURCE_FAIL` despite confirmed call isolation:
- call isolation alone is insufficient;
- do not silently weaken the 5% guardrail;
- next step requires a new architectural rationale, not another identical retry.

If `ISOLATION_FAIL`, fix only a demonstrated isolation-harness defect before drawing runtime conclusions.
