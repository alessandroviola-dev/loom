# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B speed frontier is frozen at production median `1.229233 tok/s`; its oracle speculative ceiling is NOT PROMISING. Qwen3.8 metadata readiness says both 27B dense and Flash-Next are statically portable. Current work is actual Candidate-A dense-streaming first-token/speed feasibility.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_QWEN38_27B_DENSE_STREAMING_FIRST_TOKEN_001`
Pi context: `/AGENTS.md` v3.44.

## Frozen Qwen3-30B-A3B comparator

Backend commit `96958de`.
Exact Q4/top-8 sustained 3×32: `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Closed paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 expert requantization: fidelity fail;
- DFlash: closed;
- oracle lossless speculative K=4 ceiling: final median `1.792925 tok/s`, only `1.458572×` baseline and below promising gate; real drafter not justified.

Do not reopen current-30B speed work absent a materially new verifier architecture.

## Qwen3.8 Portability Readiness 001 — BOTH PORTABLE

Result:
`research/architecture/loom-qwen38-portability-readiness-001-result.md`
Evidence:
`results-local/research/qwen38-portability-readiness-001/20260828T112000Z/`

### A — Qwen3.8-27B

Upstream `Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`.
Q4 reference `mlx-community/Qwen3.8-27B-4bit@3e6447f082e89cc7f0bc6e5441afd38dfce760ff`.

Static class: `PORTABLE_DENSE_STREAMING`.

- 64 layers: 48 Gated DeltaNet + 16 full-attention;
- largest layer `215,665,088 B`;
- projected resident `1,587,312,640 B`;
- naive one-token streamed traffic `13,702,468,608 B/token`;
- bandwidth at 1/2/5 tok/s: `13.702 / 27.405 / 68.512 GB/s`.

A is first acquisition priority because it is smaller and adapter work is bounded, not because it is expected to be fastest.

### B — Qwen3.8-Flash-Next

Upstream `Qwen/Qwen3.8-Flash-Next@de4b8e4d43b917e7706784d8bb445c9af86a3540`.
Reference `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP@327c8a604de613b42f84ba5e6b796c0931e8aa3b`.

Static class: `PORTABLE_FLASH_STREAMING`.

- 48 layers;
- 512 routed experts, top-10 + one shared;
- routed expert size `3,072,000 B`;
- routed traffic `1,474,560,000 B/token`;
- shared expert traffic `147,532,800 B/token`;
- bounded n-gram lookup estimate `1,600 B/token`;
- resident `991,928,320 B`;
- transient `154,032,152 B`;
- total projected external `3,858,155,864 B/token`;
- bandwidth at 1/2/5 tok/s: `3.858 / 7.716 / 19.291 GB/s`;
- native MTP metadata ABI covered but runtime integration not ready;
- current local disk is insufficient for the `105.434 GiB` weight payload; use external storage later.

Flash-Next is harder to integrate but more aligned with LOOM architecture and remains the stronger speed-interest candidate after A is measured.

## Environment discrepancy

Metadata readiness reported MLX/mlx-lm/mlx-vlm/oMLX absent in its probed interpreter, while accepted LOOM runs used MLX `0.32.0` and mlx-lm `0.31.3`.

Treat as environment mismatch until mechanically reconciled. No blind package upgrade/install before large download.

## Exact next step — Qwen3.8-27B Dense Streaming First-Token 001

Preregistration:
`research/architecture/loom-qwen38-27b-dense-streaming-first-token-001-preregistration.md`.

Sequence:
1. locate/freeze exact previously validated MLX Python environment;
2. storage gate and resumable fixed-revision Q4 download, <=20 GiB network;
3. static text-only 64-layer streaming adapter/dry-run;
4. representative Gated DeltaNet/full-attention layer parity;
5. deterministic first full text token with RSS <=6.5 GiB and bounded swap;
6. one 4-token normal autoregressive speed probe, MTP disabled;
7. early stop if `<0.6146165 tok/s`;
8. if justified, 3×8 or 3×16 confirmation.

A is `COMPETITIVE` only if confirmed median >=`1.1063097 tok/s` (within 10% of the current 30B comparator), otherwise a working but slower result is still useful and closes the dense candidate baseline.

After A: design/execute separate Flash-Next acquisition + Qwen4Exp/expert-major + n-gram offload baseline, then native MTP if baseline correctness is established.

Final bake-off only after both feasible Qwen3.8 candidates generate locally:
- speed/TTFT;
- RAM/swap/disk;
- frozen intelligence/quality set;
- instruction/refusal/steerability;
- speed winner, intelligence winner, combined practical winner.
