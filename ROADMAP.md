# LOOM Roadmap

Last updated: 2026-08-29
Current: `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO` completed successfully. Validator/guided-repair work is PAUSED. Immediate priority is 30B runtime acceleration via Apple-Silicon MoE expert paging feasibility.
Canonical context: `/AGENTS.md` v3.65.

## 1. Product direction

- `loom-balanced`: Qwen3-8B 3-bit, ~13 tok/s, provisional primary.
- `loom-deep`: Qwen3-30B-A3B, current custom MLX path ~1.4 tok/s and too slow for practical frequent use.
- `loom-fast`: future clean-runtime tier; legacy 4B parked.
- `loom-auto`: validator-first architecture remains planned but its active experiments are paused during 30B runtime R&D.

LOOM Heretic remains mandatory after initial runtime/capability optimization.

## 2. Validator track — paused at a clean checkpoint

Output Validator v0: GO.
Selective Rescue 001: scientific NO_GO at final 5/8 CORRECT, zero false accepts.
8B Validator-Guided Repair 001: MECHANICAL_NO_GO due hidden-spec leakage.
VERIFY_RULE Validator Hardening 001: **GO** — 24/24, FP/FN 0/0, contradiction and forbidden-heuristic rejection 2/2, p95 0.006542 ms.

A fresh sanitized guided-repair experiment remains planned but is not active.

## 3. New 30B runtime opportunity

New public evidence justifies reopening 30B runtime architecture rather than only optimizing the existing custom MLX expert-major path.

Relevant external mechanisms:
- low-bpw GGUF Qwen3-30B-A3B on 8GB-class systems;
- bounded expert residency rather than full expert materialization;
- LRU expert slots;
- direct disk-backed expert loading;
- Apple Metal shared-memory/event synchronization;
- OS/storage-aware working-set management.

Primary Apple PoC source:
`kisasexypantera94/llama.cpp`, branch `moe-expert-residency`, commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`.

Reference result: Qwen3-30B-A3B Q6_K reported at 13 tok/s after warmup on M1 Pro 16GB. This is not assumed transferable to M1 8GB.

Potato OS / ik_llama evidence motivates the research, but `ik_llama.cpp` itself is not assumed as the Mac backend because Metal is not one of its fully supported performant backends.

## 4. Current — 30B Apple MoE Paging Feasibility 001

Preregistration:
`research/architecture/loom-30b-apple-moe-paging-feasibility-001-preregistration.md`

No model inference and no model download.

Goals:
- exact PoC source checkout;
- native Metal build on base M1 8GB;
- verify expert-paging flags and Apple device path;
- confirm source mechanism (bounded slots/LRU + disk reads + Metal sync);
- measure read-only local storage readiness if possible;
- project working memory for 8/16/24/32 slots;
- classify compatibility of two frozen ByteShape ~12.5GB candidates.

GO permits the next checkpoint to authorize exactly one candidate download and one bounded real-generation experiment.

## 5. Candidate Stage-1 models if feasibility GO

Frozen candidates only:
- KQ: `Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`, ~12.4GB, published normalized quality 97.97%, SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`;
- IQ: `Qwen3-30B-A3B-Instruct-2507-IQ3_S-3.29bpw.gguf`, ~12.5GB, published normalized GPU score 97.35%, SHA256 `b8770ce5b81cb47fbdfc75a00fae220297955ef58697411888c1f3dc30a2e230`.

Do not download both. Select only after local compatibility/memory evidence.

## 6. If Stage 1 succeeds

Compare new GGUF/Metal paging runtime directly with canonical 30B custom MLX under the same concise prompt/output settings:
- TTFT;
- generation tok/s;
- E2E wall;
- resident/wired memory;
- swap;
- storage read volume/rate if measurable;
- output correctness/parity.

Only retained quality plus meaningful practical speedup can change DEEP runtime direction.

## 7. Later work

After this priority investigation:
- resume sanitized validator-guided repair and selective-DEEP graph;
- semantic verifier/open-ended validation;
- automatic validator/contract derivation;
- provider/UI;
- mandatory Heretic track;
- FAST clean-runtime reintroduction.
