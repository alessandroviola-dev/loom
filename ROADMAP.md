# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `LOOM_30B_MOE_FEASIBILITY_001_STATIC_CONDITIONAL`
Strategic next: `LOOM_30B_MOE_EXPERT_PACK_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules:
- shared stages should stay resident;
- shared intermediate cleanup consolidation materially helps;
- streamed post-forward cleanup defer materially helps and is safe through four streamed layers;
- select-time GC removal is NO-GO;
- shared eval removal is not a useful axis.

Gradient002 under the promoted lifecycle:
- S0 11.101 tok/s / 90.078 ms
- S1 8.037 / 124.425 ms
- S2 6.546 / 152.775 ms
- S4 5.015 / 199.383 ms

Dense research remains the controlled MLX implementation lab; it is no longer assumed to be the final 32B architecture.

## B — STREAMED-BLOCK-REUSE-AUDIT001 — COMPLETE

Weightless reusable topology is mechanically possible, but current strict MLX binding requires parameter leaves. Construction-only reuse is closed on the present runtime unless binding itself becomes a research factor.

## C — High-leverage architecture branch — ACTIVE

### C1 — Sparse MoE / external experts — HIGHEST PRIORITY

Current target: `Qwen/Qwen3-30B-A3B-MLX-4bit`.

Static local audit confirmed:
- 48 layers
- 128 routed experts/layer
- top-k 8
- 16,220,499,968 B total stored tensor payload
- only 819,015,680 B (0.763 GiB) mandatory/non-routed
- 15,401,484,288 B (14.344 GiB) routed expert bank
- one expert 2,506,752 B
- zero-cache selected-expert traffic 962,592,768 B = 918 MiB/token

This validates the basic sparse-capacity premise but does not yet validate useful speed.

### C2 — Flash/storage layout — NOW ACTIVE

Current safetensors layout is expert-bank-major. One expert is split across 9 discontiguous slices; median useful/span efficiency is only 0.080028% if treated as broad contiguous spans.

Decision: `REPACK_RECOMMENDED` before serious external-expert inference.

Next representation should make each complete expert, or a small number of expert components, directly addressable through compact contiguous reads.

### C3 — Expert cache/locality — NOT YET MEASURED

A 4–6 GiB static model budget could theoretically hold about 22.6%–36.5% of the full expert bank after mandatory shared tensors, but this says nothing about real cache hit rate.

Do not assume hot experts, temporal locality or route predictability. Measure them later from real routed execution traces.

### C4 — Multi-token/block amortization

Still strategically important if expert traffic remains dominant after packing/cache. Relevant approaches include Multi-token Prediction, Medusa, EAGLE and Lookahead Decoding.

### C5 — Custom LOOM architecture fallback

If existing MoE remains too bandwidth-bound after layout/cache/amortization work, derive a LOOM-native model-system design from measured failure modes: sparse neuron clusters, recursive/shared layers, learned external memory, recurrent/SSM resident core and storage-aware routing.

## D — LOOM_30B_MOE_FEASIBILITY_001_STATIC — COMPLETE / CONDITIONAL

Canonical result: `research/moe/loom-30b-moe-feasibility-001-static-result.md`.

Key decision:
- shared/static residency: structurally promising;
- zero-cache external traffic: too high for practical speed without substantial traffic reduction;
- existing safetensors physical layout: unsuitable for naïve direct expert streaming;
- first external-expert prototype: justified only if layout-aware.

## E — LOOM_30B_MOE_EXPERT_PACK_001 — NEXT

1. create deterministic derived expert-major storage without mutating source model;
2. start with one layer or controlled subset;
3. byte-validate reconstructed expert tensors against source safetensors slices;
4. reduce expert access to compact contiguous ranges;
5. measure packed range count, read amplification and actual storage throughput;
6. quantify latency for top-k=8 reads per layer under cold/warm OS-cache conditions;
7. decide whether full-bank repack is warranted.

Gate: packed expert reads must be correct, reproducible, and materially reduce I/O amplification before progressing.

## F — After expert-pack gate

1. one-layer external-expert execution prototype;
2. validate numerical parity against canonical layer execution;
3. build minimal routed path with controlled memory ownership;
4. capture real expert activation traces;
5. model hot/cold distribution and temporal locality;
6. design expert cache only from measured traces;
7. add prefetch prediction only after evidence;
8. measure end-to-end 30B token rate/memory.

## G — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. `LOOM_30B_MOE_EXPERT_PACK_001`
2. one-layer external-expert parity
3. minimal end-to-end routed execution
4. routing trace/cache study
5. storage-aware cache/prefetch
6. multi-token/block amortization if needed
7. custom LOOM architecture only if measured limits remain structural
8. capability validation
9. decensoring validation before final promotion

## Provenance note

The static audit's local evidence run-id was reported as `20260330T000001Z`, inconsistent with the actual checkpoint date 2026-08-23. Future runs must use actual runtime UTC timestamps.

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
