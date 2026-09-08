#!/usr/bin/env bash
set -euo pipefail

SUPPORTED_PI_VERSIONS="0.84.4 0.85.1"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$ROOT/src/loom-context-engine"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
EXTENSIONS_DIR="$AGENT_DIR/extensions"
LEGACY_GLOBAL_DIR="$EXTENSIONS_DIR/loom-context-engine"
FORGE_LOOM_DIR="$AGENT_DIR/forge-loom"
TARGET_DIR="$FORGE_LOOM_DIR/loom-context-engine"
BACKUP_DIR="$AGENT_DIR/loom-context-engine-backups"
LAUNCHER_DIR="$HOME/.local/bin"
LAUNCHER="$LAUNCHER_DIR/ForgeLoom"

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
  echo "Backed up existing LOOM Context Engine to $backup_path"
}

command -v pi >/dev/null 2>&1 || fail "ForgeLoom requires pi on PATH."
command -v Forge >/dev/null 2>&1 || fail "ForgeLoom requires Forge to be installed first."
command -v curl >/dev/null 2>&1 || fail "ForgeLoom requires curl."
command -v python3 >/dev/null 2>&1 || fail "ForgeLoom requires python3."
PI_VERSION="$(pi --version 2>/dev/null | tr -d '[:space:]')"
pi_version_supported "$PI_VERSION" || fail "CE-001 supports Pi versions: $SUPPORTED_PI_VERSIONS; found ${PI_VERSION:-unknown}."
[ -f "$SOURCE_DIR/index.ts" ] || fail "Missing Context Engine source: $SOURCE_DIR/index.ts"
[ -f "$SOURCE_DIR/core.mjs" ] || fail "Missing Context Engine source: $SOURCE_DIR/core.mjs"
[ -f "$ROOT/scripts/loom-deep" ] || fail "Missing LOOM lifecycle manager: $ROOT/scripts/loom-deep"

# CE must never live in Pi's global auto-discovery directory. Normal `pi` and
# normal `Forge` must not load it at all; only the ForgeLoom launcher supplies
# the private extension path explicitly with --extension.
mkdir -p "$FORGE_LOOM_DIR" "$LAUNCHER_DIR"
case "$TARGET_DIR/" in
  "$EXTENSIONS_DIR/"*) fail "Refusing to install ForgeLoom Context Engine under Pi's global extensions directory." ;;
esac

if [ -e "$LAUNCHER" ] || [ -L "$LAUNCHER" ]; then
  is_managed_launcher "$LAUNCHER" || fail "Refusing to overwrite non-LOOM launcher: $LAUNCHER"
fi

# Migrate installations made by older CE-001/CE-002 installers out of the
# globally auto-discovered path, then replace the private ForgeLoom copy.
backup_existing_dir "$LEGACY_GLOBAL_DIR" "loom-context-engine-global"
backup_existing_dir "$TARGET_DIR" "loom-context-engine-forgeloom"

cp -R "$SOURCE_DIR" "$TARGET_DIR"
find "$TARGET_DIR" -type l -print -quit | grep -q . && { rm -rf "$TARGET_DIR"; fail "Installation rejected symlinked Context Engine content."; }
[ ! -e "$LEGACY_GLOBAL_DIR" ] && [ ! -L "$LEGACY_GLOBAL_DIR" ] || fail "Global LOOM Context Engine still exists after migration: $LEGACY_GLOBAL_DIR"

# Validate that the installed Pi accepts explicit extension loading without
# running a model request. Forge is expected to pass Pi CLI arguments through.
pi --extension "$TARGET_DIR/index.ts" --help >/dev/null 2>&1 || fail "Pi rejected ForgeLoom's explicit Context Engine extension path."
Forge --extension "$TARGET_DIR/index.ts" --help >/dev/null 2>&1 || fail "Forge does not pass the explicit Context Engine extension path through to Pi."

TEMP="$(mktemp "$LAUNCHER_DIR/.ForgeLoom.XXXXXX")"
{
  cat <<'HEADER'
#!/usr/bin/env bash
# Managed by LOOM Context Engine
set -euo pipefail
HEADER
  printf 'ROOT=%q\n' "$ROOT"
  printf 'CONTEXT_EXTENSION=%q\n' "$TARGET_DIR/index.ts"
  printf 'LEGACY_GLOBAL_EXTENSION=%q\n' "$LEGACY_GLOBAL_DIR"
  cat <<'BODY'
SAFE_TOTAL="${LOOM_CONTEXT_WEBUI_SAFE_TOTAL_TOKENS:-3600}"
SAFE_INPUT="${LOOM_CONTEXT_WEBUI_SAFE_INPUT_TOKENS:-2800}"
MAX_OUTPUT="${LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS:-800}"
LEGACY_MARGIN="${LOOM_CONTEXT_WEBUI_LEGACY_COUNT_MARGIN_TOKENS:-32}"
HIGH_WATER="${LOOM_CONTEXT_HIGH_WATER_TOKENS:-1600}"
TARGET="${LOOM_CONTEXT_TARGET_TOKENS:-1200}"
MODEL="${LOOM_FORGE_MODEL:-loom-deep-30b-unlocked}"
STATUS_URL="http://127.0.0.1:18080/loom/context-engine/status"

[[ -f "$CONTEXT_EXTENSION" ]] || { echo "ForgeLoom Context Engine is missing: $CONTEXT_EXTENSION" >&2; exit 1; }
[[ ! -e "$LEGACY_GLOBAL_EXTENSION" ]] || {
  echo "ForgeLoom refused to start: a globally auto-discovered LOOM Context Engine exists at $LEGACY_GLOBAL_EXTENSION" >&2
  echo "Re-run scripts/install-forge-loom.sh to restore Forge/ForgeLoom isolation." >&2
  exit 1
}

case "$SAFE_TOTAL:$SAFE_INPUT:$MAX_OUTPUT:$LEGACY_MARGIN:$HIGH_WATER:$TARGET" in
  *[!0-9:]*|*::*|:*|*:) echo "ForgeLoom token thresholds must be positive integers." >&2; exit 64 ;;
esac
if (( TARGET > HIGH_WATER || HIGH_WATER >= SAFE_INPUT )); then
  echo "ForgeLoom requires TARGET <= HIGH_WATER < SAFE_INPUT." >&2
  exit 64
fi
if (( SAFE_INPUT + MAX_OUTPUT > SAFE_TOTAL || SAFE_TOTAL >= 4096 )); then
  echo "ForgeLoom requires SAFE_INPUT + MAX_OUTPUT <= SAFE_TOTAL < 4096." >&2
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
  python3 - "$SAFE_TOTAL" "$SAFE_INPUT" "$MAX_OUTPUT" "$LEGACY_MARGIN" "$status" <<'PY'
import json, sys
safe_total = int(sys.argv[1])
safe_input = int(sys.argv[2])
max_output = int(sys.argv[3])
legacy_margin = int(sys.argv[4])
try:
    data = json.loads(sys.argv[5])
except Exception:
    raise SystemExit(1)
ok = (
    data.get("contextEngineGateway") is True
    and data.get("hardGuardEnabled") is True
    and data.get("guardFailClosed") is True
    and data.get("safeTotalTokens") == safe_total
    and data.get("safeInputTokens") == safe_input
    and data.get("maxOutputTokens") == max_output
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
    LOOM_CONTEXT_WEBUI_MAX_OUTPUT_TOKENS="$MAX_OUTPUT" \
    LOOM_CONTEXT_WEBUI_LEGACY_COUNT_MARGIN_TOKENS="$LEGACY_MARGIN" \
    "$ROOT/scripts/loom-deep" start
fi

gateway_safe || { echo "ForgeLoom refused to start: LOOM gateway guard is not in the required safe state." >&2; exit 1; }

exec env \
  FORGE_CONTEXT_INTELLIGENCE=0 \
  LOOM_CONTEXT_ENGINE=1 \
  LOOM_CONTEXT_ACCOUNTING=1 \
  LOOM_CONTEXT_HIGH_WATER_TOKENS="$HIGH_WATER" \
  LOOM_CONTEXT_TARGET_TOKENS="$TARGET" \
  Forge --extension "$CONTEXT_EXTENSION" --model "$MODEL" "$@"
BODY
} > "$TEMP"
chmod 755 "$TEMP"
mv -f "$TEMP" "$LAUNCHER"

echo "Installed ForgeLoom-only LOOM Context Engine to $TARGET_DIR"
echo "Normal pi/Forge global extension path is clean: $LEGACY_GLOBAL_DIR"
echo "Installed launcher: $LAUNCHER"
echo "Pi compatibility accepted: $PI_VERSION"
echo "Default CE-001 envelope: target 1200; high-water 1600; final input <=2800; output <=800; total <=3600 < 4096"
echo "Legacy llama.cpp counting fallback margin: 32 tokens"
echo "Use: ForgeLoom"
