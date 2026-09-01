# LOOM_CONTEXT_WEBUI_001 — WebUI Context Intelligence gateway

## Objective

Apply the canonical global Pi2 Context Intelligence payload preparation to llama.cpp WebUI/OpenAI chat traffic without changing UOPT-002 model math, model artifacts, or the public loopback endpoint.

## Architecture

- `scripts/loom-deep` starts the UOPT-002 `llama-server` as a backend on `127.0.0.1:18081`.
- `scripts/loom-context-webui-gateway.mjs` listens only on `127.0.0.1:18080` and proxies the existing WebUI/API to that backend.
- The gateway dynamically imports the canonical global `pi2-context-intelligence-core.mjs` and calls its exported `packPayload`; LOOM carries no Caveman/Cavemem/Pi2 packing implementation.
- Only JSON POST requests to llama.cpp chat/completion routes are inspected. The core itself is fail-open and only transforms material historical `tool`/`toolResult` evidence. Static, health, and model routes stream directly to the backend.
- Optional redacted artifacts and accounting are local under `.loom/runtime/loom-deep/context-webui-ci/`; no external network or `external archive` dependency is allowed.

## Controls and rollback

- Default: `LOOM_CONTEXT_WEBUI_GATEWAY=1`, `LOOM_CONTEXT_WEBUI_CI=1`.
- Gateway bypass: `LOOM_CONTEXT_WEBUI_GATEWAY=0 scripts/loom-deep start` runs the backend directly on the public loopback port.
- CI bypass: `LOOM_CONTEXT_WEBUI_CI=0 scripts/loom-deep start` preserves the gateway/WebUI route but forwards chat payloads unchanged.
- `PI2_CONTEXT_INTELLIGENCE=0` is also honored by the gateway CI enablement check.

## Acceptance checks

1. Public WebUI static bytes, health, models, and OpenAI `/v1/chat/completions` remain compatible.
2. A matched tool-evidence payload yields identical selected-answer output through CI bypass and CI, with a measured context reduction and hash-verified recovery accounting.
3. Gateway health passthrough overhead is measured independently from model work.
4. UOPT-002 source GGUF, expert-major sidecar, and isolated runtime hashes are unchanged.
5. Gateway/backend bind only loopback and lifecycle stop removes both listeners.
