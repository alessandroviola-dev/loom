#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-002 ARCHIVE FAIL: $*" >&2; exit 1; }
pass() { echo "CE-002 ARCHIVE PASS: $*"; }
info() { echo "CE-002 ARCHIVE INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed; run bash scripts/install-forge-loom.sh"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
command -v node >/dev/null 2>&1 || fail "node not found"

LOOM_CONTEXT_VERIFY_SKIP_LIVE=1 bash scripts/verify-context-engine.sh

STATE="$ROOT/.loom/runtime/loom-deep"
GATEWAY_ACCOUNTING="$STATE/context-webui-ci/accounting.jsonl"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$STATE/ce002-live-archive/$STAMP"
ENGINE_RUNTIME="$RUN_DIR/engine-runtime"
RPC_LOG="$RUN_DIR/rpc.jsonl"
STDERR_LOG="$RUN_DIR/stderr.txt"
EXPECTED_JSON="$RUN_DIR/expected.json"
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

info "running six short turns in one isolated ForgeLoom session"
LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" python3 - "$RPC_LOG" "$STDERR_LOG" "$EXPECTED_JSON" <<'PY'
import json
import select
import subprocess
import sys
import time
from pathlib import Path

rpc_log = Path(sys.argv[1])
stderr_log = Path(sys.argv[2])
expected_path = Path(sys.argv[3])

prompts = []
for turn in range(1, 7):
    marker = f"CE002_ARCHIVE_{turn:02d}"
    unit = f" archive-{turn:02d}-abcdefghijklmnopqrstuvwxyz0123456789"
    filler = (unit * 30)[:1050]
    prompt = (
        f"{marker}. This is deterministic evidence-archive validation data. "
        f"Do not call tools. Reply with exactly {marker}_OK and nothing else. DATA:{filler}"
    )
    prompts.append(prompt)
expected_path.write_text(json.dumps({"prompts": prompts}, indent=2) + "\n", encoding="utf-8")

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

    def read_until(predicate, timeout=240):
        deadline = time.monotonic() + timeout
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
                event = json.loads(stripped)
            except Exception:
                continue
            if predicate(event):
                return event
        raise TimeoutError("timed out waiting for ForgeLoom RPC event")

    send({"id":"initial-state","type":"get_state"})
    read_until(lambda e: e.get("type") == "response" and e.get("id") == "initial-state" and e.get("success") is True)

    for turn, prompt in enumerate(prompts, start=1):
        request_id = f"turn-{turn:02d}"
        marker = f"CE002_ARCHIVE_{turn:02d}"
        send({"id":request_id,"type":"prompt","message":prompt})
        read_until(lambda e, rid=request_id: e.get("type") == "response" and e.get("id") == rid and e.get("success") is True)
        read_until(lambda e: e.get("type") == "agent_end")
        # The model output is intentionally not a quality gate; session completion is.
        print(f"CE-002 ARCHIVE INFO: {marker} turn completed", flush=True)

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
PY
pass "six-turn ForgeLoom session completed"

bash scripts/verify-context-engine.sh
pass "CE-001 gateway envelope remained valid"

python3 - "$GATEWAY_ACCOUNTING" "$before_gateway_lines" "$ENGINE_RUNTIME" "$EXPECTED_JSON" <<'PY'
import json
import sys
from pathlib import Path

gateway_path = Path(sys.argv[1])
before_gateway = int(sys.argv[2])
engine_root = Path(sys.argv[3])
expected = json.loads(Path(sys.argv[4]).read_text())

if not gateway_path.exists():
    raise SystemExit("gateway accounting missing")
gateway_rows = []
for line in gateway_path.read_text(errors="replace").splitlines()[before_gateway:]:
    try:
        gateway_rows.append(json.loads(line))
    except Exception:
        pass
checked = [row for row in gateway_rows if row.get("guardChecked") is True]
if len(checked) < 6:
    raise SystemExit(f"expected >=6 guarded provider calls, found {len(checked)}")
if any(row.get("guardBlocked") for row in checked):
    raise SystemExit("hard guard blocked at least one CE-002 archive request")
max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in checked)
max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in checked)
if max_input > 2800 or max_total > 3600:
    raise SystemExit("CE-001 safe envelope exceeded during CE-002 archive run")

accounting = []
for path in engine_root.glob("*/accounting.jsonl"):
    for line in path.read_text(errors="replace").splitlines():
        try:
            accounting.append(json.loads(line))
        except Exception:
            pass
errors = [row for row in accounting if row.get("event") == "evidence_archive_error"]
if errors:
    raise SystemExit("evidence archive errors occurred: " + repr(errors))
governors = [row for row in accounting if row.get("event") == "context_governor"]
changed = [row for row in governors if row.get("changed") is True]
if not changed:
    raise SystemExit("governor never reduced context during CE-002 archive run")
new_refs = sum(int(row.get("evidenceSessionRefsCreated", 0) or 0) for row in governors)
new_blobs = sum(int(row.get("evidenceBlobsCreated", 0) or 0) for row in governors)
if new_refs <= 0 or new_blobs <= 0:
    raise SystemExit(f"no archived evidence was created: blobs={new_blobs} refs={new_refs}
")
threshold = [row for row in accounting if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
overflow = [row for row in accounting if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"]
if threshold or overflow:
    raise SystemExit("Pi compaction/overflow occurred during CE-002 archive run")

print("CE-002 archive safety/accounting: PASS")
print(f"  provider calls guarded     : {len(checked)}")
print(f"  governor reductions        : {len(changed)}")
print(f"  evidence blobs created     : {new_blobs}")
print(f"  session refs created       : {new_refs}")
print(f"  max exact final input      : {max_input}")
print(f"  max projected total        : {max_total}")
print("  hard-guard blocks          : 0")
print("  Pi threshold compactions   : 0")
print("  Pi overflow events         : 0")
PY

LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" node scripts/loom-context-evidence.mjs verify > "$RUN_DIR/verify.json"
pass "archive hash/reference verification passed"

LOOM_CONTEXT_RUNTIME_DIR="$ENGINE_RUNTIME" node --input-type=module - "$EXPECTED_JSON" <<'NODE'
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { readEvidenceById, searchEvidence } from "./src/loom-context-engine/evidence-archive.mjs";

const expected = JSON.parse(readFileSync(process.argv[2], "utf8"));
const prompt = expected.prompts[0];
const marker = "CE002_ARCHIVE_01";
const agentDir = process.env.PI_CODING_AGENT_DIR ?? join(process.env.HOME ?? homedir(), ".pi", "agent");
const root = resolve(process.env.LOOM_CONTEXT_RUNTIME_DIR ?? join(agentDir, "loom-context-engine"));
const results = searchEvidence(root, { query: marker, limit: 10 });
if (results.length === 0) throw new Error(`archived marker not found: ${marker}`);
const blob = readEvidenceById(root, results[0].evidenceId);
const recovered = JSON.stringify(blob.message);
if (!recovered.includes(prompt)) {
  throw new Error("recovered evidence does not contain the complete original first-turn prompt");
}
console.log("CE-002 exact live recovery: PASS");
console.log(`  evidence id              : ${blob.evidenceId}`);
console.log(`  sha256                   : ${blob.sha256}`);
console.log(`  recovered prompt chars   : ${prompt.length}`);
console.log(`  search score             : ${results[0].score}`);
NODE
pass "old evicted prompt was recovered exactly by stable evidence id"

echo "CE-002 LIVE ARCHIVE COMPLETE"
echo "run dir : $RUN_DIR"
echo "rpc log : $RPC_LOG"
echo "stderr  : $STDERR_LOG"
echo "verify  : $RUN_DIR/verify.json"
