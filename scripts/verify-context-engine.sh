#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-001 VERIFY FAIL: $*" >&2; exit 1; }
pass() { echo "CE-001 VERIFY PASS: $*"; }

command -v node >/dev/null 2>&1 || fail "node not found"
command -v bash >/dev/null 2>&1 || fail "bash not found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

node --check src/loom-context-engine/core.mjs
node --check scripts/loom-context-webui-gateway.mjs
bash -n scripts/install-forge-loom.sh
bash -n scripts/smoke-context-engine.sh
pass "static syntax"

node --test test/context-engine-core.test.mjs
pass "governor unit tests"

python3 - <<'PY'
from pathlib import Path

core = Path("src/loom-context-engine/core.mjs").read_text()
ext = Path("src/loom-context-engine/index.ts").read_text()
installer = Path("scripts/install-forge-loom.sh").read_text()
gateway = Path("scripts/loom-context-webui-gateway.mjs").read_text()
smoke = Path("scripts/smoke-context-engine.sh").read_text()
profile = Path("config/loom-deep-profiles.env").read_text()

checks = {
    "physical ctx frozen": 'LOOM_DEEP_CTX="4096"' in profile,
    "Forge CI disabled by ForgeLoom": 'FORGE_CONTEXT_INTELLIGENCE=0' in installer,
    "LOOM engine opt-in": 'LOOM_CONTEXT_ENGINE=1' in installer and 'LOOM_CONTEXT_ENGINE' in ext,
    "working high-water": '2200' in core and '2200' in installer,
    "working target": '1700' in core and '1700' in installer,
    "safe total": '3600' in installer and '3600' in gateway,
    "safe input": '2800' in installer and '2800' in gateway,
    "max output": '800' in installer and '800' in gateway,
    "exact token endpoint": '/v1/chat/completions/input_tokens' in gateway,
    "fail closed": 'LOOM_CONTEXT_WEBUI_GUARD_FAIL_CLOSED=1' in installer,
    "minimal system prompt": 'before_agent_start' in ext and 'minimalSystemPrompt' in ext,
    "threshold compaction cancelled": 'event.reason === "threshold"' in ext and 'cancel: true' in ext,
    "one-shot smoke uses ForgeLoom": 'ForgeLoom --no-session -p' in smoke,
    "smoke checks exact guard": 'guardChecked' in smoke and 'projectedTotalTokens' in smoke,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("invariant check failed: " + ", ".join(failed))

if 2800 + 800 > 3600 or 3600 >= 4096:
    raise SystemExit("unsafe hard-coded CE-001 envelope")
print("CE-001 invariant checks: PASS")
PY
pass "repository invariants"

STATUS_URL="${LOOM_CONTEXT_STATUS_URL:-http://127.0.0.1:18080/loom/context-engine/status}"
if command -v curl >/dev/null 2>&1 && status="$(curl -fsS --max-time 2 "$STATUS_URL" 2>/dev/null)"; then
  python3 - "$status" <<'PY'
import json, sys

data = json.loads(sys.argv[1])
expected = {
    "contextEngineGateway": True,
    "hardGuardEnabled": True,
    "safeTotalTokens": 3600,
    "safeInputTokens": 2800,
    "maxOutputTokens": 800,
    "physicalContextTokens": 4096,
    "forbiddenReserveTokens": 496,
    "guardFailClosed": True,
    "ciStatus": "disabled",
}
bad = {k: (data.get(k), v) for k, v in expected.items() if data.get(k) != v}
if bad:
    raise SystemExit("live gateway mismatch: " + repr(bad))
print("CE-001 live gateway status: PASS")
PY
  pass "live gateway envelope"
else
  echo "CE-001 VERIFY INFO: live gateway not running; static verification completed."
fi

echo "CE-001 VERIFY COMPLETE"
