# LOOM — llama.cpp Coding Quality Compare 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY AFTER RUNNER COMMIT**

## Research question

Does the technically runnable Qwen3-8B Q2_K profile preserve enough quality to outperform the smaller Qwen3-4B Q4_K_M profile when both are served by the same pinned llama.cpp runtime on the same M1/8GB machine?

This is a quality/usefulness gate, not another raw throughput test.

## Benchmark

Reuse the already frozen **LOOM Coding Benchmark 01 v1.0.1** in `single_shot` mode.

The suite remains unchanged:
- T01 generation — 15 points
- T02 debugging — 15 points
- T03 comprehension — 15 points
- T04 refactoring — 15 points
- T05 multi-file reasoning — 25 points
- T06 instruction following — 15 points
- total — 100 points

No task prompt, supplied source, test, scorer or point weighting may be edited.

## Compared conditions

### A — 8B Q2
- Qwen3-8B
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q2_K.gguf`
- SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- observed file size ~3.056 GiB

### B — 4B Q4 control
- Qwen3-4B
- `Qwen/Qwen3-4B-GGUF`
- `Qwen3-4B-Q4_K_M.gguf`
- SHA256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- observed file size ~2.326 GiB

## Runtime condition — frozen for both

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- `llama-server`
- Metal
- context 4096
- `-ngl -1`
- Flash Attention `auto`
- server bound only to `127.0.0.1`
- Web UI disabled
- local model files only; no model download
- one model server alive at a time

The comparison is deliberately between two **Qwen3** GGUF profiles under the same runtime. It is not an apples-to-apples comparison against the existing `qwen3.5:4b-mlx` Ollama baseline.

## Prompt transport

Use `POST /completion`, not chat completions.

Reason:
- `/completion` accepts the benchmark prompt as a direct `prompt` string;
- this avoids adding a system/user chat envelope or applying a chat template in the adapter;
- the exact prompt construction from the existing `scripts/ollama_single_shot.py` adapter must be reused.

The runner must verify the existing adapter Git blob before importing its `TASKS`, `build_prompt`, and output validation semantics.

Frozen adapter blob:
`62abab57f6463c5813809b43d8f1e7bdfec5f304`

## Request settings — frozen

Each task gets exactly one request:
- exact adapter-built prompt;
- `n_predict = 2048`;
- `temperature = 0`;
- `seed = 0`;
- `stream = false`;
- `cache_prompt = false`;
- `json_schema = {}`.

`cache_prompt=false` is intentional because the pinned llama-server documentation notes that prompt-cache reuse can produce non-bit-for-bit-identical logits depending on batching. No cross-task KV reuse is wanted in this quality comparison.

`json_schema={}` constrains the response to JSON while leaving the benchmark prompt responsible for the exact required outer structure and filenames, analogous in purpose to the JSON-constrained transport used in the prior Ollama single-shot adapter.

## Delivery/scoring rules

For each condition:
1. copy the frozen benchmark into an isolated `results-local` working tree;
2. send each task once;
3. do not expose hidden tests or test feedback before the answer;
4. parse the returned completion using the same exact file-envelope rules as the prior adapter;
5. write only permitted editable files;
6. run the frozen benchmark scorer after all attempted tasks;
7. record both raw artifact score and delivery-adjusted score.

No retry, salvage, repair, re-prompt or manual intervention is permitted.

A model output that is valid JSON but violates the required file envelope remains a delivery failure.

## Profile order

Run **8B Q2 first**, then shut its server down completely, wait a short cooldown, and run 4B Q4.

The order is fixed before results because the 8B profile has the narrower demonstrated memory margin. Throughput comparison is not the primary outcome here; dedicated llama-bench results already exist for speed.

## Memory/swap guardrails

Preserve the established safety limits for both profiles:
- abort the active server if observed free memory falls below **5%**;
- abort the active server if swap exceeds **5600 MB**.

If a guardrail or server/API failure prevents remaining tasks from running:
- preserve all completed work;
- mark unrun tasks explicitly;
- score the resulting artifact tree without rescue;
- continue to the second profile only after the first server is fully stopped.

## Telemetry

For each profile record:
- exact model hash and size;
- exact server command;
- `/health` readiness;
- per-task HTTP result;
- per-task raw response and server timing object;
- adapter status;
- wall time;
- process RSS samples;
- swap samples;
- memory-pressure samples;
- profile peak RSS;
- profile peak swap;
- profile minimum free-memory percentage;
- artifact score;
- delivery-adjusted score.

Also record disk free before/after the complete comparison.

## Primary comparison

Primary quality metric:
**delivery-adjusted score / 100**.

Secondary:
- raw artifact score;
- per-task scores/failure modes.

Report the signed difference:
`8B Q2 delivery-adjusted - 4B Q4 delivery-adjusted`.

Do not invent a post-hoc threshold. Classify the observed direction descriptively as:
- `8B_HIGHER`
- `4B_HIGHER`
- `TIE`

## Decision after the comparison

### If 8B Q2 is higher
Proceed to a controlled Pi/agent compatibility smoke before any full agentic benchmark. The technical and quality evidence would then justify testing whether the larger model improves actual agent work.

### If 8B Q2 is equal or lower
Do not call it a practical upgrade merely because it has 8B parameters. Prefer investigating a separately preregistered higher-quality memory strategy (for example partial offload for Q3/Q4) and/or continue to Direct MLX.

### Regardless of score
Do not test ~9B yet unless the 8B frontier yields evidence that a larger profile is scientifically useful rather than merely launchable.
