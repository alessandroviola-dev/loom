# LOOM 4B Final Bake-off Attempt 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED / FINAL BOUNDED ATTEMPT

## Purpose

Resolve the 4B tier quickly without another rebuild.

The prior restoration checkpoint is permanently `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` because its build unexpectedly downloaded a UI asset outside the frozen network boundary. That classification is not relaxed.

However, the resulting runtime binaries are now mechanically present at the exact historical pinned llama.cpp source commit and passed diagnostics. This separate checkpoint asks only whether those existing binaries can execute the already-frozen 4B matched LRUCache task without any further build, network operation, source change, model mutation, or retry.

## Hard stop policy

This is the **final 4B recovery attempt for the current tier-selection phase**.

If this checkpoint cannot execute one valid inference because of any additional mechanical/runtime problem, classify `LOOM_4B_FINAL_ATTEMPT_ABORTED` and park the 4B tier. Proceed with 8B BALANCED + 30B DEEP product work; 4B may be revisited later as an independent optimization track.

No additional 4B restoration/build/debug checkpoint is authorized by this preregistration.

## Frozen runtime / model

Require before inference:
- llama.cpp source HEAD exactly `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- existing `build-loom-metal/bin/llama-server` executable;
- `llama-server --version` diagnostic exit 0;
- Apple M1 Metal visible;
- existing archive model only:
  `<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`;
- model SHA exactly `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`;
- Q4_K_M;
- `-ngl -1`;
- Flash Attention auto.

The unexpected prior UI asset is permitted to remain on disk but MUST NOT be used as an input to model execution and MUST NOT trigger any network operation. Record its existence as restoration provenance only.

## Network / mutation rule

During this checkpoint:
- zero network access is authorized;
- zero source/build commands are authorized;
- zero package installs/updates are authorized;
- zero model downloads/copies/conversions/requantizations are authorized;
- do not run the setup probe;
- do not rebuild anything.

If any required file is absent or any command would need network/build work, STOP `LOOM_4B_FINAL_ATTEMPT_ABORTED`.

## Runner

Use the existing local experimental runner unchanged:
`scripts/loom_4b_practical_bakeoff_runner_001.py`.

Do not edit it. Before execution verify its SHA and persist the exact SHA in evidence.

If the runner itself cannot use the now-existing pinned runtime without modification, STOP. Do not repair it in this checkpoint.

## Frozen task

Exactly the same system message, LRUCache user prompt, deterministic greedy semantics, and maximum `384` output tokens already frozen in:
`research/architecture/loom-4b-practical-bakeoff-runner-001-preregistration.md`.

Exactly one inference. No retry, rescue, re-prompt or output repair.

## Required evidence

Persist under:
`results-local/research/4b-final-bakeoff-attempt-001/<timestamp>/`

Record at minimum:
- active LOOM root/HEAD;
- runner SHA;
- source HEAD;
- server path/version;
- Metal device/backend;
- model path/SHA/quantization;
- proof no build/network/model mutation occurred;
- complete generated text;
- output token count;
- EOS vs 384 stop;
- task COMPLETE/INCOMPLETE;
- TTFT;
- generation/end-to-end throughput;
- request wall/full runner wall;
- server readiness/startup separately;
- available memory/RSS/swap telemetry;
- final classification.

## Classification

If exactly one valid frozen inference executes with correct provenance:
`LOOM_4B_FINAL_BAKEOFF_PASS`.

If another mechanical/runtime blocker prevents the inference:
`LOOM_4B_FINAL_ATTEMPT_ABORTED` and park 4B for the current phase.

Task completion is separate from runner validity.

## Interpretation boundary

Do not claim that 4B is intrinsically less intelligent than 8B from parameter count alone. Historical experiments used different quantizations/runtimes and are not a clean model-size comparison. For current product planning, however, repeated mechanical cost is itself a practical system cost; if this final attempt aborts, 4B is parked regardless of hypothetical capability.
