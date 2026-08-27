# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — expert-major is accepted/canonical; exact-Q4 speed baseline is `1.229233 tok/s`; routing-sparsity frontier produced no acceptable gain. Current work is lower-bit expert speed/quality frontier.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_LOWER_BIT_EXPERT_SPEED_QUALITY_FRONTIER_001`
Pi context: `/AGENTS.md` v3.41.

## Settled current runtime

Canonical Qwen3-30B-A3B expert-major backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Current exact-Q4 speed baseline commit:
`96958de` — `perf: keep packed expert file descriptor open`.

Validated backend SHA-256:
`6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.

Accepted exact sustained throughput:
3×32-token values `1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Q4 top-8 expert traffic/token:
`962,592,768 B`.

Remaining dominant cost is expert I/O; Stage-0 decomposition before persistent-FD optimization was expert I/O `44.61%`, expert compute `26.50%`, backbone `14.74%`, materialization/sync `11.51%`, routing `2.64%`.

Do not reopen expert-major validation or the rejected exact-Q4 micro-optimizations absent regression/new hypothesis.

## Routing Sparsity Frontier 001 — NO ACCEPTABLE GAIN

Result:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-result.md`

Evidence:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/20260827T135848Z/`

Frozen teacher oracle:
8 prompts ×16 teacher-forced positions = 128 positions.

Candidate summary:
- tau `.95`: STRICT fidelity, mean experts/layer `7.8757`, bytes/token `947,630,592`, throughput `1.216703 tok/s` (`-1.02%`);
- tau `.90`: STRICT fidelity, mean experts/layer `6.9440`, bytes/token `835,531,776`, throughput `1.223280 tok/s` (`-0.48%`);
- tau `.80`: quality FAIL from KL `0.113882` > `0.10`;
- tau `.70`: quality FAIL, top1 `87.5%`, KL `0.331111`.

No variant met the frozen >=10% gain gate. No tau selected, overlap skipped, no Stage-7 final campaign, no tracked runtime changes.

Interpretation: routing mass is too distributed. Quality-valid truncation removes too little expert work; sufficiently aggressive truncation degrades the Q4 teacher before becoming useful.

Routing sparsity is closed for this target under current fidelity gates. Do not test adjacent tau/fixed-top-k rescue.

## Exact next step — Lower-Bit Expert Speed/Quality Frontier 001

Preregistration:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-preregistration.md`.

Goal: preserve full top-8 routing but reduce bytes/compute per expert through Q3/Q2 where the installed MLX runtime actually supports them.

Stage 0 first, no full build/model forward:
- inspect local MLX API/version only;
- establish current Q4 group-size/component ABI;
- capability-gate native `bits=3` / `bits=2` using same group size and expert shapes;
- fixed round-trip pilot on layers `0,15,31,47`, expert `0`;
- no web/download/BF16 substitution/group-size search/custom kernel.

Candidate source is the deployed Q4 expert representation. Reconstruct/dequantize Q4 expert tensors and requantize to target bits; this isolates incremental compression from current production baseline.

For each supported candidate, deterministic order Q2 then Q3:
1. build separate resumable `6144/6144` lower-bit expert-major bank;
2. complete manifest/provenance/integrity and `18,048` replay;
3. zero fallback/cache;
4. run the SAME retained 128-position Q4 teacher oracle;
5. speed-test only candidates meeting USABLE fidelity;
6. eligible requires >=10% gain vs `1.229233 tok/s`, safety/RSS/swap PASS;
7. fastest eligible point gets final `3×32` sustained run + final fidelity oracle.

USABLE:
- top1 >=90%;
- teacher top1 in candidate top3 >=97%;
- KL <=0.10;
- finite logits.

STRICT:
- top1 >=95%;
- top3 >=99%;
- KL <=0.05.

No routing sparsity, mixed precision, group-size search, DFlash or speculative decoding in this checkpoint.

If neither Q2 nor Q3 is locally compatible, outcome is INCONCLUSIVE rather than inventing a new representation mid-run.

## After lower-bit frontier

If a lower-bit candidate is quality-valid and faster but still below 5 tok/s, freeze it as the verifier baseline and move to an independent speculative-decoding frontier. The likely route to the aspirational 5 tok/s target is cumulative compression + accepted multi-token output, not further top-8 pruning.

After current 30B speed work is frozen, run the planned local bake-off:
- Qwen3-30B-A3B;
- Qwen3.8-27B;
- Qwen3.8-Flash-Next;
comparing sustained tok/s, RAM/swap, intelligence/quality, and steerability/refusal characteristics.
