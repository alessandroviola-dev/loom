# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-31
Status: FINAL product persisted; UOPT-001 PARTIAL_GO/persisted; UOPT-002 architectural UNLOCKED optimization active

## Purpose

Use substantial Pi macro work packages instead of user-facing micro-checkpoints. Pi records/fixes/reverts routine failures internally and returns only at macro completion or a genuine user-action blocker.

## Finished product

Final persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Profiles:
1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — validated behavioral-unlock profile.

Final UX:
```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable endpoint: `127.0.0.1:18080` loopback only.

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted.

WP3 Behavioral Transform: valid NO_GO for bounded low-rank routes.

WP3-R2 Behavioral Unlock: GO / persisted; frozen result `0/6` refusal, `0/6` held-out degeneration, `8/8` benign.

WP4 Final Integration + Acceptance: GO / persisted.

## UOPT-001 — COMPLETE / PARTIAL_GO / PERSISTED

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Persistence commit:
`93b5f44733d120a4e9c0f0b1fea6e58309f71ccd`.

Retained UNLOCKED `-ub 2`; FAST remains `-ub 1`.

Matched retained metrics:
- decode `2.579 -> 3.161 tok/s`;
- short TTFT `19.525 -> 15.283 s`;
- ~413-token cold TTFT `199.104 -> 184.700 s`;
- ~1,150-token cold TTFT `433.558 -> 393.983 s`;
- warm long-prefix TTFT `0.195 -> 0.190 s`.

All behavior/capability/integration gates passed. Broad current-runtime tuning was exhausted; remaining bottleneck is expert paging/cold prefill.

## UOPT-002 — Architectural UNLOCKED Speed Optimization — ACTIVE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_002`

Contract:
`research/integration/loom-unlocked-speed-optimization-002.md`

Known-good rollback baseline:
persisted UOPT-001 S32 / CPU-MoE / no-mmap / UNLOCKED ub2.

Full-GO targets:
1. matched fresh decode >= `5.0 tok/s`;
2. ~1,150-token cold TTFT <= `184 s`;
3. preserve all frozen/product gates.

Stretch cold TTFT: `<120 s`.

Architectural ladder:
1. expert-granular I/O/paging attribution;
2. bounded expert residency implementation audit/reproduction;
3. router-driven sorted/merged explicit expert prefetch;
4. page-amplification mitigation without destructive/full-copy assumptions;
5. streamed expert cache and compute-I/O overlap with unchanged routed top-k;
6. exact-output speculative decode only as a justified fallback.

Relevant external research hypotheses include oversized-moe-runtime, page-aware ExpertCache, explicit-read prefetch, and expert-contiguous/SSD streaming work. Pin exact revisions and reproduce locally; never promote from external benchmark claims alone.

Storage constraint: UOPT-001 observed ~5 GiB free at that time. Re-measure. Never mutate hard-linked stable GGUFs; do not create a second full UNLOCKED GGUF if current free disk cannot safely hold it.

Frozen gates:
- refusal `0/6`;
- held-out degeneration `0/6`;
- benign `8/8`;
- no reduced-active-expert/turbo-top-k speed shortcut;
- exact provenance;
- loopback API/WebUI/Pi+WP2/cache;
- no crash/OOM/corruption;
- FAST + UOPT-001 rollback.

Evidence:
`results-local/unlocked-speed-uopt-002/<timestamp>/`.

Pi does not commit/push during UOPT-002.

## Global execution rules

1. Evidence over narrative.
2. Do not return after routine experiment NO_GO results.
3. Never relax frozen gates after seeing results.
4. Preserve exact provenance and hashes.
5. Keep known-good FAST and UNLOCKED rollback baselines.
6. No public internet exposure by default.
7. No SIP/security disabling or destructive unrelated cleanup.
8. Large local models remain outside Git.
9. External benchmark claims are hypotheses until locally reproduced.
10. Never destructively modify hard-linked stable model artifacts.
11. Pi commits only under the explicit bounded macro-boundary exception.
