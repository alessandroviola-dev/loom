#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-002 RETRIEVAL FAIL: $*" >&2; exit 1; }
pass() { echo "CE-002 RETRIEVAL PASS: $*"; }
info() { echo "CE-002 RETRIEVAL INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
command -v node >/dev/null 2>&1 || fail "node not found"

LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$STATE/ce002-live-retrieval/$STAMP"
ENGINE_RUNTIME="$RUN_DIR/engine-runtime"
RPC_LOG="$RUN_DIR/rpc.jsonl"
STDERR_LOG="$RUN_DIR/stderr.txt"
SUMMARY_JSON="$RUN_DIR/summary.json"
mkdir -p "$RUN_DIR" "$ENGINE_RUNTIME"
: >"$RPC_LOG"
: >"$STDERR_LOG"

before_gateway_lines=0
if [[ -f "$GATEWAY_ACCOUNTING" ]]; then
  before_gateway_lines="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')"
fi

info "warming ForgeLoom gateway without inference"
ForgeLoom --help >/dev/null 2>&1 || fail "ForgeLoom preflight/start failed"
bash scripts/verify-context-engine.sh
pass "live gateway is warm and in the frozen CE-001 safe profile"

info "running three setup turns plus one archive-recall turn"
LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" python3 - "$RPC_LOG" "$STDERR_LOG" "$SUMMARY_JSON" <<'PY'
import json
import select
import subprocess
import sys
import time
from pathlib import Path

rpc_log = Path(sys.argv[1])
stderr_log = Path(sys.argv[2])
summary_path = Path(sys.argv[3])

KEY = "CE002_REUSE_KEY_314159"
SECRET = "ORCHID_7391"
filler = (" alpha beta gamma delta epsilon zeta eta theta kappa lambda memory archive context evidence" * 24)[:1780]
prompts = [
    f"Historical validation datum: key {KEY} has exact secret {SECRET}. Keep no special state; reply only ACKALPHA.{filler}",
    f"This is ordinary context-filling prose with no identifiers. Reply only ACKBETA.{filler}",
    f"This is another ordinary context-filling message with no identifiers. Reply only ACKGAMMA.{filler}",
    f"Using historical evidence for {KEY}, reply with only the exact secret associated with that key. Do not guess and do not add commentary.",
]

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

    def next_event(timeout_deadline):
        while time.monotonic() < timeout_deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"ForgeLoom RPC exited early with status {proc.returncode}")
            ready, _, _ = select.select([proc.stdout], [], [], min(1.0, max(0.0, timeout_deadline - time.monotonic())))
            if not ready:
                continue
            line = proc.stdout.readline()
            if not line:
                continue
            with rpc_log.open("a", encoding="utf-8") as log:
                log.write(line)
            stripped = line.strip()
            if not stripped.startswith("{"):
                continue
            try:
                return json.loads(stripped)
            except Exception:
                continue
        raise TimeoutError("timed out waiting for ForgeLoom RPC event")

    def wait_response(request_id, timeout=240):
        deadline = time.monotonic() + timeout
        while True:
            event = next_event(deadline)
            if event.get("type") == "response" and event.get("id") == request_id:
                if event.get("success") is not True:
                    raise RuntimeError(f"RPC request failed: {event}")
                return

    def assistant_text(message):
        if not isinstance(message, dict) or message.get("role") != "assistant":
            return ""
        content = message.get("content")
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "\n".join(parts)

    def wait_agent_end(timeout=240):
        deadline = time.monotonic() + timeout
        texts = []
        while True:
            event = next_event(deadline)
            if event.get("type") in {"message_end", "message_update", "message_start"}:
                text = assistant_text(event.get("message"))
                if text:
                    texts.append(text)
            if event.get("type") == "agent_end":
                return "\n".join(texts)

    send({"id":"initial-state","type":"get_state"})
    wait_response("initial-state")

    final_text = ""
    for turn, prompt in enumerate(prompts, start=1):
        request_id = f"turn-{turn}"
        send({"id":request_id,"type":"prompt","message":prompt})
        wait_response(request_id)
        text = wait_agent_end()
        if turn == len(prompts):
            final_text = text
        print(f"CE-002 RETRIEVAL INFO: turn {turn} completed", flush=True)

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)

if SECRET not in final_text:
    raise SystemExit(f"final assistant response did not recover expected secret {SECRET!r}: {final_text[-1000:]!r}")

summary_path.write_text(json.dumps({
    "key": KEY,
    "expectedSecret": SECRET,
    "finalAssistantText": final_text,
}, indent=2) + "\n", encoding="utf-8")
print("CE-002 model archive recall: PASS")
print(f"  key                      : {KEY}")
print(f"  recovered secret         : {SECRET}")
PY
pass "model answered from old evidence without a fifth tool"

bash scripts/verify-context-engine.sh
pass "CE-001 gateway envelope remained valid"

python3 - "$GATEWAY_ACCOUNTING" "$before_gateway_lines" "$ENGINE_RUNTIME" "$SUMMARY_JSON" <<'PY'
import json
import sys
from pathlib import Path

gateway_path = Path(sys.argv[1])
before_gateway = int(sys.argv[2])
engine_root = Path(sys.argv[3])
summary = json.loads(Path(sys.argv[4]).read_text())

if not gateway_path.exists():
    raise SystemExit("gateway accounting missing")
gateway_rows = []
for line in gateway_path.read_text(errors="replace").splitlines()[before_gateway:]:
    try:
        gateway_rows.append(json.loads(line))
    except Exception:
        pass
checked = [row for row in gateway_rows if row.get("guardChecked") is True]
if len(checked) < 4:
    raise SystemExit(f"expected >=4 guarded provider calls, found {len(checked)}")
if any(row.get("guardBlocked") for row in checked):
    raise SystemExit("hard guard blocked at least one CE-002 retrieval request")
max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in checked)
max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in checked)
if max_input > 2800 or max_total > 3600:
    raise SystemExit("CE-001 safe envelope exceeded during CE-002 retrieval run")

accounting = []
for path in engine_root.glob("*/accounting.jsonl"):
    for line in path.read_text(errors="replace").splitlines():
        try:
            accounting.append(json.loads(line))
        except Exception:
            pass
archive_errors = [row for row in accounting if row.get("event") == "evidence_archive_error"]
retrieval_errors = [row for row in accounting if row.get("event") == "evidence_retrieval_error"]
if archive_errors or retrieval_errors:
    raise SystemExit(f"CE-002 archive/retrieval errors occurred: archive={archive_errors!r} retrieval={retrieval_errors!r}")

governors = [row for row in accounting if row.get("event") == "context_governor"]
retrievals = [row for row in accounting if row.get("event") == "evidence_retrieval" and row.get("applied") is True]
if not retrievals:
    raise SystemExit("no CE-002 evidence retrieval was applied")
last = retrievals[-1]
if int(last.get("lexicalCount", 0) or 0) < 1:
    raise SystemExit(f"final retrieval was not lexical: {last!r}")
if int(last.get("finalVisibleTokens", 999999) or 999999) > 1200:
    raise SystemExit(f"retrieval pushed visible context above target: {last!r}")
if not any(int(row.get("evidenceSessionRefsCreated", 0) or 0) > 0 for row in governors):
    raise SystemExit("setup evidence was never archived")

threshold = [row for row in accounting if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
overflow = [row for row in accounting if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"]
if threshold or overflow:
    raise SystemExit("Pi compaction/overflow occurred during CE-002 retrieval run")

print("CE-002 retrieval safety/accounting: PASS")
print(f"  provider calls guarded    : {len(checked)}")
print(f"  retrieval applications    : {len(retrievals)}")
print(f"  final lexical evidence    : {last.get('evidenceIds')}")
print(f"  retrieval chars           : {last.get('chars')}")
print(f"  retrieval visible tokens  : {last.get('finalVisibleTokens')}")
print(f"  max exact final input     : {max_input}")
print(f"  max projected total       : {max_total}")
print("  hard-guard blocks         : 0")
print("  Pi threshold compactions  : 0")
print("  Pi overflow events        : 0")
PY

LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" node scripts/loom-context-evidence.mjs verify > "$RUN_DIR/verify.json"
pass "archive integrity verification passed after retrieval"

echo "CE-002 LIVE RETRIEVAL COMPLETE"
echo "run dir : $RUN_DIR"
echo "rpc log : $RPC_LOG"
echo "stderr  : $STDERR_LOG"
echo "summary : $SUMMARY_JSON"
echo "verify  : $RUN_DIR/verify.json"
