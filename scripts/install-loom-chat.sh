#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
LAUNCHER_DIR="$HOME/.local/bin"
START="$LAUNCHER_DIR/LoomChat"
STOP="$LAUNCHER_DIR/LoomChatStop"

command -v node >/dev/null 2>&1 || { echo "LoomChat requires node." >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "LoomChat requires curl." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "LoomChat requires python3." >&2; exit 1; }
[[ -f "$ROOT/scripts/loom-chat" ]] || { echo "Missing scripts/loom-chat" >&2; exit 1; }
[[ -f "$ROOT/scripts/loom-chat-proxy.mjs" ]] || { echo "Missing scripts/loom-chat-proxy.mjs" >&2; exit 1; }
[[ -f "$ROOT/src/loom-chat-continuity/core.mjs" ]] || { echo "Missing LoomChat continuity core" >&2; exit 1; }

mkdir -p "$LAUNCHER_DIR"
chmod 755 "$ROOT/scripts/loom-chat"

write_launcher() {
  local path="$1" action="$2" temp
  if [[ -e "$path" ]] && ! grep -Fqx '# Managed by LOOM Chat Continuity' "$path" 2>/dev/null; then
    echo "Refusing to overwrite non-LOOM launcher: $path" >&2
    exit 1
  fi
  temp="$(mktemp "$LAUNCHER_DIR/.loom-chat-launcher.XXXXXX")"
  {
    echo '#!/usr/bin/env bash'
    echo '# Managed by LOOM Chat Continuity'
    echo 'set -euo pipefail'
    printf 'ROOT=%q\n' "$ROOT"
    printf 'exec "$ROOT/scripts/loom-chat" %q "$@"\n' "$action"
  } > "$temp"
  chmod 755 "$temp"
  mv -f "$temp" "$path"
}

write_launcher "$START" start
write_launcher "$STOP" stop

echo "Installed: $START"
echo "Installed: $STOP"
echo "Use: LoomChat"
echo "Stop: LoomChatStop"
