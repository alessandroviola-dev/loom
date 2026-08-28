# LOOM — Pi Agent Protocol

Version: 3.49
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. required gate instrumentation must persist before evidence is accepted;
8. failed frozen methods are not silently modified/rerun under the same checkpoint;
9. Integration Readiness Protocol v1 is mandatory before integration coding/model forward;
10. production code is canonical only after exact review and Git persistence;
11. production/user-facing Python must not depend on untracked research helper modules;
12. token streaming must use tokenizer-compatible stateful detokenization and stop/control tokens must not be emitted;
13. user-facing runtime claims require real end-to-end generation evidence.

External root: `<external-archive>/`

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB and compare large-model utility against smaller skill/tool-enhanced systems.

## Frozen Qwen3-30B-A3B research comparator

Canonical expert backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Backend commit: `96958de`.
Backend SHA-256: `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact-Q4/top-8 sustained 3×32: `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Closed current-verifier speed paths:
- expert-major accepted/canonical;
- routing sparsity no acceptable gain;
- Q2/Q3 from deployed Q4 fidelity fail;
- DFlash closed;
- exact K=4 oracle verifier ceiling `1.792925 tok/s`, not promising for a real drafter.

## Qwen3.8 readiness — BOTH PORTABLE, EXECUTION PARKED

`QWEN38_BOTH_PORTABLE` from metadata-only readiness.
Qwen3.8-27B projected dense-streamed external traffic: `13,702,468,608 B/token`.
Qwen3.8-Flash-Next projected external baseline: `3,858,155,864 B/token`.
Both large executions remain parked until after practical 30B/8B/4B comparison unless explicitly reactivated.

## LOOM 30B Interactive Runtime v1 — CANONICAL / FUNCTIONAL_SLOW

Historical functional classification:
`LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW`.

Result:
`research/architecture/loom-30b-interactive-runtime-v1-001-result.md`
Evidence:
`results-local/research/30b-interactive-runtime-v1-001/20260828T122908Z/summary.json`

Validated environment:
- `.venvs/stretch030-mlx0320-fix1/bin/python`;
- Python `3.13.0`;
- MLX `0.32.0`;
- mlx-lm `0.31.3`.

Historical long-form metrics:
- TTFT `47.832 s`;
- decode `1.116 tok/s`;
- end-to-end `0.921 tok/s`;
- peak RSS `1,447,067,648 B`.

Only frozen READY miss: TTFT >30 s. Do not relax this threshold post hoc.

Canonicalization repair: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`.
EOS-finalize micro-repair: `LOOM_30B_INTERACTIVE_V1_EOS_FINALIZE_GO`.

Canonical production runtime commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c` — `feat: add canonical LOOM 30B interactive runtime`.

Canonical files:
- `scripts/loom_30b_runtime_core_v1_001.py` — SHA-256 `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` — SHA-256 `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Remote verification against prior checkpoint confirms commit `d3691b7` contains exactly those two added runtime files and no unrelated file changes.

Canonical guarantees:
- 16-position token/routing/float32-logit SHA parity PASS;
- exact incremental KV/recurrent reuse PASS;
- no full transcript re-prefill;
- stateful Unicode streaming equivalence PASS;
- EOS/control marker never emitted;
- detokenizer finalized on EOS and length termination;
- literal `<|im_end|>` user-content boundary smoke PASS;
- `7319` conversation smoke PASS;
- PACKED-only; SOURCE fallback 0; no persistent expert payload cache; deterministic packed fd close.

## Current checkpoint — MANUAL USER SESSION

No Pi work is required now.

User must pull current docs if needed, then launch the committed runtime with the validated Python environment and conduct a real free-form multi-turn conversation.

Manual-use goals:
- confirm startup succeeds from committed code;
- ask several normal real questions, not frozen test prompts;
- observe TTFT, text streaming, answer coherence, multi-turn memory and practical patience/latency;
- use `/reset` once and confirm state clears;
- exit with `/exit` and confirm clean teardown.

Do not alter model/runtime semantics during this session.

If manual use is acceptable, freeze **LOOM 30B v1 FUNCTIONAL_SLOW** as the large practical comparator and open the matched Qwen-family 30B vs 8B vs 4B bake-off.

## Strategic sequence after manual v1

1. Practical 30B vs 8B vs 4B: TTFT, tok/s, RAM/swap, time-to-correct-task and frozen intelligence tasks.
2. Decide 30B deep/primary vs small fast primary + 30B escalation vs skill/tool/protocol-centric small model.
3. Use `LOOM_HERETIC_TECHNICAL_PAPER.md` only after runtime-role selection, with frozen refusal/steerability and capability-preservation gates.
4. Separate R&D may study higher-precision mixed-bit quantization, fused Metal expert kernels, vectored expert I/O, trace-driven bounded caches and TTFT/prefill optimization.

Project priority remains practical utility.