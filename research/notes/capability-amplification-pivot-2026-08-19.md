# LOOM Research Pivot — Capability Amplification & Memory Hierarchy

Date: 2026-08-19
Status: **ADOPTED**

## Decision

LOOM is no longer centered primarily on the question:

> What is the largest local LLM that can be made to fit into 8 GB?

The main research question becomes:

> **What is the greatest useful capability that can be produced by an 8 GB local system?**

This explicitly allows the system around the model to be part of the research object: deterministic validation, repair, agents, tools, retrieval, specialization/distillation, routing, and later memory hierarchy / SSD streaming.

## Evidence motivating the pivot

The runtime frontier is already informative:
- Direct MLX makes Qwen3-8B 3-bit full-session runnable, but frozen coding quality did not clearly improve over smaller references.
- Qwen3-8B 4-bit repeatedly approaches or crosses the reference M1/8 GB free-memory boundary in continuous coding workloads.
- Repeated quantization/context/KV rescues risk becoming an open-ended local optimization ladder.

At the same time, LOOM already has strong internal evidence that system design matters:
- frozen 4B single-shot baseline: artifact 40.71/100, strict/delivery-adjusted 30.00/100, delivery 3/6;
- same `qwen3.5:4b-mlx` family through Pi file-agentic mode: artifact/delivery-adjusted 77.15/100, delivery 6/6.

The model did not become larger; the surrounding interaction/delivery system changed.

## Two-track program

### Amplify — small model, big capability

Primary subject first: `qwen3.5:4b-mlx` via Ollama.

Progression should add one factor at a time where possible:
1. frozen single-shot baseline;
2. deterministic validator + max one repair (`Capability Amplifier 001`);
3. later planner/verifier or tool loop if justified;
4. retrieval if justified;
5. specialization / LoRA / SFT / distillation only after inference-time amplification is characterized.

A faster llama.cpp 4B remains a secondary control after the mechanism is established on the canonical Ollama/MLX 4B.

### Stretch — big model, small machine

Later investigate architectures that avoid requiring the full useful model state to be resident at once:
- SSD / layer / expert streaming;
- MoE expert offload;
- hierarchical caching;
- selective routing from a small resident controller;
- other runtime mechanisms justified by evidence.

Colibrì/SSD-streaming research moves into this track rather than being the immediate main branch.

## Measurement philosophy

LOOM should no longer optimize tokens/second alone.

Every meaningful capability experiment should record a joint frontier including:
- end-to-end quality;
- structured delivery/reliability;
- RAM/free-memory/swap pressure;
- total wall time;
- total model calls;
- total prompt/generated tokens;
- disk footprint when relevant.

The goal is not to claim that a small model becomes intrinsically more intelligent than a large model. The goal is to determine when a **small-model system** can outperform a larger naive model on a useful workload under constrained hardware.

## Immediate next experiment

`research/amplify/capability-amplifier-001-plan.md`

Primary model: `qwen3.5:4b-mlx`.

Mechanism: frozen initial single-shot attempt + deterministic validation + at most one repair.
