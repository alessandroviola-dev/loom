# Stretch 002 — Single-Layer MLX Materialization + Eviction — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can LOOM materialize only one transformer layer from the verified local `Qwen3-8B-3bit` safetensors artifact into MLX memory, then release that layer and recover MLX allocator memory, without constructing or evaluating the full model?

## Motivation

Stretch 001 (`20260819-154335`) established:
- 36/36 transformer layers are exactly addressable;
- each layer contains 25 tensors and exactly 84,427,264 B (~80.52 MiB);
- shared/non-layer payload is 544,546,816 B;
- layer 18 selective disk I/O read exactly 84,427,264 B at 1153.794 MiB/s;
- no model launch was needed.

Result:
`research/stretch/layer-streaming-feasibility-001-result.md`

## Subject / environment

Model directory:
`results-local/mlx/models/Qwen3-8B-3bit`

Weight file:
`model.safetensors`

Frozen Direct MLX environment:
`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`

Expected package versions:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Probe layer: **18**.

## Scope boundary

This experiment does **not**:
- build `qwen3.Model`;
- instantiate 36 transformer blocks;
- create tokenizer/KV cache;
- perform attention/MLP forward computation;
- generate tokens;
- claim end-to-end layer-streamed inference.

It tests raw MLX tensor materialization and allocator reclamation only.

## Frozen method

### Stage A — provenance and host preflight

Require:
- Darwin arm64;
- frozen Direct MLX venv and exact package versions;
- local `model.safetensors` present;
- safetensors header maps exactly 25 tensors to `.layers.18.`;
- exact selected byte total = 84,427,264 B;
- 3 consecutive host samples >=60% free memory;
- swap <=5600 MB;
- no Ollama model launch and no network/download.

The 60% gate is specific to this bounded ~80.52 MiB materialization probe and is not inherited from Amplify's 70% model-generation gate.

### Stage B — lazy file registration check

Inside the frozen MLX child process:
1. call `mx.clear_cache()` and `mx.reset_peak_memory()`;
2. record MLX active/cache/peak memory baseline;
3. call `mx.load(model.safetensors)`;
4. retain only the exact 25 arrays whose names belong to layer 18;
5. drop the dictionary references to all non-selected arrays and run Python GC;
6. record MLX active/cache memory **before** `mx.eval(selected_layer)`.

Guard against accidental full-file eager loading:
- pre-eval active-memory increase must be <=32 MiB relative to baseline.

If this threshold is exceeded, classify `EAGER_FULL_FILE_LOAD_SUSPECTED` and do not claim single-layer materialization.

### Stage C — materialize selected layer

- `mx.eval(selected_layer)` on the selected 25-array tree only;
- record active/cache/peak MLX memory;
- record system free memory, swap and child RSS continuously from the parent;
- materialization must complete without safety breach.

Evidence gate:
- active-memory increase after eval must be >0;
- selected tensor count and expected byte total must remain exact.

No requirement is imposed that MLX active-memory delta equal safetensors bytes exactly because allocator representation/alignment may differ.

### Stage D — eviction/recovery

- delete all references to selected arrays;
- run `gc.collect()`;
- call `mx.clear_cache()`;
- wait briefly;
- record final active/cache/peak memory.

`EVICTION_PASS` requires:
- final active memory <= baseline active + 1 MiB;
- final cache memory <= baseline cache + 1 MiB.

System free-memory recovery is recorded but is diagnostic rather than a strict gate because macOS memory accounting/page cache may lag allocator state.

## Runtime safety

Parent monitor samples system memory and swap while child executes.

Abort and classify `PARTIAL_RESOURCE_FAIL` if:
- free memory <5%; or
- swap >5600 MB.

Missing required system telemetry => `TELEMETRY_FAIL`.

No process purge, swap manipulation or model deletion is allowed.

## Classifications

- `SINGLE_LAYER_MLX_EVICTION_PASS`
- `SINGLE_LAYER_MLX_MATERIALIZATION_PASS_EVICTION_INCONCLUSIVE`
- `EAGER_FULL_FILE_LOAD_SUSPECTED`
- `HOST_STATE_NOT_READY`
- `PREFLIGHT_FAIL`
- `RUNTIME_FAIL`
- `PARTIAL_RESOURCE_FAIL`
- `TELEMETRY_FAIL`

## Decision rules

1. If `SINGLE_LAYER_MLX_EVICTION_PASS`: preregister Stretch 003 as a **two-layer sequential materialize/evaluate/evict cycle**, still without full model generation. The purpose is to prove repeated bounded residency rather than a one-off load.
2. If materialization passes but eviction is inconclusive: diagnose allocator/cache behavior before any streamed forward prototype.
3. If eager full-file loading is detected: do not reinterpret it as a layer-streaming pass; investigate a lower-level selective tensor loader.
4. If resource safety fails despite the bounded layer: stop and diagnose before continuing.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_single_layer_mlx_materialization_002.py
python3 scripts/stretch_single_layer_mlx_materialization_002.py
```

No model download is expected.