# LOOM 30B Apple MoE Paging Stage 1 001 — Preregistration

Date: 2026-08-29
Status: **PREREGISTERED / NOT YET RUN**

## Purpose

Perform the first real Qwen3-30B-A3B generation on the base M1 8 GiB host using the frozen Apple Metal expert-residency PoC and exactly one ByteShape GGUF. Determine whether bounded expert paging produces coherent output and materially exceeds the current ~1.4 tok/s DEEP path without unsafe host pressure.

This is runtime feasibility/performance Stage 1, not a final quality comparison or production integration.

## Frozen runtime

Source/runtime:
- repo `kisasexypantera94/llama.cpp`
- branch `moe-expert-residency`
- commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
- Metal build only; no source patching
- reuse the exact successful feasibility checkout/build when intact, otherwise rebuild from the exact frozen commit with the already-validated CMake flags

## Single authorized model download

Repository: `byteshape/Qwen3-30B-A3B-Instruct-2507-GGUF`
File EXACTLY:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Expected:
- remote size ~12.4 GB
- SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`
- published normalized quality 97.97%

Download may use HTTPS with resumable transport. No other model file may be downloaded. Transport resume/retry is allowed only before inference and does not authorize changing the artifact.

If SHA256 does not match, STOP before inference.

## Frozen inference workload

Prompt EXACTLY:
`Spiega in italiano, in circa 120 parole, perché un modello Mixture-of-Experts può avere molti parametri totali ma usarne solo una parte per ogni token. Descrivi anche il ruolo del router e un vantaggio pratico.`

Generation:
- deterministic temperature 0
- maximum 96 generated tokens
- context 1024
- `--moe-n-layers 48`
- `--no-mmap`
- `--no-warmup`
- expert tensor override exactly as required by the frozen PoC for CPU source weights
- `-ub 1` for every profile so slot count is the only sweep factor
- one fresh process per measured profile
- no speculative decoding
- no prompt/RAG/tools/system capability injection

Required coherence check: output must be readable Italian and correctly state at minimum that only a subset of experts is selected/active per token and that a router/gating mechanism selects experts. This is a coarse functional guard only, not a quality benchmark.

## Frozen slot sweep

Profiles in order:
1. `S8`: `--moe-n-slots 8`
2. `S16`: `--moe-n-slots 16`
3. `S24`: `--moe-n-slots 24`, conditionally

S8 and S16 are required unless S8 triggers the host-safety abort below.

S24 may run only if S16 exits cleanly and all are true:
- no critical/red memory-pressure condition observed;
- peak swap <= 3.5 GiB during S16;
- no OOM/process kill;
- host remains responsive and at least 5% memory headroom is observed by the harness's frozen host telemetry.

Do not test 32 slots.

If a lower profile fails scientifically but the process/host remains mechanically safe, continue only as permitted by the frozen safety rule. If host safety is triggered, stop higher profiles immediately.

## Metrics/evidence

For every attempted profile persist:
- exact command and binary/model SHA;
- stdout/stderr and output text;
- exit/stop reason;
- model load/start wall;
- TTFT where observable;
- generated token count;
- generation tok/s from runtime timings, plus E2E wall;
- prompt/prefill rate where observable;
- expert paging/cache statistics if the PoC exposes them;
- RSS/wired/compressed memory, swap and memory pressure before/during/after;
- storage read bytes/rate if observable without mutating system configuration;
- cleanup and proof no lingering inference process.

Aggregate:
- best safe profile by measured generation tok/s;
- speedup ratio against canonical current DEEP compact generation reference `1.402 tok/s` and exact-Q4 production reference `1.229233 tok/s`; these are historical practical references, not one-factor same-model comparisons;
- memory/swap cost of S8 vs S16 vs S24 when attempted.

## Frozen classification

`LOOM_30B_APPLE_MOE_PAGING_STAGE1_GO` only if all are true:
1. exact model SHA verified;
2. exact frozen source/runtime provenance verified;
3. at least one measured profile exits cleanly with coherent output;
4. best safe measured generation throughput >= `2.5 tok/s`;
5. no model-output corruption/NaN/repeated-token collapse;
6. no critical host memory-pressure/OOM safety event in the promoted best profile;
7. all required evidence persisted;
8. zero source/runtime/package/system mutation outside authorized download/build artifacts.

Otherwise scientific `...STAGE1_NO_GO`.
Instrumentation/download/build invalidity preventing a valid test: `...STAGE1_MECHANICAL_NO_GO`.

A GO does not automatically replace canonical DEEP. It authorizes Stage 2: reproducibility + matched practical comparison + quality preservation on a fresh compact suite.

## Boundaries

Allowed network: exactly the single frozen GGUF download and, only if the prior frozen source checkout is unavailable/corrupt, the exact frozen source refetch.

Forbidden:
- second GGUF/model download;
- changing quantization/model after seeing results;
- 8B/4B inference;
- current custom 30B runtime modification;
- package-manager installs;
- source patching;
- slot counts other than 8/16/24;
- post-hoc flag tuning;
- retries of a measured inference condition;
- validator/guided-repair research;
- Heretic/provider/UI/production integration;
- Git commit/push by Pi.

Create exactly:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Evidence root:
`results-local/research/30b-apple-moe-paging-stage1-001/<timestamp>/`.