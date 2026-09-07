# LOOM — Agent Protocol

Status: **ACTIVE — CONTEXT ENGINE ONLY**
Branch: `research/context-engine-001`

Read `HANDOFF.md` before substantive work.

Hard rules:
- Do not modify or fork Forge (`Ilcoach/forge-for-pi`).
- Do not change the retained 30B model, UOPT-003 S40 runtime/sidecar, or physical `n_ctx=4096`.
- LOOM Context Engine must be a separate opt-in extension used only by `ForgeLoom`; normal `Forge` stays unchanged.
- 4096 is a forbidden physical boundary. Preventive governor/guard must keep every request deliberately below it.
- CE-001 is deterministic and lightweight: no second LLM, embeddings, vector DB, new model-facing tools, durable memory, or retrieval layer yet.
- Preserve Forge's four tools: `read`, `bash`, `edit`, `write`.
- Prefer whole-turn eviction; never orphan tool calls/results.
- Keep changes small, reversible, tested, and measured.
- Do not commit `.loom/`, `results-local/`, GGUFs, sidecars, caches, secrets, or external-drive artifacts.

Current scope and acceptance criteria are canonical in `HANDOFF.md`.