# LOOM 30B Expert-Major Canonicalization 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Productionize the already accepted full-bank expert-major runtime backend into reusable canonical LOOM code without reopening the settled physical-I/O or runtime-performance questions.

This is a productionization checkpoint, not a new scientific mechanism experiment.

Final outcomes only:
- `EXPERT_MAJOR_CANONICALIZATION_GO`
- `EXPERT_MAJOR_CANONICALIZATION_NO_GO`
- `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`

## Established acceptance baseline

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Accepted runtime evidence:
- full bank `6144/6144`, `15,401,484,288 B`;
- static dry-run `18,048` accesses, zero unresolved/fallback/cache;
- three-position full-runtime exactness PASS with identical raw float32 final-logit SHA;
- runtime PACKED/SOURCE ratios `0.794284`, `0.846718`, `0.768208`;
- median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS, swap delta `0 MiB`, no unsafe pressure.

Do not rebuild or re-benchmark the accepted mechanism unless a canonicalization regression requires a bounded check specified below.

## Stage 0 — recover accepted implementation

Use only local retained evidence and current repo state; no network/model download.

1. Inspect the accepted funnel directory:
   `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`.
2. Identify the exact accepted full-bank builder/manifest format, backend adapter code, runtime interface and acceptance workload.
3. Verify the retained full-bank artifact and manifest still pass their stored integrity/provenance contract before reusing them.
4. Determine the minimal reusable repo code needed for:
   - deterministic full-bank build/reuse;
   - manifest validation;
   - `(layer_id, expert_id) -> payload` resolution;
   - SOURCE/PACKED backend selection;
   - zero hidden fallback and no persistent expert cache.

If accepted implementation/provenance cannot be recovered unambiguously: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE` and STOP.

## Stage 1 — canonical code integration

Pi may edit runtime/source code in the working tree, but must not commit/push or edit project decision docs.

Requirements:
- preserve the existing SOURCE backend unchanged as a control/fallback-free selectable implementation;
- add a reusable expert-major backend through an explicit backend interface;
- preserve routing, expert math, quantization, dtypes, KV behavior, scheduling/synchronization and output computation;
- no persistent expert cache;
- full-bank artifact remains external/local and is not added to Git;
- builder/validator must be deterministic and resumable where materially expensive;
- manifest scope/provenance must be machine-readable;
- fail closed on missing/corrupt/incompatible expert entry; do not silently fall back to SOURCE;
- keep changes minimal and localized.

## Stage 2 — static production gate

Before model forward:
- Python/code syntax or compile checks PASS;
- full manifest validates `6144/6144`;
- complete mapping uniqueness and bounds PASS;
- replay the retained required access sequence through the canonical backend: `18,048` accesses, zero unresolved, zero ambiguous, zero SOURCE fallback;
- confirm no persistent expert cache/state accumulation;
- report changed files and a concise diff/stat summary.

Any deterministic production-code defect that prevents these gates from passing after the intended minimal implementation is complete => `EXPERT_MAJOR_CANONICALIZATION_NO_GO`.
A genuinely missing/inaccessible accepted artifact/environment dependency => INCONCLUSIVE.

## Stage 3 — canonical exactness regression gate

Use the same accepted frozen workload and exactly three consecutive decode positions.

Compare canonical SOURCE vs canonical PACKED and require:
- identical routed expert identities/order at every layer/position;
- mapping/hash PASS;
- identical raw final-logit float32 SHA for all three positions;
- zero backend fallback;
- no persistent expert cache;
- no unsafe memory-pressure event.

Any valid exactness mismatch => `EXPERT_MAJOR_CANONICALIZATION_NO_GO` and STOP.

## Stage 4 — bounded performance/safety smoke

This is not a new full A/B campaign.

Use one fresh-process matched pair only, frozen order `SOURCE -> PACKED`, with the same accepted workload/settings:
- prefill;
- one unmeasured warmup decode token;
- exactly three measured decode tokens;
- record aggregate wall, RSS, swap, backend/routing status.

Purpose: detect a productionization regression, not re-estimate the accepted effect.

PASS requires:
- valid complete timing;
- no fallback/error/unsafe pressure;
- PACKED aggregate decode wall <= `0.95 × SOURCE`;
- PACKED peak RSS <= SOURCE + `128 MiB`;
- PACKED swap delta <= SOURCE + `64 MiB`;
- no persistent expert cache.

If valid but PACKED/SOURCE wall ratio > `0.95`, or safety regresses: `EXPERT_MAJOR_CANONICALIZATION_NO_GO`.

## Final decision

`EXPERT_MAJOR_CANONICALIZATION_GO` iff Stages 0–4 PASS.

On GO, return the exact changed-file list, tests/evidence, artifact path/manifest path and concise instructions for ChatGPT/user to review and commit the production code. Pi must not Git commit/push or edit AGENTS/HANDOFF/ROADMAP.

## Hard bounds / efficiency

- no network/model download;
- reuse accepted full-bank artifact; do not rebuild if integrity PASSes;
- no new cache/eviction mechanism;
- no DFlash;
- no physical-cold-I/O benchmark;
- one performance pair only;
- exactly three exactness positions;
- deterministic scripts/JSON for coverage/provenance;
- read only directly relevant code/evidence;
- no broad history re-derivation;
- no rescue threshold changes.

Evidence:
`results-local/research/30b-expert-major-canonicalization-001/<UTC>/`
