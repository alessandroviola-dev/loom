# LOOM

**Big models. Small machines.**

LOOM is a research project focused on making capable local AI — including self-hosted coding agents and larger language models — practical on constrained consumer hardware.

The initial reference platform is an Apple Silicon M1 Mac with 8 GB unified memory.

## Research directions

- Local self-hosted coding agents
- Ollama and MLX inference
- Direct MLX execution
- llama.cpp and aggressive GGUF quantization
- CPU/GPU hybrid offload
- Memory compression and swap behavior
- SSD-backed inference and expert streaming
- Mixture-of-Experts (MoE)
- Colibrì experiments
- Reproducible benchmarks for quality, speed and memory pressure

## Current checkpoint

The first baseline has been completed with Qwen 3.5 4B MLX through Ollama. See `HANDOFF.md` and `benchmarks/results/baseline-001-qwen35-4b-mlx.md`.

## Project rule

`HANDOFF.md` is the canonical state of the project and must be updated after every meaningful project step.
