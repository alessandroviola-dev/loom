# DFlash / Qwen3-30B-A3B relevance 001

Date: 2026-08-23
Status: SOURCE REVIEW COMPLETE — EXPERIMENTALLY RELEVANT

## Trigger

A supplied video (`Qwen3.8 27B + Harness Il Coding Agent LOCALE Definitivo.mp4`) was transcribed locally with faster-whisper and visually audited. The video is useful primarily as a pointer to block speculative decoding / DFlash2, not as evidence that a 27B model fits an 8 GB Mac.

Video findings supplied by Pi:
- presenter machine: MacBook Pro M4 Pro, 24 GB RAM;
- observed memory pressure during 27B use: ~22.68 GB used, 95% RAM, ~7.74 GB swap;
- local baseline around 10.5 eval tok/s in llama.cpp in one shown run; separate Ollama run around 5.99 eval tok/s;
- external M5 Max comparison showed ~34 -> 70 tok/s with DFlash2 (~2.06x), not reproduced locally;
- DFlash2 in the video used a ~2B draft for Qwen3.8-27B and proposed a block for target verification;
- no local acceptance trace was demonstrated in the video;
- video does not show 27B viability on 8 GB.

## Independent verification

Independent source review establishes that DFlash is a real block-diffusion speculative-decoding mechanism. llama.cpp documents `draft-dflash` as producing an entire draft block in one forward pass and then using the target to verify it.

More importantly for LOOM, an exact-target draft already exists:

`RedHatAI/Qwen3-30B-A3B-speculator.dflash`

It is explicitly trained for `Qwen/Qwen3-30B-A3B` and reports:
- model size: ~0.7B parameters;
- five draft transformer layers;
- target hidden-state taps at layers 1, 12, 23, 34, 45;
- deployment example with DFlash speculative decoding;
- per-task average acceptance length approximately 2.46–3.77 in the published table.

This is materially more relevant than the Qwen3.8-27B video draft because it targets the same Qwen3-30B-A3B family currently used by LOOM.

## Critical systems interpretation

DFlash is NOT a memory-fit solution by itself. It adds a draft model and therefore additional residency/workspace pressure.

Its LOOM value is a possible I/O-amortization mechanism:
- a draft block gives the target multiple candidate positions to verify together;
- the target MoE router may select overlapping experts across those positions;
- in an external-expert runtime, each unique expert could in principle be loaded once for all positions routed to it in that verification block;
- therefore the relevant storage variable becomes the UNION of experts selected across a verified block, divided by accepted output tokens, not simply 8 experts/layer/token.

This reduction is NOT yet proven. If routing across block positions has little overlap, DFlash may improve compute utilization while barely reducing external expert bytes/token. If overlap is strong, it could materially reduce storage traffic per accepted token.

## Exact research question

For Qwen3-30B-A3B on LOOM:

`external expert bytes / accepted output token = bytes(union of experts touched in verification block) / accepted tokens`

Measure this empirically before assuming DFlash solves the 918 MiB/token zero-cache baseline.

## Caveats

- DFlash target verification is model/runtime specific.
- Published acceptance results are from GPU server environments, not M1 8 GB.
- Additional draft memory may be material on an 8 GB system.
- A reported public Qwen3-30B-A3B case also exists where DFlash reduced throughput despite acceptance length ~2, showing that acceptance alone does not guarantee wall-clock speedup.
- Any LOOM integration must separate compute speedup, storage-I/O reduction, draft residency cost, and correctness.

## Decision

Promote DFlash/block speculative decoding from a generic long-term idea to a concrete parallel research branch, but do not interrupt device-verified physical-I/O measurement.

Recommended checkpoints:
1. `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`
2. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001` — exact draft size/architecture/quantization feasibility and 8 GB budget impact
3. `LOOM_30B_MOE_BLOCK_ROUTING_OVERLAP_001` — measure union-of-experts across multi-token verification blocks
4. only then decide whether DFlash should be integrated into the external-expert runtime.

No claim that DFlash makes 30B usable on 8 GB is currently supported.
