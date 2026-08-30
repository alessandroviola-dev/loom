# LOOM — Active Handoff

Last updated: 2026-08-30
Status: ACTIVE — accelerated macro-work-package mode. WP1 Runtime + Product Serving completed GO. Canonical DEEP runtime is now S32 on persistent localhost `llama-server`; S24 is rollback. Next planned package is WP2 Context Intelligence (Caveman + Cavemem only), but it is not yet authorized.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Pi context: `/AGENTS.md` v3.81.
Plan: `research/integration/loom-accelerated-macro-workpackages-v1.md`.

## Canonical DEEP after WP1

Model:
`Qwen3-30B-A3B-Instruct-2507-Q3_K_S-3.25bpw.gguf`
SHA256 `c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251`.

Source:
`kisasexypantera94/llama.cpp@41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`

Canonical server binary:
`llama-server`
SHA256 `58aec7b9a924ce0bc7910b889d91cc6d55064991459ddddea70a5c8f3ca08506`.

Canonical runtime profile: **S32**.
Rollback: S24.

Matched deterministic S24/S32 3x96-token A/B with byte-identical outputs:
- S24 median decode `4.382 tok/s`, E2E `29.185 s`;
- S32 median decode `5.596 tok/s`, E2E `23.849 s`;
- decode ratio `1.2768x`;
- E2E ratio `0.8172`.

S32 resources:
- peak RSS `3914.6 MiB`;
- peak sampled swap `1651.88 MiB`;
- minimum sampled free memory `10%`;
- no crash/OOM/corruption/critical pressure indication.

Final flags include:
`--ctx-size 4096 --parallel 1 --moe-n-slots 32 --moe-n-layers 48 --no-mmap --no-warmup --cpu-moe -b 4096 -ub 1 --cache-ram 512`.

## WP1 — COMPLETE / GO

Classification:
`LOOM_RUNTIME_PRODUCTIZATION_WP1_GO`

Canonical result:
`research/integration/loom-runtime-productization-wp1-result.md`

Evidence:
`results-local/runtime-productization-wp1/20260830T124040Z/`

Operational commands:
```bash
scripts/loom-deep-server start
scripts/loom-deep-server status
scripts/loom-deep-server health
scripts/loom-deep-server stop
```

WebUI:
`http://127.0.0.1:18080/`

API:
`http://127.0.0.1:18080/v1/chat/completions`

Health:
`http://127.0.0.1:18080/health`

Selected UI is the existing embedded `llama-server` WebUI. No custom LOOM frontend was built. Final server uses offline/local-only configuration and loopback binding.

Serving-path prompt/KV reuse is directly validated with `--cache-ram 512`:
- cold: 136 prompt tokens, 27.809 s;
- reuse: 134 cached / 2 evaluated tokens, 280.389 ms;
- reuse E2E: 0.332 s.

Pi local integration is operational through `http://127.0.0.1:18080/v1`; final offline Pi request completed coherently.

Current provider/model id remains `loom-local/loom-deep-30b-s24`. This is stale naming relative to the S32 runtime and should be renamed in a later authorized configuration/integration pass. It does not invalidate WP1.

## Historical acceleration retained

Prompt Cache R2 remains validated:
`LOOM_30B_ACCEL_PROMPT_CACHE_R2_GO`.

Earlier completion-mode stable-prefix result:
- median C/B prompt-eval ratio `0.04025`;
- median C/B E2E ratio `0.10751`;
- decode preservation `99.43%`.

The final persistent server now separately validates prompt/KV reuse in serving mode.

## Next planned macro package — WP2 Context Intelligence

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Status: **PLANNED / NOT YET AUTHORIZED**.

Permanent mechanisms selected:
- Caveman — deterministic context compression/packing/recovery handles;
- Cavemem — progressive local project memory/retrieval.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems. Borrow only negligible-overhead ideas when required to support Caveman/Cavemem.

WP2 should be measured against real Pi/LOOM token use and task quality.

## Later

WP3 — Behavioral Transform:
priority Abliterix-derived MoE-aware approach -> Heretic -> Senbonzakura-style methods -> clean LOOM-native equivalent, chosen by technical fit to GGUF/llama.cpp/Apple Silicon.

WP4 — Final Integration + Acceptance:
assemble best validated outputs and perform final end-to-end acceptance.

Pi must not commit/push. ChatGPT persists canonical Git state at macro-work-package boundaries.
