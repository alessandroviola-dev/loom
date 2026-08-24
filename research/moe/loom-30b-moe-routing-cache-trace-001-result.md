# LOOM — 30B MoE Routing Cache Trace 001

Classification: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001_PASS`
Run: `20260824T090555Z`

Raw evidence: `results-local/moe/routing-cache-trace-001/20260824T090555Z/`

## Scope

Collected a multi-prompt real autoregressive routing corpus from the external-expert Qwen3-30B-A3B path, then simulated cache policies without implementing a cache. Cache economics use the measured PACKED one-read/expert baseline from `TRACE_PACK_DECODE_AB_001`; trace acquisition itself may use source exact ranges.

## Trace

- prompts: 3/3 completed;
- 96 traced decode positions (93 one-position transitions);
- routing selections: 36,864;
- unique `(layer, expert)` keys touched: 3,747 / 6,144 = 60.9863%;
- consecutive same-layer intersection mean/P50/P90: 3.545 / 3 / 6 experts out of top-k 8;
- reference reuse within 1/2/4/8/16/32 tokens: 42.923% / 53.079% / 62.826% / 72.030% / 78.692% / 80.265%.

Mean / P90 working-set sizes in experts:
- 1 token: 384 / 384;
- 2: 597.86 / 653.8;
- 4: 910.31 / 1,025;
- 8: 1,333.39 / 1,462.4;
- 16: 1,823.69 / 1,988;
- 32: 2,425 / 2,581.

## Online cache simulation

Best online policy in the tested set: `GLOBAL_LRU`.

Global LRU:
- 1 GiB / 428 experts: 43.473% hit, 544,121,856 B external/token;
- 1.5 GiB / 642: 52.067%, 461,399,040 B/token;
- 2 GiB / 856: 59.961%, 385,413,120 B/token;
- 3 GiB / 1,285: 71.864%, 270,833,664 B/token;
- 4 GiB / 1,713: 79.598%, 196,388,352 B/token.

Small global LRU budgets <=512 MiB produced zero hits because the sequential whole-token working set exceeds capacity and churns before the same layer is revisited on the next token. Per-layer equal LRU avoids total zero-hit behavior at small sizes but is not materially better at the large budgets of interest.

The 4 GiB global-LRU case reduces external expert traffic by 79.598% from the 962,592,768-B zero-cache baseline.

## Upper bounds / references

At 4 GiB:
- online global LRU: 79.598% hit;
- per-layer equal LRU: 79.083%;
- online LFU: 62.961%;
- offline Belady oracle: 87.961%;
- trace-fitted static hot set: 82.935%.

The online LRU is therefore reasonably close to the trace-fitted static hot set and within ~8.4 percentage points of the non-implementable oracle at 4 GiB.

## Projected packed economics

For 4 GiB global LRU:
- external bytes/token: 196,388,352 B;
- APPLICATION_PACKED expert-read estimate: 0.090195 s/token;
- projected current-runtime decode: 0.574136 s/token = 1.74175 tok/s;
- DEVICE_CONSERVATIVE projection: 0.577718 s/token = 1.73095 tok/s;
- raw-packed-byte-cache projection: 0.612595 s/token = 1.63240 tok/s;
- optimistic live-MLX-expert-cache projection: 0.574136 s/token = 1.74175 tok/s.

These are projections, not measured cached generation.

Logical working set for the 4 GiB candidate at the maximum trace KV observed:
- cache: 4,294,066,176 B;
- backbone: 819,015,680 B;
- KV: 9,240,576 B;
- total: 5,122,322,432 B.

Headroom remains ~1.32 / 1.86 / 2.39 GB under 6.0 / 6.5 / 7.0 GiB envelopes, before unmeasured large-cache MLX object/allocator overhead.

## Block-union structure

Mean union bytes/position for ordinary consecutive-token blocks:
- 2: 749,343,645 B;
- 3: 642,396,979 B;
- 4: 570,480,569 B;
- 5: 519,237,866 B;
- 6: 479,315,740 B;
- 7: 446,068,713 B;
- 8: 417,808,712 B.

A structural cache+block counterfactual reaches 197,015,040 B/position for a 2-position case. This is routing structure only; it is not DFlash speed or accepted-token performance.

## Structural speed ceiling

The current PACKED non-read floor is ~0.483941 s/token. Therefore even a perfect 100%-hit expert cache cannot exceed ~2.06637 tok/s without reducing/amortizing non-read work.

Under the current single-token runtime:
- 2 tok/s: structurally possible;
- 3 tok/s: not possible from cache alone;
- 5 tok/s: not possible from cache alone.

Thus multi-token/block amortization and/or additional fixed-cost reduction is required for 3+ tok/s.

## Decision

- routing/cache study: PASS;
- next real cache candidate: `GLOBAL_LRU`, 4 GiB logical, 1,713 experts;
- full 14.344-GiB expert pack: CONDITIONAL;
- preferred storage representation: `HOT_SET_PACK_SOURCE_COLD`;
- DFlash/static block branch: CONDITIONAL but increasingly justified because cache-only speed has a measured structural ceiling.

The next runtime experiment should implement a memory-safe real cache and measure exact output, actual hit rate, bytes/token, MLX/RSS/swap and decode speed. A raw packed-byte cache is the safer first realization because large live-MLX cache object/allocator overhead remains unmeasured.