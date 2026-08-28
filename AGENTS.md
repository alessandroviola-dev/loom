# LOOM — Pi Agent Protocol

Version: 3.44
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. Integration Readiness Protocol v1 is mandatory before integration coding/model forward: `research/architecture/loom-integration-readiness-protocol-v1.md`;
12. producer/consumer compatibility must be proven mechanically before adapter coding;
13. static adapter dry-run with zero unresolved accesses and forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts are not promoted implicitly to runtime artifacts;
15. metadata/coverage/provenance checks use deterministic scripts/JSON where possible;
16. settled mechanisms are not reopened absent regression/materially different target;
17. production regressions require a new bounded preregistered repair;
18. validation-only metadata stays out of hot runtime when representable by a smaller contract;
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading speed work freezes fidelity metrics/thresholds before candidate results;
21. verifier-ceiling experiments using oracle proposals are upper bounds only and never production speed;
22. large new-model downloads require a metadata-only portability/readiness gate first;
23. if environment discovery conflicts with an accepted execution stack, reconcile the exact interpreter/venv before package installs or large downloads;
24. first-token/new-model checkpoints must early-stop when measured performance already makes a full campaign decision-irrelevant.

External root: `<external-archive>/`

## Frozen Qwen3-30B-A3B comparison baseline

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Production baseline commit:
`96958de`.

Exact-Q4/top-8 sustained throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Closed speed paths:
- expert-major accepted/canonical;
- routing sparsity no acceptable gain;
- Q2/Q3 expert requantization fidelity fail;
- DFlash closed;
- lossless oracle speculative ceiling K=4 median `1.792925 tok/s`, NOT PROMISING for a real drafter.

This 30B runtime is now the frozen production comparator. Do not reopen its speed frontier absent a materially new verifier architecture.

## Qwen3.8 Portability Readiness 001 — BOTH PORTABLE

`LOOM_QWEN38_PORTABILITY_READINESS_001 = QWEN38_BOTH_PORTABLE`.

Result:
`research/architecture/loom-qwen38-portability-readiness-001-result.md`
Evidence:
`results-local/research/qwen38-portability-readiness-001/20260828T112000Z/`

### Candidate A — Qwen3.8-27B

Fixed identities:
- upstream `Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`;
- Q4 reference `mlx-community/Qwen3.8-27B-4bit@3e6447f082e89cc7f0bc6e5441afd38dfce760ff`.

Static classification: `PORTABLE_DENSE_STREAMING`.

Facts:
- 64 language layers: 48 Gated DeltaNet + 16 full-attention;
- largest layer `215,665,088 B`;
- projected resident `1,587,312,640 B`;
- naive one-token streamed external weight traffic `13,702,468,608 B/output-token`;
- bandwidth at 1/2/5 tok/s: `13.702 / 27.405 / 68.512 GB/s`.

Interpretation: simplest/cheapest candidate to acquire and highest probability of first-token success, but naive dense streaming is structurally bandwidth-heavy and is not expected to beat the sparse 30B without a later multi-token mechanism. Official architecture includes multi-step MTP, but MTP is not part of the first baseline execution checkpoint.

### Candidate B — Qwen3.8-Flash-Next

Fixed identities:
- upstream `Qwen/Qwen3.8-Flash-Next@de4b8e4d43b917e7706784d8bb445c9af86a3540`;
- reference `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP@327c8a604de613b42f84ba5e6b796c0931e8aa3b`.

Static classification: `PORTABLE_FLASH_STREAMING`.

Facts:
- 48 layers;
- 512 routed experts/layer, top-10 routed + one shared;
- routed expert size `3,072,000 B`;
- routed expert traffic `1,474,560,000 B/token`;
- shared expert traffic `147,532,800 B/token`;
- bounded n-gram lookup estimate `1,600 B/token`;
- projected resident `991,928,320 B`;
- transient `154,032,152 B`;
- projected total external `3,858,155,864 B/token`;
- bandwidth at 1/2/5 tok/s: `3.858 / 7.716 / 19.291 GB/s`;
- native MTP metadata ABI covered but runtime adapter not ready.

Interpretation: much larger download and harder adapter, but architecture aligns more strongly with LOOM through expert-major storage, deterministic n-gram offload and native MTP.

Readiness consumed only `2,024,970 B` network and zero safetensor payload bytes.

## Environment discrepancy to resolve

The metadata readiness probe reported MLX-family packages absent in its interpreter, while accepted Qwen3 experiments used MLX `0.32.0` / mlx-lm `0.31.3`.

This is presumed interpreter/environment mismatch until disproven. The next checkpoint MUST locate/freeze the previously accepted Python environment before any large download. Do not blindly upgrade/install into the project environment.

## Current checkpoint — Qwen3.8-27B Dense Streaming First-Token 001

`LOOM_QWEN38_27B_DENSE_STREAMING_FIRST_TOKEN_001`

Preregistration:
`research/architecture/loom-qwen38-27b-dense-streaming-first-token-001-preregistration.md`

Purpose:
1. reconcile/freeze execution environment;
2. acquire only fixed Q4 Candidate A, preferably to healthy external storage;
3. build minimum 64-layer text-only dense streaming adapter;
4. static dry-run and representative layer parity;
5. deterministic first full text token under bounded memory;
6. run a 4-token normal autoregressive speed probe;
7. early-stop if throughput `<0.6146165 tok/s`;
8. only if justified, confirm with 3×8 or 3×16 tokens.

MTP is disabled for this checkpoint. It may be studied independently only after baseline dense streaming works and measured performance justifies further investment.

Final outcomes:
- `QWEN38_27B_DENSE_COMPETITIVE`;
- `QWEN38_27B_DENSE_WORKS_SLOW`;
- `QWEN38_27B_DENSE_FIRST_TOKEN_ONLY`;
- `QWEN38_27B_DENSE_INCONCLUSIVE`.

After Candidate A classification, proceed to a separate Flash-Next external-storage/Qwen4Exp/N-gram/MTP adaptation checkpoint. Only after both real candidates produce local text should the matched three-model speed/intelligence/steerability bake-off run.
