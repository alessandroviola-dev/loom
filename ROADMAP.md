# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`
Strategic next: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Architecture feasibility — PROVEN

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact anatomy:
- total tensor payload 16,220,499,968 B;
- resident non-routed target 819,015,680 B;
- external routed bank 15,401,484,288 B;
- 48 layers, 128 experts/layer, top-k 8;
- one expert 2,506,752 B;
- zero-cache expert payload 962,592,768 B/position;
- BF16 KV 98,304 B/token.

Established on M1 8 GB:
- lossless expert-major representation;
- device-verified SSD feasibility;
- bitwise-exact one-layer external experts;
- complete shared backbone residency;
- bitwise-exact 48-layer full forward;
- production-like GC cadence with zero swap delta;
- first real greedy generation.

## B — First real greedy generation — PASS

`LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`:
- prompt -> correct `4`, then EOS;
- zero-cache decode 1.54535 s / 0.6471 tok/s;
- 962,592,768 expert bytes/decode token;
- source layout 3,456 component preads/token;
- no expert leak, no swap growth.

This established the first real sequential baseline but showed expert access dominated decode.

## C — Expert-major real decode A/B — PASS

`LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001_PASS`.

Report: `research/moe/loom-30b-moe-trace-pack-decode-ab-001-result.md`.

A trace-scoped 962,592,768-B expert-major binary containing the 384 experts required by the canonical decode step was validated exactly.

One-factor A/B:
- source layout: 3,456 preads/token;
- packed layout: 384 preads/token;
- useful bytes unchanged;
- read-call reduction: 88.89%;
- router/logits/output parity: PASS.

Measured effect:
- expert-read median 1.085528 -> 0.442087 s (-59.27%);
- total decode median 1.645328 -> 0.926028 s (-43.72%);
- decode-equivalent 0.607781 -> 1.079881 tok/s.

Packed treatment remains memory-safe:
- MLX peak ~881 MB;
- RSS peak ~911 MB;
- swap delta 0;
- final expert residency 0.

Strategic consequence: **PACKED is now the correct baseline for cache economics.** Storage layout alone roughly doubled the practical one-step decode rate relative to the original source-range path, without reducing bytes transferred.

## D — Current bottleneck after packing

Packed treatment median cost:
- expert access ~47.74%;
- attention ~19.56%;
- reconstruction ~4.72%;
- expert compute ~0.45%;
- other ~27.52%, including material synchronization cost.

Expert traffic remains 918 MiB/token at zero cache. Packing improves access geometry but does not solve transfer volume.

The next high-leverage question is therefore real cross-token expert reuse.

## E — Routing/cache trace — NEXT CORE

Checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`.

Goal: collect a materially longer real generation trace and quantify cache value before implementing any cache.

### Trace acquisition

Use a deterministic prompt that reliably produces a nontrivial answer. Target:
- minimum 16 decode positions;
- preferred 24–32 if safe;
- bounded generation;
- greedy deterministic output;
- BF16 KV;
- resident backbone + serial external experts + `GC_END_ONLY`.

Because the existing packed binary covers only the prior one-step trace, arbitrary trace acquisition may temporarily use source exact ranges. Performance from that acquisition is not the promoted packed baseline.

### Required trace analysis

For every token/layer:
- top-k expert IDs and weights;
- same-layer overlap with previous tokens;
- reuse distance;
- expert frequency/hotness;
- transition structure;
- working-set size by layer and globally.

### Cache simulation

No real cache yet.

Simulate at minimum:
- LRU;
- LFU or frequency-aware admission;
- segmented/hot-cold policy if trace evidence supports it.

Budgets:
- 512 MiB;
- 1 GiB;
- 2 GiB;
- 3 GiB;
- 4 GiB.

One complete expert = 2,506,752 B.

Report for each policy/budget:
- experts capacity;
- hit rate;
- misses/token;
- external bytes/token;
- traffic reduction vs 962,592,768-B zero-cache baseline;
- estimated packed reads/token;
- estimated packed I/O/access wall using measured packed-path costs;
- memory headroom with resident backbone + observed KV.

Do not infer speed from hit rate alone; calculate packed-path lower-bound economics explicitly.

## F — Full expert-major pack decision

Current status: CONDITIONAL.

The 43.72% real decode gain strongly supports expert-major storage, but we do not yet automatically duplicate all 14.344 GiB routed weights.

After cache trace, choose among:
1. full 14.344-GiB expert-major pack;
2. hot-set packed cache + source cold fallback;
3. on-demand packed representation;
4. layer-segmented packs.

Prefer the smallest representation that captures measured performance value.

## G — Real cache implementation

Only after trace simulation:
1. select one policy/budget;
2. implement against PACKED semantics;
3. preserve deterministic output;
4. measure actual bytes/token, decode tok/s, MLX/RSS/swap;
5. compare with packed zero-cache ~1.08 decode-equivalent tok/s and original source zero-cache ~0.65 tok/s.

## H — DFlash / block speculative branch — LATER/PARALLEL

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

Audit static footprint/compatibility after cache economics are known. Potential value is accepted-token amortization and union-of-experts reuse; it must be net-positive after draft memory/workspace and remaining external traffic.

## I — Performance escalation order

If packed + cache remains insufficient:
- block union/coalescing;
- DFlash/speculative verification;
- route prediction/prefetch;
- lower storage granularity / neuron clusters;
- faster external NVMe as a secondary hardware branch;
- LOOM-native model/system co-design if necessary.

## J — Promotion gates

After practical speed exists:
- longer stable generation;
- capability/coding benchmark;
- context scaling;
- reproducibility;
- behavioral decensoring via Heretic or LOOM-native equivalent.

## Immediate order

1. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
2. choose full/hot/on-demand packed representation from trace evidence
3. implement smallest trace-backed expert cache
4. remeasure real generation
5. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`
6. DFlash/block integration only if net-positive
7. capability benchmark
8. custom architecture research if necessary
9. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.