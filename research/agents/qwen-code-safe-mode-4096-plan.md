# Qwen Code Safe-Mode 4096 Diagnostic — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Question

Can Qwen Code 0.21.13 form and execute the first local Ollama request at context 4096 when optional/custom workspace context is removed with official `--safe-mode`?

## Motivation

Historical normal-config smoke at context 4096 failed before model inference:

- Qwen Code 0.21.13
- `qwen3.5:4b-mlx`
- estimated initial prompt: ~4474 tokens
- hard limit: 4096
- always-on context warning: ~1429 tokens
- no tool call
- Ollama model remained unloaded

Pi minimal read-only at the same model/context succeeded.

This experiment isolates Qwen Code's optional customization/context surface from its core harness overhead.

## Official behavior relied on

Qwen Code documents `--safe-mode` as disabling session customizations such as context files, hooks, extensions, skills, MCP servers, custom subagents, permission rules, memory features and sandbox/settings-derived customization behavior for the invocation.

Model/auth selection is explicitly supplied on the CLI:

- `--auth-type openai`
- `--model qwen3.5:4b-mlx`
- `--openai-api-key ollama`
- `--openai-base-url http://localhost:11434/v1`

The tracked LOOM project model provider already defines the model with context window 4096 and max output 2048. The CLI selection matches that provider/model. `QWEN_CODE_MAX_OUTPUT_TOKENS=2048` is also set as a defensive output cap.

## Frozen task

Read-only smoke prompt:

- require Qwen Code to use a repository file-reading tool on `README.md`;
- no writes, renames, deletes or shell commands;
- return exactly the first Markdown heading `# LOOM`.

## Invocation characteristics

- `--safe-mode`
- `--auth-type openai`
- `--model qwen3.5:4b-mlx`
- explicit Ollama OpenAI-compatible endpoint/key
- `--approval-mode plan`
- JSON output
- max wall time 2 minutes
- max tool calls 5
- max session turns 8
- stop Ollama model before run

## Measurements

- process exit code
- Qwen version
- parsed JSON / semantic API error
- selected model
- tool names
- final result
- stderr warnings including estimated prompt/context information
- git status/diff before and after
- memory/swap/Ollama state before and after

## Success criteria

Strict success requires:

1. Qwen process completes without semantic API failure;
2. at least one file-reading tool is executed;
3. final result exactly `# LOOM`;
4. tracked working tree remains unchanged.

## Interpretation

### Safe mode succeeds at 4096

Evidence that optional/custom Qwen Code context was the binding cause of the historical 4474>4096 preflight failure. Core safe-mode harness is viable at 4096.

### Safe mode still fails pre-inference at 4096

Evidence that Qwen Code's core prompt/tool surface itself is too large or too close to the limit for this model/context, even after customization removal.

### Request reaches Ollama but fails later

Separately classify tool transport/model behavior; do not collapse it into the historical preflight-context failure.

## Non-claims

This is not a coding benchmark and does not compare Qwen Code quality with Pi. It only tests feasibility/overhead of the minimal safe-mode harness.

No context increase to 8192 is allowed during this run. Any later 8192 test is a separate experiment.
