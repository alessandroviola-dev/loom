# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`
Strategic next: `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB while balancing memory/residency, speed/usability, practical capability and behavioral freedom/decensoring.

Final promoted models require validated decensoring via Heretic or a clean LOOM-native equivalent: `research/behavior/decensoring-requirement-v1.md`.

## A — Architecture/runtime feasibility — PROVEN

Target: local `Qwen3-30B-A3B-MLX-4bit`.

Established on M1 8 GB:
- full external-expert execution across all 48 layers;
- exact final logits;
- complete shared-backbone residency;
- real greedy generation;
- packed expert-major access as a real decode win;
- long routing trace and cache economics;
- 4-GiB raw RAM cache rejected for memory pressure.

Canonical target values and stable invariants live in `/AGENTS.md`.

## B — Current real baseline

`FIRST_GREEDY_GENERATION_001_PASS`:
- source zero-cache decode ~0.647 tok/s.

`TRACE_PACK_DECODE_AB_001_PASS`:
- packed decode-equivalent ~1.080 tok/s;
- exact output preserved;
- expert access remains a major cost.

`REAL_RAW_CACHE_001_MEMORY_FAIL`:
- actual LRU hit ~80.9%;
- +2.41 GiB swap;
- decode slowed to ~0.205 tok/s.

Conclusion: reuse is real but a large resident cache is not the path on M1 8 GB. The single-token runtime ceiling remains ~2.066 tok/s even with ideal cache hits.

## C — DFlash exact-target static — COMPLETE / INTEGRATION BLOCKED

`LOOM_30B_DFLASH_SPECULATOR_STATIC_001`:
- exact-target BF16 drafter ~1.2685 GiB;
- 5 draft layers;
- block=8 / proposals=7;
- target taps `[1,12,23,34,45]`;
- static memory fit plausible;
- no native LOOM/MLX DFlash path.

DFlash is considered only as a target-work amortization mechanism, not a model-fit mechanism.

## D — Target DFlash interface — PASS

`LOOM_DFLASH_TARGET_INTERFACE_001_PASS`.

Report: `research/architecture/loom-30b-dflash-target-interface-001-result.md`.

Exact target tap contract is now proven in the real external-expert runtime:
- 1-based post-block outputs `[1,12,23,34,45]`;
- prefill `[1,28,2048]`, decode `[1,1,2048]`;
- float32;
- router/logits/token sequence remain bitwise exact;
- tap payload 1,146,880 B prefill / 40,960 B decode;
- MLX peak delta +18,612,224 B;
- RSS unchanged;
- swap delta 0;
- no expert leak.

This closes the first runtime prerequisite for a DFlash port.

## E — Multi-position/block target verifier — NEXT

Checkpoint: `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`.

Goal: prove target verification of multiple candidate positions independently of the learned drafter.

Required experiment:
1. use real deterministic continuation tokens from existing generation/trace evidence;
2. establish exact speculative candidate/logit alignment from source/runtime semantics;
3. compare sequential teacher-forced verification with one causal multi-position target block for B=2,4,7;
4. verify KV advancement and per-position logits/token decisions;
5. preserve external-expert ownership and memory safety;
6. measure layer-local unique-expert union and bytes/verified-position;
7. if semantics pass, evaluate a union-coalesced external-expert path where each unique expert is loaded once per layer/block;
8. separate correctness from performance promotion.

If this fails, DFlash integration remains blocked.

## F — DFlash implementation gate

Only after both:
- target interface PASS;
- block verifier PASS;

may LOOM implement the learned DFlash drafter.

Then measure:
- actual BF16/quantized resident and workspace footprint;
- acceptance length on local workloads;
- target verification steps/output token;
- unique external expert bytes/accepted token;
- sustained generation tok/s;
- memory pressure and deterministic correctness.

A drafter that fits but does not improve accepted-token economics is not promoted.

## G — Storage/cache later

Possible complementary work after block economics:
- smaller/admission-controlled cache under strict swap gates;
- packed hot-set + source-cold fallback;
- on-demand/layer-segmented pack;
- full expert-major pack only if arbitrary cold-miss economics justify duplicating the routed bank.

Do not retry the failed 4-GiB raw cache or jump to persistent live-MLX caching.

## H — Promotion path

1. `LOOM_30B_DFLASH_BLOCK_VERIFIER_001`.
2. Minimal DFlash port if PASS.
3. Sustained real generation benchmark.
4. Capability/coding benchmark.
5. Context scaling and memory stability.
6. If speed remains insufficient: route prediction/prefetch, finer-grained sparsity or LOOM-native system/model co-design.
7. Behavioral decensoring validation before final promotion.

## Token-efficient Pi workflow

Root `/AGENTS.md` is authoritative persistent context. Pi prompts should contain only the active delta, exact inputs, gates, evidence and concise return fields. Pi remains local execution only; ChatGPT owns Git/HANDOFF/ROADMAP.

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
