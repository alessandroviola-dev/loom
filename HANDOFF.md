# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — Apple Metal MoE paging S24 is canonical `loom-deep`. Persistent/cache feasibility audit completed GO. Current checkpoint is the preregistered no-patch `--prompt-cache` experiment before paging/I/O attribution.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_ACCEL_PROMPT_CACHE_001`
Pi context: `/AGENTS.md` v3.73.

## Canonical DEEP

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`
with `llama-completion -no-cnv` SHA256 `38a8446fe0e34e22b7c6e9cffa563167992f46c65fe3387db95bbf5a151cc73f`.

Profile:
S24.

Validated generation baseline:
~4.39–4.40 tok/s.

Stage2 product-candidate result:
`LOOM_30B_STAGE2_PRODUCT_CANDIDATE_GO`.
Apple S24 is canonical DEEP on product-utility grounds.

## Persistent/cache feasibility — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-accel-persistent-cache-feasibility-001-result.md`

Evidence:
`results-local/research/30b-accel-persistent-cache-feasibility-001/20260830T101246Z/`

Classification:
`LOOM_30B_ACCEL_PERSISTENT_CACHE_FEASIBILITY_GO`.

Key findings:
- no built `llama-server` is available;
- built canonical `llama-completion` exposes explicit `--prompt-cache` support;
- first no-patch experiment should compare stable-prefix warm prompt cache against cache-disabled target baseline;
- audit performed no inference, GGUF open, patch, build, download, package install or Git action.

## Exact next action — prompt cache 001

Preregistration:
`research/architecture/loom-30b-accel-prompt-cache-001-preregistration.md`

Three independent rounds. Each round:
1. B: cache-disabled target prompt in a fresh process;
2. W: warm prompt with a fresh per-round `--prompt-cache` file;
3. C: target prompt in a fresh process using that same cache file.

Stable prefix, warm suffix and target suffix are frozen byte-for-byte in the preregistration.

Primary metric:
median C/B target prompt-eval wall ratio.

GO requires:
- median prompt-eval wall ratio <=0.70;
- median target E2E C/B <1.00;
- warm-cache generation throughput >=90% of baseline generation throughput;
- deterministic correct outputs;
- no critical memory/OOM/corruption/runaway;
- peak swap <=3.5 GiB;
- complete durable evidence;
- no model/source/runtime/package mutation.

Prompt cache is evaluated as a prefill/E2E optimization only; it is not a direct decode-speed claim.

## After prompt-cache

Proceed to paging/I/O attribution to isolate direct decode bottlenecks in S24. Use that evidence to choose the first source-level expert prefetch/overlap experiment inspired by mini-SGLang principles.

Acceleration target:
5+ tok/s first, then investigate 6–9 tok/s without unacceptable quality or memory cost.

Later: Caveman-style deterministic context packing for end-to-end agent speed. Validator work remains paused; Heretic remains mandatory later.
