# LOOM_UNLOCKED_SPEED_UOPT_006_SHORT_MATRIX

Date: 2026-09-05  
Branch: `research/unlocked-speed-001`  
Classification: **Phase 1 short matrix COMPLETE / NO_GO for phase 2**

## Scope and invariants

This was a bounded (under 60-minute), loopback-only preflight and short A/B
matrix against the unchanged UOPT-003 production S40 configuration. Each cell
started a fresh isolated `llama-server` process on a private test port; the
production lifecycle manager, profile/configuration, model, sidecar and runtime
were not changed. The production manager was not running before or after the
matrix, and its selected profile remains `unlocked` / S40.

All cells used the same UOPT-002 isolated runtime, model, lossless sidecar,
S40 (`--moe-n-slots 40`), 48 MoE layers, CPU-MoE, no-mmap, context 4096, cache
RAM 512 MiB, `-ub 4`, and a fixed 299-token repeated-ngram prompt with greedy
deterministic sampling (`temperature=0`, `top_k=0`, `top_p=1`, `min_p=0`,
`seed=424242`, `n_predict=80`, no prompt-cache reuse). No model was downloaded;
no draft model, `ngram-cache`, EAGLE-3, DFlash, DSpark or MTP was used.

The actual runtime SHA-256 was
`088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b`.
Its own `--help` explicitly lists `none`, `ngram-simple`, and `ngram-mod` as
valid `--spec-type` values. Startup logs confirm that both ngram implementations
initialized successfully; `none` explicitly reports no speculative
implementation.

## Short matrix

One fresh short smoke was run for each mode. A mandatory one-fresh-run-per-cell
streaming instrumentation correction measured TTFT; it was not an extended
benchmark. No treatment met the 5% decode gate, so no further repetitions were
run.

| S40 mode | Decode tok/s (primary smoke) | Decode vs `none` | Prefill tok/s | TTFT s (streaming correction) | Greedy output parity | Verdict |
|---|---:|---:|---:|---:|---|---|
| `--spec-type none` | 5.918 | baseline | 12.732 | 22.897 | baseline | baseline retained |
| `--spec-type ngram-simple` | 5.949 | **+0.52%** | 15.311 | 19.111 | exact text equality | **NO_GO** (<5%) |
| `--spec-type ngram-mod` | 5.892 | **-0.45%** | 15.308 | 19.435 | exact text equality | **NO_GO** (regression) |

The streaming correction independently measured decode at 5.972 (`none`),
5.998 (`ngram-simple`, +0.44%), and 5.981 (`ngram-mod`, +0.14%). It confirms
that neither treatment approaches the 5% decode gate. The apparent
prefill/TTFT improvement is a single serial fresh-process observation under
variable host memory pressure, and cannot be attributed to speculation: the
runtime exposed zero drafted and zero accepted tokens in both treatments.
It is not a performance claim.

## Runtime-exposed speculative counters

Only counters printed by the runtime are used. For both ngram modes the final
statistics line reported `#calls(b,g,a) = 1 78 0`, `#gen drafts = 0`,
`#acc drafts = 0`, `#gen tokens = 0`, and `#acc tokens = 0`. Therefore
acceptance rate is **N/A (0/0)**, not 0%: no draft token was generated to be
accepted or rejected. `none` has no speculative implementation and no
acceptance counter.

## Memory and expert resolver/cache observations

Streaming-run post-request RSS was effectively identical: `4.676 GiB`
(`none`), `4.676 GiB` (`ngram-simple`), and `4.675 GiB` (`ngram-mod`).
Per-cell `vm.swapusage` snapshots showed no growth during the request:
`1699.88 -> 1619.88 MiB`, `1779.75 -> 1699.69 MiB`, and
`1711.75 -> 1554.38 MiB`, respectively. These serial host-wide snapshots are
recorded as observations rather than a cross-cell memory performance claim.
`ngram-mod` logged its actual additional 16 MiB ngram table allocation, with
no material RSS difference in this short probe.

The unchanged sidecar resolver emitted its final per-layer telemetry. Aggregated
primary-smoke cache results were: `none` 143,528 requests / 131,742 hits /
11,786 misses (91.788% hit rate); `ngram-simple` 143,528 / 131,749 / 11,779
(91.793%); `ngram-mod` 143,528 / 131,793 / 11,735 (91.824%). Resolver time was
14.826 s, 14.808 s, and 14.793 s respectively. These small differences do not
supply a speculative benefit because the speculative counters show zero drafted
and accepted tokens. No stall or request error occurred.

## Decision and recommendation

`ngram-simple` and `ngram-mod` both preserve the measured greedy output, but
neither generated speculative tokens and neither reached the immediate >=5%
decode gate. `ngram-mod` regressed in the primary comparable smoke. Both modes
are **NO_GO**, and **UOPT-006 phase 2 is not recommended** on this evidence.

Production UOPT-003 S40 remains the stable, unchanged baseline. No promotion,
Git action, runtime update, artifact mutation, or external-volume dependency
was made.

## Evidence

Complete local-only evidence is retained under:

`results-local/unlocked-speed-uopt-006/`

This includes the runtime help preflight, immutable-artifact provenance,
commands, raw JSON responses/timings, streaming TTFT captures, Prometheus
metrics, process/swap snapshots and final server telemetry for all three cells.
