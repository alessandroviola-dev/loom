# LOOM — Agent Protocol

Status: **ACTIVE — CE-002 EVIDENCE ARCHIVE / RETRIEVAL**
Branch: `research/context-engine-002`

Read `HANDOFF.md` before substantive work.

Hard rules:
- Do not modify or fork Forge (`Ilcoach/forge-for-pi`).
- Do not change the retained 30B model, UOPT-003 S40 runtime/sidecar, or physical `n_ctx=4096`.
- CE-001 is frozen as an accepted rollback/reference checkpoint; do not change its branch or reopen its thresholds without demonstrated regression evidence.
- LOOM Context Engine remains a separate opt-in extension used only by `ForgeLoom`; normal `pi` and normal `Forge` stay unchanged.
- 4096 is a forbidden physical boundary. CE-002 must preserve the CE-001 governor/gateway envelope and may not trade safety headroom for retrieval features.
- Preserve Forge's four tools: `read`, `bash`, `edit`, `write`.
- CE-002 may add durable local evidence storage, stable evidence IDs/hashes, exact recovery, compact task state, and lightweight lexical retrieval.
- No second LLM, embeddings, vector DB, network memory service, or new model-facing tool unless measured evidence later demonstrates a need and the owner explicitly approves it.
- Evidence storage must be local-only, content-addressed/deduplicated where practical, integrity-verifiable, and must retain the exact original evidence rather than only summaries.
- Never orphan tool calls/results in the model-visible context. Persistent Pi/Forge session semantics remain unchanged.
- Keep changes small, reversible, tested, and measured.
- Do not commit `.loom/`, `results-local/`, GGUFs, sidecars, generated evidence archives, caches, secrets, or external-drive artifacts.

Current scope and acceptance criteria are canonical in `HANDOFF.md`.
