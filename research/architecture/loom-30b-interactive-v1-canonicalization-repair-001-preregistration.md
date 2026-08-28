# LOOM 30B Interactive Runtime v1 Canonicalization Repair 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — execute before committing interactive v1

## Purpose

Repair only the reproducibility/streaming/boundary issues discovered during code review of the functionally validated local candidate `scripts/loom_30b_interactive_v1_001.py`, without changing model semantics, quantization, routing, expert-major behavior or accepted performance thresholds.

Frozen evidence from `LOOM_30B_INTERACTIVE_RUNTIME_V1_001` remains valid as functional evidence; this checkpoint decides whether the user-facing implementation can become canonical/reproducible.

Final outcomes:
- `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`
- `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_NO_GO`
- `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_INCONCLUSIVE`

## Frozen reviewed candidate

Uploaded/reviewed candidate SHA-256:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`

Current candidate imports:
- canonical tracked `loom_30b_moe_expert_major_backend_001`;
- local research helper `loom_30b_moe_first_greedy_generation_001`;
- local research helper `loom_30b_moe_shared_backbone_residency_001`.

The latter two are not tracked on the current Git branch and therefore must not remain runtime dependencies of a canonical CLI.

## Stage 0 — exact local provenance/dependency gate

Before edits:
- verify local candidate SHA matches the frozen reviewed SHA above;
- `git status --short` and `git ls-files` the candidate and every direct local Python dependency;
- freeze exact SHAs of the two local helper scripts used by the validated run;
- no broad repository/history scan;
- no network/package changes/model changes.

If the candidate SHA differs, preserve diff and stop as INCONCLUSIVE unless the difference is mechanically explained as the pull/docs-only state.

## Stage 1 — promote a minimal tracked runtime core

Create one minimal production/runtime module, intended path:
`scripts/loom_30b_runtime_core_v1_001.py`.

Move/copy only the exact helper functionality required by the interactive runtime from the validated local research helpers, including as needed:
- Q4 projection/component constants;
- model inventory/header reading required to load the accepted local artifact;
- dtype map;
- catalog/component source mapping;
- resident backbone load/ownership validation;
- BF16 KV cache;
- exact attention-with-cache path;
- routing;
- direct external expert computation.

Requirements:
- no import dependency on untracked research scripts;
- canonical expert-major backend remains unchanged;
- same local model/PACKED artifacts;
- no SOURCE fallback/cache;
- no new model semantics;
- fresh-process import dependency audit must show every project Python dependency is Git-tracked after the candidate files are staged.

Do not commit/push in this checkpoint.

## Stage 2 — correct streaming detokenization and stop emission

Replace per-token standalone `tokenizer.decode([token])` streaming with the stateful `tokenizer.detokenizer` API provided by the frozen mlx-lm `0.31.3` environment:
- reset a fresh detokenizer at each assistant turn;
- check stop/EOS token before adding/emitting it;
- add only non-stop generated tokens to the detokenizer;
- emit `detokenizer.last_segment` incrementally;
- call `finalize()` at normal length termination and emit the final segment;
- final `generated_text` must equal normal tokenizer decode of the visible generated token sequence after normalization expected by the tokenizer;
- EOS/special stop marker must never be printed to the user.

Frozen Unicode streaming test must include output/token sequences whose UTF-8 text requires multi-token detokenization; emitted concatenated text must equal one-shot decode exactly and contain no replacement-character corruption introduced by streaming.

## Stage 3 — robust incremental chat boundary

Remove dependence on scanning the entire re-tokenized transcript for the second-last hard-coded EOS occurrence.

Derive and validate the next-turn canonical control/user/generation suffix deterministically from the frozen Qwen chat template while preserving exact original generated token IDs already represented in KV.

Requirements:
- previous generated IDs are never reconstructed from decoded assistant text for KV history;
- if a final generated token remains pending because max-token termination occurred, materialize exactly that pending token before the assistant-close/new-user suffix;
- canonical assistant-close/user/generation control tokens are derived/validated mechanically from the tokenizer/template;
- a user message containing literal special-token-looking text such as `<|im_end|>` must not alter boundary selection;
- no full prior transcript re-prefill;
- same causal token sequence as canonical chat semantics.

Do not change the model's stop-token set post hoc. Validate the expected chat terminator against `tokenizer.eos_token_ids` at startup and fail closed on incompatible artifact semantics.

## Stage 4 — exact semantic regression gate

Re-run the frozen semantic parity test against the canonical greedy path:
- exactly first 16 generated positions (or prior allowed EOS rule);
- identical input/chat-template semantics;
- identical greedy IDs;
- identical routed expert identities/order;
- identical raw float32 final-logit SHA;
- finite logits;
- zero fallback/cache.

Also run a two-turn exact state-reuse comparison and require no full transcript re-prefill.

Any semantic mismatch => `...CANONICALIZATION_NO_GO` and STOP.

## Stage 5 — functional regression gate

Run:
1. frozen 3-turn `7319` memory smoke;
2. a special-token-looking user-input boundary smoke containing literal `<|im_end|>` text;
3. Unicode streaming equivalence smoke;
4. one bounded 32-token real interactive answer with live streaming.

Require:
- no printed EOS/control marker;
- streamed concatenation == final decoded visible text;
- conversation memory PASS;
- exact state reuse PASS;
- zero SOURCE fallback/persistent expert cache;
- clean `/reset`, `/exit`, Ctrl-C/EOF teardown;
- PACKED fd deterministically closed.

Performance is regression-only here: decode throughput must not regress by >10% versus the comparable functional-v1 measurement absent environment noise; do not change the historical `READY` TTFT threshold or reclassify the original result.

## Stage 6 — tracked dependency/canonicalization gate

Before GO, return the exact intended staged file set, but DO NOT stage/commit automatically.

Expected production files should be limited to:
- `scripts/loom_30b_runtime_core_v1_001.py` (new);
- `scripts/loom_30b_interactive_v1_001.py` (new/repaired).

Canonical backend must have zero diff.

Mechanically verify recursively that production imports resolve only to:
- Python stdlib;
- frozen installed packages;
- Git-tracked LOOM runtime files;
- accepted local model/runtime artifacts addressed as data, not Python modules.

No production Python import may require the untracked research helper scripts.

## Decision

`LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO` iff:
- exact reviewed source provenance is reconciled;
- minimal runtime core is self-contained/tracked-ready;
- semantic parity/state reuse PASS;
- streaming detokenization/EOS handling PASS;
- adversarial boundary smoke PASS;
- functional regression PASS;
- canonical backend unchanged;
- intended file set is bounded and reproducible.

`NO_GO` for deterministic code/semantic/reproducibility failure.
`INCONCLUSIVE` only for genuine environment/provenance ambiguity.

## Hard bounds

- no network;
- no package install/upgrade;
- no model/weight/quantization/routing changes;
- no speed frontier work;
- no Qwen3.8;
- no 8B/4B bake-off;
- no Heretic/refusal editing;
- no Git commit/push/project decision-doc edits by Pi;
- no canonical backend modification;
- no threshold rescue.

Evidence:
`results-local/research/30b-interactive-v1-canonicalization-repair-001/<UTC>/`

After GO, ChatGPT reviews exact diffs/SHAs, then the user commits only the approved runtime files. A manual terminal conversation follows before the 30B-vs-8B-vs-4B bake-off.