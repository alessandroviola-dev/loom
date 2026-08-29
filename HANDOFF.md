# LOOM — Active Handoff

Last updated: 2026-08-29
Status: ACTIVE — Apple Metal MoE expert paging Stage1R2 completed **GO** with the first valid 30B measurements on base M1 8 GiB. Best safe profile S24 reached 4.40 tok/s. Canonical DEEP is not replaced yet; next checkpoint is a metadata/provenance comparability audit before Stage2 reproducibility + matched practical/quality evaluation.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_STAGE2_COMPARABILITY_AUDIT_001`
Pi context: `/AGENTS.md` v3.69.

## Product direction

- BALANCED 8B remains provisional primary at ~13 tok/s.
- DEEP 30B historical custom MLX path is ~1.4 tok/s.
- Apple Metal MoE paging is now a serious DEEP candidate after S24 reached 4.40 tok/s, but Stage2 must establish reproducibility and quality before product-default changes.
- FAST retained conceptually; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

## Validator track — paused cleanly

`LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`: 24/24, FP/FN 0/0, p95 0.006542 ms. Sanitized guided-repair remains paused, not cancelled.

## Apple MoE paging mechanism — GO

Frozen source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Correct one-shot frontend:
`llama-completion -no-cnv`

Frozen frontend SHA256:
`38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`

Frozen recovered harness:
`scripts/loom_30b_apple_moe_paging_stage1_001.py`
SHA256:
`4b1dd6edb2d8a9bda64a034cbf771b05d2bfc7c267c9ee547b49e8d465154eac`

The harness uses durable direct streaming, bounded parent-memory accounting, 64 MiB/profile output cap, incremental telemetry and finalization on all exit paths.

## Stage1 / Stage1R mechanical history

Stage1:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1_MECHANICAL_NO_GO`.

Stage1R:
`LOOM_30B_APPLE_MOE_PAGING_STAGE1R_MECHANICAL_NO_GO`.

No performance claim follows from those attempts. The mechanical root causes were instrumentation/evidence durability and use of interactive `llama-cli`.

## Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Evidence:
`results-local/research/30b-apple-moe-paging-stage1r2-001/20260829T211631Z/final-report.json`

Classification:
**`LOOM_30B_APPLE_MOE_PAGING_STAGE1R2_GO`**.

Verified model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Size: `12,424,439,872` bytes.
SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Measured profiles:
- S8: 2.99 generation tok/s; prompt 2.95 tok/s; load 19.294 s; E2E 52.606 s; headroom 33%; swap 1110.0 MiB.
- S16: 3.58 generation tok/s; prompt 3.43 tok/s; load 16.625 s; E2E 45.110 s; headroom 22%; swap 1110.0 MiB.
- S24: **4.40 generation tok/s**; prompt **3.95 tok/s**; load **14.426 s**; E2E **37.704 s**; headroom 13%; swap 1125.94 MiB.

S24 is the best safe profile. No critical memory pressure, OOM, output corruption, NaN, repeated-token collapse or output-runaway occurred. All profiles produced the same deterministic coherent Italian answer satisfying the Stage1 functional guard.

Historical contextual speedup at S24:
- **3.1384×** vs 1.402 tok/s compact practical DEEP reference;
- **3.5795×** vs 1.229233 tok/s historical exact-Q4 reference.

These are not strict same-artifact one-factor comparisons.

TTFT was not separately observable in Stage1R2; load and E2E were retained.

## Exact next action — Stage2 comparability audit

Before preregistering a matched quality comparison, inspect existing repository/local metadata only to identify the exact historical custom MLX 30B checkpoint/artifact used for the ~1.4 tok/s references.

Determine whether the historical artifact is:
1. exact checkpoint-identical to `Qwen3-30B-A3B-Instruct-2507`;
2. same architecture/family but different checkpoint;
3. insufficiently identified for strict quality comparison.

No inference, download, package install, source/runtime edit, model mutation or Git action by Pi.

After this audit, preregister Stage2 with S24 reproducibility + fresh matched practical tasks + memory/swap stability + quality/correctness preservation. If checkpoint identity differs, performance may still be compared as practical runtime classes, while quality claims must be explicitly nonmatched or separately controlled.

Do not replace canonical DEEP solely from Stage1R2.