# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache 001 closed MECHANICAL_NO_GO because the frozen output budget/validator invalidated otherwise clean cache measurements. Current checkpoint is preregistered Prompt Cache R1 recovery.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCEL_PROMPT_CACHE_R1_001`
Pi context: `/AGENTS.md` v3.74.

## Canonical DEEP

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv` SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile: S24.
Validated decode baseline: ~4.39–4.40 tok/s.

Stage2 product result:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 is canonical DEEP.

## Prompt Cache 001 — MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`

Observed diagnostic evidence:
- cache-disabled prompt eval ~71–74 s;
- warm-cache prompt eval ~2.95–3.07 s;
- median C/B prompt-eval ratio 0.04174;
- median C/B E2E ratio 0.08973;
- decode preservation 96.98%;
- fresh 26,449,272-byte cache files created/reused with matching hashes;
- runtime reported 262/269 prompt-token match;
- memory/swap safe.

These are diagnostic only, not a scientific GO, because every invocation failed the frozen functional validator.

Mechanical cause:
- `-n 8` truncated `4317` to `...porta 4`;
- warm answer semantically included `ambra` but exact-string validation rejected explanatory text.

## Exact next action — Prompt Cache R1

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-preregistration.md`

Recovery only:
- generation budget `-n 24`;
- semantic validator frozen before execution: W contains `ambra`; B/C contain standalone `4317`.

Scientific design unchanged:
- same exact prompts;
- canonical S24 only;
- three independent B -> W -> C rounds;
- fresh cache per round;
- prompt-cache reuse is the sole scientific factor;
- primary GO threshold median C/B prompt-eval wall <=0.70;
- lower E2E, decode >=90%, safe memory and complete evidence required.

Reuse the frozen Prompt Cache 001 wrapper unchanged and verify its exact SHA before inference.

## After R1

Proceed to paging/I/O attribution for direct decode acceleration. Then preregister expert-prefetch/overlap intervention if attribution supports it.

Target: 5+ decode tok/s first, then investigate 6–9 tok/s. Caveman-style context packing remains later end-to-end work.
