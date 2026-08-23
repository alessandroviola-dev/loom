# STREAMED-BLOCK-REUSE-AUDIT 001 — Result

Date: 2026-08-23
Classification: `STREAMED_BLOCK_REUSE_AUDIT_001_COMPLETE`

Current layer-35 path: load safetensors; select 25 layer arrays totaling 84,427,264 B; release full container and run select-time GC; construct a fresh Qwen3 TransformerBlock; convert the quantizable leaves; bind current weights; evaluate parameters; run the block; evaluate output; release transient module and values; use the final post-head cleanup.

Main finding: weight-independent block topology and quantized metadata can exist without retaining streamed weights. Runtime ownership validation showed a parameter-free shell with zero retained native MLX parameter bytes and no surviving references to the 25 selected layer arrays.

The current strict MLX weight-loading path nevertheless requires existing same-shape parameter leaves. A truly parameter-free shell therefore cannot preserve the current binding lifecycle. Placeholder arrays would violate the metadata-only-shell requirement, while direct path-wise rebinding would introduce a second factor.

Decision: do not run a construction-only block-reuse performance A/B under the current strict binding path. Revisit only if binding itself is made an explicit research factor.

Reusable structure feasibility: `CONDITIONAL`.
Persistent Python shell estimate: ~3,658 B.
Logical streaming requirement remains 84,427,264 B/token.
Ownership/reference validation: PASS.
Block-output parity in the audit harness: PASS.

Raw local evidence: `results-local/memory/streamed-block-reuse-audit-001/20260823-181531/`.
