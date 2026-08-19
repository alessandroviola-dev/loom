# Stretch 001 — Dense Layer Streaming Feasibility — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Does the already-cached dense Qwen3-8B MLX artifact have a sufficiently clean layer-addressable safetensors layout that LOOM can read exactly one transformer layer from SSD without reading/materializing the full model?

This is the first concrete experiment in the **Stretch — big model, small machine** branch.

## Important scope boundary

Stretch 001 is **not yet end-to-end streamed inference**.

It tests two prerequisites only:
1. exact static mapping from safetensors tensors to transformer layer IDs and byte ranges;
2. selective disk I/O of one complete layer using only those byte ranges.

No claim about lower-RAM LLM inference is allowed from this experiment alone.

If Stretch 001 passes, the next experiment may materialize one layer into MLX and verify release/reclamation behavior before attempting any full forward pass.

## Subject artifact

Preferred local subject:
`mlx-community/Qwen3-8B-3bit`

Rationale:
- already acquired and verified during Direct MLX work;
- dense Qwen3 architecture, suitable for layer decomposition;
- no new model download required;
- using an 8B artifact makes the storage hierarchy question meaningful while this first probe itself does not load the model.

Fallback is **not automatic**. If the preferred artifact is not found locally, classify `MODEL_NOT_FOUND` and stop.

## External implementation rationale

Primary-source facts checked on 2026-08-19:
- safetensors stores tensor names, shapes and exact data offsets in a JSON header and supports loading selected tensors/slices;
- MLX uses lazy arrays in several file-loading paths, but normal mlx-lm model loading evaluates model parameters and does not constitute a finished out-of-core layer-streaming runtime;
- an open MLX feature request explicitly proposes block-wise/memory-mapped model weights, asynchronous prefetch and residency/eviction for models larger than RAM;
- MLX exposes active/cache memory instrumentation and cache controls that can support later materialization experiments.

Therefore LOOM treats layer streaming as a runtime-research problem, not as a pre-existing MLX-LM feature.

## Stage A — header-only layer map

The runner must:
- locate only an already-cached local snapshot of `mlx-community/Qwen3-8B-3bit`;
- perform no network access and no model download;
- read `config.json`;
- read only the first 8 bytes + JSON header of every `.safetensors` file;
- build a catalog of tensor name, dtype, shape, shard, relative offset and exact byte size;
- map tensors to layer IDs using the canonical `.layers.<N>.` name component;
- compare discovered layer IDs with `num_hidden_layers` from config;
- report per-layer tensor counts and exact byte totals;
- report non-layer/shared tensor bytes separately.

Stage A PASS requires:
- `num_hidden_layers` is a positive integer;
- every layer ID from 0 to `num_hidden_layers - 1` is present;
- no out-of-range layer ID is present;
- every mapped tensor has valid non-negative offsets and positive byte length.

## Stage B — selective layer I/O

If Stage A passes:
- choose the middle transformer layer by default (`num_hidden_layers // 2`), unless `--probe-layer` is explicitly supplied;
- read from each safetensors shard only the exact byte ranges belonging to that layer;
- read incrementally in bounded chunks, not by loading the full tensor set into memory;
- compute a streaming SHA-256 digest over the selected layer bytes;
- verify total bytes read equals the exact layer byte total from the header map;
- record wall time and effective MiB/s;
- record system free-memory and swap immediately before and after selective I/O.

The digest is an integrity fingerprint for the probe, not a model-quality check.

## Safety / storage policy

- no model launch;
- no MLX model construction;
- no Ollama interaction;
- no cache mutation;
- no model-file writes;
- no model deletion;
- no new download;
- only a small JSON result may be written under `results-local/stretch/...`;
- record disk free before/after.

## Classifications

`LAYER_ADDRESSABLE_IO_PASS`
- Stage A complete layer map PASS;
- Stage B reads exactly the selected layer bytes;
- no I/O or telemetry error.

`LAYER_MAP_FAIL`
- expected transformer-layer mapping cannot be established from the cached artifact.

`SELECTIVE_IO_FAIL`
- map is valid but exact selected byte ranges cannot be read/verified.

`MODEL_NOT_FOUND`
- preferred local model snapshot is absent; no download attempted.

`TELEMETRY_PARTIAL`
- layer map/I/O succeeds but required host telemetry cannot be parsed; do not treat as model/runtime failure.

## Required output

Record:
- resolved local model directory/snapshot ID
- model/config metadata
- safetensors shard count
- total tensor bytes
- total mapped layer bytes
- non-layer/shared bytes
- discovered layer IDs
- per-layer byte min/mean/median/max
- selected probe layer
- selected layer tensor count/shard count/bytes
- selective read wall time and MiB/s
- SHA-256 fingerprint of selected layer byte stream
- free-memory/swap before and after
- disk free before/after
- classification.

## Decision after Stretch 001

If `LAYER_ADDRESSABLE_IO_PASS`:
- preregister Stretch 002: **single-layer MLX materialization + eviction**;
- load only one layer's tensors into MLX, force evaluation, measure active/cache/system memory, delete references, collect/clear cache using a version-safe protocol, and verify memory recovery;
- still do not attempt full token generation yet.

If `LAYER_MAP_FAIL`:
- inspect artifact naming/sharding before designing custom format conversion.

If `SELECTIVE_IO_FAIL`:
- diagnose file-layout/read-path issue before any MLX work.

No large-model acquisition is authorized by Stretch 001.

## Planned execution

Runner:
`scripts/stretch_layer_streaming_feasibility_001.py`
