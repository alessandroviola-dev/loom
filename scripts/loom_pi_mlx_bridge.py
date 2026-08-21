#!/usr/bin/env python3
"""Loopback-only compatibility shim for Pi and mlx_lm's OpenAI chat server.

Pi 0.84.2 can conservatively reduce an unknown local model's request to one
output token despite its configured 4096-token context.  This minimal proxy
preserves the frozen Pi model configuration and rewrites only that transport
artifact to the frozen 2048-token output ceiling before forwarding to the
installed mlx_lm server.  It neither loads a model nor contacts a remote host.
"""
from __future__ import annotations

import argparse
import http.client
import json
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--upstream-port", type=int, required=True)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--request-log", type=Path, required=True)
    parser.add_argument("--request-dir", type=Path, help="Persist each received chat-completion body verbatim as request-NN.json before bridge forwarding.")
    parser.add_argument("--capture-only", action="store_true", help="Save the unmodified Pi POST body and return a synthetic completion without contacting upstream.")
    parser.add_argument("--capture-file", type=Path, help="Destination for the exact decoded capture-only request JSON.")
    parser.add_argument("--boundary-reclaim", action="store_true", help="After each fully relayed chat-completion SSE response, invoke the upstream ownership-checked request-local prompt-cache detach and exactly one allocator-cache clear before accepting another model request.")
    parser.add_argument("--boundary-log", type=Path, help="JSONL evidence destination required with --boundary-reclaim.")
    parser.add_argument("--abort-free-percent", type=int, default=5, help="Post-boundary resource abort floor; used only with --boundary-reclaim.")
    parser.add_argument("--max-swap-mb", type=float, default=5600.0, help="Post-boundary resource abort ceiling; used only with --boundary-reclaim.")
    args = parser.parse_args()
    if args.boundary_reclaim and args.boundary_log is None:
        parser.error("--boundary-reclaim requires --boundary-log")
    if args.capture_only and args.capture_file is None:
        parser.error("--capture-only requires --capture-file")
    lock = threading.Lock()
    request_counter = 0
    boundary_blocked_reason: str | None = None
    if args.request_dir is not None:
        args.request_dir.mkdir(parents=True, exist_ok=False)

    def log(record: dict) -> None:
        with lock, args.request_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp_utc": now(), **record}, ensure_ascii=False) + "\n")

    def boundary_log(record: dict) -> None:
        if args.boundary_log is not None:
            with lock, args.boundary_log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"timestamp_utc": now(), **record}, ensure_ascii=False) + "\n")

    def upstream_json(method: str, path: str, body: bytes | None = None, timeout: float = 30) -> dict:
        connection = http.client.HTTPConnection("127.0.0.1", args.upstream_port, timeout=timeout)
        try:
            connection.request(method, path, body=body, headers={"Content-Type": "application/json", "Connection": "close"})
            response = connection.getresponse()
            raw = response.read()
            if response.status != 200:
                raise RuntimeError(f"{method} {path} status {response.status}: {raw.decode(errors='replace')}")
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise RuntimeError(f"{method} {path} non-object response")
            return value
        finally:
            connection.close()

    def host_resource() -> dict:
        pressure = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=20, check=False)
        free_match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure.stdout + pressure.stderr)
        swap = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=15, check=False)
        swap_match = re.search(r"used\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])", swap.stdout, re.I)
        scale = {"K": 1 / 1024, "M": 1, "G": 1024, "T": 1048576}
        return {"free_percent": int(free_match.group(1)) if free_match else None,
                "swap_used_mb": round(float(swap_match.group(1).replace(",", ".")) * scale[swap_match.group(2).upper()], 2) if swap_match else None}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *_: object) -> None:
            return

        def do_GET(self) -> None:
            if args.capture_only:
                if self.path.startswith("/v1/models"):
                    payload = {"object": "list", "data": []}
                elif self.path == "/health":
                    payload = {"status": "ok"}
                else:
                    payload = {"status": "capture-only"}
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
            self.forward(None)

        def do_POST(self) -> None:
            nonlocal request_counter, boundary_blocked_reason
            if args.boundary_reclaim and boundary_blocked_reason is not None and self.path.endswith("/chat/completions"):
                payload = json.dumps({"error": {"message": boundary_blocked_reason, "type": "boundary_reclamation_blocked"}}).encode()
                self.send_response(503); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)
                log({"method": "POST", "path": self.path, "blocked": True, "reason": boundary_blocked_reason})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            request_file = None
            if args.request_dir is not None and self.path.endswith("/chat/completions"):
                with lock:
                    request_counter += 1
                    request_file = args.request_dir / f"request-{request_counter:02d}.json"
                    # Persist exactly the bytes Pi sent to the bridge, before its
                    # documented max-token transport rewrite.
                    request_file.write_bytes(raw_body)
            self.loom_request_turn = request_counter if self.path.endswith("/chat/completions") else None
            body = raw_body
            original_max = forwarded_max = None
            tool_names: list[str] = []
            model = None
            payload = None
            try:
                payload = json.loads(raw_body)
                if isinstance(payload, dict):
                    model = payload.get("model")
                    original_max = payload.get("max_tokens", payload.get("max_completion_tokens"))
                    tools = payload.get("tools") or []
                    if isinstance(tools, list):
                        tool_names = [str(x.get("function", {}).get("name")) for x in tools if isinstance(x, dict)]
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass

            if args.capture_only and self.path.endswith("/chat/completions"):
                # Preserve the received bytes, before any ordinary bridge rewrite.
                args.capture_file.parent.mkdir(parents=True, exist_ok=True)
                args.capture_file.write_bytes(raw_body)
                log({"method": "POST", "path": self.path, "capture_only": True, "model": model, "original_max_tokens": original_max, "tool_names": tool_names, "captured_bytes": len(raw_body)})
                completion = {"id": "chatcmpl-loom-capture", "object": "chat.completion.chunk", "created": 0, "model": model or "capture-only", "choices": [{"index": 0, "delta": {"content": "DONE"}, "finish_reason": "stop"}]}
                if isinstance(payload, dict) and payload.get("stream"):
                    encoded = ("data: " + json.dumps(completion, ensure_ascii=False) + "\n\ndata: [DONE]\n\n").encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                else:
                    completion["object"] = "chat.completion"
                    completion["choices"][0] = {"index": 0, "message": {"role": "assistant", "content": "DONE"}, "finish_reason": "stop"}
                    encoded = json.dumps(completion, ensure_ascii=False).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                return

            if isinstance(payload, dict) and self.path.endswith("/chat/completions"):
                # This is deliberately the only ordinary-forwarding transformation.
                payload["max_tokens"] = args.max_tokens
                payload.pop("max_completion_tokens", None)
                forwarded_max = args.max_tokens
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            log({"method": "POST", "path": self.path, "model": model, "original_max_tokens": original_max, "forwarded_max_tokens": forwarded_max, "tool_names": tool_names, "request_file": str(request_file) if request_file else None, "received_bytes": len(raw_body)})
            self.forward(body)

        def forward(self, body: bytes | None) -> None:
            nonlocal boundary_blocked_reason
            connection = http.client.HTTPConnection("127.0.0.1", args.upstream_port, timeout=900)
            try:
                headers = {"Content-Type": self.headers.get("Content-Type", "application/json"), "Connection": "close"}
                if body is not None:
                    headers["Content-Length"] = str(len(body))
                connection.request(self.command, self.path, body=body, headers=headers)
                response = connection.getresponse()
                self.send_response(response.status, response.reason)
                for key, value in response.getheaders():
                    if key.lower() not in {"connection", "transfer-encoding", "content-length"}:
                        self.send_header(key, value)
                self.send_header("Connection", "close")
                self.end_headers()
                completed_sse = False
                sse_tail = b""
                while chunk := response.read(8192):
                    self.wfile.write(chunk)
                    self.wfile.flush()
                    sse_tail = (sse_tail + chunk)[-32:]
                    completed_sse = completed_sse or b"data: [DONE]" in sse_tail
                if args.boundary_reclaim and self.command == "POST" and self.path.endswith("/chat/completions"):
                    turn = getattr(self, "loom_request_turn", None)
                    record = {"turn": turn, "response_fully_relayed": completed_sse, "ownership_verification": "FAIL", "detach": None, "clear_cache": None, "resource": None}
                    try:
                        if not completed_sse or not isinstance(turn, int):
                            raise RuntimeError("completed SSE [DONE] or request-local turn identity unavailable")
                        record["before"] = upstream_json("GET", "/loom-telemetry")
                        record["detach"] = upstream_json("POST", "/loom-release-completed-request", json.dumps({"turn": turn}).encode())
                        checks = (record["detach"] or {}).get("checks") or {}
                        required = ("asked_turn_matches_current", "finished_record_exists", "weakref_alive", "response_finish_reason", "target_not_in_unfinished_batch", "target_has_prompt_cache")
                        if not record["detach"].get("ok") or not all(checks.get(key) is True for key in required):
                            raise RuntimeError(f"ownership verification refused/failed: {record['detach']}")
                        record["ownership_verification"] = "PASS"
                        record["after_detach"] = upstream_json("GET", "/loom-telemetry")
                        record["clear_cache"] = upstream_json("POST", "/loom-clear-allocator-cache", b"{}")
                        if not record["clear_cache"].get("ok") or record["clear_cache"].get("calls") != 1:
                            raise RuntimeError(f"clear-cache failure: {record['clear_cache']}")
                        record["after_clear"] = upstream_json("GET", "/loom-telemetry")
                        record["resource"] = host_resource()
                        free, swap = record["resource"].get("free_percent"), record["resource"].get("swap_used_mb")
                        if (isinstance(free, int) and free < args.abort_free_percent) or (isinstance(swap, (int, float)) and swap > args.max_swap_mb):
                            record["resource_abort"] = f"post-boundary resource gate: {record['resource']}"
                            boundary_blocked_reason = record["resource_abort"]
                    except Exception as exc:
                        record["error"] = f"{type(exc).__name__}: {exc}"
                        boundary_blocked_reason = "boundary reclamation infrastructure failure: " + record["error"]
                    boundary_log(record)
                    log({"event": "boundary_reclamation", **record})
            except Exception as exc:
                log({"method": self.command, "path": self.path, "bridge_error": f"{type(exc).__name__}: {exc}"})
                self.send_error(502, str(exc))
            finally:
                connection.close()

    server = ThreadingHTTPServer(("127.0.0.1", args.listen_port), Handler)
    log({"event": "bridge_started", "listen": f"127.0.0.1:{args.listen_port}", "upstream": f"127.0.0.1:{args.upstream_port}", "max_tokens": args.max_tokens, "boundary_reclaim": args.boundary_reclaim})
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log({"event": "bridge_stopped"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
