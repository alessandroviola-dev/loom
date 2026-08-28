# LOOM 30B Interactive Runtime v1 Canonicalization Repair 001 — Result

Date: 2026-08-28
Branch: `research/stretch-015-divergence-attribution`
Final classification: `LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`

## Frozen reviewed source

Original reviewed candidate SHA-256 verified:
`25607adf29b8bd045a938b6bd32afa2322d95ebaa5e156da5f86010a4101bcfa`.

This repair does not change the historical `LOOM_30B_INTERACTIVE_V1_FUNCTIONAL_SLOW` classification or its TTFT threshold. It only repairs production reproducibility/streaming/boundary defects found during source review.

## Intended production files

Runtime core:
`scripts/loom_30b_runtime_core_v1_001.py`
SHA-256:
`75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`.

Repaired CLI:
`scripts/loom_30b_interactive_v1_001.py`
SHA-256:
`08e84d1b19afdd4bad757db29d0d804783a35ee41db17696c14c56c8913488cb`.

Changed file set is limited to those two files. They remain local/unstaged until ChatGPT reviews exact source and the user explicitly stages/commits them.

## Dependency / backend gate

Dependency audit: PASS.

The repaired production runtime no longer imports the untracked research helpers used by the original candidate. Production imports resolve to the tracked canonical expert-major backend plus the new minimal runtime core and installed/runtime-safe dependencies.

Canonical backend remained unchanged.
Validated backend SHA-256 remains:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

## Semantic regression

16-position exact semantic parity: PASS.

Required equivalence passed for:
- greedy token IDs;
- routed expert identities/order;
- raw float32 final-logit SHA;
- finite logits.

State reuse: PASS.

Original generated IDs remain the causal history. Incremental next-turn processing preserves the accepted KV/state semantics with no full previous-transcript re-prefill.

## Streaming / boundary repair

Unicode streaming equivalence: PASS.

The repaired path uses stateful mlx-lm detokenization and produced exact one-shot-equivalent text without replacement-character corruption.

EOS-visible-marker gate: PASS.
Stop/EOS is suppressed before detokenizer/emission.

Special-token-looking boundary gate: PASS.
A user message containing literal `<|im_end|>` did not alter next-turn boundary selection.

The next-turn suffix is mechanically template-derived rather than selected by scanning the complete transcript for the second-last EOS.

## Functional regression

Frozen three-turn memory smoke: PASS.
Final answer: `7319`.

Bounded real generation:
- configured 32-token bound;
- output terminated after 5 generated tokens;
- decode throughput `1.449028 tok/s`;
- TTFT `18.288247 s`.

This bounded repair run is regression evidence only and does not replace the longer interactive-v1 performance campaign.

## Memory / safety

Peak RSS:
`964,984,832 B`.

Observed system swap:
`1471.06 MiB`.

No critical memory pressure was observed. The repair preregistration did not define a new swap threshold; historical interactive-v1 safety/performance evidence remains the user-facing reference.

Fallback/cache:
- PACKED;
- SOURCE fallback `0`;
- no persistent expert cache;
- deterministic PACKED descriptor close PASS.

## Decision

`LOOM_30B_INTERACTIVE_V1_CANONICALIZATION_GO`.

The bounded repair resolved the exact defects found during source review while preserving model semantics and the canonical expert-major backend.

This GO authorizes final human/ChatGPT source review only. It does NOT by itself make the files canonical. Canonical status requires:
1. exact review of both local files against the reported SHAs;
2. staging only those approved files;
3. `git diff --cached --check` and intended-file verification;
4. commit/push;
5. remote verification.

After persistence, the user runs a real manual terminal conversation before LOOM 30B v1 is frozen as the practical comparator.

## Evidence

`results-local/research/30b-interactive-v1-canonicalization-repair-001/20260828T131045Z/`
