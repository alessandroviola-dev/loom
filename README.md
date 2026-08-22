# LOOM

**Big models. Small machines.**

LOOM is a research project focused on making capable local AI — including self-hosted coding agents and larger language models — practical on constrained consumer hardware.

The initial reference platform is an Apple Silicon M1 Mac with 8 GB unified memory.

## Project objective

LOOM targets the strongest practical **full-parameter-count** local model that can be made usable on small hardware while jointly optimizing four axes:

1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

A model is not considered fully promoted as a final LOOM-produced LLM until it also has a validated decensored behavioral profile. That profile may be produced with the Heretic approach or with a LOOM-native independently implemented equivalent, and must be evaluated for collateral capability/resource damage rather than treated as a prompt-only jailbreak.

Frozen requirement:
`research/behavior/decensoring-requirement-v1.md`

## Research directions

- Local self-hosted coding agents
- Ollama and MLX inference
- Direct MLX execution
- llama.cpp and aggressive GGUF quantization
- CPU/GPU hybrid offload
- Memory compression and swap behavior
- SSD-backed inference and expert/layer streaming
- Mixture-of-Experts (MoE)
- Colibrì experiments
- Reproducible benchmarks for quality, speed and memory pressure
- Contrastive residual-direction analysis and reversible low-rank behavioral editing
- Decensored / behavioral-freedom model profiles with preservation benchmarks

## Current checkpoint

The active branch is currently characterizing and reducing fixed and per-layer costs in exact real-M1 partial-residency execution. See `HANDOFF.md` for the canonical checkpoint and `ROADMAP.md` for the ordered research path.

The behavioral-editing requirement does not interrupt the active memory/runtime sequence; it is a later model-promotion requirement unless a frozen experiment explicitly enters that research axis.

## Project rule

`HANDOFF.md` is the canonical active state of the project and must be updated after every meaningful project step.
