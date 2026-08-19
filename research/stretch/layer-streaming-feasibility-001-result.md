# Stretch 001 — Dense Layer Streaming Feasibility — Result

Date: 2026-08-19
Run: `20260819-154335`
Classification: **LAYER_ADDRESSABLE_IO_PASS**

## Subject

Local artifact:
`results-local/mlx/models/Qwen3-8B-3bit`

No model launch, no MLX model construction, no network access and no download occurred.

## Stage A — safetensors layer map

- `num_hidden_layers`: 36
- safetensors shards: 1
- tensor count: 907
- total tensor bytes: 3,583,928,320 B
- discovered layer IDs: 0..35
- missing layer IDs: none
- unexpected layer IDs: none
- non-layer/shared bytes: 544,546,816 B
- every transformer layer: exactly 84,427,264 B
- layer min/mean/median/max: 84,427,264 B

Derived presentation values:
- per-layer: ~80.52 MiB
- shared/non-layer: ~519.32 MiB
- total tensor payload: ~3.338 GiB
- all transformer-layer payload: 3,039,381,504 B (~2.831 GiB)

## Stage B — exact selective I/O

Probe layer: 18

- tensors: 25
- shards touched: 1
- expected bytes: 84,427,264
- bytes actually read: 84,427,264
- exact byte-count match: PASS
- wall: 0.069784 s
- effective throughput: 1153.794 MiB/s
- SHA-256: `2185c6f5cf1528ad8c0789426491e88ba6acc9ca36d11992a95742d4bd5f452d`

System state:
- pre-I/O: 68% free / 850.5 MB swap
- post-I/O: 69% free / 850.5 MB swap
- disk free: 36.310 -> 36.310 GiB

## Canonical interpretation

The verified local Qwen3-8B 3-bit safetensors artifact is cleanly transformer-layer-addressable. LOOM can identify every tensor belonging to a chosen layer and read exactly that layer's byte ranges from storage without reading/materializing the full model.

This is a prerequisite for dense layer streaming, not evidence that end-to-end lower-RAM inference already works. The next experiment must test whether one selected layer can be materialized in MLX and subsequently released with observable allocator/system-memory recovery without constructing the full model.

Do not infer token throughput for a future streamed runtime directly from the 1153.794 MiB/s single selective-read measurement; OS page cache, repeated reads, compute overlap and per-token rereading can materially change effective behavior.