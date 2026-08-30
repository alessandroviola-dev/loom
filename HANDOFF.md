# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache 001 closed MECHANICAL_NO_GO because the frozen output budget/validator invalidated otherwise clean cache measurements. R1 then stopped before inference because its preregistration required reuse of an unchanged wrapper that hard-coded the very conditions R1 needed to change. Current checkpoint is preregistered Prompt Cache R2 recovery.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCEL_PROMPT_CACHE_R2_001`
Pi context: `/AGENTS.md` v3.75.

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

## Prompt Cache R1 — MECHANICAL_NO_GO before inference

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/`

Blocker artifact:
`mechanical-blocker.json`.

Frozen parent wrapper verified:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/prompt_cache_runner.py`
SHA256 `1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`.

R1 correctly stopped because the unchanged wrapper hard-coded:
- `-n 8`;
- exact-string validation;
- Prompt Cache 001 evidence/classification handling.

R1 simultaneously required the wrapper unchanged and required `-n 24` plus semantic validation, so the contract was mechanically unexecutable. No inference occurred and R1 contributes no new performance evidence.

## Exact next action — Prompt Cache R2

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-preregistration.md`

Scientific design unchanged:
- same exact prompts;
- canonical S24 only;
- generation budget `-n 24`;
- semantic validator frozen: W contains standalone `ambra`; B/C contain standalone `4317`;
- three independent B -> W -> C rounds;
- fresh cache per round;
- prompt-cache reuse is the sole scientific factor;
- primary GO threshold median C/B prompt-eval wall <=0.70;
- lower E2E, decode >=90%, safe memory and complete evidence required.

R2 mechanical wrapper recovery:
- verify parent wrapper exact SHA `1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`;
- leave parent unchanged;
- derive a separate R2 wrapper before inference;
- only preregistered mechanical changes are authorized;
- synthetic-test validator/harness without opening GGUF;
- persist and freeze derived-wrapper SHA before first inference;
- no wrapper changes after inference begins.

## After R2

Proceed to paging/I/O attribution for direct decode acceleration. Then preregister expert-prefetch/overlap intervention if attribution supports it.

Target: 5+ decode tok/s first, then investigate 6–9 tok/s. Caveman-style context packing remains later end-to-end work.
