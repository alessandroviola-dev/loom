#!/usr/bin/env bash
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"
exec python3 scripts/live-coding-evidence-retrieval-lite.py "$@"
