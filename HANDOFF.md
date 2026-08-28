# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — 30B DEEP and 8B BALANCED matched evidence exist. The 4B model artifact is verified and the historical pinned llama.cpp runtime binaries now exist, but the restoration checkpoint remains NO_GO because the build unexpectedly downloaded a UI asset outside authorization. One final no-rebuild/no-network 4B inference attempt is authorized; if it mechanically fails, park 4B for this phase.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_4B_FINAL_BAKEOFF_ATTEMPT_001`
Pi context: `/AGENTS.md` v3.54.

## Product direction

- 4B FAST;
- 8B BALANCED;
- 30B DEEP;
- LOOM AUTO with evidence-based routing/escalation 4B -> 8B -> 30B.

Do not freeze router thresholds before broader matched evidence.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional. Execute after tier selection/initial optimization with frozen refusal/steerability and capability-preservation gates.

## 30B DEEP

Canonical runtime commit `d3691b765004849abb01a7675e5a6e7c5d0edd4c`.
Historical long-form decode `1.116 tok/s`, TTFT `47.832 s`.
LRUCache / 384-token cap: correct O(1) design but INCOMPLETE during `put()`; latency minutes.

## 8B BALANCED

Matched result: `LOOM_8B_BAKEOFF_RUNNER_PASS`; task INCOMPLETE at 384 tokens.
TTFT `2.992 s`; generation `13.357 tok/s`; end-to-end `12.275 tok/s`; E2E wall `31.284 s`.
Output strategy correct but unfinished; not coding-quality PASS.

## 4B FAST

Historical condition:
- Qwen3-4B Q4_K_M;
- model SHA `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- pinned llama.cpp `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- Metal;
- historical text generation `22.33 tok/s ±0.02`.

Verified archive artifact:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

First matched attempt: `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`; no inference.

Restoration result:
`research/architecture/loom-4b-llama-runtime-restoration-001-result.md`.
Classification: `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` solely because an unexpected UI asset was downloaded by the build outside the frozen network authorization. That classification stays closed.

Mechanically restored state:
- source HEAD exact pinned commit;
- setup/build exit 0;
- `llama-cli`, `llama-bench`, `llama-server` exist and diagnostics pass;
- Metal device PASS;
- no model acquisition/load/inference occurred;
- tracked LOOM diffs clean.

## Exact next action — one final 4B attempt

Preregistration:
`research/architecture/loom-4b-final-bakeoff-attempt-001-preregistration.md`.

Do not rebuild or rerun setup. No network/package/model mutation. Use existing binaries and existing experimental runner unchanged. Verify provenance then execute exactly one frozen 384-token LRUCache inference.

If inference executes validly: `LOOM_4B_FINAL_BAKEOFF_PASS`.
If any additional mechanical/runtime blocker prevents it: `LOOM_4B_FINAL_ATTEMPT_ABORTED`, park 4B for this phase, and continue with 8B + 30B. No further 4B recovery work unless explicitly reactivated later.

After this, broaden product evaluation and proceed toward tier optimization/router. Do not let 4B block progress.