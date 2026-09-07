#!/usr/bin/env bash
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || { echo "CE-001 REALISTIC FAIL: python3 not found" >&2; exit 1; }
command -v ForgeLoom >/dev/null 2>&1 || { echo "CE-001 REALISTIC FAIL: ForgeLoom not installed" >&2; exit 1; }

bash scripts/verify-context-engine.sh
exec python3 scripts/realistic-context-engine-benchmark.py
