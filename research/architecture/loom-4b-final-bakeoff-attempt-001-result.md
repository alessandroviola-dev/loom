# LOOM 4B Final Bake-off Attempt 001 — Result

Date: 2026-08-28
Status: **`LOOM_4B_FINAL_ATTEMPT_ABORTED`**

## Decision

The final authorized 4B recovery attempt for the current phase is closed. The 4B tier is **parked for current tier selection**. This is an engineering/runtime-availability decision, not a model-capability conclusion.

No further 4B runtime recovery, rebuild, setup-probe, retry or repair is authorized in this phase unless explicitly reactivated later under a new checkpoint.

## Provenance

- active LOOM HEAD: `ad8591017fd3c9559f257c72eae769d3ce1e61c4`;
- experimental runner SHA-256: `c4f201f2d23ce10fdc33d4e9eb735081626a143d43a690f5cc5b9cfa74dd4125`;
- model: `Qwen/Qwen3-4B-GGUF`, `Qwen3-4B-Q4_K_M.gguf`, Q4_K_M;
- model SHA-256 verified: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.

## Mechanical stop

The required pinned runtime surface expected by the frozen runner was unavailable at the exact runner-resolved path:

`experiments/llama.cpp/build-loom-metal/bin/llama-server`

The server path was absent and the diagnostic `--version` exited `127`. Therefore the runner was not launched and no model inference occurred.

This is separate from the prior restoration checkpoint: that checkpoint had built and diagnosed a pinned server in another historical results-local location but closed `NO_GO` because the build unexpectedly fetched a UI asset outside its network authorization. The final attempt forbade repair/path adaptation/rebuild and therefore correctly stopped instead of silently changing the frozen condition.

## Outcome

- generated text: none;
- output tokens: N/A;
- task status: `NOT_ASSESSED` / inference not run;
- TTFT/generation/end-to-end: N/A;
- server startup/readiness: not started;
- process memory/RSS/swap: N/A;
- hardware diagnostic: Apple M1, Metal support reported;
- no network/build/package/model mutation occurred;
- model SHA/stat remained unchanged;
- no runner modification occurred.

Evidence:
`results-local/research/4b-final-bakeoff-attempt-001/20260828T151352Z/`

## Interpretation boundary

Do **not** conclude that 4B is less intelligent than 8B from this result. There is no current matched 4B inference.

Product decision for this phase: the legacy 4B llama.cpp path has consumed enough recovery effort and is no longer allowed to block progress. Continue with the validated LOOM 8B BALANCED and LOOM 30B DEEP tiers. A future FAST tier may be reintroduced through a cleaner runtime path (for example a fresh MLX-native 4B condition) after the higher-value 8B/30B architecture work.
