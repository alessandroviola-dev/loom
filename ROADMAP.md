# LOOM Roadmap

Last updated: 2026-08-30
Current: Apple Metal MoE paging S24 is canonical `loom-deep`. Prompt Cache R2 completed scientific GO and is now a validated stable-prefix prefill/E2E optimization. Immediate priority is Paging/I/O Attribution Preflight 001, then the actual canonical S24 paging/I/O attribution if instrumentation preflight passes. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.76.

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
1. prompt/prefix cache — **validated GO for stable-prefix prefill/E2E**;
2. paging/I/O attribution — current;
3. overlap scheduling / expert I/O prefetch only if attribution supports it;
4. lighter quant only under separate artifact/quality preregistration if justified;
5. persistent server path only under explicit build preregistration;
6. Caveman-style context packing later.

Target: 5+ decode tok/s first, then investigate 6–9 tok/s.

## 4. Persistent/cache feasibility — GO

No built `llama-server`; canonical `llama-completion` supports `--prompt-cache`.

## 5. Prompt Cache 001 — historical MECHANICAL_NO_GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/`.

Strong diagnostic cache reuse was observed, but no scientific GO is claimed because all nine invocations failed the frozen functional-validity contract.

## 6. Prompt Cache R1 — historical MECHANICAL_NO_GO before inference

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r1-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/`.

R1 correctly stopped before inference because its wrapper-freeze contract was internally incompatible with the required mechanical recovery. No performance evidence was generated.

## 7. Prompt Cache R2 — GO

Canonical result:
`research/architecture/loom-30b-accel-prompt-cache-r2-001-result.md`

Evidence:
`results-local/research/30b-accel-prompt-cache-r2-001/20260830T105738Z/`.

Validated result:
- all 14 frozen gates passed;
- 9/9 functionally valid invocations;
- median C/B prompt-eval ratio **`0.04025`**;
- median C/B E2E ratio **`0.10751`**;
- median B/C generation `3.49 / 3.47 tok/s`;
- decode preservation **`99.43%`**;
- cache reuse directly confirmed by cache artifacts and runtime 262/269 token prefix match;
- peak RSS `2948.83 MiB`;
- peak swap `1267.56 MiB`.

Classification:
**`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`**.

Product meaning:
prompt cache is a validated canonical DEEP optimization for workloads with a reusable stable prefix. It materially reduces prefill/E2E latency but does not increase decode throughput.

## 8. Current — Paging/I/O Attribution Preflight 001

Preregistration:
`research/architecture/loom-30b-accel-paging-io-attribution-preflight-001-preregistration.md`

Purpose:
validate non-mutating instrumentation before the actual S24 inference attribution run.

Pinned-source mechanism:
- MoE offloader maintains bounded per-layer LRU residency;
- misses trigger expert-pool `pread(...)` operations;
- reads complete inside `resolve(...)` before the sidecar signals completion;
- multiple pool reads may execute through `dispatch_apply`;
- internal hit/miss counters exist but are not currently exposed by the inspected interface.

Preflight design:
- no GGUF access and no inference;
- inventory already-installed macOS tracing/telemetry tools;
- frozen deterministic Python `os.pread` synthetic process;
- validate process isolation, raw evidence capture and deterministic parsing;
- require at least one high-value direct read observable (count/bytes/timing/offset);
- freeze one observation method for the actual inference attribution;
- no source patch/rebuild, package install, dynamic interposition or security-setting change.

## 9. Next — Actual paging/I/O attribution

Only after preflight GO, preregister canonical S24 inference measurement for:
- expert paging read activity;
- bytes/read operations per decoded token where directly measurable;
- read timing/storage wait versus decode wall where directly measurable;
- temporal relation between paging and token production;
- safe memory/swap;
- whether the evidence supports an I/O-overlap/prefetch intervention.

Do not patch runtime during attribution unless a separate instrumentation checkpoint is explicitly preregistered after a preflight NO_GO.

## 10. Candidate intervention after attribution

If attribution demonstrates a material expert-I/O bottleneck with plausible overlap headroom:
- preregister a minimal expert-prefetch/overlap intervention;
- preserve S24 quality/memory constraints;
- target 5+ decode tok/s first;
- only then investigate 6–9 tok/s.

No prefetch/overlap implementation is authorized before attribution evidence exists.

## 11. Later work

After 30B runtime priority:
- Caveman context packing;
- resume validator/guided repair;
- semantic verifier;
- provider/UI;
- mandatory Heretic;
- FAST reintroduction.
