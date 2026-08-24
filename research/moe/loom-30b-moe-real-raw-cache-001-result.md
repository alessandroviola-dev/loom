# LOOM 30B MoE — REAL RAW CACHE 001

Run: `20260824T092553Z`
Classification: `LOOM_30B_MOE_REAL_RAW_CACHE_001_MEMORY_FAIL`

## Experiment

Real `GLOBAL_LRU` raw-expert-byte cache on the Qwen3-30B-A3B external-expert runtime.

Preregistered cache:
- logical budget: 4,294,967,296 B;
- capacity: 1,713 `(layer, expert)` entries;
- one expert: 2,506,752 B;
- raw canonical expert bytes resident; transient MLX expert arrays only;
- cache persisted across P1/P2/P3;
- cold path used original source component ranges.

Raw evidence:
`results-local/moe/real-raw-cache-001/20260824T092553Z/`

## Correctness

- CONTROL/TREATMENT completed P1/P2/P3.
- deterministic token parity: PASS.
- final persistent routed MLX expert arrays: 0 / 0 B.
- cache-clear ownership gate: PASS.

The cache did not change model semantics.

## Cache behavior

Real decode positions: 93.

Across 98,304 expert accesses:
- hits: 81,230;
- misses: 17,074;
- evictions: 15,361;
- actual decode hit rate: **80.9056%**;
- trace-simulation expectation: 79.598%;
- difference: +1.3076 pp.

Per-prompt hit rates:
- P1: 83.6694%;
- P2: 78.4610%;
- P3: 80.5864%.

Cross-prompt retained-cache hits:
- P2: 355;
- P3: 289.

The routing-cache simulation was therefore validated well: the expected ~80% reuse is real and stable across these workloads.

Traffic:
- source bytes/decode token: 183,801,525.68 B;
- traffic reduction vs 962,592,768-B zero-cache baseline: **80.9056%**;
- source component reads/decode token: 659.9032.

## Performance — failure

CONTROL:
- 1.428821 s/token;
- 0.699878 tok/s.

4-GiB RAW GLOBAL_LRU treatment:
- **4.883706 s/token**;
- **0.204763 tok/s**;
- P50/P90/P95: 4.163989 / 7.461670 / 8.372438 s;
- last-half rate: 0.224337 tok/s.

Relative effect: **-70.7431% throughput** / +3.454885 s/token.

Treatment mean categories per token:
- cold-read: 1.928012 s;
- cache management: 0.051188 s;
- MLX reconstruction: 1.791990 s;
- expert compute: 0.212459 s;
- attention/shared: 0.529872 s;
- other: 0.354431 s.

Thus high cache hit rate did not translate to speed. The resident raw cache induced severe system-memory pressure and made the remaining work substantially slower.

## Memory gate — FAIL

Peak cache entries: 1,713.
Peak raw payload: 4,294,066,176 B.
Measured cache-object overhead lower-bound: 516,217 B.

Treatment:
- MLX peak: 903,008,264 B;
- sampled RSS: 767,049,728 B;
- `ru_maxrss`: 1,088,946,176 B;
- swap: **829.50 -> 3240.06 MiB**;
- swap delta: **+2410.56 MiB**;
- memory pressure: **FAIL**;
- progressive memory growth: YES.

The low sampled resident-process number does not make the 4-GiB cache safe: the large cache payload was aggressively compressed/swapped, and the system-level swap delta is the decisive failure signal.

## Decisions

- Real 4-GiB raw cache materially useful: **NO**.
- 4-GiB raw cache on M1 8 GB: **NO / MEMORY FAIL**.
- Persistent live-MLX cache experiment next: **NO**.
- Full expert-major pack: not promoted by this result.
- Returned storage direction: `SOURCE_COLD_ONLY` for the immediate runtime; the prior measured on-disk expert-major access benefit remains valid independently.
- DFlash/block branch required for >2 tok/s: **YES**.

The failed 4-GiB cache must not be silently rescued by reducing its size inside this checkpoint. Smaller/admission-controlled caches may be separate future experiments if later evidence makes them worthwhile.

## Strongest conclusion

The routing model was correct — ~81% reuse exists — but retaining 4 GiB of raw expert payload on an 8-GB M1 creates severe swap pressure and reverses the expected performance gain. Expert reuse is scientifically real; this particular realization is operationally invalid. The next high-leverage branch is multi-token/block amortization / exact-target DFlash rather than a larger or live-MLX cache.