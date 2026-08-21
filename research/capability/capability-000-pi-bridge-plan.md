# CAPABILITY 000 — canonical Qwen3-8B -> Pi bridge

Date: 2026-08-21
Status: FROZEN / IMPLEMENTATION PENDING

## Purpose

Before CAPABILITY 001, prove that Pi can use the **current canonical LOOM Qwen3-8B 3-bit model** as its actual local reasoning model. The historical Pi benchmark used Ollama + Qwen3.5 4B and must not be mistaken for the current system.

This phase is infrastructure only. It does not score model intelligence and does not optimize inference.

## Frozen subject

- local model: `results-local/mlx/models/Qwen3-8B-3bit/`
- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- Python 3.13
- normal Qwen3 chat template
- `enable_thinking=false`
- no S1_R8 at M1
- no Ollama model substitution
- no cloud/provider fallback

REALGEN 001 is the semantic/performance reference: 13.184615357 real generation tok/s on the frozen six-prompt run. CAPABILITY 000 does not need to reproduce that performance number; it must preserve model identity and ordinary generation semantics.

## Bridge requirement

Expose the frozen local model through the smallest local API surface accepted by Pi 0.84.2.

Preferred order:

1. inspect whether the installed `mlx_lm` already supplies a compatible OpenAI-style server that can load the exact local model and accept Pi chat/tool traffic;
2. reuse it if it preserves the frozen model/tokenizer identity and needs no model conversion;
3. otherwise implement a minimal repository-local adapter/server.

Do not modify installed MLX packages.

The bridge may expose only localhost. It must not make external network/provider calls.

## Pi isolation

Reuse the historical isolated Pi pattern:

- run-local `PI_CODING_AGENT_DIR` or equivalent;
- production Pi settings/auth/sessions untouched;
- `PI_OFFLINE=1`;
- update/version/telemetry work disabled where supported;
- provider base URL points only at localhost;
- extensions/skills/prompt templates/themes/context files disabled for benchmark execution unless CAPABILITY 001 explicitly requires otherwise.

## Protocol qualification

Before an agentic smoke, prove and record:

- actual model path loaded;
- model/tokenizer/config identity;
- provider/base URL used by Pi;
- no Ollama model is serving the request;
- no remote API key/provider is used;
- context limit selected for Pi;
- tool schema/message traffic is accepted by the bridge.

If Pi requires an OpenAI chat/tool protocol not supported by the current server, implement only the minimum compatibility translation needed. Do not alter the model prompt/task content to rescue capability.

## Functional smoke

Use a disposable workspace outside the canonical repository worktree.

Expose Pi tools:
- `read`
- `write`
- `edit`
- `bash`

Freeze this smoke task:

1. workspace contains `numbers.txt` with exactly:
   `7\n11\n13\n`
2. tell the agent to read `numbers.txt`;
3. compute the sum;
4. create `answer.txt` containing exactly `31\n`;
5. run `cat answer.txt` with bash to verify it;
6. final assistant text must be exactly `DONE`.

Functional PASS requires:

- Pi process exits successfully;
- at least one actual model-generated tool call is observed;
- `answer.txt` is exactly correct;
- `numbers.txt` is byte-identical;
- no unexpected persistent files;
- tool paths remain inside the disposable workspace;
- no event/JSON parse failure;
- no external provider/network fallback.

Strict PASS additionally requires final text exactly `DONE`.

## Resource policy

This is not a causal performance comparison. Do not require the historical 60% free-memory launch gate.

Record host state, but only abort under the inherited hard runtime safety boundary:

- free memory <5%; or
- swap >5600 MB.

No purge or artificial host-state manipulation.

## Result classes

- `CAPABILITY_000_PI_BRIDGE_PASS`
- `CAPABILITY_000_PI_BRIDGE_FUNCTIONAL_PASS_STRICT_FAIL`
- `CAPABILITY_000_PI_PROTOCOL_INCOMPATIBLE`
- `CAPABILITY_000_RUNTIME_FAIL`
- `CAPABILITY_000_RESOURCE_ABORT`

Only a functional PASS allows CAPABILITY 001 to run.

## Pi role boundary

Pi writes code and runs this test locally. Pi does NOT commit, push, edit HANDOFF, or edit ROADMAP. ChatGPT reviews evidence and performs repository synchronization afterward.
