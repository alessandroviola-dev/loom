# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`
Strategic next: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001`
Then: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
Parallel later: `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — 30B sparse-MoE target

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Exact anatomy:
- total tensor payload 16,220,499,968 B;
- mandatory/non-routed 819,015,680 B;
- routed expert bank 15,401,484,288 B;
- 48 MoE layers;
- 128 experts/layer;
- top-k 8;
- one expert 2,506,752 B;
- zero-cache useful expert traffic 962,592,768 B/position (918 MiB).

## B — Architecture feasibility — PROVEN

The following are now established on the reference M1 8 GB:

### Expert-major representation

`LOOM_30B_MOE_EXPERT_PACK_001_PASS`:
- lossless packing;
- source 9 ranges/expert -> packed 1 contiguous range;
- no byte amplification.

### Physical SSD

`LOOM_30B_MOE_PHYSICAL_IO_002_CONDITIONAL`:
- random expert physical ~1,890.4 MB/s;
- expert P50 1.197 ms;
- top-k P50 9.839 ms;
- storage-only zero-cache floor ~0.4816 s/token;
- 2.076 tok/s theoretical storage-only ceiling.

### External expert computation

`LOOM_30B_MOE_ONE_LAYER_EXTERNAL_EXPERT_001_PASS`:
- bitwise-exact decoder layer;
- 320,864,256 B full layer bank -> 2,506,752 B max logical expert live;
- 99.21875% expert residency reduction.

### Shared target residency

`LOOM_30B_MOE_SHARED_BACKBONE_RESIDENCY_001_PASS`:
- 819,015,680 B exact resident backbone;
- zero routed experts resident;
- BF16 KV 96 KiB/token;
- no construction swap growth.

### Full target forward

`LOOM_30B_MOE_FULL_FORWARD_EXTERNAL_001_CONDITIONAL`:
- 48/48 layers;
- router and hidden states bitwise exact;
- final logits exact;
- full 16.22 GB target capacity represented while routed bank stays external.

### Hot-path observer overhead removed

`LOOM_30B_MOE_FULL_FORWARD_OVERHEAD_ATTRIBUTION_001_PASS`:
- forced GC + RSS sampling caused almost all apparent ~20 s runtime;
- safe `GC_END_ONLY` full F1 forward: 1.641729 s;
- exact logits/router;
- zero expert leak;
- zero isolated swap delta.

## C — First real greedy generation — PASS

`LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`.

Report: `research/moe/loom-30b-moe-first-greedy-generation-001-result.md`.

Prompt: `Quanto fa 2+2? Rispondi solo con il numero.`

Result:
- 28-token formatted prompt;
- generated IDs `[19, 151645]`;
- decoded `4`, then canonical EOS;
- deterministic rerun PASS;
- BF16 KV advances exactly 98,304 B/token;
- final routed expert residency 0 B;
- no progressive memory growth;
- swap delta 0;
- memory-pressure PASS.

Performance:
- prefill: 18.6661 s / 1.5000 prompt tok/s;
- measured decode step: 1.54535 s;
- real zero-cache decode: **0.6471 tok/s**.

Decode cost:
- attention/shared 0.16335 s;
- expert reads **1.04423 s**;
- MLX reconstruction 0.04054 s;
- expert compute 0.19710 s;
- aggregation 0.01206 s.

Traffic:
- 962,592,768 useful expert bytes/decode token;
- 384 selected experts;
- 3,456 source component reads/token.

Short consecutive-token routing trace:
- 768 selections;
- same-layer reuse ratio ~27.86%;
- perfect previous-token retention counterfactual only ~13.93% bytes reduction.

The trace is too short for cache policy design.

## D — Decode storage-layout A/B — NEXT CORE

Checkpoint: `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001`.

Why this comes before cache:
- real decode spends 1.044 s of 1.545 s in expert reads;
- current source layout requires 9 component `pread`s/expert = 3,456 calls/token;
- device-verified expert-sized contiguous I/O previously established a much lower ~0.4816 s storage-only reference;
- expert-major representation is already proven lossless but not yet benchmarked on the actual generation hot path.

Experiment:
1. derive the exact `(layer, expert)` set used by the canonical measured decode trace;
2. pack only those required experts into a trace-scoped derived representation, not the full 14.344 GiB bank;
3. validate packed bytes exactly;
4. run a one-factor A/B:
   - CONTROL = current source 9-range expert access;
   - TREATMENT = one contiguous read/expert;
5. identical backbone, KV, router choices, model math and `GC_END_ONLY` lifecycle;
6. require identical logits/output;
7. measure source vs packed expert-read wall and total decode wall;
8. decide whether the full expert-major pack is justified.

No expert cache in this checkpoint.

## E — Longer routing/cache trace — AFTER D

Checkpoint: `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`.

Use a deterministic prompt engineered to require a longer output, target >=16 decode positions where model behavior permits.

Measure:
- real `(layer, expert)` sequences across consecutive generated tokens;
- reuse distance and same-layer transitions;
- expert hotness by layer;
- simulated LRU/segmented/admission policies;
- budgets 512 MiB, 1 GiB, 2 GiB, 3 GiB, 4 GiB;
- physical bytes/token avoided;
- expected I/O lower bounds from measured cache hits.

Only after this simulation implement the smallest promising cache.

## F — Cache implementation

If trace evidence supports useful reuse:
1. implement one policy only;
2. preserve exact output/token sequence;
3. measure real bytes/token and decode tok/s;
4. audit residency and swap;
5. compare against zero-cache 0.6471 tok/s baseline.

Storage-only reference traffic reductions remain:
- 5 tok/s envelope: 58.47%;
- 10 tok/s envelope: 79.24%.

These are necessary but not sufficient because compute/runtime adds latency.

## G — DFlash / block speculative branch — LATER/PARALLEL

Exact-target speculator: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`.

DFlash is not a memory-fit solution. Audit it only against the measured baseline and available expert-cache budget.

Possible value:
- multiple-position target verification;
- union-of-experts amortization;
- accepted tokens per target verification step.

Integration requires net-positive accepted-token economics after draft residency/workspace and expert traffic are included.

## H — Full expert-major pack decision

Do not automatically duplicate the full 14.344 GiB routed bank.

Build the complete pack only if `TRACE_PACK_DECODE_AB_001` demonstrates material real decode benefit from 9->1 range access that justifies the additional storage and preprocessing.

## I — Capability / promotion

After practical speed exists:
- broader generation tests;
- practical/coding capability benchmark;
- longer-context memory stability;
- reproducibility;
- behavioral decensoring validation via Heretic or LOOM-native equivalent.

## J — If performance remains insufficient

Escalation order:
- trace-backed expert cache;
- block union/coalescing;
- DFlash/speculative verification;
- route prediction/prefetch;
- lower storage granularity / neuron clusters;
- faster external NVMe as a secondary hardware branch;
- LOOM-native architecture co-design if necessary.

## Immediate order

1. `LOOM_30B_MOE_TRACE_PACK_DECODE_AB_001`
2. `LOOM_30B_MOE_ROUTING_CACHE_TRACE_001`
3. smallest trace-backed expert cache
4. real generation re-benchmark
5. `LOOM_30B_DFLASH_SPECULATOR_STATIC_001`
6. DFlash/block integration only if net-positive
7. capability benchmark
8. custom architecture research if necessary
9. decensoring validation before final promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
