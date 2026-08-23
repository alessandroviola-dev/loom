# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_001_CACHE_CONTROL_INVALID`
Active side research: `VIDEO_RESEARCH_INGEST_001`
Strategic next: `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Dense Qwen3-8B laboratory — RETAINED

Dense experiments established exact partial residency and several lifecycle rules. Dense research remains a controlled MLX implementation laboratory; it is no longer assumed to be the final 32B architecture.

## B — High-leverage architecture branch — ACTIVE

Primary direction: sparse MoE / external experts.

Qwen3-30B-A3B is the first concrete ~30B target.

## C — 30B STATIC FEASIBILITY — CONDITIONAL

Exact local anatomy:
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B (0.763 GiB);
- routed expert bank 15,401,484,288 B (14.344 GiB);
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert 2,506,752 B;
- selected expert bytes/layer 20,054,016 B;
- zero-cache useful expert traffic/token 962,592,768 B (918 MiB).

Decision: external-expert research is structurally justified.

## D — EXPERT-PACK-001 — PASS

Two-layer prototype proved lossless expert-major packing:
- 256 experts / 641,728,512 B validated;
- zero mismatches;
- 9 source ranges/expert -> 1 packed range/expert;
- top-k reads 72 -> 8;
- byte amplification stays 1.0x;
- 100% packed useful/span efficiency.

Pack correctness is canonical. Performance numbers from the pack run are not physical-SSD evidence.

## E — PHYSICAL-IO-001 — CACHE CONTROL INVALID

Run ID: `20260823T204945Z`.

The benchmark correctly stopped at its sanity gate:
- `F_NOCACHE` and `F_RDAHEAD` were verified and accepted;
- warm control measured ~14,439 MB/s;
- nominal cache-minimized path measured ~13,800 MB/s;
- only ~1.046x distinction;
- the >RAM/random/top-k/token-like phases were not run.

Conclusion: process-level timing plus these file flags did not prove physical SSD service. No physical bandwidth, physical latency, token-rate or cache-hit requirement is promoted from this run.

This is an instrumentation result, not an architectural NO-GO.

## F — PHYSICAL-IO-002 — NEXT

Use device-level evidence to distinguish cache from physical storage.

Required:
1. resolve the actual internal physical disk backing the model volume;
2. sample macOS `iostat` device statistics/cumulative transfer totals around workloads;
3. require device-level MB transfer deltas to correspond materially to requested bytes before accepting storage throughput;
4. keep >RAM unique working set and 2,506,752 B expert-sized reads;
5. retain `F_NOCACHE` / no-read-ahead controls where supported;
6. only after the device-I/O gate passes, measure random expert, top-k=8 and 384-expert token-like storage workloads;
7. quantify physical I/O-only token bounds and required reuse from accepted device-verified data.

If this method still cannot isolate physical storage without privileged tooling, classify the physical baseline as unresolved rather than inventing a number.

## G — Multi-token/speculative amortization — SOURCE INGEST ACTIVE

A supplied video concerning Qwen3.8-27B, DFlash2 and Harness is being transcribed/visually audited under `VIDEO_RESEARCH_INGEST_001`.

Potential relevance: block/speculative decoding may amortize expensive target/expert work across multiple accepted tokens. Do not promote this line based on the video alone until source claims are verified and separated from hardware/model-fit claims.

## H — Decision after physical I/O + video review

Candidate next experimental branches:
- one-layer exact external-expert execution;
- full expert-major pack if justified;
- expert routing trace/cache study;
- DFlash2/speculative block amortization if independently applicable to the target runtime;
- route prediction/prefetch only after trace evidence.

## I — Longer-term architecture options

If existing MoE remains insufficient:
- contextual neuron/cluster sparsity;
- multi-token/block amortization;
- recursive/shared-weight architectures;
- external learned memory;
- recurrent/SSM resident core;
- storage layout co-designed with routing.

## J — Promotion gates

Any promoted architecture must pass:
- full intended model capacity represented;
- memory/residency accounting;
- practical generation speed;
- capability benchmark;
- reproducibility/exactness where applicable;
- behavioral decensoring stage with collateral capability validation.

## Immediate order

1. complete `VIDEO_RESEARCH_INGEST_001` already running on Pi
2. review DFlash2/video evidence
3. `LOOM_30B_MOE_PHYSICAL_IO_002_DEVICE_VERIFIED`
4. one-layer external-expert execution
5. full pack / routing trace/cache study as evidence dictates
6. multi-token/block amortization if justified
7. full 48-layer external-expert execution
8. custom LOOM architecture research if necessary
9. capability validation
10. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
