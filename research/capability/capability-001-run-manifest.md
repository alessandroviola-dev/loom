# CAPABILITY 001 — canonical run manifest

Date: 2026-08-21
Status: RUN READY
Branch: `research/stretch-015-divergence-attribution`
Bridge code commit: `4d204471aedb9262ccaa3b86f29b0e344d0c2884`

## Authority

The run is governed by, without modification:

- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`

This manifest does not change task content or scoring. It only pins the admitted runtime and execution provenance.

## Frozen runtime provenance

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max assistant output 2048
- `enable_thinking=false`
- `prefill_step_size=512`
- built-in M1 `qmv_fast`
- `loom-mlx-local` localhost-only provider
- Pi tools: `read`, `write`, `edit`, `bash`
- bridge source: `scripts/loom_pi_mlx_bridge.py` at commit `4d204471aedb9262ccaa3b86f29b0e344d0c2884`

Request boundary after each completed response:
1. ownership-check the finished `GenerationBatch.Response`;
2. detach only its stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

## Host/task execution

Each of the 12 tasks gets a fresh isolated Pi session and disposable workspace. Before each task process/session, require system free >=60% on two consecutive passive samples and swap <=5600 MB. Wait passively for natural recovery; no host manipulation.

After admitted execution begins, resource-abort only at system free <5% or swap >5600 MB. No rescue/retry.

## Frozen suite

- C01-C06: existing Coding Benchmark 01 v1.0.1 T01-T06, unchanged. The runner must locate and reuse the existing canonical prompts, fixtures, tests and hidden scorer assets; it must not recreate or rewrite missing benchmark material.
- G01: safe fast-forward synchronization.
- G02: dirty-tree protection.
- G03: divergence diagnosis.
- E01: balanced-ratio causal interpretation.
- E02: upper-bound/impossible-target reasoning.

If the canonical C01-C06 assets cannot be located exactly, classify infrastructure incomplete rather than reconstructing them.

## Scoring

Primary: task passes / 12.

Secondary: C01-C06 existing benchmark score /100; critical failures; constraint violations; tool/protocol errors; retry/correction count; per-task wall time; token/resource diagnostics where available.

There is no quality promotion threshold. If all 12 tasks execute and are scorable, classification is `CAPABILITY_001_BASELINE_COMPLETE` regardless of score.

## Evidence

Persist under `results-local/capability/capability-001/<run-id>/` with exact prompts, fixture hashes, raw Pi events/stderr, tool traces, final workspace/hashes, scorer outputs and resource snapshots.

Pi implements/runs the harness only. No Git synchronization, HANDOFF or ROADMAP updates from Pi.
