# LOOM Roadmap

Last updated: 2026-08-30
Current: Apple Metal MoE expert paging Stage1R2 GO at 4.40 tok/s. Stage2 comparability audit completed: historical MLX and new GGUF are architecture-matched but checkpoint-different. Immediate priority is a preregistered Stage2 product-candidate validation. Validator/guided-repair remains PAUSED.
Canonical context: `/AGENTS.md` v3.70.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: historical custom MLX ~1.4 tok/s; Apple Metal MoE paging candidate S24 now 4.40 tok/s.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture planned but paused during 30B runtime R&D.
- LOOM Heretic remains mandatory after initial runtime/capability optimization.

Do not replace canonical DEEP until Stage2 product validation passes.

## 2. Stage1R2 — COMPLETE / GO

Canonical result:
`research/architecture/loom-30b-apple-moe-paging-stage1r2-001-result.md`

Best safe profile S24:
- generation 4.40 tok/s
- prompt 3.95 tok/s
- load 14.426 s
- E2E 37.704 s
- peak swap 1125.94 MiB
- minimum headroom 13%
- no critical pressure/OOM/corruption/runaway

Candidate model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`.

## 3. Stage2 comparability audit — COMPLETE

Canonical result:
`research/architecture/loom-30b-stage2-comparability-audit-001-result.md`

Classification:
`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`.

Historical MLX lineage:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`, declared upstream `Qwen/Qwen3-30B-A3B`, MLX Q4/group128.

New candidate:
`Qwen/Qwen3-30B-A3B-Instruct-2507`, ByteShape Q3_K_S-3.25bpw.

Core MoE structure matches, but checkpoint/version, RoPE/context configuration, quantization and chat template differ. Strict same-checkpoint runtime/quality parity claims are forbidden.

## 4. Current — Stage2 product-candidate validation

Preregister fresh matched evaluation covering:
- S24 reproducibility across fresh processes;
- matched practical tasks on historical MLX and new candidate;
- decode/prompt throughput;
- load/TTFT where observable and E2E;
- memory/wired/compressed/swap;
- quality/correctness under frozen criteria;
- explicit product promotion gate.

A Stage2 GO may promote Apple Metal MoE paging as canonical DEEP on product utility grounds despite checkpoint difference.

## 5. After Stage2 — 30B acceleration funnel

Primary architecture reference from the repository research bundle: mini-SGLang concepts, independently adapted for Apple Silicon:
- persistent process / stable prefix caching;
- KV/prompt reuse;
- chunked prefill;
- overlap scheduling;
- expert/I/O prefetch.

Do not port CUDA-specific implementation blindly.

Secondary end-to-end optimization: Caveman-style deterministic context packing after runtime validation.

Goal: push current 4.40 tok/s toward 5+ first, then explore whether 6–9 tok/s is achievable without unacceptable quality or memory cost.

## 6. Later work

After the 30B runtime priority:
- resume sanitized validator-guided repair/selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic;
- FAST clean-runtime reintroduction.
