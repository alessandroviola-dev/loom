#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "CE-001 RESOURCE FAIL: $*" >&2; exit 1; }
pass() { echo "CE-001 RESOURCE PASS: $*"; }
info() { echo "CE-001 RESOURCE INFO: $*"; }

command -v ForgeLoom >/dev/null 2>&1 || fail "ForgeLoom is not installed"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
command -v ps >/dev/null 2>&1 || fail "ps not found"
command -v sysctl >/dev/null 2>&1 || fail "sysctl not found"

STATE="$ROOT/.loom/runtime/loom-deep"
BACKEND_PID_FILE="$STATE/llama-server-backend.pid"
[[ -s "$BACKEND_PID_FILE" ]] || fail "LOOM backend pid file missing; run ForgeLoom --help first"
BACKEND_PID="$(<"$BACKEND_PID_FILE")"
kill -0 "$BACKEND_PID" 2>/dev/null || fail "LOOM backend is not running"

# Historical retained S40 reference from the frozen UOPT handoff.
BASELINE_RSS_GIB="${LOOM_CE001_BASELINE_RSS_GIB:-4.676}"
MAX_RSS_REGRESSION_PCT="${LOOM_CE001_MAX_RSS_REGRESSION_PCT:-15}"
MAX_SWAP_DELTA_MIB="${LOOM_CE001_MAX_SWAP_DELTA_MIB:-512}"

info "sampling one short warm ForgeLoom request; no coding benchmark is run"
python3 - "$BACKEND_PID" "$BASELINE_RSS_GIB" "$MAX_RSS_REGRESSION_PCT" "$MAX_SWAP_DELTA_MIB" <<'PY'
import re
import subprocess
import sys
import threading
import time

backend_pid = int(sys.argv[1])
baseline_gib = float(sys.argv[2])
max_regression_pct = float(sys.argv[3])
max_swap_delta_mib = float(sys.argv[4])


def rss_kib(pid: int) -> int:
    try:
        out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True, stderr=subprocess.DEVNULL).strip()
        return int(out.split()[0]) if out else 0
    except Exception:
        return 0


def swap_used_mib() -> float:
    try:
        out = subprocess.check_output(["sysctl", "vm.swapusage"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return float("nan")
    m = re.search(r"used\s*=\s*([0-9.]+)([KMGTP])", out, re.I)
    if not m:
        return float("nan")
    value = float(m.group(1))
    unit = m.group(2).upper()
    factor = {"K": 1/1024, "M": 1, "G": 1024, "T": 1024*1024, "P": 1024*1024*1024}[unit]
    return value * factor

swap_before = swap_used_mib()
backend_before = rss_kib(backend_pid)

proc = subprocess.Popen(
    ["ForgeLoom", "--no-session", "-p", "Reply with exactly CE001_RESOURCE_OK and nothing else."],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

peak_backend = backend_before
peak_agent = 0
stop = False


def sample():
    global peak_backend, peak_agent
    while not stop:
        peak_backend = max(peak_backend, rss_kib(backend_pid))
        peak_agent = max(peak_agent, rss_kib(proc.pid))
        time.sleep(0.20)

thread = threading.Thread(target=sample, daemon=True)
thread.start()
try:
    stdout, stderr = proc.communicate(timeout=600)
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, stderr = proc.communicate()
    stop = True
    thread.join(timeout=2)
    raise SystemExit("ForgeLoom resource probe timed out")
stop = True
thread.join(timeout=2)

if proc.returncode != 0:
    print(stderr[-2000:], file=sys.stderr)
    raise SystemExit(f"ForgeLoom resource probe exited with status {proc.returncode}")
if "CE001_RESOURCE_OK" not in stdout:
    raise SystemExit("model did not return CE001_RESOURCE_OK")

# Give macOS a short settling window before the post-run swap sample.
time.sleep(2)
swap_after = swap_used_mib()
backend_after = rss_kib(backend_pid)

peak_backend_gib = peak_backend / (1024 * 1024)
peak_agent_mib = peak_agent / 1024
allowed_gib = baseline_gib * (1 + max_regression_pct / 100.0)
regression_pct = ((peak_backend_gib / baseline_gib) - 1.0) * 100.0 if baseline_gib else float("nan")
swap_delta = swap_after - swap_before if swap_before == swap_before and swap_after == swap_after else float("nan")

print("CE-001 resource regression report")
print(f"  historical S40 RSS ref   : {baseline_gib:.3f} GiB")
print(f"  allowed RSS (+{max_regression_pct:g}%): {allowed_gib:.3f} GiB")
print(f"  backend RSS before       : {backend_before / (1024*1024):.3f} GiB")
print(f"  backend RSS peak         : {peak_backend_gib:.3f} GiB")
print(f"  backend RSS after        : {backend_after / (1024*1024):.3f} GiB")
print(f"  RSS delta vs reference   : {regression_pct:+.2f}%")
print(f"  ForgeLoom agent peak RSS : {peak_agent_mib:.1f} MiB")
if swap_before == swap_before and swap_after == swap_after:
    print(f"  swap before              : {swap_before:.1f} MiB")
    print(f"  swap after               : {swap_after:.1f} MiB")
    print(f"  swap delta               : {swap_delta:+.1f} MiB")
else:
    print("  swap                     : unavailable")

if peak_backend_gib > allowed_gib:
    raise SystemExit(f"backend RSS peak {peak_backend_gib:.3f} GiB exceeds {allowed_gib:.3f} GiB (+{max_regression_pct:g}% limit)")
if swap_delta == swap_delta and swap_delta > max_swap_delta_mib:
    raise SystemExit(f"swap grew by {swap_delta:.1f} MiB, above {max_swap_delta_mib:g} MiB limit")
PY

pass "retained S40 resource profile stayed within the CE-001 regression envelope"
echo "CE-001 RESOURCE COMPLETE"
