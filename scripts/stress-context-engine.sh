#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-001 STRESS FAIL: $*" >&2; exit 1; }
pass() { echo "CE-001 STRESS PASS: $*"; }
info() { echo "CE-001 STRESS INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run: bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

TURNS="${LOOM_CE001_STRESS_TURNS:-12}"
FILLER_CHARS="${LOOM_CE001_STRESS_FILLER_CHARS:-1200}"
case "$TURNS:$FILLER_CHARS" in
  *[!0-9:]*|*::*|:*|*:) fail "stress turns/filler must be positive integers" ;;
esac
(( TURNS >= 6 )) || fail "stress test requires at least 6 turns"
(( FILLER_CHARS >= 600 )) || fail "stress filler must be at least 600 chars"

LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
STRESS_DIR="$STATE/ce001-stress"
mkdir -p "$STRESS_DIR"
RPC_LOG="$STRESS_DIR/rpc.jsonl"
STDERR_LOG="$STRESS_DIR/stderr.txt"
SUMMARY_JSON="$STRESS_DIR/rpc-summary.json"
: >"$RPC_LOG"
: >"$STDERR_LOG"

before_gateway_lines=0
if [[ -f "$GATEWAY_ACCOUNTING" ]]; then
  before_gateway_lines="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')"
fi
start_epoch="$(python3 - <<'PY'
import time
print(time.time())
PY
)"

info "running $TURNS turns in one ForgeLoom RPC session"
python3 - "$TURNS" "$FILLER_CHARS" "$RPC_LOG" "$STDERR_LOG" "$SUMMARY_JSON" <<'PY'
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

turns = int(sys.argv[1])
filler_chars = int(sys.argv[2])
rpc_log = Path(sys.argv[3])
stderr_log = Path(sys.argv[4])
summary_path = Path(sys.argv[5])

with stderr_log.open("w", encoding="utf-8") as err:
    proc = subprocess.Popen(
        ["ForgeLoom", "--no-session", "--mode", "rpc"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=err,
        text=True,
        bufsize=1,
    )
    assert proc.stdin is not None and proc.stdout is not None

    def send(obj):
        proc.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
        proc.stdin.flush()

    def read_until(predicate, timeout=180):
        deadline = time.monotonic() + timeout
        seen = []
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"ForgeLoom RPC exited early with status {proc.returncode}")
            ready, _, _ = select.select([proc.stdout], [], [], min(1.0, max(0.0, deadline - time.monotonic())))
            if not ready:
                continue
            line = proc.stdout.readline()
            if line == "":
                continue
            with rpc_log.open("a", encoding="utf-8") as log:
                log.write(line)
            stripped = line.strip()
            if not stripped.startswith("{"):
                continue
            try:
                event = json.loads(stripped)
            except Exception:
                continue
            seen.append(event)
            if predicate(event):
                return event, seen
        raise TimeoutError("timed out waiting for ForgeLoom RPC event")

    # Confirm the RPC process is ready enough to answer a state request.
    send({"id":"initial-state","type":"get_state"})
    read_until(lambda e: e.get("type") == "response" and e.get("id") == "initial-state" and e.get("success") is True)

    completed = 0
    total_user_chars = 0
    for turn in range(1, turns + 1):
        marker = f"CE001_STRESS_{turn:02d}"
        unit = f" inert-{turn:02d}-abcdefghijklmnopqrstuvwxyz0123456789"
        filler = (unit * ((filler_chars // len(unit)) + 2))[:filler_chars]
        prompt = (
            f"{marker}. This is inert context-window stress data, not a coding task. "
            f"Do not call tools. Reply with exactly {marker}_OK and nothing else. DATA:{filler}"
        )
        total_user_chars += len(prompt)
        request_id = f"turn-{turn:02d}"
        send({"id":request_id,"type":"prompt","message":prompt})
        read_until(lambda e, rid=request_id: e.get("type") == "response" and e.get("id") == rid and e.get("success") is True)
        read_until(lambda e: e.get("type") == "agent_end")
        completed += 1

    send({"id":"final-state","type":"get_state"})
    state_event, _ = read_until(lambda e: e.get("type") == "response" and e.get("id") == "final-state" and e.get("success") is True)
    state = state_event.get("data") or {}
    summary_path.write_text(json.dumps({
        "turnsRequested": turns,
        "turnsCompleted": completed,
        "totalUserChars": total_user_chars,
        "messageCount": state.get("messageCount"),
        "sessionId": state.get("sessionId"),
        "autoCompactionEnabled": state.get("autoCompactionEnabled"),
    }, indent=2) + "\n", encoding="utf-8")

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
PY
pass "multi-turn RPC session completed"

bash scripts/verify-context-engine.sh
pass "live gateway remained in the CE-001 safe profile"

AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
ENGINE_RUNTIME="${LOOM_CONTEXT_RUNTIME_DIR:-$AGENT_DIR/loom-context-engine}"

python3 - "$GATEWAY_ACCOUNTING" "$before_gateway_lines" "$ENGINE_RUNTIME" "$start_epoch" "$SUMMARY_JSON" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

gateway_path = Path(sys.argv[1])
before_gateway = int(sys.argv[2])
engine_root = Path(sys.argv[3]).expanduser()
start = float(sys.argv[4])
summary = json.loads(Path(sys.argv[5]).read_text())

if summary.get("turnsCompleted") != summary.get("turnsRequested"):
    raise SystemExit("not all RPC stress turns completed")
if not isinstance(summary.get("messageCount"), int) or summary["messageCount"] < summary["turnsCompleted"] * 2:
    raise SystemExit("persistent in-memory transcript did not grow as expected: " + repr(summary))

if not gateway_path.exists():
    raise SystemExit("gateway accounting file missing")
gateway_rows = []
for line in gateway_path.read_text(errors="replace").splitlines()[before_gateway:]:
    try:
        gateway_rows.append(json.loads(line))
    except Exception:
        pass
checked = [r for r in gateway_rows if r.get("guardChecked") is True]
if len(checked) < summary["turnsCompleted"]:
    raise SystemExit(f"expected >= {summary['turnsCompleted']} guarded calls, found {len(checked)}")
if any(r.get("guardBlocked") for r in checked):
    raise SystemExit("hard guard blocked at least one stress request")
max_input = max(int(r.get("finalInputTokens", 0)) for r in checked)
max_total = max(int(r.get("projectedTotalTokens", 0)) for r in checked)
min_headroom_4096 = min(4096 - int(r.get("projectedTotalTokens", 0)) for r in checked)
if max_input > 2800 or max_total > 3600:
    raise SystemExit("stress request exceeded the configured safe envelope")

engine_rows = []
if engine_root.exists():
    for path in engine_root.glob("*/accounting.jsonl"):
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
                    epoch = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except Exception:
                    continue
                if epoch >= start - 1.0:
                    engine_rows.append(row)
        except OSError:
            pass

governors = [r for r in engine_rows if r.get("event") == "context_governor"]
if len(governors) < summary["turnsCompleted"]:
    raise SystemExit(f"expected >= {summary['turnsCompleted']} governor events, found {len(governors)}")
changed = [r for r in governors if r.get("changed") is True]
if not changed:
    raise SystemExit("governor never compacted during stress")
if not any(int(r.get("turnsDropped", 0) or 0) > 0 for r in changed):
    raise SystemExit("governor changed context but never dropped an old turn")
max_raw_estimate = max(int(r.get("beforeTokens", 0) or 0) for r in governors)
max_visible_estimate = max(int(r.get("afterTokens", 0) or 0) for r in governors)
changed_after = [int(r.get("afterTokens", 0) or 0) for r in changed if r.get("reason") != "best-effort-active-turn-too-large"]
if changed_after and max(changed_after) > 1200:
    raise SystemExit("governor failed to return to calibrated target")
if max_raw_estimate <= 4096:
    raise SystemExit(f"raw transcript estimate never exceeded physical ctx: {max_raw_estimate}")
threshold_after = [r for r in engine_rows if r.get("event") == "pi_compaction_after" and r.get("reason") == "threshold"]
overflow = [r for r in engine_rows if r.get("event") in {"pi_compaction_before", "pi_compaction_after"} and r.get("reason") == "overflow"]
if threshold_after:
    raise SystemExit("Pi threshold compaction completed during stress")
if overflow:
    raise SystemExit("Pi overflow compaction occurred during stress")

print("CE-001 multi-turn stress envelope: PASS")
print(f"  RPC turns completed       : {summary['turnsCompleted']}")
print(f"  persistent message count  : {summary['messageCount']}")
print(f"  raw user payload chars    : {summary['totalUserChars']}")
print(f"  max raw history estimate  : {max_raw_estimate}")
print(f"  max visible estimate      : {max_visible_estimate}")
print(f"  governor compactions      : {len(changed)}")
print(f"  max exact final input     : {max_input}")
print(f"  max projected total       : {max_total}")
print(f"  min headroom to 4096      : {min_headroom_4096}")
print("  hard-guard blocks         : 0")
print("  Pi threshold compactions  : 0")
print("  Pi overflow compactions   : 0")
PY
pass "raw session exceeded 4096-equivalent history while every model view stayed safely bounded"

echo "CE-001 STRESS COMPLETE"
echo "rpc log: $RPC_LOG"
echo "stderr : $STDERR_LOG"
echo "summary: $SUMMARY_JSON"
