# Baseline 001 — Qwen 3.5 4B MLX / Ollama

Date: 2026-08-18
Status: COMPLETE

## Configuration

- Runtime: Ollama
- Model: `qwen3.5:4b-mlx`
- Backend: MLX (confirmed in `server.log`)
- Processor: 100% GPU
- Context: 4096
- Model size shown by `ollama ps`: 4.3 GB

## Throughput test

- Output tokens: 256
- Generation: 15.02 tok/s
- Prompt tokens: 56
- Prompt processing: 4.36 tok/s
- Total duration: 30.01 s
- Load duration: 0.07 s

## Memory — model resident

- PhysMem used: 7500 MB
- Wired: 2037 MB
- Compressor: 3131 MB
- Unused: 130 MB
- memory_pressure free: 32%
- Swap used: 3833.81 MB

## Memory — model unloaded

- PhysMem used: 6529 MB
- Wired: 2058 MB
- Compressor: 811 MB
- Unused: 1101 MB
- memory_pressure free: 62%
- Swap used: 1857.19 MB

## Conclusion

The 4B MLX configuration is practical at roughly 15 tok/s generation, but it materially increases compression and swap activity. This establishes the initial practical ceiling that larger-model techniques must improve upon or justify through higher task quality.
