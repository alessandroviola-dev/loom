# LOOM — Pi Agent Protocol

Version: 3.65
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not commit/push/PR/edit project decision docs unless explicitly authorized.
GitHub is canonical. Active clone: `<repository-root>`.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue/post-hoc gate relaxation;
3. fail closed before expensive execution;
4. invalid/inconclusive runs support no performance claim;
5. production code requires exact review + Git persistence;
6. do not tune on exposed evaluation examples;
7. hidden ground truth/spec metadata must never enter model repair/judge inputs unless explicitly preregistered as public input;
8. expensive model downloads require a separately authorized/preregistered checkpoint.

## Product direction

**Big models. Small machines.**
- BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary tier.
- DEEP: Qwen3-30B-A3B, current canonical custom MLX path ~1.4 tok/s; **30B runtime acceleration is now the active priority**.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but is temporarily PAUSED during the 30B runtime investigation.

LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Validator track — PAUSED after successful hardening

Output Validator v0 remains GO.
Selective Rescue 001 remains scientific NO_GO at final `5/8` CORRECT.
8B Validator-Guided Repair 001 remains MECHANICAL_NO_GO due hidden-spec leakage.

### VERIFY_RULE Validator Hardening 001 — GO
Result: `research/architecture/loom-verify-rule-validator-hardening-001-result.md`
Evidence: `results-local/research/verify-rule-validator-hardening-001/20260829T123542Z/report.json`
Harness SHA `66aaee0fa5cba740113b92a0bdf94d8043150e6ac86e2e92c51093a6c67a58bc`.

Observed:
- `24/24` fixtures correct;
- confusion `TP 8 / TN 16 / FP 0 / FN 0`;
- contradiction reject `2/2`;
- forbidden-heuristic reject `2/2`;
- p95 `0.006542 ms`;
- no inference/network/external packages.

The planned fresh sanitized guided-repair suite is PAUSED, not cancelled. Do not execute it unless canonical context explicitly reactivates it.

## Current priority — 30B Apple MoE Paging Feasibility 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-preregistration.md`

Question: can the Apple M1 8GB host build and expose a real Metal expert-paging runtime for Qwen3-30B-A3B before any model download?

Frozen primary source:
- `kisasexypantera94/llama.cpp`
- branch `moe-expert-residency`
- commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Public reference evidence reports the mechanism on Apple Silicon, including Qwen3-30B-A3B Q6_K on M1 Pro 16GB at 13 tok/s after warmup. This is external reference evidence only, not a claim for the M1 8GB host.

`ik_llama.cpp` is reference material for quant/kernel ideas; do not assume it is the Mac backend because its maintainers do not treat Metal as a fully performant supported backend.

This feasibility checkpoint allows source-code network fetch only. **No model download, no inference, no package-manager installs, no source patching.**

Create exactly:
`scripts/loom_30b_apple_moe_paging_feasibility_001.py`

Required: exact source checkout, native Metal build, MoE flag/device verification, source proof of bounded expert slots + disk reads + Metal synchronization, read-only local storage probe if possible, 8GB memory projection, and compatibility classification of the frozen ByteShape KQ-3.25 and IQ-3.29 candidates.
