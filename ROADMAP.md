# LOOM Roadmap

Last updated: 2026-08-30
Current: Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache 001 closed MECHANICAL_NO_GO because of output-budget/validator design, despite strong diagnostic cache reuse. Immediate priority is Prompt Cache R1 recovery, then paging/I/O attribution. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.74.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: **Qwen3-30B-A3B-Instruct-2507 Q3_K_S-3.25bpw on Apple Metal MoE paging S24**.
- historical custom MLX ~1.4 tok/s: historical comparison/fallback only.
- `loom-fast`: future clean-runtime tier.
- `loom-auto`: paused during 30B acceleration.
- LOOM Heretic remains mandatory later.

## 2. Canonical DEEP validation

Stage1R2 GO: best safe ~4.40 tok/s.
Stage2 product GO: Apple S24 promoted to canonical DEEP.
Validated fresh-process decode baseline: ~4.39–4.40 tok/s.

## 3. Acceleration funnel

Primary reference: mini-SGLang concepts independently adapted for Apple Silicon.

Priority:
1. prompt/prefix cache;
2. paging/I/O attribution;
3. overlap scheduling / expert I/O prefetch;
4. lighter quant only under separate artifact/quality preregistration if justified;
5. persistent server path only under explicit build preregistration;
6. Caveman-style context packing later.

Target: 5+ decode tok/s first, then investigate 6–9 tok/s.

## 4. Persistent/cache feasibility — GO

No built `llama-server`; canonical `llama-completion` supports `--prompt-cache`.

## 5. Prompt Cache 001 — MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`.

Diagnostic observations:
- median C/B prompt-eval ratio **0.04174**;
- median C/B E2E ratio **0.08973**;
- decode preservation **96.98%**;
- cache creation/reuse and 262/269 token prefix match observed;
- safe memory/swap.

No scientific GO is claimed because all nine invocations failed functional validity under the frozen contract.

Mechanical defects:
- `-n 8` truncated target `4317`;
- exact-string warm validator rejected semantically correct explanatory output containing `ambra`.

## 6. Current — Prompt Cache R1 001

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-preregistration.md`

Mechanical recovery deltas only:
- `-n 24`;
- frozen semantic validation (`ambra` for W, standalone `4317` for B/C).

Everything else remains frozen: prompts, S24, B/W/C order, three rounds, fresh cache per round, same acceleration thresholds and no runtime/model mutation.

If R1 GO, prompt cache becomes a validated prefill/E2E optimization for stable-prefix workloads. It still does not count as direct decode acceleration.

## 7. Next decode-focused checkpoint

Paging/I/O attribution on canonical S24:
- expert hit/miss behavior;
- expert bytes read/token;
- synchronous `pread` cost;
- storage wait vs compute;
- headroom for overlap/prefetch.

Do not patch runtime before attribution is completed and a new intervention is preregistered.

## 8. Later work

After 30B runtime priority:
- Caveman context packing;
- resume validator/guided repair;
- semantic verifier;
- provider/UI;
- mandatory Heretic;
- FAST reintroduction.
