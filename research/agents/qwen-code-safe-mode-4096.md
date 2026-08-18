# Qwen Code Safe-Mode 4096 Diagnostic — Result

Date: 2026-08-18
Status: COMPLETED / VALID

## Configuration

- Qwen Code 0.21.13
- model: `qwen3.5:4b-mlx`
- Ollama OpenAI-compatible endpoint
- intended context: 4096
- `--safe-mode`
- read-only README smoke task
- model unloaded before run
- no 8192 rescue

## Result

Run id: `qwen-safe-20260818-233219`

- process exit: 0
- timeout: false
- model detected: `qwen3.5:4b-mlx`
- tool calls: none
- semantic result: API context-limit error
- estimated prompt tokens: **4363**
- hard limit: **4096**
- over limit: **267 tokens**
- compression status: `NOOP`
- working tree unchanged: true
- safe mode warning confirmed that customizations were disabled

Historical normal-config smoke estimate: ~4474 tokens.
Safe mode therefore reduced the initial estimate by only **111 tokens** (~2.5%).

## Interpretation

1. Optional Qwen Code customizations/context are not the main binding constraint at context 4096.
2. Even the official safe-mode harness cannot form the first request within the 4096-token budget for this smoke task.
3. No tool call occurred, so this remains a pre-inference / harness-packaging failure, not evidence about the model's ability to use tools.
4. Pi already succeeds at context 4096 and has completed the frozen coding benchmark agentically, so further Qwen Code minimization is low-priority for LOOM's main research path.
5. Do not run an 8192 rescue unless Qwen Code comparison becomes strategically useful later; it is not required for current Phase 4 progression.

## Decision

Qwen Code is retained as a **secondary harness comparator** and deprioritized. LOOM returns to the main runtime/model-capability roadmap with llama.cpp.
