# LOOM — Agent Protocol

Version: 5.00
Status: **ACTIVE — CONTEXT ENGINE RESEARCH ONLY**

The owner explicitly reopened LOOM on 2026-09-07 for one purpose: build a host-side Context Engine that lets the retained local 30B UNLOCKED model operate safely with a physical 4096-token context window over long Forge sessions.

## Scope

Current research branch: `research/context-engine-001`.

Allowed work is limited to the external LOOM Context Engine, its launcher/integration, tests, accounting, and documentation.

The retained model/runtime product remains frozen:

- `models/loom-deep-30b-unlocked.gguf`
- UOPT-003 S40 profile
- expert-major sidecar
- patched llama-server runtime
- physical `n_ctx = 4096`

Do not resume UOPT speed/quantization/speculation research, download/build replacement models, mutate runtime patches, or alter the retained production profile unless the owner explicitly authorizes it.

## Architectural invariants

1. **Do not modify Forge.** `Ilcoach/forge-for-pi` remains the canonical general-purpose Forge.
2. LOOM Context Engine is a separate extension owned by this repository and is opt-in only.
3. Normal `Forge` behavior must remain unchanged. LOOM-specific behavior activates only through the dedicated `ForgeLoom` mode/launcher.
4. In `ForgeLoom`, Forge Context Intelligence may be disabled for that process only so that a single component owns context transformation.
5. The 30B physical context remains exactly **4096**. The engine must solve continuity through bounded working context, not by increasing `n_ctx`.
6. **4096 is a forbidden operational boundary, not a target.** Preventive compaction/pruning must run before every LLM call and keep the visible context well below the physical limit.
7. Everything removed from the model-visible context must remain in the original Pi/Forge session; later phases may add explicit durable evidence storage/recovery.
8. CE-001 must stay deterministic and lightweight: no second LLM, embeddings, vector database, or new model-facing tools.
9. Preserve Forge's four-tool surface: `read`, `bash`, `edit`, `write`.
10. Make small reversible commits and record measured evidence before claiming a GO.

## CE-001 goal

Implement and validate the preventive Context Governor only:

- Pi `context` event interception before every model call;
- bounded sliding-window view over the full session;
- whole-turn eviction first, preserving current tool-call/result coherence;
- deterministic compaction of oversized current-turn tool outputs only when necessary;
- high-water trigger and lower post-compaction target;
- exact final request token guard at the LOOM gateway using llama.cpp token counting;
- local accounting/telemetry;
- dedicated `ForgeLoom` launcher/profile that enables the engine without changing normal Forge.

CE-001 is a GO only if a frozen long-running workload can exceed 4096 cumulative session tokens while:

- no request approaches/exceeds the configured safe ceiling;
- Pi/Forge threshold or overflow compaction is never needed;
- the session remains alive;
- the task still completes correctly;
- RAM/swap and throughput do not materially regress.

Do not add durable task state, BM25/FTS retrieval, semantic memory, or archive/recovery sophistication until CE-001 proves the governor itself.

## Git hygiene

Never commit:

- `.loom/`
- `results-local/`
- model GGUFs or sidecars
- caches/temp files
- external-drive artifacts
- home-directory configuration
- secrets
- unrelated untracked scripts

Read `HANDOFF.md` before work. Treat older closure/UOPT documents as historical evidence, not as instructions to resume optimization.