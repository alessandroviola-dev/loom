#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-002 CODING RETRIEVAL FAIL: $*" >&2; exit 1; }
pass() { echo "CE-002 CODING RETRIEVAL PASS: $*"; }
info() { echo "CE-002 CODING RETRIEVAL INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
command -v node >/dev/null 2>&1 || fail "node not found"

LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$STATE/ce002-live-coding-retrieval/$STAMP"
ENGINE_RUNTIME="$RUN_DIR/engine-runtime"
WORKSPACE="$RUN_DIR/workspace"
RPC_LOG="$RUN_DIR/rpc.jsonl"
STDERR_LOG="$RUN_DIR/stderr.txt"
SUMMARY_JSON="$RUN_DIR/summary.json"
mkdir -p "$WORKSPACE/src" "$ENGINE_RUNTIME"
: >"$RPC_LOG"
: >"$STDERR_LOG"

cat > "$WORKSPACE/src/retry_policy.py" <<'PY'
"""Retry policy supplied by an external service contract."""


def retry_delay(attempt: int) -> int:
    """Return the configured delay for supported attempts 1 through 4."""
    if attempt < 1 or attempt > 4:
        raise ValueError("attempt must be between 1 and 4")
    # Placeholder is intentionally wrong; exact contract values come from CI evidence.
    return 1
PY

cat > "$WORKSPACE/README.md" <<'MD'
# CE-002 isolated coding retrieval fixture

`src/retry_policy.py` implements a small external retry contract. The exact delay values are not stored in this workspace; they are supplied by an earlier external CI diagnostic in the agent session.
MD

before_gateway_lines=0
if [[ -f "$GATEWAY_ACCOUNTING" ]]; then
  before_gateway_lines="$(wc -l < "$GATEWAY_ACCOUNTING" | tr -d '[:space:]')"
fi

info "warming ForgeLoom gateway without inference"
ForgeLoom --help >/dev/null 2>&1 || fail "ForgeLoom preflight/start failed"
bash scripts/verify-context-engine.sh
pass "live gateway is warm and in the frozen CE-001 safe profile"

info "running three setup turns plus one coding repair turn"
LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" python3 - "$WORKSPACE" "$RPC_LOG" "$STDERR_LOG" "$SUMMARY_JSON" <<'PY'
import hashlib
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

workspace = Path(sys.argv[1])
rpc_log = Path(sys.argv[2])
stderr_log = Path(sys.argv[3])
summary_path = Path(sys.argv[4])

ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXPECTED = [5, 13, 29, 61]
filler = (" ordinary context filler alpha beta gamma delta epsilon zeta theta lambda archive window coding state" * 24)[:1780]
old_diagnostic = (
    f"External CI diagnostic {ERROR} for {TARGET}: the exact supported delay contract is "
    "attempt 1 -> 5 seconds, attempt 2 -> 13 seconds, attempt 3 -> 29 seconds, attempt 4 -> 61 seconds; "
    "attempts outside 1..4 must raise ValueError. Preserve this external diagnostic for later repair. "
    "Do not call tools now. Reply only ACK_DIAGNOSTIC."
)
prompts = [
    old_diagnostic + filler,
    "Ordinary unrelated context. Do not call tools. Reply only ACK_FILLER_2." + filler,
    "Another unrelated context turn. Do not call tools. Reply only ACK_FILLER_3." + filler,
    (
        f"Fix {ERROR} in {TARGET}. Inspect the file, edit only {TARGET}, and do not create other files. "
        "Use the exact historical external-CI contract associated with that error; do not invent values and do not ask me to repeat it. "
        "After editing, run a short Python command that imports retry_delay and prints its values for attempts 1 through 4."
    ),
]


def snapshot(root: Path):
    result = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or rel.endswith(".pyc") or rel.startswith(".ruff_cache/") or rel == ".DS_Store":
            continue
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

before = snapshot(workspace)

with stderr_log.open("w", encoding="utf-8") as err:
    proc = subprocess.Popen(
        ["ForgeLoom", "--no-session", "--mode", "rpc"],
        cwd=workspace,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=err,
        text=True,
        bufsize=1,
        env=os.environ.copy(),
    )
    assert proc.stdin is not None and proc.stdout is not None

    def send(obj):
        proc.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
        proc.stdin.flush()

    def next_event(deadline):
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"ForgeLoom RPC exited early with status {proc.returncode}")
            ready, _, _ = select.select([proc.stdout], [], [], min(1.0, max(0.0, deadline - time.monotonic())))
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

    def wait_response(request_id, timeout=420):
        deadline = time.monotonic() + timeout
        while True:
            event = next_event(deadline)
            if event.get("type") == "response" and event.get("id") == request_id:
                if event.get("success") is not True:
                    raise RuntimeError(f"RPC request failed: {event}")
                return

    def wait_agent_end(timeout=420):
        deadline = time.monotonic() + timeout
        while True:
            event = next_event(deadline)
            if event.get("type") == "agent_end":
                return

    send({"id":"initial-state","type":"get_state"})
    wait_response("initial-state")

    for turn, prompt in enumerate(prompts, start=1):
        rid = f"turn-{turn}"
        send({"id":rid,"type":"prompt","message":prompt})
        wait_response(rid)
        wait_agent_end()
        print(f"CE-002 CODING RETRIEVAL INFO: turn {turn} completed", flush=True)

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)

after = snapshot(workspace)
changed = sorted({*before, *after} - {path for path in set(before) & set(after) if before[path] == after[path]})
if changed != [TARGET]:
    raise SystemExit(f"unexpected persisted workspace changes: {changed!r}")

sys.path.insert(0, str(workspace / "src"))
from retry_policy import retry_delay

actual = [retry_delay(i) for i in range(1, 5)]
if actual != EXPECTED:
    raise SystemExit(f"hidden contract verification failed: expected {EXPECTED!r}, got {actual!r}")
for bad in (0, 5):
    try:
        retry_delay(bad)
    except ValueError:
        pass
    else:
        raise SystemExit(f"retry_delay({bad}) did not raise ValueError")

summary_path.write_text(json.dumps({
    "error": ERROR,
    "target": TARGET,
    "expected": EXPECTED,
    "actual": actual,
    "changed": changed,
    "oldDiagnostic": old_diagnostic,
}, indent=2) + "\n", encoding="utf-8")
print("CE-002 coding contract repair: PASS")
print(f"  error anchor             : {ERROR}")
print(f"  target                   : {TARGET}")
print(f"  hidden expected delays   : {EXPECTED}")
print(f"  actual delays            : {actual}")
print(f"  persisted changed files  : {changed}")
PY
pass "model applied old external CI evidence to the isolated code repair"

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
error = summary["error"]
old_diagnostic = summary["oldDiagnostic"]

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
    raise SystemExit("hard guard blocked at least one coding-retrieval request")
max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in checked)
max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in checked)
if max_input > 2800 or max_total > 3600:
    raise SystemExit("CE-001 safe envelope exceeded during coding retrieval run")

accounting = []
for path in engine_root.glob("*/accounting.jsonl"):
    for line in path.read_text(errors="replace").splitlines():
        try:
            accounting.append(json.loads(line))
        except Exception:
            pass
retrievals = [row for row in accounting if row.get("event") == "evidence_retrieval"]
if not retrievals:
    raise SystemExit("no CE-002 retrieval accounting event was recorded")
final_retrieval = retrievals[-1]
ids = list(final_retrieval.get("evidenceIds") or [])
if not ids:
    raise SystemExit("final retrieval did not record an evidence id")
visible = int(final_retrieval.get("finalVisibleTokens", 0) or 0)
if visible > 1200:
    raise SystemExit(f"retrieval-visible estimate exceeded 1200: {visible}")

blobs = engine_root / "evidence" / "blobs"
matched = False
for evidence_id in ids:
    if not isinstance(evidence_id, str) or not evidence_id.startswith("ev1-"):
        continue
    path = blobs / f"{evidence_id[4:]}.json"
    if not path.exists():
        continue
    try:
        blob = json.loads(path.read_text())
    except Exception:
        continue
    text = json.dumps(blob.get("message"), sort_keys=True)
    if error in text and "attempt 1 -> 5 seconds" in text and "attempt 4 -> 61 seconds" in text:
        matched = True
        break
if not matched:
    raise SystemExit(f"retrieval evidence ids did not point to the archived external diagnostic: {ids!r}")

threshold = [row for row in accounting if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
overflow = [row for row in accounting if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"]
if threshold or overflow:
    raise SystemExit("Pi compaction/overflow occurred during coding retrieval run")
archive_errors = [row for row in accounting if row.get("event") == "evidence_archive_error"]
retrieval_errors = [row for row in accounting if row.get("event") == "evidence_retrieval_error"]
if archive_errors or retrieval_errors:
    raise SystemExit(f"CE-002 archive/retrieval errors recorded: archive={archive_errors!r} retrieval={retrieval_errors!r}")

print("CE-002 realistic coding retrieval safety/accounting: PASS")
print(f"  guarded provider calls    : {len(checked)}")
print(f"  retrieval applications    : {len(retrievals)}")
print(f"  final evidence ids        : {ids}")
print(f"  retrieval visible tokens  : {visible}")
print(f"  max exact final input     : {max_input}")
print(f"  max projected total       : {max_total}")
print("  hard-guard blocks         : 0")
print("  Pi threshold compactions  : 0")
print("  Pi overflow events        : 0")
PY

LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" node scripts/loom-context-evidence.mjs verify > "$RUN_DIR/verify.json"
pass "archive integrity verification passed after coding retrieval"

echo "CE-002 LIVE CODING RETRIEVAL COMPLETE"
echo "run dir : $RUN_DIR"
echo "rpc log : $RPC_LOG"
echo "stderr  : $STDERR_LOG"
echo "summary : $SUMMARY_JSON"
echo "verify  : $RUN_DIR/verify.json"
