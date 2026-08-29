# LOOM — Active Handoff

Last updated: 2026-08-29
Status: ACTIVE — `V_VERIFY_RULE` hardening completed GO. The validator/guided-repair track is now PAUSED by explicit project decision while 30B runtime acceleration becomes the immediate priority.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_APPLE_MOE_PAGING_FEASIBILITY_001`
Pi context: `/AGENTS.md` v3.65.

## Product direction

- BALANCED 8B remains the fast provisional primary tier (~13 tok/s).
- DEEP 30B remains quality/escalation tier but current custom MLX runtime is too slow (~1.4 tok/s).
- FAST concept retained; legacy 4B parked.
- LOOM AUTO validator-first work remains valid but paused during this runtime investigation.
- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Closed validator checkpoint

`LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`

Result:
`research/architecture/loom-verify-rule-validator-hardening-001-result.md`

Evidence:
`results-local/research/verify-rule-validator-hardening-001/20260829T123542Z/report.json`

Observed: 24/24 correct fixtures, FP/FN 0/0, contradiction rejection 2/2, forbidden-heuristic rejection 2/2, p95 0.006542 ms, no inference/network/package mutation.

A future fresh sanitized guided-repair suite is PAUSED, not cancelled. Do not execute it now.

## New external runtime evidence

Public work shows a materially different approach to oversized MoE inference:
- Potato OS reports Qwen3-30B-A3B low-bpw GGUF around 8–9 tok/s on Raspberry Pi 5 8GB + SSD;
- an Apple-Silicon llama.cpp PoC implements bounded Metal expert slots, LRU residency, disk-backed expert loading and Metal synchronization;
- that PoC reports Qwen3-30B-A3B Q6_K on M1 Pro 16GB at 13 tok/s after warmup.

The Apple PoC source is frozen for investigation:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`, branch `moe-expert-residency`.

These are external reference results only. They do not establish performance on the user's base M1 8GB.

## Exact next action

Read:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-preregistration.md`

Create only:
`scripts/loom_30b_apple_moe_paging_feasibility_001.py`

Feasibility only:
1. verify host/toolchain/storage;
2. fetch exact frozen PoC source commit into results-local;
3. build native Metal CLI without source patches/package installs;
4. verify `--moe-n-slots`, `--moe-n-layers`, `--no-mmap`, `--no-warmup` and Apple Metal device path;
5. source-confirm bounded expert cache/LRU + disk read + Metal sync mechanism;
6. perform read-only local I/O diagnostic if an existing large artifact is available;
7. project 8/16/24/32 expert-slot memory envelopes for the M1 8GB;
8. classify ByteShape Q3_K_S-3.25bpw and IQ3_S-3.29bpw compatibility.

No model download. No inference. No package-manager mutation. No source patching. No Git commit/push.

If GO, the following checkpoint may authorize exactly ONE ~12.5GB GGUF download and a bounded real-generation test.
