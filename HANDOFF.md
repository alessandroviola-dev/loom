# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is optimizing useful capability on an Apple M1 / 8 GB reference system through two coordinated tracks: **Amplify** (small model, better system capability) and **Stretch** (larger capability through memory hierarchy / out-of-core execution).

Current checkpoint: `STRETCH_001_LAYER_ADDRESSABILITY_READY`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware.

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset, replace or destroy production Pi configuration.
- Controlled Pi experiments use run-local `PI_CODING_AGENT_DIR`.
- Never silently delete verified models or canonical results.
- Record disk around model acquisitions / large runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory and swap are decisive; process RSS is diagnostic only.
- Do not relabel harness/parser/capture defects as model failures.
- Do not assign aggregate quality scores to partial resource/runtime runs.
- Change one experimental factor at a time for causal tests.
- Do not weaken guardrails post-hoc.
- No automatic context-reduction rescue ladders.
- No new large-model acquisition until local-artifact feasibility is exhausted.

Verified GGUF, Direct MLX 3-bit and Direct MLX 4-bit artifacts remain retained.

# Frozen references

## Canonical Ollama/MLX 4B

Model: `qwen3.5:4b-mlx`
Context baseline: 4096

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71/100
- strict / delivery-adjusted 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- same local 4B family through Pi file tools
- artifact / delivery-adjusted 77.15/100
- strict protocol-adjusted 60.00/100
- delivery 6/6
- protocol 4/6
- no hidden-test feedback
- whole run ~612 s.

Canonical system finding:
> Replacing fragile full-file JSON transport with direct filesystem tools materially improved end-to-end coding usefulness for the same local 4B family. This motivates the Amplify branch.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4 control:
- pp512 230.85 tok/s
- tg128 22.33 tok/s
- minimum free memory 22%.

This remains the strongest alternate 4B execution profile. It is not the same model/runtime/quantization condition as `qwen3.5:4b-mlx`, so comparisons must be capability/efficiency comparisons rather than runtime-only causal claims.

## 8B runtime frontier

Direct MLX Qwen3-8B 3-bit:
- smoke PASS
- T01 PASS
- full Coding Benchmark COMPLETE
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57/100
- delivery-adjusted 27.86/100
- delivery 2/6
- technically stable but not promoted on quality.

Direct MLX Qwen3-8B 4-bit:
- smoke PASS
- standalone T01 PASS narrowly
- continuous full profile repeatedly crosses frozen memory guardrail
- exact unquantized-KV 4096 profile closed.

llama.cpp Qwen3-8B:
- Q2 runnable/API-servable but poor frozen coding delivery
- Q3 NP1 + Q8_0 KV API smoke PASS
- real Coding T01 reaches 4% free and aborts.

# Research tracks

## Track A — Amplify

Goal: improve end-to-end capability of a smaller resident model through deterministic scaffolding, validation, repair, tools, planner/verifier loops, retrieval and eventually specialization/distillation.

### Amplifier 001 — warm-resident

Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Diagnostic: `research/amplify/capability-amplifier-001-resource-diagnostic.md`

Run `20260819-142640`:
- host gate 74/74/74% free
- T01 initial 6/6, 15/15
- T02 initial 3/7, 6.43/15
- repair authorized
- `PARTIAL_RESOURCE_FAIL`: free 4% <5%
- peak swap 2500.88 MB
- no aggregate quality result.

Interpretation: warm continuous Ollama residency lacks sufficient headroom. Do not call this a leak.

### Amplifier 002 — call-isolated

Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Diagnostic: `research/amplify/capability-amplifier-002-resource-diagnostic.md`

One changed factor vs 001: unload and confirm target absent from `ollama ps` before/after every model call.

Valid run `20260819-144256`:
- host gate 71/72/72% free
- T01 initial 6/6
- T02 initial 3/7
- unload confirmed
- T02 repair starts 68% free / 2346.94 MB swap
- trajectory 68 -> 63 -> 23 -> 16 -> 4% free
- `PARTIAL_RESOURCE_FAIL`
- peak swap 2611.50 MB.

Interpretation: call isolation works but is insufficient. Recovery gating alone is not the leading fix.

### Amplifier 003 — repair context 3072 — FROZEN RESOURCE FAIL

Plan: `research/amplify/capability-amplifier-003-repair-context-3072-plan.md`
Runner blob: `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`
Diagnostic: `research/amplify/capability-amplifier-003-resource-diagnostic.md`

Valid run `20260819-150342`:
- initial context 4096
- repair context 3072
- host gate 71/74/74% free
- T01 initial 6/6
- T02 initial 3/7
- T02 repair starts 70% free / 2069.12 MB swap
- repair trajectory 70 -> 65 -> 31 -> 7 -> 6 -> 4% free
- `PARTIAL_RESOURCE_FAIL`: free 4% <5%
- overall peak swap 2318.12 MB
- post-abort unload returns 70% free
- no completed repair API response.

Important observation:
- successful T01/T02 initial calls themselves reach only 6% free.

Interpretation:
> Reducing repair context from 4096 to 3072 changes pressure but does not make the repair safe. Do not automatically descend to 2048 and do not infer a specific KV/allocator/MLX/Ollama root cause.

### T02 repair prompt anatomy — FROZEN

Record:
`research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`

Read-only measurement:
- initial prompt 1638 UTF-8 bytes
- repair prompt 4573 UTF-8 bytes
- repair / initial = 2.792x
- validation feedback = 2762 B
- validation feedback ≈60.4% of full repair prompt
- current candidate = 458 B
- original task prompt = 681 B
- repair API response absent.

Interpretation:
> Repair information is materially inflated and the largest incremental component is deterministic validation feedback. One bounded Compact Repair experiment is justified.

### Amplifier 004 — Compact Feedback — READY / QUEUED

Plan:
`research/amplify/capability-amplifier-004-compact-feedback-plan.md`

Runner:
`scripts/capability_amplifier_004_compact_feedback.py`

Runner blob:
`3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`

Single changed factor vs 003:
- deterministic variable failure-detail body capped at **768 UTF-8 bytes**.

Preserved:
- model/runtime
- initial context 4096
- repair context 3072
- task prompt in repair
- current candidate in repair
- validation/test mechanism
- max one repair
- candidate selection
- sampler/output budget
- call isolation
- host gate and guardrails
- scorer/task order
- no Pi/retrieval/planner/human intervention.

For test failures, preserve `Passed X/Y frozen tests.` plus a deterministic UTF-8-safe tail of scorer stderr. For parser failures, preserve parser-error first line plus a deterministic raw-output tail. No semantic/model-based summarizer.

Decision rule:
- if 004 still resource-fails, stop prompt-level rescue on this Ollama/MLX profile; do not create a budget ladder.
- if COMPLETE, freeze quality/resource/efficiency and apply existing prospective gates.

Amplifier 004 is ready but is **not the immediate next run**; Stretch 001 is executed first.

# Track B — Stretch / Memory Hierarchy

Goal: explore whether model capability can exceed normal RAM residency by using SSD/RAM as an explicit hierarchy: layer streaming, expert streaming, prefetch, eviction, caching and later selective routing.

Core distinction:
- dense layer streaming uses all transformer layers but keeps only a bounded subset resident at once;
- dynamic layer skipping / early exit is a separate later research problem and must not be assumed safe for a normally trained dense model.

Current external implementation boundary:
- safetensors exposes exact per-tensor byte offsets and supports selected tensor/slice access;
- MLX has lazy array/file-loading behavior and explicit memory instrumentation/cache controls;
- normal mlx-lm model loading is not a finished out-of-core layer-streaming runtime;
- current MLX discussions/feature requests explicitly identify block-wise/mmap weights, asynchronous prefetch and eviction as missing/desired capabilities for larger-than-RAM models.

Therefore LOOM treats this as custom runtime research, not configuration tuning.

## Stretch 001 — Dense Layer Streaming Feasibility — READY

Plan:
`research/stretch/layer-streaming-feasibility-001-plan.md`

Runner:
`scripts/stretch_layer_streaming_feasibility_001.py`

Runner blob:
`890444928abd6cc24e7194317c92b36b50fd994b`

Preferred subject:
`mlx-community/Qwen3-8B-3bit`

Reason:
- already cached/verified from Direct MLX work
- dense architecture
- no new download
- meaningful 8B weight footprint while the probe itself does not launch the model.

### Stretch 001 Stage A

Header-only safetensors inspection:
- locate existing local snapshot only
- no network/download
- parse `config.json`
- read only safetensors 8-byte header length + JSON header
- map every tensor to `.layers.<N>.` where applicable
- compare exact layer IDs against `num_hidden_layers`
- compute exact bytes/tensor and bytes/layer
- report non-layer/shared bytes separately.

Stage A PASS requires exact layer coverage 0..N-1 with valid ranges.

### Stretch 001 Stage B

Selective disk-I/O probe:
- default target = middle transformer layer
- read only exact byte ranges for that layer
- bounded 4 MiB read chunks
- no full tensor/model materialization
- streaming SHA-256 fingerprint
- verify bytes read == header-derived expected layer bytes
- record wall time and effective MiB/s
- record free-memory/swap before and after.

Classifications:
- `LAYER_ADDRESSABLE_IO_PASS`
- `LAYER_MAP_FAIL`
- `SELECTIVE_IO_FAIL`
- `MODEL_NOT_FOUND`
- `TELEMETRY_PARTIAL`.

No model launch, no MLX model construction, no cache mutation, no model-file writes, no model deletion, no download.

## If Stretch 001 passes

Preregister Stretch 002:
**Single-layer MLX materialization + eviction**.

Stretch 002 should:
- materialize only one layer's tensors in MLX
- force evaluation
- measure MLX active/cache memory and system free/swap
- release all references
- use a version-safe GC/cache-reclamation protocol
- verify system/MLX memory recovery
- still not run full token generation.

Only after that passes should LOOM attempt a streamed full forward path.

# Exact next step

Run Stretch 001 only:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_layer_streaming_feasibility_001.py
python3 scripts/stretch_layer_streaming_feasibility_001.py
```

Expected behavior:
- no Ollama launch
- no MLX model launch
- no network/download
- reads the already cached 8B 3-bit safetensors metadata and one selected layer's byte ranges
- writes only a small JSON summary under `results-local/stretch/layer-streaming-feasibility-001/<runid>/`.

If the local cached snapshot is not found, do not download anything; report the output and diagnose the cache path.

# Continuation rule

After every meaningful experiment/decision/result, update `HANDOFF.md` and `ROADMAP.md` before moving to the next checkpoint.
