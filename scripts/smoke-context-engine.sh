#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-001 SMOKE FAIL: $*" >&2; exit 1; }
pass() { echo "CE-001 SMOKE PASS: $*"; }
info() { echo "CE-001 SMOKE INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run: bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
SMOKE_DIR="$STATE/ce001-smoke"
mkdir -p "$SMOKE_DIR"
OUTPUT="$SMOKE_DIR/output.txt"
STDERR="$SMOKE_DIR/stderr.txt"

before_lines=0
if [[ -f "$GATEWAY_ACCOUNTING" ]]; then
  before_lines="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')"
fi
start_epoch="$(python3 - <<'PY'
import time
print(time.time())
PY
)"

prompt="${LOOM_CE001_SMOKE_PROMPT:-Reply with exactly CE001_SMOKE_OK and nothing else.}"
info "running one local ForgeLoom inference"
set +e
ForgeLoom --no-session -p "$prompt" >"$OUTPUT" 2>"$STDERR"
status=$?
set -e
if (( status != 0 )); then
  echo "--- ForgeLoom stderr ---" >&2
  tail -80 "$STDERR" >&2 || true
  echo "--- ForgeLoom stdout ---" >&2
  tail -80 "$OUTPUT" >&2 || true
  fail "ForgeLoom exited with status $status"
fi
pass "ForgeLoom one-shot request completed"

# Give append-only accounting a moment to flush after the client exits.
for _ in 1 2 3 4 5; do
  [[ -f "$GATEWAY_ACCOUNTING" ]] && current="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')" && (( current > before_lines )) && break
  sleep 0.2
done
[[ -f "$GATEWAY_ACCOUNTING" ]] || fail "gateway accounting file not found: $GATEWAY_ACCOUNTING"

python3 - "$GATEWAY_ACCOUNTING" "$before_lines" <<'PY'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
before = int(sys.argv[2])
lines = path.read_text(errors="replace").splitlines()[before:]
rows = []
for line in lines:
    try:
        rows.append(json.loads(line))
    except Exception:
        pass
checked = [r for r in rows if r.get("guardChecked") is True]
if not checked:
    raise SystemExit("no exact gateway guard accounting row was produced")
row = checked[-1]
if row.get("guardBlocked"):
    raise SystemExit("gateway blocked smoke request: " + repr(row))
required = ["finalInputTokens", "outputReserve", "projectedTotalTokens", "requestInputCeiling", "safeTotalTokens"]
missing = [k for k in required if not isinstance(row.get(k), int)]
if missing:
    raise SystemExit("missing numeric guard fields: " + ", ".join(missing))
if row["finalInputTokens"] > row["requestInputCeiling"]:
    raise SystemExit("input exceeded request ceiling")
if row["projectedTotalTokens"] > row["safeTotalTokens"]:
    raise SystemExit("projected total exceeded safe total")
print("CE-001 exact gateway envelope: PASS")
print(f"  final input       : {row['finalInputTokens']}")
print(f"  input ceiling     : {row['requestInputCeiling']}")
print(f"  output reserve    : {row['outputReserve']}")
print(f"  projected total   : {row['projectedTotalTokens']}")
print(f"  safe total        : {row['safeTotalTokens']}")
print(f"  headroom to safe  : {row['safeTotalTokens'] - row['projectedTotalTokens']}")
print(f"  headroom to 4096  : {4096 - row['projectedTotalTokens']}")
print(f"  gateway prep ms   : {row.get('gatewayPreparationMs', 'n/a')}")
PY
pass "exact final request stayed inside the safe envelope"

AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
ENGINE_RUNTIME="${LOOM_CONTEXT_RUNTIME_DIR:-$AGENT_DIR/loom-context-engine}"
python3 - "$ENGINE_RUNTIME" "$start_epoch" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1]).expanduser()
start = float(sys.argv[2])
rows = []
if root.exists():
    for path in root.glob("*/accounting.jsonl"):
        try:
            for line in path.read_text(errors="replace").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                ts = row.get("timestamp")
                if not isinstance(ts, str):
                    continue
                try:
                    from datetime import datetime
                    epoch = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except Exception:
                    continue
                if epoch >= start - 1.0:
                    rows.append(row)
        except OSError:
            pass

events = {r.get("event") for r in rows}
required = {"session_start", "system_prompt_minimized", "context_governor"}
missing = sorted(required - events)
if missing:
    raise SystemExit("missing Context Engine runtime events: " + ", ".join(missing))
threshold_after = [r for r in rows if r.get("event") == "pi_compaction_after" and r.get("reason") == "threshold"]
overflow = [r for r in rows if r.get("event") in {"pi_compaction_before", "pi_compaction_after"} and r.get("reason") == "overflow"]
if threshold_after:
    raise SystemExit("Pi threshold compaction completed during smoke")
if overflow:
    raise SystemExit("Pi overflow compaction occurred during smoke")
governors = [r for r in rows if r.get("event") == "context_governor"]
latest = governors[-1]
print("CE-001 Pi extension events: PASS")
print(f"  governor estimated before: {latest.get('beforeTokens', 'n/a')}")
print(f"  governor estimated after : {latest.get('afterTokens', 'n/a')}")
print(f"  governor changed         : {latest.get('changed', 'n/a')}")
print(f"  turns dropped            : {latest.get('turnsDropped', 'n/a')}")
print(f"  Pi threshold compactions : 0")
print(f"  Pi overflow compactions  : 0")
PY
pass "Context Engine extension hooks observed"

if grep -Fq "CE001_SMOKE_OK" "$OUTPUT"; then
  pass "model returned smoke marker"
else
  info "model output did not contain CE001_SMOKE_OK; infrastructure still passed. Output saved at $OUTPUT"
fi

echo "CE-001 SMOKE COMPLETE"
echo "output: $OUTPUT"
echo "stderr: $STDERR"
