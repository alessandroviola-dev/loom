#!/usr/bin/env bash
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || { echo "CE-001 REALISTIC FAIL: python3 not found" >&2; exit 1; }
command -v ForgeLoom >/dev/null 2>&1 || { echo "CE-001 REALISTIC FAIL: ForgeLoom not installed" >&2; exit 1; }

# Static checks first. The realistic run may begin after the previous harness has
# stopped/left the managed LOOM stack cold, so do not require a live gateway yet.
LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

# ForgeLoom performs its CE-001 gateway/profile preflight before invoking Forge.
# --help exits without an LLM request, but it still starts a cold managed LOOM
# server when needed. This keeps the later RPC 60s handshake from accidentally
# including the much slower model/server cold-start path.
echo "CE-001 REALISTIC INFO: ensuring ForgeLoom gateway is warm and safe before RPC"
ForgeLoom --help >/dev/null 2>&1 || {
  echo "CE-001 REALISTIC FAIL: ForgeLoom preflight/start failed" >&2
  exit 1
}

bash scripts/verify-context-engine.sh

# A real agentic task can require several local 30B inference/tool cycles. The
# Python harness still has a finite per-task guard, but its default is raised for
# this slow retained runtime so legitimate multi-call work is not misclassified
# as an RPC/context failure. Operators can override it explicitly.
export LOOM_CE001_REALISTIC_TASK_TIMEOUT="${LOOM_CE001_REALISTIC_TASK_TIMEOUT:-1800}"
export PYTHONUNBUFFERED=1

echo "CE-001 REALISTIC INFO: starting frozen 6-task benchmark in one ForgeLoom session"
exec python3 scripts/realistic-context-engine-benchmark.py
