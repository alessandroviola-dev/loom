#!/usr/bin/env python3
"""Single-request live CE-002 coding retrieval acceptance gate.

This gate is intentionally lightweight for constrained Macs:
- archive fixture is seeded offline after session creation;
- exactly one user coding prompt is sent to the retained local model;
- provider attempts are capped;
- wall-clock timeout is capped;
- LOOM backend is stopped on exit to release memory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".loom" / "runtime" / "loom-deep"
GATEWAY_ACCOUNTING = STATE / "context-webui-ci" / "accounting.jsonl"
ERROR = "ERROR_CE002_271828"
TARGET = "src/retry_policy.py"
EXPECTED = [5, 13, 29, 61]
MAX_PROVIDER_CALLS = 6
AGENT_TIMEOUT_SECONDS = 360


def fail(message: str) -> None:
    raise SystemExit(f"CE-002 LITE FAIL: {message}")


def info(message: str) -> None:
    print(f"CE-002 LITE INFO: {message}", flush=True)


def passed(message: str) -> None:
    print(f"CE-002 LITE PASS: {message}", flush=True)


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


def run_checked(args: list[str], *, env: dict[str, str] | None = None, stdout=None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=ROOT, env=env, stdout=stdout, check=True, text=True)


def stop_loom_best_effort() -> None:
    try:
        subprocess.run(
            [str(ROOT / "scripts" / "loom-deep"), "stop"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        )
    except Exception:
        pass


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
    spec = importlib.util.spec_from_file_location("ce002_retry_policy_lite", target)
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
        self.reader = threading.Thread(target=self._reader, name="ce002-lite-rpc-reader", daemon=True)
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

    def wait_response(self, request_id: str, timeout: int) -> dict:
        event = self.wait_for(
            lambda e: e.get("type") == "response" and e.get("id") == request_id,
            timeout,
        )
        if event.get("success") is not True:
            raise RuntimeError(f"RPC request failed: {event}")
        return event

    def wait_agent_end(self, timeout: int) -> None:
        self.wait_for(lambda e: e.get("type") == "agent_end", timeout)

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                try:
                    self.stdin.close()
                except Exception:
                    pass
                try:
                    self.proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    self.proc.terminate()
                    try:
                        self.proc.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        self.proc.kill()
                        self.proc.wait(timeout=5)
        finally:
            self.stderr_handle.close()


def extract_session_id(state_response: dict) -> str:
    data = state_response.get("data") if isinstance(state_response.get("data"), dict) else {}
    value = data.get("sessionId")
    if not isinstance(value, str) or not value:
        fail(f"get_state did not return sessionId: {state_response!r}")
    return value


def seed_evidence(root_dir: Path, session_id: str, workspace: Path) -> str:
    seed_script = r'''
import { archiveEvictedEvidence } from "./src/loom-context-engine/evidence-archive.mjs";
const [rootDir, sessionId, cwd] = process.argv.slice(1);
const message = {
  role: "user",
  content: "Historical external-CI fact record: ERROR_CE002_271828; target path src/retry_policy.py; exact supported delay contract: attempt 1 -> 5 seconds, attempt 2 -> 13 seconds, attempt 3 -> 29 seconds, attempt 4 -> 61 seconds; attempts outside 1..4 raise ValueError."
};
const result = archiveEvictedEvidence({
  rootDir,
  sessionId,
  originalMessages: [message],
  visibleMessages: [],
  cwd,
  capturedAt: "2026-09-08T00:00:00.000Z"
});
process.stdout.write(JSON.stringify(result));
'''
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", seed_script, str(root_dir), session_id, str(workspace)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    result = json.loads(completed.stdout)
    ids = result.get("evidenceIds") or []
    if result.get("candidates") != 1 or len(ids) != 1:
        fail(f"offline evidence seed produced unexpected result: {result!r}")
    evidence_id = ids[0]
    if not isinstance(evidence_id, str) or not evidence_id.startswith("ev1-"):
        fail(f"offline evidence seed returned invalid id: {evidence_id!r}")
    return evidence_id


def provider_rows_since(start_line: int) -> list[dict]:
    return [row for row in load_jsonl(GATEWAY_ACCOUNTING)[start_line:] if row.get("guardChecked") is True]


def watchdog(session: RpcSession, start_line: int, stop_event: threading.Event, state: dict[str, str]) -> None:
    while not stop_event.wait(1.0):
        count = len(provider_rows_since(start_line))
        if count > MAX_PROVIDER_CALLS:
            state["reason"] = f"provider attempt cap exceeded: {count}>{MAX_PROVIDER_CALLS}"
            try:
                session.proc.terminate()
            except Exception:
                pass
            return


def main() -> None:
    for command in ("ForgeLoom", "python3", "node"):
        if subprocess.run(["bash", "-lc", f"command -v {command}"], stdout=subprocess.DEVNULL).returncode != 0:
            fail(f"{command} not found")

    verify_env = os.environ.copy()
    verify_env["LOOM_CONTEXT_VERIFY_SKIP_LIVE"] = "1"
    run_checked(["bash", "scripts/verify-context-engine.sh"], env=verify_env)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir = STATE / "ce002-live-coding-retrieval-lite" / stamp
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
        '    return 1\n',
        encoding="utf-8",
    )
    (workspace / "README.md").write_text(
        "# CE-002 lightweight retrieval fixture\n\n"
        "The exact retry contract is intentionally absent from the workspace.\n",
        encoding="utf-8",
    )

    session: RpcSession | None = None
    watchdog_stop = threading.Event()
    watchdog_state: dict[str, str] = {}

    try:
        info("resetting LOOM backend before the single live request")
        stop_loom_best_effort()

        info("warming guarded ForgeLoom backend without inference")
        run_checked(["ForgeLoom", "--help"], stdout=subprocess.DEVNULL)
        run_checked(["bash", "scripts/verify-context-engine.sh"])
        passed("gateway is warm and in the frozen CE-001 safe profile")

        before_gateway_lines = len(load_jsonl(GATEWAY_ACCOUNTING))
        before = snapshot(workspace)

        rpc_env = os.environ.copy()
        rpc_env["LOOM_CONTEXT_RUNTIME_DIR"] = str(engine_runtime)
        session = RpcSession(workspace, rpc_log, stderr_log, rpc_env)
        session.send({"id": "initial-state", "type": "get_state"})
        state_response = session.wait_response("initial-state", 60)
        session_id = extract_session_id(state_response)

        evidence_id = seed_evidence(engine_runtime, session_id, workspace)
        info(f"seeded one immutable evidence blob offline: {evidence_id}")

        evidence_env = os.environ.copy()
        evidence_env["LOOM_CONTEXT_RUNTIME_DIR"] = str(engine_runtime)
        run_checked(["node", "scripts/loom-context-evidence.mjs", "verify"], env=evidence_env, stdout=subprocess.DEVNULL)
        passed("offline evidence archive verified before inference")

        prompt = (
            f"Fix {ERROR} in {TARGET}. Inspect the file, edit only {TARGET}, and do not create other files. "
            "Use the historical external-CI evidence associated with that error; do not invent values. "
            "After editing, run one short Python verification for attempts 1 through 4, then stop and answer briefly."
        )

        watcher = threading.Thread(
            target=watchdog,
            args=(session, before_gateway_lines, watchdog_stop, watchdog_state),
            name="ce002-lite-provider-watchdog",
            daemon=True,
        )
        watcher.start()

        info("sending the only live model prompt in this gate")
        session.send({"id": "coding-turn", "type": "prompt", "message": prompt})
        session.wait_response("coding-turn", 60)
        try:
            session.wait_agent_end(AGENT_TIMEOUT_SECONDS)
        except Exception:
            if watchdog_state.get("reason"):
                fail(watchdog_state["reason"])
            raise
        finally:
            watchdog_stop.set()

        provider_rows = provider_rows_since(before_gateway_lines)
        if not provider_rows:
            fail("no guarded provider request was recorded")
        if len(provider_rows) > MAX_PROVIDER_CALLS:
            fail(f"provider attempt cap exceeded: {len(provider_rows)}>{MAX_PROVIDER_CALLS}")
        if any(row.get("guardBlocked") for row in provider_rows):
            fail("hard guard blocked at least one request")

        after = snapshot(workspace)
        changed = sorted({*before, *after} - {path for path in set(before) & set(after) if before[path] == after[path]})
        if changed != [TARGET]:
            fail(f"unexpected persisted workspace changes: {changed!r}")
        actual = verify_retry_policy(workspace)

        accounting: list[dict] = []
        for path in engine_runtime.glob("*/accounting.jsonl"):
            accounting.extend(load_jsonl(path))
        retrievals = [row for row in accounting if row.get("event") == "evidence_retrieval"]
        if not retrievals:
            fail("no CE-002 retrieval accounting event was recorded")
        matched_retrievals = [row for row in retrievals if evidence_id in (row.get("evidenceIds") or [])]
        if not matched_retrievals:
            fail(f"retrieval did not use seeded evidence id {evidence_id}")
        max_visible = max(int(row.get("finalVisibleTokens", 0) or 0) for row in matched_retrievals)
        if max_visible > 1200:
            fail(f"retrieval-visible estimate exceeded 1200: {max_visible}")

        max_input = max(int(row.get("finalInputTokens", 0) or 0) for row in provider_rows)
        max_total = max(int(row.get("projectedTotalTokens", 0) or 0) for row in provider_rows)
        if max_input > 2800 or max_total > 3600:
            fail("CE-001 safe envelope exceeded")

        threshold = [row for row in accounting if row.get("event") == "pi_compaction_after" and row.get("reason") == "threshold"]
        overflow = [
            row for row in accounting
            if row.get("event") in {"pi_compaction_before", "pi_compaction_after"} and row.get("reason") == "overflow"
        ]
        errors = [
            row for row in accounting
            if row.get("event") in {"evidence_archive_error", "evidence_retrieval_error"}
        ]
        if threshold or overflow:
            fail("Pi compaction/overflow occurred")
        if errors:
            fail(f"CE-002 archive/retrieval errors recorded: {errors!r}")

        run_checked(["node", "scripts/loom-context-evidence.mjs", "verify"], env=evidence_env, stdout=subprocess.DEVNULL)

        summary = {
            "sessionId": session_id,
            "evidenceId": evidence_id,
            "providerCalls": len(provider_rows),
            "expected": EXPECTED,
            "actual": actual,
            "changed": changed,
            "retrievalApplications": len(retrievals),
            "maxRetrievalVisibleTokens": max_visible,
            "maxExactFinalInput": max_input,
            "maxProjectedTotal": max_total,
            "hardGuardBlocks": 0,
            "piThresholdCompactions": 0,
            "piOverflowEvents": 0,
        }
        summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        print("CE-002 LITE coding retrieval: PASS")
        print(f"  evidence id               : {evidence_id}")
        print(f"  provider calls            : {len(provider_rows)} / {MAX_PROVIDER_CALLS} max")
        print(f"  actual delays             : {actual}")
        print(f"  persisted changed files   : {changed}")
        print(f"  retrieval applications    : {len(retrievals)}")
        print(f"  max retrieval visible     : {max_visible}")
        print(f"  max exact final input     : {max_input}")
        print(f"  max projected total       : {max_total}")
        print("  hard-guard blocks         : 0")
        print("  Pi threshold compactions  : 0")
        print("  Pi overflow events        : 0")
        passed("single-request archive-to-code workflow completed safely")
        print("CE-002 LIVE CODING RETRIEVAL LITE COMPLETE")
        print(f"run dir : {run_dir}")

    finally:
        watchdog_stop.set()
        if session is not None:
            session.close()
        info("stopping LOOM backend to release memory")
        stop_loom_best_effort()


if __name__ == "__main__":
    main()
