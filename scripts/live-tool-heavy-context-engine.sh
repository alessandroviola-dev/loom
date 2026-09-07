#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-001 LIVE TOOL FAIL: $*" >&2; exit 1; }
pass() { echo "CE-001 LIVE TOOL PASS: $*"; }
info() { echo "CE-001 LIVE TOOL INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run: bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"

INSTALLED_CORE="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/extensions/loom-context-engine/core.mjs"
[[ -f "$INSTALLED_CORE" ]] || fail "installed Context Engine core missing; run installer"
cmp -s src/loom-context-engine/core.mjs "$INSTALLED_CORE" || fail "installed Context Engine is stale; run: bash scripts/install-forge-loom.sh"

LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
RUN_DIR="$STATE/ce001-live-tool-heavy/$(date +%Y%m%d-%H%M%S)"
WORKSPACE="$RUN_DIR/workspace"
RPC_LOG="$RUN_DIR/rpc.jsonl"
STDERR_LOG="$RUN_DIR/stderr.txt"
META_JSON="$RUN_DIR/meta.json"
mkdir -p "$WORKSPACE"
: >"$RPC_LOG"
: >"$STDERR_LOG"

python3 - "$WORKSPACE" <<'PY'
import sys
from pathlib import Path
root = Path(sys.argv[1])
for name, tag in [("alpha.txt", "ALPHA"), ("beta.txt", "BETA"), ("gamma.txt", "GAMMA"), ("delta.txt", "DELTA")]:
    lines = []
    for i in range(1, 91):
        lines.append(f"{tag} line {i:03d} payload abcdefghijklmnopqrstuvwxyz0123456789 marker-{tag}-{i:03d}")
    (root / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
(root / "task.txt").write_text("status=CE001_OLD\nvalidation=tool-heavy-live-regression\n", encoding="utf-8")
PY

info "warming ForgeLoom gateway without inference"
ForgeLoom --help >/dev/null 2>"$RUN_DIR/warm.stderr" || fail "ForgeLoom warm-up failed"
bash scripts/verify-context-engine.sh
pass "live gateway is warm and in the CE-001 safe profile"

before_gateway_lines=0
if [[ -f "$GATEWAY_ACCOUNTING" ]]; then
  before_gateway_lines="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')"
fi
start_epoch="$(python3 - <<'PY'
import time
print(time.time())
PY
)"

info "running one isolated tool-heavy ForgeLoom turn"
python3 - "$WORKSPACE" "$RPC_LOG" "$STDERR_LOG" "$META_JSON" <<'PY'
import json
import select
import subprocess
import sys
import time
from pathlib import Path

workspace = Path(sys.argv[1])
rpc_log = Path(sys.argv[2])
stderr_log = Path(sys.argv[3])
meta_path = Path(sys.argv[4])

prompt = """CE-001 live tool-heavy regression. Follow these steps using tools and do not answer before completing them:
1. Read alpha.txt.
2. Read beta.txt.
3. Read gamma.txt.
4. Read delta.txt.
5. Read task.txt.
6. Use edit (not bash and not write) to replace CE001_OLD with CE001_NEW in task.txt.
7. Use bash exactly for verification: grep -n 'CE001_NEW' task.txt && wc -c alpha.txt beta.txt gamma.txt delta.txt task.txt
8. Read task.txt again and verify the new marker is present.
Do not use bash to read or modify the four payload files. Do not modify alpha.txt, beta.txt, gamma.txt, or delta.txt. When all steps succeed, reply with exactly CE001_TOOL_HEAVY_OK and nothing else."""

with stderr_log.open("w", encoding="utf-8") as err:
    proc = subprocess.Popen(
        ["ForgeLoom", "--no-session", "--mode", "rpc"],
        cwd=workspace,
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

    def read_until(predicate, timeout):
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

    send({"id":"initial-state","type":"get_state"})
    state_event, _ = read_until(
        lambda e: e.get("type") == "response" and e.get("id") == "initial-state" and e.get("success") is True,
        180,
    )
    state = state_event.get("data") or {}
    session_id = state.get("sessionId")
    if not isinstance(session_id, str) or not session_id:
        raise RuntimeError(f"RPC state did not expose sessionId: {state!r}")

    send({"id":"tool-heavy","type":"prompt","message":prompt})
    read_until(
        lambda e: e.get("type") == "response" and e.get("id") == "tool-heavy" and e.get("success") is True,
        180,
    )
    _, events = read_until(lambda e: e.get("type") == "agent_end", 1200)

    meta_path.write_text(json.dumps({"sessionId": session_id, "agentEndObserved": True}, indent=2) + "\n", encoding="utf-8")

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
PY
pass "tool-heavy ForgeLoom turn completed"

[[ "$(cat "$WORKSPACE/task.txt")" == *"CE001_NEW"* ]] || fail "task.txt was not edited to CE001_NEW"
for f in alpha.txt beta.txt gamma.txt delta.txt; do
  [[ -f "$WORKSPACE/$f" ]] || fail "$f missing after run"
done

grep -q 'CE001_TOOL_HEAVY_OK' "$RPC_LOG" || fail "model did not return CE001_TOOL_HEAVY_OK marker"

bash scripts/verify-context-engine.sh
pass "live gateway remained in the CE-001 safe profile"

python3 - "$GATEWAY_ACCOUNTING" "$before_gateway_lines" "$META_JSON" "$start_epoch" "$RPC_LOG" <<'PY'
import json
import sys
from pathlib import Path

gateway_path = Path(sys.argv[1])
before_gateway = int(sys.argv[2])
meta = json.loads(Path(sys.argv[3]).read_text())
start = float(sys.argv[4])
rpc_path = Path(sys.argv[5])
session_id = meta["sessionId"]
agent_dir = Path.home() / ".pi" / "agent"
engine_root = Path(__import__("os").environ.get("LOOM_CONTEXT_RUNTIME_DIR", str(agent_dir / "loom-context-engine"))).expanduser()
engine_path = engine_root / session_id.replace("/", "_").replace("\\", "_") / "accounting.jsonl"

if not gateway_path.exists():
    raise SystemExit("gateway accounting file missing")
gateway_rows = []
for line in gateway_path.read_text(errors="replace").splitlines()[before_gateway:]:
    try:
        row = json.loads(line)
    except Exception:
        continue
    if row.get("path") in {"/v1/chat/completions", "/chat/completions"}:
        gateway_rows.append(row)
if not gateway_rows:
    raise SystemExit("no live chat gateway accounting rows found")
blocks = [r for r in gateway_rows if r.get("guardBlocked") is True or r.get("event") in {"hard_guard_block", "hard_guard_unavailable"}]
if blocks:
    raise SystemExit("live tool-heavy run hit hard guard: " + json.dumps(blocks, separators=(",", ":")))
guards = [r for r in gateway_rows if r.get("guardChecked") is True]
if len(guards) != len(gateway_rows):
    raise SystemExit(f"not every live provider attempt was guard-checked: {len(guards)}/{len(gateway_rows)}")
max_input = max(int(r.get("finalInputTokens", 0) or 0) for r in guards)
max_total = max(int(r.get("projectedTotalTokens", 0) or 0) for r in guards)
min_headroom = min(4096 - int(r.get("projectedTotalTokens", 0) or 0) for r in guards)
if max_input > 2800 or max_total > 3600:
    raise SystemExit("live tool-heavy request exceeded CE-001 safe envelope")

if not engine_path.exists():
    raise SystemExit(f"session accounting missing: {engine_path}")
engine_rows = []
for line in engine_path.read_text(errors="replace").splitlines():
    try:
        engine_rows.append(json.loads(line))
    except Exception:
        pass
governors = [r for r in engine_rows if r.get("event") == "context_governor"]
if len(governors) < 2:
    raise SystemExit(f"expected multiple provider attempts, found {len(governors)} governor events")
changed = [r for r in governors if r.get("changed") is True]
if not changed:
    raise SystemExit("tool-heavy run never exercised governor reduction")
changed_over_target = [r for r in changed if int(r.get("afterTokens", 0) or 0) > 1200]
if changed_over_target:
    raise SystemExit("updated governor missed 1200 target live: " + json.dumps(changed_over_target, separators=(",", ":")))
if any(r.get("reason") == "best-effort-active-turn-too-large" for r in governors):
    raise SystemExit("live run still produced best-effort-active-turn-too-large")

active_turn_activity = [
    r for r in changed
    if int(r.get("toolResultsCompacted", 0) or 0) > 0
    or int(r.get("toolCallArgumentsCompacted", 0) or 0) > 0
    or int(r.get("activeTurnEmergencyPasses", 0) or 0) > 0
    or int(r.get("activeTurnToolExchangesDropped", 0) or 0) > 0
]
if not active_turn_activity:
    raise SystemExit("live run compacted context but did not exercise active-turn tool-history logic")

pi_after = [r for r in engine_rows if r.get("event") == "pi_compaction_after"]
pi_overflow = [r for r in engine_rows if r.get("event") in {"pi_compaction_before", "pi_compaction_after"} and r.get("reason") == "overflow"]
if pi_after:
    raise SystemExit(f"Pi actual compaction occurred: {pi_after!r}")
if pi_overflow:
    raise SystemExit(f"Pi overflow activity occurred: {pi_overflow!r}")

max_raw = max(int(r.get("beforeTokens", 0) or 0) for r in governors)
max_visible = max(int(r.get("afterTokens", 0) or 0) for r in governors)
arg_compactions = sum(int(r.get("toolCallArgumentsCompacted", 0) or 0) for r in changed)
exchanges_dropped = sum(int(r.get("activeTurnToolExchangesDropped", 0) or 0) for r in changed)
emergency_passes = sum(int(r.get("activeTurnEmergencyPasses", 0) or 0) for r in changed)

print("CE-001 live tool-heavy regression envelope: PASS")
print(f"  provider attempts             : {len(governors)}")
print(f"  governor reductions           : {len(changed)}")
print(f"  max raw estimate              : {max_raw}")
print(f"  max visible estimate          : {max_visible}")
print(f"  tool-arg compactions          : {arg_compactions}")
print(f"  emergency passes              : {emergency_passes}")
print(f"  active tool exchanges dropped : {exchanges_dropped}")
print(f"  max exact final input         : {max_input}")
print(f"  max projected total           : {max_total}")
print(f"  min headroom to 4096          : {min_headroom}")
print("  hard-guard blocks             : 0")
print("  Pi actual compactions         : 0")
print("  Pi overflow events            : 0")
PY

pass "active-turn tool-history fix held under a real ForgeLoom tool chain"
echo "CE-001 LIVE TOOL COMPLETE"
echo "run dir: $RUN_DIR"
echo "rpc log: $RPC_LOG"
echo "stderr : $STDERR_LOG"
