# LOOM — DFlash Target Interface 001 Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`
Raw evidence: `results-local/research/dflash-target-interface-001/20260824T101801Z/`

## Purpose

Validate the target-side interface required by the exact-target DFlash speculator without integrating any drafter weights, fusion, block masking or speculative acceptance.

## Result

The current Qwen3-30B-A3B external-expert target can expose the exact DFlash hidden-state taps while preserving target behavior and external-expert lifecycle.

### Tap contract

Required tap IDs: `[1,12,23,34,45]`.

Recovered semantics:
- IDs are **1-based post-block outputs**;
- tap `n` corresponds to `layers[n-1]` output;
- prefill shape: `[1,28,2048]`;
- decode shape: `[1,1,2048]`;
- dtype: `float32`;
- captured references are released before the next forward.

### Correctness

Baseline vs taps-enabled target:
- router parity: bitwise exact;
- final logits: bitwise exact;
- generated token sequence parity: `[19,151645]`;
- no routed-expert accumulation.

### Tap memory

Logical tap payload:
- prefill: `1,146,880 B`;
- decode: `40,960 B`.

Measured runtime memory:
- baseline MLX peak: `881,332,232 B`;
- taps-enabled MLX peak: `899,944,456 B`;
- delta: `+18,612,224 B`;
- RSS high-water: `965,066,752 B` in both runs;
- swap delta: `0.0 MiB`.

### Ownership

- routed expert tensors before/after: `0`;
- routed expert bytes before/after: `0 B`;
- final logical live expert bytes: `0 B`.

## Gate

`PASS`.

The exact DFlash target taps are now a proven runtime interface on the M1/8-GB external-expert target. Tap capture is memory-safe at this checkpoint and does not alter routing, logits or generated tokens.

## Next decision

A multi-position/block target verifier is justified: **YES**.

The next checkpoint should prove, independently of the learned DFlash drafter, that the target can verify multiple candidate positions with correct causal/KV semantics and external-expert lifecycle. It should compare block verification against sequential teacher-forced target evaluation and quantify layer-local expert union bytes per verified position. DFlash integration remains blocked until that verifier passes.
