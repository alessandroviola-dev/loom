# LOOM — llama.cpp 8B Q2 Server Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Purpose

Test whether the technically runnable Qwen3-8B Q2_K profile can also be served through `llama-server` on the reference M1 8 GB machine at context 4096 without breaching the existing LOOM memory/swap guardrails.

This is the bridge between raw llama.cpp capability and two later practical tests:
1. running the frozen Coding Benchmark 01 through a clean HTTP API instead of the problematic interactive CLI path;
2. evaluating Pi compatibility through llama.cpp's OpenAI-compatible API if model quality justifies it.

This smoke is not itself a quality benchmark.

## Frozen source/model

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Release/Metal build tree
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- expected SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- observed model size 3.056 GiB

## Server build prerequisite

The CMake configuration already has `LLAMA_BUILD_SERVER=ON`, but earlier setup built only `llama-cli` and `llama-bench` targets.

The smoke runner may build exactly the `llama-server` target in the existing pinned build tree if `build-loom-metal/bin/llama-server` is absent. This does not alter source or experimental model settings.

## Frozen server launch

Launch one local server only:

- `-m <verified Q2 path>`
- `-ngl -1`
- `-c 4096`
- `-fa auto`
- `--host 127.0.0.1`
- fixed local high port chosen by the runner
- fixed API alias `loom-qwen3-8b-q2`
- `--no-webui`

No external network binding and no server tools/agent mode.

## Readiness

Poll the official public `GET /health` endpoint.

At the pinned llama.cpp server, HTTP 503 with a loading-model error is an expected transient state; readiness requires HTTP 200 before timeout.

## One API request

After readiness, send one synchronous `POST /v1/chat/completions` request using the OpenAI-compatible route documented by llama.cpp:

- model alias `loom-qwen3-8b-q2`
- one user message: `Reply only with OK.`
- temperature 0
- maximum 8 output tokens
- streaming disabled
- reasoning effort `none` where supported by the pinned route

Success requires a valid JSON response with a non-empty assistant content field. Exact textual `OK` is diagnostic, not required for transport success.

## Guardrails

Preserve the established Q2 safety thresholds through server load and request:

- terminate if observed free memory falls below **5%**;
- terminate if observed swap exceeds **5600 MB**;
- terminate on server/readiness timeout;
- no same-run reduction of context or GPU layers.

## Telemetry

Record:

- exact model SHA256;
- source commit and server version;
- server build status if target had to be built;
- exact launch command;
- readiness wall time;
- HTTP health history/status;
- request wall time and response JSON;
- process peak RSS;
- peak observed swap;
- minimum free-memory percentage;
- disk free before/after;
- server stdout/stderr logs;
- clean/forced shutdown status.

## Classification

### FULL_PASS

- exact source/model verification PASS;
- server target available;
- server reaches `/health` HTTP 200;
- no guardrail breach;
- `/v1/chat/completions` returns HTTP 200 and valid JSON with non-empty assistant content;
- server can be terminated cleanly after the request.

### FAIL

Any build, readiness, API, timeout or safety-guardrail failure.

No rescue parameters in the same run.

## Decision after smoke

If FULL_PASS:
- freeze llama-server as the API transport for a same-runtime Coding Benchmark 01 comparison between Qwen3 4B Q4_K_M and Qwen3 8B Q2_K;
- only after objective quality results decide whether to connect Pi.

If FAIL due memory pressure:
- record that raw Q2 capability does not automatically imply a viable context-4096 server profile;
- do not misclassify it as a model-quality failure;
- choose a separately preregistered direct-quality or memory/offload path.