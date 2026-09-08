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
node --check src/forgeloom-runtime-hardening/policy.mjs
node --check src/forgeloom-runtime-hardening/output-budget.mjs
node --experimental-strip-types --check src/forgeloom-runtime-hardening/index.ts
node --check scripts/loom-context-webui-gateway.mjs
bash -n scripts/install-forge-loom.sh
bash -n scripts/smoke-context-engine.sh
if [[ -f scripts/stress-context-engine.sh ]]; then bash -n scripts/stress-context-engine.sh; fi
pass "static syntax"

node --test test/context-engine-core.test.mjs
node --test test/forgeloom-runtime-hardening.test.mjs
pass "governor/runtime unit tests"

python3 - <<'PY'
from pathlib import Path

core = Path("src/loom-context-engine/core.mjs").read_text()
ext = Path("src/loom-context-engine/index.ts").read_text()
hardening = Path("src/forgeloom-runtime-hardening/index.ts").read_text()
policy = Path("src/forgeloom-runtime-hardening/policy.mjs").read_text()
output_budget = Path("src/forgeloom-runtime-hardening/output-budget.mjs").read_text()
installer = Path("scripts/install-forge-loom.sh").read_text()
gateway = Path("scripts/loom-context-webui-gateway.mjs").read_text()
smoke = Path("scripts/smoke-context-engine.sh").read_text()
profile = Path("config/loom-deep-profiles.env").read_text()

checks = {
    "physical ctx frozen": 'LOOM_DEEP_CTX="4096"' in profile,
    "Forge CI disabled by ForgeLoom": 'FORGE_CONTEXT_INTELLIGENCE=0' in installer,
    "LOOM engine opt-in": 'LOOM_CONTEXT_ENGINE=1' in installer and 'LOOM_CONTEXT_ENGINE' in ext,
    "working high-water": '1600' in core and '1600' in ext and '1600' in installer,
    "working target": '1200' in core and '1200' in ext and '1200' in installer,
    "safe total": '3600' in installer and '3600' in gateway,
    "safe input": '2800' in installer and '2800' in gateway,
    "minimum output reserve": 'MIN_OUTPUT="${LOOM_CONTEXT_WEBUI_MIN_OUTPUT_TOKENS:-800}"' in installer and 'minOutputTokens' in gateway,
    "adaptive output ceiling": 'MAX_OUTPUT="${LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS:-1600}"' in installer and 'adaptiveOutputBudget' in gateway,
    "adaptive allocator wired": 'allocateOutputBudget' in gateway and 'dynamicOutputCeiling' in gateway and 'safeInputTokens + minOutputTokens' in output_budget,
    "exact token endpoint": '/v1/chat/completions/input_tokens' in gateway,
    "legacy exact fallback": '/apply-template' in gateway and '/tokenize' in gateway,
    "fail closed": 'LOOM_CONTEXT_WEBUI_GUARD_FAIL_CLOSED=1' in installer,
    "minimal system prompt": 'before_agent_start' in ext and 'minimalSystemPrompt' in ext,
    "threshold compaction cancelled": 'event.reason === "threshold"' in ext and 'cancel: true' in ext,
    "one-shot smoke uses ForgeLoom": 'ForgeLoom --no-session -p' in smoke,
    "smoke checks exact guard": 'guardChecked' in smoke and 'projectedTotalTokens' in smoke,
    "private ForgeLoom extension root": 'FORGE_LOOM_DIR="$AGENT_DIR/forge-loom"' in installer,
    "legacy global extension migration": 'LEGACY_GLOBAL_DIR="$EXTENSIONS_DIR/loom-context-engine"' in installer and 'backup_existing_dir "$LEGACY_GLOBAL_DIR"' in installer,
    "explicit ForgeLoom extension load": 'Forge --extension "$CONTEXT_EXTENSION" --extension "$HARDENING_EXTENSION" --model "$MODEL"' in installer,
    "global duplicate runtime guard": 'globally auto-discovered LOOM Context Engine exists' in installer,
    "runtime hardening private": 'HARDENING_TARGET_DIR="$FORGE_LOOM_DIR/runtime-hardening"' in installer,
    "path grounding": 'probedMissingPaths' in hardening and 'Never invent companion modules' in policy,
    "paged output continuation": 'RECOVERY_MESSAGE_TYPE' in hardening and 'deliverAs: "steer"' in hardening and 'sanitizeRecoveryContext' in hardening and 'NESSUNA SPIEGAZIONE' in policy,
    "language-aware recovery": 'detectUserLanguage' in hardening and 'recupero pagina' in policy,
    "recovery checkpoint persistence": 'recoveryNeedsCheckpoint' in hardening and 'shouldForceRecoveryCheckpoint' in hardening and 'task non è concluso finché un edit/write non riesce' in policy,
    "no-progress runaway guard": 'MAX_NO_PROGRESS_TRUNCATIONS' in hardening and 'ctx.abort()' in hardening,
    "auto stop": 'trap release_client EXIT' in installer and 'ForgeLoomStop' in installer,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("invariant check failed: " + ", ".join(failed))

if 2800 + 800 > 3600 or 3600 >= 4096:
    raise SystemExit("unsafe guaranteed CE envelope")
if 1600 >= 3600 or 1600 < 800:
    raise SystemExit("invalid adaptive output range")
if 1600 + 900 >= 2800:
    raise SystemExit("working high-water leaves insufficient measured fixed-overhead headroom")
print("CE-001 invariant checks: PASS")
print("Forge/ForgeLoom extension isolation invariants: PASS")
print("ForgeLoom runtime hardening invariants: PASS")
PY
pass "repository invariants"

if [[ "${LOOM_CONTEXT_VERIFY_SKIP_LIVE:-0}" == "1" ]]; then
  echo "CE-001 VERIFY INFO: live gateway check skipped by request."
else
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
    "minOutputTokens": 800,
    "maxOutputTokens": 1600,
    "adaptiveOutputBudget": True,
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
fi

echo "CE-001 VERIFY COMPLETE"
