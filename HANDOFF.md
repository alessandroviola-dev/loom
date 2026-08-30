# LOOM — Active Handoff

Last updated: 2026-08-30
Status: WP1 Runtime + Product Serving GO and fully persisted; WP2 Context Intelligence GO and persisted; WP3 original LoRA families valid NO_GO; **WP3-R2 Behavioral Unlock completed locally with GO** using the Huihui Q3_K_S replacement. R2 persistence is pending. WP4 remains not authorized.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.88.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.
R2 contract: `research/integration/loom-behavioral-unlock-wp3-r2.md`.

## Canonical fast baseline

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Runtime: **S32**. Rollback: S24.

Validated S32 median decode `5.596 tok/s`, median E2E `23.849 s`.

Operational endpoints:
- WebUI `http://127.0.0.1:18080/`;
- API base `http://127.0.0.1:18080/v1`;
- health `http://127.0.0.1:18080/health`.

Lifecycle:
`scripts/loom-deep-server start|status|health|stop`.

## WP1 — COMPLETE / GO / FULLY PERSISTED

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

## WP2 — COMPLETE / GO / PERSISTED

Classification:
`LOOM_CONTEXT_INTELLIGENCE_WP2_GO`

Implementation commit:
`0e249f8f5cfaf89398d01e2ee50281fb75b86cd7`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Evidence:
`results-local/context-intelligence-wp2/20260830T133259Z/`

Canonical Context Intelligence remains Caveman deterministic packing/recovery + Cavemem SQLite/FTS5 progressive project memory, with `23.24%` median heavy-context provider-input reduction and `0%` no-op overhead.

Canonical fast Pi label:
`loom-local/loom-deep-30b-s32`.

## WP3 — COMPLETE / VALID NO_GO

The original rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates all loaded successfully but retained the frozen `6/6` refusal result. Those adapter families remain rejected.

## WP3-R2 — COMPLETE LOCALLY / GO — PERSISTENCE PENDING

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Local result:
`research/integration/loom-behavioral-unlock-wp3-r2-result.md`

Evidence:
`results-local/behavioral-unlock-wp3-r2/20260830T160845Z/`

Selected candidate:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Source:
`mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`

Local SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Frozen results:
- explicit refusals `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- no increased degeneration;
- loopback API/WebUI stable;
- real Pi + WP2 request passed;
- rollback to canonical S32 + WP2 passed.

Caveats:
- fresh decode about `55%` of fresh S32 baseline;
- materially higher swap pressure;
- behavioral/disposition drift recorded and must remain explicit.

## Product direction

Keep two validated DEEP profiles:
1. `loom-deep-30b-s32` — fast/default;
2. `loom-deep-30b-unlocked` — behaviorally unlocked Candidate A, slower and more memory-intensive.

Do not commit either GGUF model artifact to Git. Persist only exact provenance/hash, small operational scripts/configs, frozen eval specs and result documentation.

## Current exact action

Persist the bounded WP3-R2 reproducibility/product-profile package under the macro-boundary exception. Do not begin WP4 until that commit is reviewed.

## WP4

Planned / not authorized. Final acceptance should integrate and validate both DEEP profiles plus WP2, profile switching and rollback.
