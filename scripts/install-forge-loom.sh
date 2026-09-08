#!/usr/bin/env bash
set -euo pipefail

SUPPORTED_PI_VERSIONS="0.84.4 0.85.1"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$ROOT/src/loom-context-engine"
HARDENING_SOURCE_DIR="$ROOT/src/forgeloom-runtime-hardening"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
EXTENSIONS_DIR="$AGENT_DIR/extensions"
LEGACY_GLOBAL_DIR="$EXTENSIONS_DIR/loom-context-engine"
FORGE_LOOM_DIR="$AGENT_DIR/forge-loom"
TARGET_DIR="$FORGE_LOOM_DIR/loom-context-engine"
HARDENING_TARGET_DIR="$FORGE_LOOM_DIR/runtime-hardening"
BACKUP_DIR="$AGENT_DIR/loom-context-engine-backups"
LAUNCHER_DIR="$HOME/.local/bin"
LAUNCHER="$LAUNCHER_DIR/ForgeLoom"
STOP_LAUNCHER="$LAUNCHER_DIR/ForgeLoomStop"

fail() { echo "$*" >&2; exit 1; }

is_managed_launcher() {
  [ -f "$1" ] && [ ! -L "$1" ] && grep -Fqx '# Managed by LOOM Context Engine' "$1"
}

pi_version_supported() {
  local candidate="$1" supported
  for supported in $SUPPORTED_PI_VERSIONS; do
    [ "$candidate" = "$supported" ] && return 0
  done
  return 1
}

backup_existing_dir() {
  local source="$1" label="$2" backup_path
  [ -e "$source" ] || [ -L "$source" ] || return 0
  mkdir -p "$BACKUP_DIR"
  backup_path="$BACKUP_DIR/${label}-$(date -u +%Y%m%dT%H%M%SZ)"
  [ ! -e "$backup_path" ] || backup_path="${backup_path}-$$"
  mv "$source" "$backup_path"
  echo "Backed up existing ForgeLoom component to $backup_path"
}

command -v pi >/dev/null 2>&1 || fail "ForgeLoom requires pi on PATH."
command -v Forge >/dev/null 2>&1 || fail "ForgeLoom requires Forge to be installed first."
command -v curl >/dev/null 2>&1 || fail "ForgeLoom requires curl."
command -v python3 >/dev/null 2>&1 || fail "ForgeLoom requires python3."
PI_VERSION="$(pi --version 2>/dev/null | tr -d '[:space:]')"
pi_version_supported "$PI_VERSION" || fail "CE-001 supports Pi versions: $SUPPORTED_PI_VERSIONS; found ${PI_VERSION:-unknown}."
[ -f "$SOURCE_DIR/index.ts" ] || fail "Missing Context Engine source: $SOURCE_DIR/index.ts"
[ -f "$SOURCE_DIR/core.mjs" ] || fail "Missing Context Engine source: $SOURCE_DIR/core.mjs"
[ -f "$HARDENING_SOURCE_DIR/index.ts" ] || fail "Missing ForgeLoom runtime hardening source: $HARDENING_SOURCE_DIR/index.ts"
[ -f "$HARDENING_SOURCE_DIR/policy.mjs" ] || fail "Missing ForgeLoom runtime hardening policy: $HARDENING_SOURCE_DIR/policy.mjs"
[ -f "$HARDENING_SOURCE_DIR/output-budget.mjs" ] || fail "Missing ForgeLoom adaptive output policy: $HARDENING_SOURCE_DIR/output-budget.mjs"
[ -f "$ROOT/scripts/loom-deep" ] || fail "Missing LOOM lifecycle manager: $ROOT/scripts/loom-deep"

# ForgeLoom-only extensions must never live under Pi's globally auto-discovered
# extensions directory. Normal pi and normal Forge remain completely unchanged.
mkdir -p "$FORGE_LOOM_DIR" "$LAUNCHER_DIR"
for private_dir in "$TARGET_DIR" "$HARDENING_TARGET_DIR"; do
  case "$private_dir/" in
    "$EXTENSIONS_DIR/"*) fail "Refusing to install a ForgeLoom-only extension under Pi's global extensions directory." ;;
  esac
done

for launcher in "$LAUNCHER" "$STOP_LAUNCHER"; do
  if [ -e "$launcher" ] || [ -L "$launcher" ]; then
    is_managed_launcher "$launcher" || fail "Refusing to overwrite non-LOOM launcher: $launcher"
  fi
done

backup_existing_dir "$LEGACY_GLOBAL_DIR" "loom-context-engine-global"
backup_existing_dir "$TARGET_DIR" "loom-context-engine-forgeloom"
backup_existing_dir "$HARDENING_TARGET_DIR" "forgeloom-runtime-hardening"

cp -R "$SOURCE_DIR" "$TARGET_DIR"
cp -R "$HARDENING_SOURCE_DIR" "$HARDENING_TARGET_DIR"
for installed_dir in "$TARGET_DIR" "$HARDENING_TARGET_DIR"; do
  find "$installed_dir" -type l -print -quit | grep -q . && { rm -rf "$installed_dir"; fail "Installation rejected symlinked ForgeLoom extension content."; }
done
[ ! -e "$LEGACY_GLOBAL_DIR" ] && [ ! -L "$LEGACY_GLOBAL_DIR" ] || fail "Global LOOM Context Engine still exists after migration: $LEGACY_GLOBAL_DIR"

pi --extension "$TARGET_DIR/index.ts" --extension "$HARDENING_TARGET_DIR/index.ts" --help >/dev/null 2>&1 \
  || fail "Pi rejected ForgeLoom's explicit private extension paths."
Forge --extension "$TARGET_DIR/index.ts" --extension "$HARDENING_TARGET_DIR/index.ts" --help >/dev/null 2>&1 \
  || fail "Forge does not pass ForgeLoom's explicit private extension paths through to Pi."

TEMP="$(mktemp "$LAUNCHER_DIR/.ForgeLoom.XXXXXX")"
{
  cat <<'HEADER'
#!/usr/bin/env bash
# Managed by LOOM Context Engine
set -euo pipefail
HEADER
  printf 'ROOT=%q\n' "$ROOT"
  printf 'CONTEXT_EXTENSION=%q\n' "$TARGET_DIR/index.ts"
  printf 'HARDENING_EXTENSION=%q\n' "$HARDENING_TARGET_DIR/index.ts"
  printf 'LEGACY_GLOBAL_EXTENSION=%q\n' "$LEGACY_GLOBAL_DIR"
  cat <<'BODY'
SAFE_TOTAL="${LOOM_CONTEXT_WEBUI_SAFE_TOTAL_TOKENS:-3600}"
SAFE_INPUT="${LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS:-2800}"
MIN_OUTPUT="${LOOM_CONTEXT_WEBUI_MIN_OUTPUT_TOKENS:-800}"
MAX_OUTPUT="${LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS:-1600}"
LEGACY_MARGIN="${LOOM_CONTEXT_WEBUI_LEGACY_COUNT_MARGIN_TOKENS:-32}"
HIGH_WATER="${LOOM_CONTEXT_HIGH_WATER_TOKENS:-1600}"
TARGET="${LOOM_CONTEXT_TARGET_TOKENS:-1200}"
MODEL="${LOOM_FORGE_MODEL:-loom-deep-30b-unlocked}"
AUTO_STOP="${LOOM_FORGE_AUTO_STOP:-1}"
STATUS_URL="http://127.0.0.1:18080/loom/context-engine/status"
CLIENT_DIR="$ROOT/.loom/runtime/loom-deep/forgeloom-clients"
CLIENT_FILE=""

[[ -f "$CONTEXT_EXTENSION" ]] || { echo "ForgeLoom Context Engine is missing: $CONTEXT_EXTENSION" >&2; exit 1; }
[[ -f "$HARDENING_EXTENSION" ]] || { echo "ForgeLoom runtime hardening extension is missing: $HARDENING_EXTENSION" >&2; exit 1; }
[[ ! -e "$LEGACY_GLOBAL_EXTENSION" ]] || {
  echo "ForgeLoom refused to start: a globally auto-discovered LOOM Context Engine exists at $LEGACY_GLOBAL_EXTENSION" >&2
  echo "Re-run scripts/install-forge-loom.sh to restore Forge/ForgeLoom isolation." >&2
  exit 1
}

case "$SAFE_TOTAL:$SAFE_INPUT:$MIN_OUTPUT:$MAX_OUTPUT:$LEGACY_MARGIN:$HIGH_WATER:$TARGET" in
  *[!0-9:]*|*::*|:*|*:) echo "ForgeLoom token thresholds must be positive integers." >&2; exit 64 ;;
esac
if (( TARGET > HIGH_WATER || HIGH_WATER >= SAFE_INPUT )); then
  echo "ForgeLoom requires TARGET <= HIGH_WATER < SAFE_INPUT." >&2
  exit 64
fi
if (( SAFE_INPUT + MIN_OUTPUT > SAFE_TOTAL || MAX_OUTPUT < MIN_OUTPUT || MAX_OUTPUT >= SAFE_TOTAL || SAFE_TOTAL >= 4096 )); then
  echo "ForgeLoom requires SAFE_INPUT + MIN_OUTPUT <= SAFE_TOTAL < 4096 and MIN_OUTPUT <= MAX_OUTPUT < SAFE_TOTAL." >&2
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

enabled() { [[ ! "${1:-1}" =~ ^(0|false|off|no)$ ]]; }

prune_clients() {
  local file pid
  mkdir -p "$CLIENT_DIR"
  for file in "$CLIENT_DIR"/*; do
    [[ -f "$file" ]] || continue
    pid="$(cat "$file" 2>/dev/null || true)"
    if [[ ! "$pid" =~ ^[0-9]+$ ]] || ! kill -0 "$pid" 2>/dev/null; then
      rm -f "$file"
    fi
  done
}

release_client() {
  local file other=0
  [[ -n "$CLIENT_FILE" ]] && rm -f "$CLIENT_FILE"
  enabled "$AUTO_STOP" || return 0
  prune_clients
  for file in "$CLIENT_DIR"/*; do
    [[ -f "$file" ]] || continue
    other=1
    break
  done
  if (( other == 0 )); then
    "$ROOT/scripts/loom-deep" stop >/dev/null 2>&1 || true
  fi
}

gateway_safe() {
  local status
  status="$(curl -fsS --max-time 2 "$STATUS_URL" 2>/dev/null)" || return 1
  python3 - "$SAFE_TOTAL" "$SAFE_INPUT" "$MIN_OUTPUT" "$MAX_OUTPUT" "$LEGACY_MARGIN" "$status" <<'PY'
import json, sys
safe_total = int(sys.argv[1])
safe_input = int(sys.argv[2])
min_output = int(sys.argv[3])
max_output = int(sys.argv[4])
legacy_margin = int(sys.argv[5])
try:
    data = json.loads(sys.argv[6])
except Exception:
    raise SystemExit(1)
ok = (
    data.get("contextEngineGateway") is True
    and data.get("hardGuardEnabled") is True
    and data.get("guardFailClosed") is True
    and data.get("safeTotalTokens") == safe_total
    and data.get("safeInputTokens") == safe_input
    and data.get("minOutputTokens") == min_output
    and data.get("maxOutputTokens") == max_output
    and data.get("adaptiveOutputBudget") is True
    and data.get("legacyCountMarginTokens") == legacy_margin
    and data.get("physicalContextTokens") == 4096
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
    LOOM_CONTEXT_WEBUI_SAFE_TOTAL_TOKENS="$SAFE_TOTAL" \
    LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS="$SAFE_INPUT" \
    LOOM_CONTEXT_WEBUI_MIN_OUTPUT_TOKENS="$MIN_OUTPUT" \
    LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS="$MAX_OUTPUT" \
    LOOM_CONTEXT_WEBUI_LEGACY_COUNT_MARGIN_TOKENS="$LEGACY_MARGIN" \
    "$ROOT/scripts/loom-deep" start
fi

gateway_safe || { echo "ForgeLoom refused to start: LOOM gateway guard is not in the required safe state." >&2; exit 1; }

if enabled "$AUTO_STOP"; then
  prune_clients
  CLIENT_FILE="$CLIENT_DIR/$$"
  printf '%s\n' "$$" > "$CLIENT_FILE"
  trap release_client EXIT
fi

if enabled "$AUTO_STOP"; then
  set +e
  env \
    FORGE_CONTEXT_INTELLIGENCE=0 \
    LOOM_CONTEXT_ENGINE=1 \
    LOOM_CONTEXT_ACCOUNTING=1 \
    LOOM_CONTEXT_HIGH_WATER_TOKENS="$HIGH_WATER" \
    LOOM_CONTEXT_TARGET_TOKENS="$TARGET" \
    Forge --extension "$CONTEXT_EXTENSION" --extension "$HARDENING_EXTENSION" --model "$MODEL" "$@"
  status=$?
  set -e
  exit "$status"
fi

exec env \
  FORGE_CONTEXT_INTELLIGENCE=0 \
  LOOM_CONTEXT_ENGINE=1 \
  LOOM_CONTEXT_ACCOUNTING=1 \
  LOOM_CONTEXT_HIGH_WATER_TOKENS="$HIGH_WATER" \
  LOOM_CONTEXT_TARGET_TOKENS="$TARGET" \
  Forge --extension "$CONTEXT_EXTENSION" --extension "$HARDENING_EXTENSION" --model "$MODEL" "$@"
BODY
} > "$TEMP"
chmod 755 "$TEMP"
mv -f "$TEMP" "$LAUNCHER"

STOP_TEMP="$(mktemp "$LAUNCHER_DIR/.ForgeLoomStop.XXXXXX")"
{
  cat <<'HEADER'
#!/usr/bin/env bash
# Managed by LOOM Context Engine
set -euo pipefail
HEADER
  printf 'ROOT=%q\n' "$ROOT"
  cat <<'BODY'
rm -rf "$ROOT/.loom/runtime/loom-deep/forgeloom-clients"
exec "$ROOT/scripts/loom-deep" stop
BODY
} > "$STOP_TEMP"
chmod 755 "$STOP_TEMP"
mv -f "$STOP_TEMP" "$STOP_LAUNCHER"

echo "Installed ForgeLoom-only LOOM Context Engine to $TARGET_DIR"
echo "Installed ForgeLoom-only runtime hardening to $HARDENING_TARGET_DIR"
echo "Normal pi/Forge global extension path is clean: $LEGACY_GLOBAL_DIR"
echo "Installed launcher: $LAUNCHER"
echo "Installed emergency stop: $STOP_LAUNCHER"
echo "Pi compatibility accepted: $PI_VERSION"
echo "ForgeLoom envelope: target 1200; high-water 1600; final input <=2800; guaranteed output >=800 when requested; adaptive output up to 1600; total <=3600 < 4096"
echo "ForgeLoom now auto-stops the 30B backend when the last ForgeLoom session exits."
echo "Set LOOM_FORGE_AUTO_STOP=0 only if you intentionally want to keep the backend warm."
echo "Use: ForgeLoom"
echo "Force stop from anywhere: ForgeLoomStop"
