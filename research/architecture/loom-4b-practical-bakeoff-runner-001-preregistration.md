# LOOM 4B Practical Bake-off Runner 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED / NOT YET RUN

## Question

Under the already-validated LOOM 4B runtime control, how quickly and completely can the 4B tier answer the exact same 384-token LRUCache task already run on LOOM 30B and LOOM 8B?

This is a practical tier comparison, not a one-factor model-size experiment. The 4B uses its historically validated llama.cpp/Metal Q4_K_M path while the 8B uses Direct MLX 3-bit/group64 and the 30B uses the LOOM expert-major runtime. Runtime/model/quantization differences are part of each tier's practical system condition and must be reported explicitly.

## Recovered historical LOOM 4B condition

Canonical historical runtime control:
`research/runtime/llama-cpp-4b-control-001.md`

Historical runner:
`scripts/llama_cpp_4b_control.py`

Frozen identities:
- model repo: `Qwen/Qwen3-4B-GGUF`;
- model file: `Qwen3-4B-Q4_K_M.gguf`;
- quantization: `Q4_K_M`;
- model SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- historical size: `2.326 GiB`;
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- Metal build: historical `build-loom-metal`;
- `-ngl -1` full/max Metal offload request;
- Flash Attention `auto`;
- Apple M1 / 8 GB.

Historical control measured text generation `22.33 tok/s ± 0.02`, prompt processing `230.85 tok/s ± 0.12`, peak process RSS `1914.91 MB`, peak swap `1097.19 MB`, minimum free memory `22%`.

## Artifact rule

No network/model acquisition is authorized.

Pi must first check the historical active-clone path:
`results-local/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`

and verify the exact SHA above.

If that exact artifact is absent, Pi may inspect the archive only by explicit absolute path:
`<external-archive>/models/Qwen3-4B-GGUF/`

Pi must not silently copy, redownload, convert or requantize an artifact. If no exact SHA-matching Q4_K_M artifact is available, classify `LOOM_4B_BAKEOFF_ARTIFACT_NOT_READY` and STOP before model execution.

## Runtime rule

Verify before execution:
- llama.cpp source exists locally at the pinned commit;
- historical Metal build/server or required executable exists;
- Metal backend is visible;
- no rebuild/update/package mutation is allowed in this checkpoint.

If the pinned runtime is unavailable, classify `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY` and STOP. Do not substitute Ollama.

## New runner

Create only:
`scripts/loom_4b_practical_bakeoff_runner_001.py`

Do not modify any historical runner or production runtime.

The runner may reuse code/semantics from the historical 4B runtime/quality runners but must be a bounded one-shot evaluator.

Preferred request surface: the already validated pinned `llama-server`/Metal path, using its Qwen3 chat-template support and a streamed local request so TTFT is observable. If historical tooling only supports a different already-validated llama.cpp request surface, preserve it and document the exact factor; do not invent a new serving stack.

## Frozen messages

System message EXACTLY:
`You are a helpful assistant. Answer clearly and directly.`

User prompt EXACTLY:
`Scrivi in Python una classe LRUCache con capacità configurabile. Requisiti: deve avere i metodi get(key) e put(key, value); get deve restituire -1 se la chiave non esiste; ogni get o put deve aggiornare l'ordine di utilizzo; quando la cache supera la capacità deve eliminare l'elemento usato meno recentemente; get e put devono avere complessità O(1); non usare functools.lru_cache; aggiungi alla fine un piccolo test eseguibile. Prima spiegami in massimo 5 righe la strategia scelta, poi scrivi il codice completo.`

Maximum generated tokens EXACTLY: `384`.

Generation:
- deterministic greedy / temperature 0;
- no retries;
- one request;
- natural EOS or 384-token stop.

## Forbidden changes

No:
- Ollama substitution;
- model download;
- model conversion/requantization;
- llama.cpp update/rebuild;
- prompt optimization;
- extra system instructions;
- skills/protocol retrieval;
- memory/RAG;
- tools;
- test feedback;
- self-repair/retry;
- Heretic/behavioral editing;
- speculative decoding;
- UI work.

## Required preflight

Before inference prove:
1. exact active Git root;
2. exact model path and SHA;
3. model filename/quantization;
4. exact llama.cpp commit/build identity;
5. Metal device/backend available;
6. host memory/swap telemetry readable;
7. no network/model acquisition occurred;
8. source diff contains only the new runner.

## Required evidence

Persist under:
`results-local/research/4b-practical-bakeoff-runner-001/<timestamp>/`

Record:
- exact provenance;
- exact rendered/request messages or deterministic request payload;
- generated text;
- output token count;
- EOS vs length stop;
- task completion `COMPLETE` or `INCOMPLETE`;
- TTFT;
- prompt/prefill tokens, wall and tok/s when available;
- generation wall and tok/s;
- end-to-end wall and output tok/s;
- p50/p95 per-token or streamed-token timing when meaningfully observable;
- server startup/readiness separately from request timing;
- process RSS;
- system free-memory and swap before/after/peak/min;
- Metal/runtime diagnostics;
- runner full wall;
- exact evidence path.

If llama.cpp exposes authoritative internal timing counters, persist them and distinguish them from client-observed wall/TTFT.

## Task completion rule

Runner validity and task quality are separate.

The runner may PASS with a 384-token length stop, but task status MUST be `INCOMPLETE` if the requested executable class/test is visibly unfinished or syntactically incomplete.

Do not award completion merely for choosing the correct data structure.

## Classification

`LOOM_4B_BAKEOFF_RUNNER_PASS` only if provenance/runtime/model/request evidence is valid and exactly one frozen inference executes.

Otherwise fail closed with a mechanical readiness/evidence classification.

## Interpretation boundary

The matched 4B result may be compared descriptively with:
- LOOM 8B matched LRUCache result: 384 tokens, TTFT `2.992 s`, generation `13.357 tok/s`, end-to-end `12.275 tok/s`, task INCOMPLETE;
- LOOM 30B manual LRUCache: same 384-token cap, task INCOMPLETE, canonical runtime around `1.1 tok/s`, subjective waiting minutes.

Do not claim model-size causality because runtimes/quantization/model variants differ.

After this one-shot result, freeze a broader compact 4B/8B/30B practical suite before choosing router thresholds.