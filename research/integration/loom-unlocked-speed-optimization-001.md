# LOOM UNLOCKED Speed Optimization — UOPT-001

Date: 2026-08-31
Branch: `research/unlocked-speed-001`
Checkpoint: `LOOM_UNLOCKED_SPEED_UOPT_001`
Status: AUTHORIZED

## Objective

Push the validated UNLOCKED profile to the maximum practical decode throughput on the current Apple M1 8 GiB host while preserving its validated behavior/capability and the finished LOOM product interfaces.

Primary target: **>= 5.0 tok/s matched fresh decode**.

Stretch target: exceed FAST's historical 5.596 tok/s without weakening frozen gates.

Baseline from WP4:
- UNLOCKED decode: `2.963 tok/s` operational snapshot;
- model: `models/loom-deep-30b-unlocked.gguf`;
- SHA256: `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`;
- runtime SHA256: `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`;
- final serving flags include `--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

## Frozen invariants

A speed candidate is promotable only if all remain true:

1. unchanged UNLOCKED frozen held-out explicit refusal result: `0/6`;
2. unchanged benign capability: `8/8`;
3. held-out degeneration remains `0/6`;
4. exact model provenance is recorded; if a new quant is tested, it must derive from the same validated Huihui exact-base derivative and get a new SHA/provenance record;
5. loopback-only serving remains `127.0.0.1`;
6. Pi + WP2, API, WebUI, prompt/KV cache and FAST rollback remain functional;
7. no hidden cloud inference or conversation-data egress;
8. no destructive host/security changes.

Do not trade away the behavioral-unlock result merely to reach the speed target.

## Measurement protocol

Performance claims must use matched deterministic fresh-decode probes, not unmatched refusal-length E2E timings.

For each serious candidate:
- identical prompt and generation settings;
- at least 3 fresh runs after one warmup unless a candidate is obviously non-competitive;
- report median decode tok/s, prefill tok/s, E2E, RSS, swap, memory-pressure/free-memory signal;
- record runtime/model hashes and exact flags;
- preserve full evidence under `results-local/unlocked-speed-uopt-001/<timestamp>/`.

Use the current validated UNLOCKED profile as rollback baseline throughout.

## Optimization ladder

Pi should move through this ladder autonomously, keeping winners and reverting losers. Do not return after routine NO_GO experiments.

### A — current-runtime parameter frontier

First exhaust cheap reversible runtime tuning on the exact current UNLOCKED GGUF:
- MoE slot/residency frontier around current S32, including plausible smaller/larger values;
- `mmap` vs `no-mmap` only where safe and measurable;
- CPU-MoE / Metal placement combinations supported by the runtime;
- batch/ubatch and relevant thread/Metal knobs;
- cache settings only if they affect fresh decode without breaking prompt-cache behavior.

Do not assume the FAST optimum is also the UNLOCKED optimum.

### B — newer compatible llama.cpp / MoE paging implementations

Compare the pinned runtime against current evidence-backed Qwen3-MoE runtimes/patches. Priority research target:
- bounded expert-residency / mmap-prefetch approaches such as the recent `oversized-moe-runtime` work, which reports a Qwen3-30B-A3B decode improvement from `5.79` to `8.81 tok/s` with a residency quota of 48 experts/tensor on its tested system;
- newer llama.cpp MoE/Metal changes that can be isolated and benchmarked without changing model behavior.

Treat external benchmark numbers as hypotheses, never as LOOM results. Pin exact upstream revision before any adoption and audit the patch/runtime boundary.

### C — exact-lineage quantization frontier

If runtime work alone cannot reach the target, test smaller/faster quantizations of the same validated Huihui abliterated derivative. A new quant is eligible only if:
- exact source lineage and conversion/quantization provenance are recorded;
- the frozen `0/6`, `8/8`, `0/6` gates still pass;
- practical capability does not materially regress;
- the speed/resource gain is real under matched probes.

Prefer the smallest number of scientifically useful candidates; do not create a broad quantization zoo.

### D — combined best runtime + best eligible quant

Only after A-C identify independent winners, test the strongest justified combination and verify full LOOM integration.

## Promotion rules

### `LOOM_UNLOCKED_SPEED_UOPT_001_GO`

Requires:
- matched fresh decode median >= `5.0 tok/s`;
- all frozen behavior/capability invariants pass;
- stable API/WebUI/Pi+WP2/cache;
- no crash/OOM/corruption;
- exact hashes/provenance;
- clean rollback to current FAST and current validated UNLOCKED baseline.

### `LOOM_UNLOCKED_SPEED_UOPT_001_PARTIAL_GO`

Allowed only if the branch finds a reproducible substantial improvement but remains below 5.0 tok/s after exhausting justified local routes. Preserve the fastest validated profile and report the physical bottleneck with evidence.

### Genuine blocker

Return to the user only for an action Pi cannot safely/legitimately perform locally, such as a required paid external resource, unavailable credential, destructive host change, or missing artifact that cannot be reconstructed. Routine experiment failure is not a blocker.

## Product integration

Do not alter FAST behavior or make an experimental runtime the default during research.

Keep normal product UX intact:

```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

A promoted optimization may replace the implementation behind `unlocked` only after final acceptance. FAST remains the rollback/default profile unless separately changed by an explicit later decision.

## Persistence

Pi does not commit/push during execution. At macro completion, return one bounded report for review. Git persistence, if authorized, must exclude GGUFs, `.loom/`, `results-local/`, home config, caches, external repo checkouts and unrelated historical files.
