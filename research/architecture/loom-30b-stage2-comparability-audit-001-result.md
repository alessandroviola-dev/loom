# LOOM 30B Stage2 Comparability Audit 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_STAGE2_COMPARABILITY_ARCHITECTURE_MATCH_CHECKPOINT_DIFFERENT`**

## Summary

The historical custom-MLX DEEP artifact and the new Apple Metal MoE paging GGUF share the same Qwen3-30B-A3B core MoE architecture, but they are not the same checkpoint.

Therefore Stage2 may compare them only as **product candidates** under fresh matched tasks. It must not claim strict runtime-only parity, same-checkpoint quantization preservation, or direct quality equivalence.

## Evidence

Local audit root:
`results-local/research/30b-stage2-comparability-audit-001/20260830T092100Z/`

Files:
- `report.json`
- `provenance-sources.txt`
- `comparability-matrix.json`

## Historical MLX identity

Historical artifact:
`Qwen/Qwen3-30B-A3B-MLX-4bit@4e2776a4cc73a8a251d0b797010a5b07fd541a3e`

Declared upstream base:
`Qwen/Qwen3-30B-A3B`

Quantization/runtime representation:
- MLX affine Q4
- group size 128

Strongest provenance evidence includes local config/index/shard hashes, Hugging Face reference metadata, prior identity-audit evidence and the lossless expert-bank contract.

The exact original unquantized upstream revision was not recovered.

## New GGUF identity

Artifact:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`

Verified SHA256:
`c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`

Embedded identity:
- architecture: `qwen3moe`
- Instruct checkpoint
- version: `2507`
- upstream model identity: `Qwen/Qwen3-30B-A3B-Instruct-2507`

## Comparability matrix

Matched:
- Qwen3 MoE family
- 48 layers
- 128 routed experts
- top-8 expert routing
- hidden size 2048
- tokenizer family/key IDs broadly align

Different / unresolved:
- checkpoint/version differs
- historical artifact is not established as Instruct-2507
- RoPE/context configuration differs
- quantization representation differs
- chat-template text is proven non-identical
- byte-identical tokenizer proof is absent
- exact new upstream commit is unresolved

## Historical performance references

### 1.402 tok/s

Historical compact practical DEEP suite:
- historical MLX Q4/top-8 PACKED runtime
- five practical tasks
- pooled visible decode throughput

### 1.229233 tok/s

Historical exact-Q4 custom MLX sustained benchmark:
- same historical MLX artifact lineage
- 32-token sustained generation
- median across three fresh processes

The two historical numbers use the same historical model lineage but different workloads/conditions.

Neither is a strict same-artifact one-factor comparator for the new Instruct-2507 GGUF.

## Stage2 scientific consequence

Stage2 is allowed to compare:
- practical output quality/correctness on fresh matched tasks
- decode and prompt throughput
- load/TTFT where observable
- E2E wall
- memory/wired/compressed/swap behavior
- stability/reproducibility

Stage2 must be framed as a **product-candidate comparison**.

Stage2 must not claim:
- strict runtime-only speedup at equal checkpoint
- same-checkpoint quantization preservation
- direct quality parity caused only by runtime/quantization changes

If the new candidate wins the frozen product criteria, it may still be promoted as LOOM DEEP on product utility grounds despite checkpoint difference.

## Unresolved provenance

- original unquantized historical Qwen revision
- exact upstream commit for the GGUF checkpoint
- byte-identical tokenizer proof

These unresolved items do not block a product-candidate Stage2, but they prohibit strict same-checkpoint scientific claims.
