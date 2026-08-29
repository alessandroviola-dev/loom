# LOOM 30B Apple MoE Paging Stage 1R2 001 — Result

Date: 2026-08-29
Classification: **`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**

## Summary

Stage1R2 produced the first scientifically valid real-generation measurements for the Apple Metal MoE expert-paging path on the base M1 8 GiB host.

The frozen noninteractive `llama-completion -no-cnv` frontend, recovered bounded-output harness, exact ByteShape Q3_K_S-3.25bpw GGUF, and frozen `moe-expert-residency` source all verified successfully. S8, S16, and S24 completed cleanly. S24 was the fastest safe profile at **4.40 generation tok/s** and passed the preregistered host-safety gate.

This is a Stage-1 runtime feasibility/performance GO. It does **not** yet replace canonical DEEP and does not establish matched quality parity with the historical custom MLX path.

## Evidence

Evidence root:
`results-local/research/30b-apple-moe-paging-stage1r2-001/20260829T211631Z/`

Final report:
`results-local/research/30b-apple-moe-paging-stage1r2-001/20260829T211631Z/final-report.json`

## Frozen provenance verified

Harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`

Harness SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Frontend:
`llama-completion`

Frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Model size:
`12,424,439,872` bytes

Model SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

No active `llama-cli`, `llama-completion`, or Stage1R2 harness process remained after completion.

## Measured profiles

| Profile | Slots | Generation tok/s | Prompt tok/s | Generated | Runtime load | E2E wall |
|---|---:|---:|---:|---:|---:|---:|
| S8 | 8 | 2.99 | 2.95 | 95 | 19.294 s | 52.606 s |
| S16 | 16 | 3.58 | 3.43 | 95 | 16.625 s | 45.110 s |
| S24 | 24 | **4.40** | **3.95** | 95 | **14.426 s** | **37.704 s** |

TTFT was not separately observable in the retained combined stream.

The runtime retained exact raw timing rows and a no-inference timing extraction per profile in `runtime-timings-extraction.json`.

## Memory / host safety

| Profile | RSS peak | Wired peak | Compressed peak | Swap peak | Minimum headroom |
|---|---:|---:|---:|---:|---:|
| S8 | 1812.109 MiB | 3645.703 MiB | 1416.812 MiB | 1110.0 MiB | 33% |
| S16 | 2362.859 MiB | 4336.297 MiB | 1588.922 MiB | 1110.0 MiB | 22% |
| S24 | 2935.766 MiB | 5032.297 MiB | 1567.734 MiB | 1125.94 MiB | 13% |

Observed:
- no critical memory pressure;
- no OOM/process kill;
- no corruption/NaN/repeated-token collapse;
- no output-runaway cap event;
- S16 safety gate passed, therefore S24 was authorized;
- S24 completed with 13% minimum reported headroom and ~1.10 GiB peak swap;
- each output was only ~3 KiB, far below the 64 MiB instrumentation safety cap;
- runtime exposed `graphs reused = 150`;
- raw `iostat` observations are retained in per-profile telemetry.

## Functional coherence

All three profiles produced the same deterministic readable Italian response and satisfied the coarse preregistered guard: the output states that only a subset of experts is active/selected for each token and that a router/gating mechanism selects the experts.

Representative retained excerpt:

> Un modello Mixture-of-Experts (MoE) può avere un numero molto elevato di parametri totali, ma utilizza solo una piccola parte di essi per ogni token. Questo perché il modello è composto da molti "esperti" (sottomodelli specializzati), ma per ogni input (token), un router decide quali esperti attivare.

This guard establishes basic functionality only, not broad quality parity.

## Speedup context

Best safe profile: **S24 — 4.40 tok/s**.

Historical comparison:
- vs canonical compact practical DEEP reference `1.402 tok/s`: **3.1384×**;
- vs historical exact-Q4 production reference `1.229233 tok/s`: **3.5795×**.

These ratios are practical historical references, not one-factor same-artifact comparisons. The ByteShape GGUF is `Qwen3-30B-A3B-Instruct-2507`; exact checkpoint/artifact identity of the historical custom MLX path must be reconciled before making quality-parity or strictly matched runtime claims.

## Gate evaluation

Stage1R2 GO requirements:
1. recovered harness SHA exact — PASS;
2. model SHA/size exact — PASS;
3. frozen source commit/cleanliness exact — PASS;
4. `llama-completion` SHA exact — PASS;
5. clean coherent measured profile exists — PASS;
6. best safe throughput >=2.5 tok/s — PASS (`4.40`);
7. no corruption/NaN/repeated-token collapse — PASS;
8. no critical memory/OOM in promoted profile — PASS;
9. no output-runaway event — PASS;
10. complete durable evidence retained — PASS;
11. no authorized-boundary violation reported — PASS.

Final classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**.

## Interpretation

The alternative Apple Metal expert-paging path is now materially more promising than the custom MLX 30B path for interactive DEEP use. On this one frozen workload, S24 reached 4.40 tok/s while staying within the preregistered host-safety limits.

The monotonic S8 -> S16 -> S24 improvement indicates that increasing resident expert slots materially reduced effective paging cost on this workload. S24 also reduced measured runtime load and E2E wall relative to lower-slot profiles.

However, Stage1R2 is a single prompt/sweep and the GGUF checkpoint may not be identical to the historical custom MLX checkpoint. Therefore no production replacement or general quality claim follows yet.

## Exact next step

Before Stage2 matched comparison, perform a bounded **Stage2 comparability audit** to identify the exact historical custom MLX 30B checkpoint/artifact and determine whether ByteShape `Qwen3-30B-A3B-Instruct-2507` is checkpoint-identical, architecture-only comparable, or quality-nonmatched.

Then preregister Stage2 to establish:
- S24 reproducibility across fresh processes;
- matched practical-task performance;
- TTFT/load/E2E behavior;
- memory/swap stability;
- quality/correctness preservation on a fresh compact suite;
- explicit interpretation rules if the old and new 30B checkpoints differ.

Do not replace canonical DEEP solely from Stage1R2.