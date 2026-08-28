# LOOM 30B Interactive v1 EOS Finalize Repair 001 — Preregistration

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — execute before persistence

## Purpose

Repair one final user-facing streaming defect found during ChatGPT exact-source review after `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`.

The validated runtime core SHA remains accepted and MUST NOT change:
`75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`.

Reviewed repaired CLI SHA before this micro-repair:
`08e84d1b19afdd4bad757db29d0d804783a35ee41db17696c14c56c8913488cb`.

## Finding

`generate_turn()` suppresses EOS before adding it to the stateful detokenizer, which is correct, but calls `detokenizer.finalize()` only when termination is by max-token length. If normal EOS arrives while the detokenizer still buffers a valid visible fragment, final `detokenizer.text` may not yet equal one-shot decode of all visible IDs.

The frozen mlx-lm streaming-detokenizer contract requires finalization at end of generation so remaining buffered visible text is flushed. EOS itself must remain unadded/unemitted.

## Authorized repair

Modify only:
`scripts/loom_30b_interactive_v1_001.py`

Required behavior:
1. after the generation loop, always finalize the stateful detokenizer exactly once, regardless of EOS vs length termination;
2. EOS/stop token remains checked before `add_token()` and is never added or emitted;
3. after `finalize()`, emit exactly `detokenizer.last_segment` if non-empty;
4. final streamed concatenation, `detokenizer.text`, and normal tokenizer decode of visible IDs must be exactly equivalent under the frozen tokenizer semantics;
5. do not change token IDs, model forwards, routing, KV/state bookkeeping, stop set, chat boundary logic, runtime core or canonical backend.

## Regression gate

Run a bounded local test using the frozen environment that covers both:
- length termination;
- EOS termination with a visible-token sequence that leaves a detokenizer fragment buffered before finalization (or a deterministic tokenizer-level construction proving the same condition if the model cannot be forced without semantic changes).

Require:
- no visible EOS/control marker;
- no replacement-character corruption;
- streamed text == final detokenizer text == one-shot decode;
- existing 16-position semantic parity unchanged or mechanically proven unaffected by the text-only post-loop repair;
- PACKED-only, SOURCE fallback 0, no expert cache;
- runtime core and canonical backend SHAs unchanged.

No long benchmark is required. No TTFT/speed claim is produced by this repair.

## Decision

- `LOOM_30B_INTERACTIVE_V1_EOS_FINALIZE_GO` if all gates PASS;
- `..._NO_GO` for deterministic streaming/equivalence failure;
- `..._INCONCLUSIVE` only for genuine environment/instrumentation ambiguity.

## Hard bounds

- no network/package changes;
- no runtime-core modification;
- no canonical-backend modification;
- no model/weight/quantization/routing/KV semantic change;
- no 8B/4B/Qwen3.8/Heretic/speed work;
- no Git commit/push/project-doc edits by Pi.

Evidence:
`results-local/research/30b-interactive-v1-eos-finalize-repair-001/<UTC>/`

After GO, ChatGPT reviews the final CLI SHA/diff; then the user stages the two production files and persists them.