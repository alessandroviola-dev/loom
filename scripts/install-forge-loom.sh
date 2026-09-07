#!/usr/bin/env bash
set -euo pipefail

EXPECTED_PI_VERSION="0.84.4"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$ROOT/src/loom-context-engine"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
EXTENSIONS_DIR="$AGENT_DIR/extensions"
TARGET_DIR="$EXTENSIONS_DIR/loom-context-engine"
BACKUP_DIR="$AGENT_DIR/loom-context-engine-backups"
LAUNCHER_DIR="$HOME/.local/bin"
LAUNCHER="$LAUNCHER_DIR/ForgeLoom"

fail() { echo "$*" >&2; exit 1; }

is_managed_launcher() {
  [ -f "$1" ] && [ ! -L "$1" ] && grep -Fqx '# Managed by LOOM Context Engine' "$1"
}

command -v pi >/dev/null 2>&1 || fail "ForgeLoom requires pi on PATH."
command -v Forge >/dev/null 2>&1 || fail "ForgeLoom requires Forge to be installed first."
command -v curl >/dev/null 2>&1 || fail "ForgeLoom requires curl."
command -v python3 >/dev/null 2>&1 || fail "ForgeLoom requires python3."
PI_VERSION="$(pi --version 2>/dev/null | tr -d '[:space:]')"
[ "$PI_VERSION" = "$EXPECTED_PI_VERSION" ] || fail "CE-001 is validated against Pi $EXPECTED_PI_VERSION via Forge; found ${PI_VERSION:-unknown}."
[ -f "$SOURCE_DIR/index.ts" ] || fail "Missing Context Engine source: $SOURCE_DIR/index.ts"
[ -f "$SOURCE_DIR/core.mjs" ] || fail "Missing Context Engine source: $SOURCE_DIR/core.mjs"
[ -f "$ROOT/scripts/loom-deep" ] || fail "Missing LOOM lifecycle manager: $ROOT/scripts/loom-deep"

mkdir -p "$EXTENSIONS_DIR" "$LAUNCHER_DIR"
if [ -e "$LAUNCHER" ] || [ -L "$LAUNCHER" ]; then
  is_managed_launcher "$LAUNCHER" || fail "Refusing to overwrite non-LOOM launcher: $LAUNCHER"
fi
if [ -e "$TARGET_DIR" ] || [ -L "$TARGET_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  BACKUP_PATH="$BACKUP_DIR/loom-context-engine-$(date -u +%Y%m%dT%H%M%SZ)"
  [ ! -e "$BACKUP_PATH" ] || BACKUP_PATH="${BACKUP_PATH}-$$"
  mv "$TARGET_DIR" "$BACKUP_PATH"
  echo "Backed up existing LOOM Context Engine to $BACKUP_PATH"
fi

cp -R "$SOURCE_DIR" "$TARGET_DIR"
find "$TARGET_DIR" -type l -print -quit | grep -q . && { rm -rf "$TARGET_DIR"; fail "Installation rejected symlinked Context Engine content."; }

TEMP="$(mktemp "$LAUNCHER_DIR/.ForgeLoom.XXXXXX")"
{
  cat <<'HEADER'
#!/usr/bin/env bash
# Managed by LOOM Context Engine
set -euo pipefail
HEADER
  printf 'ROOT=%q\n' "$ROOT"
  cat <<'BODY'
SAFE_INPUT="${LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS:-3000}"
HIGH_WATER="${LOOM_CONTEXT_HIGH_WATER_TOKENS:-2400}"
TARGET="${LOOM_CONTEXT_TARGET_TOKENS:-1900}"
MODEL="${LOOM_FORGE_MODEL:-loom-deep-30b-unlocked}"
STATUS_URL="http://127.0.0.1:18080/loom/context-engine/status"

case "$SAFE_INPUT:$HIGH_WATER:$TARGET" in
  *[!0-9:]*|*::*|:*|*:) echo "ForgeLoom token thresholds must be positive integers." >&2; exit 64 ;;
esac
if (( TARGET > HIGH_WATER || HIGH_WATER >= SAFE_INPUT || SAFE_INPUT >= 4096 )); then
  echo "ForgeLoom requires TARGET <= HIGH_WATER < SAFE_INPUT < 4096." >&2
  exit 64
fi

for arg in "$@"; do
  case "$arg" in
    --model|--model=*|--provider|--provider=*)
      echo "ForgeLoom owns model selection. Set LOOM_FORGE_MODEL instead of passing --model/--provider." >&2
      exit 64
      ;;
  esac
done

gateway_safe() {
  local status
  status="$(curl -fsS --max-time 2 "$STATUS_URL" 2>/dev/null)" || return 1
  python3 - "$SAFE_INPUT" "$status" <<'PY'
import json, sys
safe = int(sys.argv[1])
try:
    data = json.loads(sys.argv[2])
except Exception:
    raise SystemExit(1)
ok = (
    data.get("contextEngineGateway") is True
    and data.get("hardGuardEnabled") is True
    and data.get("guardFailClosed") is True
    and data.get("safeInputTokens") == safe
    and data.get("ciStatus") == "disabled"
)
raise SystemExit(0 if ok else 1)
PY
}

if ! gateway_safe; then
  "$ROOT/scripts/loom-deep" stop >/dev/null 2>&1 || true
  env \
    LOOM_CONTEXT_WEBUI_CI=0 \
    LOOM_CONTEXT_WEBUI_HARD_GUARD=1 \
    LOOM_CONTEXT_WEBUI_GUARD_FAIL_CLOSED=1 \
    LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS="$SAFE_INPUT" \
    "$ROOT/scripts/loom-deep" start
fi

gateway_safe || { echo "ForgeLoom refused to start: LOOM gateway guard is not in the required safe state." >&2; exit 1; }

exec env \
  FORGE_CONTEXT_INTELLIGENCE=0 \
  LOOM_CONTEXT_ENGINE=1 \
  LOOM_CONTEXT_ACCOUNTING=1 \
  LOOM_CONTEXT_HIGH_WATER_TOKENS="$HIGH_WATER" \
  LOOM_CONTEXT_TARGET_TOKENS="$TARGET" \
  Forge --model "$MODEL" "$@"
BODY
} > "$TEMP"
chmod 755 "$TEMP"
mv -f "$TEMP" "$LAUNCHER"

echo "Installed LOOM Context Engine to $TARGET_DIR"
echo "Installed launcher: $LAUNCHER"
echo "Use: ForgeLoom"
