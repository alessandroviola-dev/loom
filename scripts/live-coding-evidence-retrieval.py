#!/usr/bin/env python3
"""Robust live CE-002 coding-evidence retrieval acceptance gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"
ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXPECTED = [5, 13, 29, 61]


def fail(message: str) -> None:
    raise SystemExit(f"CE-002 CODING RETRIEVAL FAIL: {message}")


def pass_line(message: str) -> None:
    print(f"CE-002 CODING RETRIEVAL PASS: {message}", flush=True)


def info(message: str) -> None:
    print(f"CE-002 CODING RETRIEVAL INFO: {message}", flush=True)


def run_checked(args: list[str], *, env: dict[str, str] | None = None, stdout=None) -> None:
    subprocess.run(args, cwd=ROOT, env=env, stdout=stdout, check=True)


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        try:
            value = json.loads(line)
        except Exception:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or rel.endswith(".pyc") or rel.startswith(".ruff_cache/") or rel == ".DS_Store":
            continue
        result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify_retry_policy(workspace: Path) -> list[int]:
    target = workspace / TARGET
    spec = importlib.util.spec_from_file_location("ce002_retry_policy_gate", target)
    if spec is None or spec.loader is None:
        fail("could not import repaired retry policy")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    retry_delay = getattr(module, "retry_delay", None)
    if not callable(retry_delay):
        fail("retry_delay is missing or not callable")
    actual = [retry_delay(i) for i in range(1, 5)]
    if actual != EXPECTED:
        fail(f"hidden contract verification failed: expected {EXPECTED!r}, got {actual!r}")
    for bad in (0, 5):
        try:
            retry_delay(bad)
        except ValueError:
            pass
        else:
            fail(f"retry_delay({bad}) did not raise ValueError")
    return actual


class RpcSession:
    def __init__(self, workspace: Path, rpc_log: Path, stderr_log: Path, env: dict[str, str]):
        self.rpc_log = rpc_log
        self.stderr_handle = stderr_log.open("w", encoding="utf-8")
        self.proc = subprocess.Popen(
            ["ForgeLoom", "--no-session", "--mode", "rpc"],
            cwd=workspace,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.stderr_handle,
            text=True,
            bufsize=1,
            env=env,
        )
        if self.proc.stdin is None or self.proc.stdout is None:
            fail("ForgeLoom RPC pipes unavailable")
        self.stdin = self.proc.stdin
        self.stdout = self.proc.stdout
        self.lines: queue.Queue[str | None] = queue.Queue()
        self.pending: list[dict] = []
        self.reader = threading.Thread(target=self._reader, name="ce002-rpc-reader", daemon=True)
        self.reader.start()

    def _reader(self) -> None:
        try:
            with self.rpc_log.open("a", encoding="utf-8", buffering=1) as log:
                for line in self.stdout:
                    log.write(line)
                    self.lines.put(line)
        finally:
            self.lines.put(None)

    def send(self, obj: dict) -> None:
        self.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
        self.stdin.flush()

    def _new_event(self, deadline: float) -> dict:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("timed out waiting for ForgeLoom RPC event")
            try:
                line = self.lines.get(timeout=min(1.0, remaining))
            except queue.Empty:
                if self.proc.poll() is not None:
                    raise RuntimeError(f"ForgeLoom RPC exited early with status {self.proc.returncode}")
                continue
            if line is None:
                if self.proc.poll() is None:
                    continue
                raise RuntimeError(f"ForgeLoom RPC stdout closed with status {self.proc.returncode}")
            stripped = line.strip()
            if not stripped.startswith("{"):
                continue
            try:
                event = json.loads(stripped)
            except Exception:
                continue
            if isinstance(event, dict):
                return event

    def wait_for(self, predicate, timeout: int) -> dict:
        deadline = time.monotonic() + timeout
        for index, event in enumerate(self.pending):
            if predicate(event):
                return self.pending.pop(index)
        while True:
            event = self._new_event(deadline)
            if predicate(event):
                return event
            self.pending.append(event)

    def wait_response(self, request_id: str, timeout: int) -> None:
        event = self.wait_for(
            lambda e: e.get("type") == "response" and e.get("id") == request_id,
            timeout,
        )
        if event.get("success") is not True:
            raise RuntimeError(f"RPC request failed: {event}")

    def wait_agent_end(self, timeout: int) -> None:
        self.wait_for(lambda e: e.get("type") == "agent_end", timeout)

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=5)
        finally:
            self.stderr_handle.close()


def main() -> None:
    for command in ("ForgeLoom", "python3", "node"):
        if subprocess.run(["bash", "-lc", f"command -v {command}"], stdout=subprocess.DEVNULL).returncode != 0:
            fail(f"{command} not found")

    env = os.environ.copy()
    env["LOOM_CONTEXT_VERIFY_SKIP_LIVE"] = "1"
    run_checked(["bash", "scripts/verify-context-engine.sh"], env=env)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir = STATE / "ce002-live-coding-retrieval" / stamp
    engine_runtime = run_dir / "engine-runtime"
    workspace = run_dir / "workspace"
    rpc_log = run_dir / "rpc.jsonl"
    stderr_log = run_dir / "stderr.txt"
    summary_json = run_dir / "summary.json"
    (workspace / "src").mkdir(parents=True, exist_ok=True)
    engine_runtime.mkdir(parents=True, exist_ok=True)
    rpc_log.write_text("", encoding="utf-8")
    stderr_log.write_text("", encoding="utf-8")

    (workspace / TARGET).write_text(
        '"""Retry policy supplied by an external service contract."""\n\n\n'
        'def retry_delay(attempt: int) -> int:\n'
        '    """Return the configured delay for supported attempts 1 through 4."""\n'
        '    if attempt < 1 or attempt > 4:\n'
        '        raise ValueError("attempt must be between 1 and 4")\n'
        '    # Placeholder is intentionally wrong; exact contract values come from CI evidence.\n'
        '    return 1\n',
        encoding="utf-8",
    )
    (workspace / "README.md").write_text(
        "# CE-002 isolated coding retrieval fixture\n\n"
        "`src/retry_policy.py` implements a small external retry contract. The exact delay values are not stored in this workspace; they are supplied by an earlier external CI diagnostic in the agent session.\n",
        encoding="utf-8",
    )

    before_gateway_lines = len(load_jsonl(GATEWAY_ACCOUNTING))

    info("warming ForgeLoom gateway without inference")
    run_checked(["ForgeLoom", "--help"], stdout=subprocess.DEVNULL)
    run_checked(["bash", "scripts/verify-context-engine.sh"])
    pass_line("live gateway is warm and in the frozen CE-001 safe profile")

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

    before = snapshot(workspace)
    rpc_env = os.environ.copy()
    rpc_env["LOOM_CONTEXT_RUNTIME_DIR"] = str(engine_runtime)
    session = RpcSession(workspace, rpc_log, stderr_log, rpc_env)
    info("running three setup turns plus one coding repair turn")
    try:
        session.send({"id": "initial-state", "type": "get_state"})
        session.wait_response("initial-state", 120)
        for turn, prompt in enumerate(prompts, start=1):
            request_id = f"turn-{turn}"
            timeout = 900 if turn == 4 else 300
            session.send({"id": request_id, "type": "prompt", "message": prompt})
            session.wait_response(request_id, min(timeout, 300))
            session.wait_agent_end(timeout)
            info(f"turn {turn} completed")
    finally:
        session.close()

    after = snapshot(workspace)
    changed = sorted({*before, *after} - {path for path in set(before) & set(after) if before[path] == after[path]})
    if changed != [TARGET]:
        fail(f"unexpected persisted workspace changes: {changed!r}")
    actual = verify_retry_policy(workspace)

    summary_json.write_text(
        json.dumps(
            {
                "error": ERROR,
                "target": TARGET,
                "expected": EXPECTED,
                "actual": actual,
                "changed": changed,
                "oldDiagnostic": old_diagnostic,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print("CE-002 coding contract repair: PASS")
    print(f"  error anchor             : {ERROR}")
    print(f"  target                   : {TARGET}")
    print(f"  hidden expected delays   : {EXPECTED}")
    print(f"  actual delays            : {actual}")
    print(f"  persisted changed files  : {changed}")
    pass_line("model applied old external CI evidence to the isolated code repair")

    run_checked(["bash", "scripts/verify-context-engine.sh"])
    pass_line("CE-001 gateway envelope remained valid")

    gateway_rows = load_jsonl(GATEWAY_ACCOUNTING)[before_gateway_lines:]
    checked = [row for row in gateway_rows if row.get("guardChecked") is True]
    if len(checked) < 4:
        fail(f"expected >=4 guarded provider calls, found {len(checked)}")
    if any(row.get("guardBlocked") for row in checked):
        fail("hard guard blocked at least one coding-retrieval request")
    max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in checked)
    max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in checked)
    if max_input > 2800 or max_total > 3600:
        fail("CE-001 safe envelope exceeded during coding retrieval run")

    accounting: list[dict] = []
    for path in engine_runtime.glob("*/accounting.jsonl"):
        accounting.extend(load_jsonl(path))
    retrievals = [row for row in accounting if row.get("event") == "evidence_retrieval"]
    if not retrievals:
        fail("no CE-002 retrieval accounting event was recorded")
    final_retrieval = retrievals[-1]
    ids = list(final_retrieval.get("evidenceIds") or [])
    if not ids:
        fail("final retrieval did not record an evidence id")
    visible = int(final_retrieval.get("finalVisibleTokens", 0) or 0)
    if visible > 1200:
        fail(f"retrieval-visible estimate exceeded 1200: {visible}")

    blobs = engine_runtime / "evidence" / "blobs"
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
        if ERROR in text and "attempt 1 -> 5 seconds" in text and "attempt 4 -> 61 seconds" in text:
            matched = True
            break
    if not matched:
        fail(f"retrieval evidence ids did not point to the archived external diagnostic: {ids!r}")

    threshold = [row for row in accounting if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
    overflow = [
        row for row in accounting
        if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"
    ]
    archive_errors = [row for row in accounting if row.get("event") == "evidence_archive_error"]
    retrieval_errors = [row for row in accounting if row.get("event") == "evidence_retrieval_error"]
    if threshold or overflow:
        fail("Pi compaction/overflow occurred during coding retrieval run")
    if archive_errors or retrieval_errors:
        fail(f"CE-002 archive/retrieval errors recorded: archive={archive_errors!r} retrieval={retrieval_errors!r}")

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

    verify_json = run_dir / "verify.json"
    verify_env = os.environ.copy()
    verify_env["LOOM_CONTEXT_RUNTIME_DIR"] = str(engine_runtime)
    with verify_json.open("w", encoding="utf-8") as handle:
        run_checked(["node", "scripts/loom-context-evidence.mjs", "verify"], env=verify_env, stdout=handle)
    pass_line("archive integrity verification passed after coding retrieval")

    print("CE-002 LIVE CODING RETRIEVAL COMPLETE")
    print(f"run dir : {run_dir}")
    print(f"rpc log : {rpc_log}")
    print(f"stderr  : {stderr_log}")
    print(f"summary : {summary_json}")
    print(f"verify  : {verify_json}")


if __name__ == "__main__":
    main()
