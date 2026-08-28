# LOOM Roadmap

Last updated: 2026-08-28
Current: `QWEN38_BOTH_PORTABLE`
Immediate next: `LOOM_QWEN38_27B_DENSE_STREAMING_FIRST_TOKEN_001`
Canonical context: `/AGENTS.md` v3.44.

## Frozen current 30B comparator

Qwen3-30B-A3B exact-Q4/top-8:
- backend commit `96958de`;
- sustained 3×32 `1.115874`, `1.229233`, `1.254611 tok/s`;
- production median `1.229233 tok/s`;
- exactness/safety PASS.

Closed speed attempts:
- routing sparsity: no acceptable gain;
- Q2/Q3 experts: fidelity fail;
- DFlash: closed;
- perfect-oracle lossless K=4 verifier ceiling: median `1.792925 tok/s`, NOT PROMISING for a real drafter.

Conclusion: current-Qwen3 5 tok/s work is frozen absent a materially different verifier architecture.

## Qwen3.8 Portability Readiness — BOTH PASS

Result:
`research/architecture/loom-qwen38-portability-readiness-001-result.md`.

### Candidate A — Qwen3.8-27B dense

Fixed Q4 reference:
`mlx-community/Qwen3.8-27B-4bit@3e6447f082e89cc7f0bc6e5441afd38dfce760ff`.

Static feasibility:
- 64 language layers;
- largest layer `215,665,088 B`;
- resident `1,587,312,640 B`;
- naive streamed external traffic `13,702,468,608 B/token`;
- required bandwidth 1/2/5 tok/s: `13.702 / 27.405 / 68.512 GB/s`.

Portable under bounded layer streaming, but static bandwidth makes ordinary one-token decode likely slower than the current sparse 30B. Actual execution is needed before eliminating it. Official architecture contains MTP, but baseline must be measured with MTP disabled.

### Candidate B — Qwen3.8-Flash-Next

Fixed Q4+MTP reference:
`Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP@327c8a604de613b42f84ba5e6b796c0931e8aa3b`.

Static feasibility:
- 48 layers;
- 512 routed experts, top-10 + shared;
- routed expert `3,072,000 B`;
- routed traffic `1,474,560,000 B/token`;
- shared expert traffic `147,532,800 B/token`;
- bounded n-gram lookup estimate `1,600 B/token`;
- resident `991,928,320 B`;
- transient `154,032,152 B`;
- projected external `3,858,155,864 B/token`;
- bandwidth 1/2/5 tok/s: `3.858 / 7.716 / 19.291 GB/s`;
- MTP metadata covered, runtime adapter pending;
- ~105.434 GiB weight payload requires external storage.

Flash-Next is the architecture of greatest LOOM interest because expert-major storage, deterministic n-gram offload and native MTP can potentially compound.

## Current — Candidate A actual execution

Preregistration:
`research/architecture/loom-qwen38-27b-dense-streaming-first-token-001-preregistration.md`.

Before download:
- reconcile the Python/MLX environment mismatch from readiness;
- prefer the previously validated MLX 0.32.0 / mlx-lm 0.31.3 environment;
- no blind global upgrade;
- storage gate and fixed-revision resumable download only.

Execution:
1. acquire Q4 Candidate A, <=20 GiB network;
2. static 64-layer text-only adapter/dry-run;
3. representative layer parity;
4. first deterministic full text token under bounded memory;
5. 4-token normal autoregressive speed probe;
6. early stop below `0.6146165 tok/s`;
7. if justified, 3×8 or 3×16 confirmation.

`QWEN38_27B_DENSE_COMPETITIVE` requires confirmed median >=`1.1063097 tok/s` and all safety/validity gates PASS.

MTP is not enabled in the baseline checkpoint; it is a separate possible optimization only if ordinary local generation works and merits further work.

## Candidate B after A

Create a separate Flash-Next execution checkpoint using external storage. Required components:
- fixed Q4+MTP artifact acquisition;
- Qwen4Exp bounded-state adapter;
- deterministic 512-expert resolver/expert-major layout;
- exact n-gram hash/partition offload;
- text first-token baseline with native MTP initially disabled;
- only after baseline correctness: independent native-MTP throughput checkpoint.

## Final three-model bake-off

After real local generation exists for A and B, compare against canonical Qwen3-30B-A3B on identical M1/8GB constraints:
- sustained tok/s and TTFT;
- RAM/swap/disk;
- intelligence/quality on a frozen common LOOM eval set;
- instruction following/refusal/steerability profile;
- raw speed winner;
- intelligence winner;
- combined practical winner.

Do not infer final winners from static bandwidth projections or external hardware benchmarks.
