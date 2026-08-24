# LOOM — 30B DFlash Speculator Static 001 — Result

Date: 2026-08-24
Classification: `CONDITIONAL_STATIC_MEMORY_FIT__INTEGRATION_BLOCKED`
Raw evidence: `results-local/research/dflash-speculator-static-001/20260824T100455Z/`

## Result

Exact-target candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Static audit recovered:
- learned BF16 weight elements: 680,813,824;
- total tensor elements including mappings: 680,997,760;
- published safetensors: 1,362,042,120 B (1.268501 GiB);
- tensor payload: 1,362,035,584 B;
- architecture: 5-layer Qwen3-style drafter, hidden 2048, 32 Q heads, 4 KV heads, head_dim 128, MLP 6144, draft vocab 32,000;
- block size 8, configured proposals 7;
- exact target hidden-state taps: `[1, 12, 23, 34, 45]`;
- tap concatenation width 10,240, fused by `fc[2048,10240] + RMSNorm`;
- fused target context is injected into draft K/V in each draft layer.

Representation accounting:
- BF16 published: 1,362,042,120 B / 1.268501 GiB exact;
- FP16 same-shape: same width-equivalent footprint;
- INT8 raw lower bound: 681,228,296 B / 0.634443 GiB, quantization metadata/scale overhead unverified;
- INT4 raw lower bound: 340,821,384 B / 0.317415 GiB, quantization metadata/scale overhead unverified.

Static M1/8-GB budgeting is plausible. With the measured LOOM hybrid resident basis 1,538,371,592 B, 1 GiB runtime reserve and target BF16 KV, a BF16 drafter at 2,048 target tokens leaves about 4.111 GiB arithmetic headroom under 8 GiB and 2.111 GiB under a conservative 6-GiB process budget. Analytical DFlash BF16 KV is 10,240 B/context-token; a 2,048+8 retained draft cache adds 21,053,440 B (~0.0196 GiB). This is static accounting, not a runtime memory measurement.

## Compatibility

- Current MLX/LOOM runtime: no native DFlash path. Integration requires a custom port.
- llama.cpp upstream: conditional `draft-dflash`/GGUF support exists, but no local executable/GGUF drafter/compatible LOOM external-expert target path is established.
- vLLM publisher path: CUDA/server-oriented and not evidence for M1/8 GB.

Main blockers before integration:
1. capture target taps `[1,12,23,34,45]` in the external-expert target path without changing target semantics;
2. implement/verify target-context fusion and draft block masking;
3. prove exact multi-position target verification while preserving external-expert lifecycle;
4. measure acceptance, routing-union bytes/accepted token, workspace and parity locally.

## Decision

Architecture/bytes: PASS.
Target taps: PASS.
Footprint: `PASS_WITH_QUANTIZATION_LIMIT`.
M1 static memory: `CONDITIONAL_PASS`.
Current-runtime compatibility: `FAIL_NO_NATIVE_PATH`.
Integration: **NO**.

Strongest supported conclusion: the BF16 exact-target DFlash drafter is statically small enough to remain scientifically interesting on M1 8 GB, but it is not integration-ready for LOOM. The next experiment should establish the target-side DFlash interface (tap capture/parity and memory overhead) before any drafter port.
