#!/usr/bin/env python3
"""Deterministic local API/cache/resource probe for the two WP4 profiles."""
from __future__ import annotations
import argparse, json, subprocess, time
from pathlib import Path
from statistics import median
from urllib.request import Request, urlopen


def command(*args: str) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def post(url: str, body: dict) -> dict:
    request = Request(url.rstrip("/") + "/v1/chat/completions", data=json.dumps(body).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=900) as response:
        return json.loads(response.read())


def sample(pid: int) -> dict:
    return {
        "timestamp": time.time(),
        "rss_kib": command("ps", "-o", "rss=", "-p", str(pid)),
        "swap": command("sysctl", "vm.swapusage"),
        "memory_pressure": command("memory_pressure", "-Q"),
    }


def request(url: str, model: str, prompt: str, max_tokens: int) -> dict:
    body = {"model": model, "messages": [{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}], "temperature": 0, "top_p": 1,
            "seed": 424242, "max_tokens": max_tokens, "stream": False}
    started = time.monotonic()
    response = post(url, body)
    return {"elapsed_s": time.monotonic() - started, "timings": response.get("timings", {}),
            "text": response["choices"][0]["message"]["content"] or ""}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--pid", type=int, required=True); ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    performance_prompt = "In exactly 24 words, explain why deterministic local testing makes software integrations easier to reproduce and diagnose."
    # A repeatable >512-token prefix makes the inherited server-side cache observable on the second identical request.
    cache_prompt = "Cache compatibility checkpoint. " + "The stable local profile uses one loopback endpoint and preserves deterministic evidence. " * 80 + "Reply only: cache-ok."
    before = sample(args.pid)
    performance = [request(args.url, args.model, performance_prompt, 48) for _ in range(3)]
    cache_first = request(args.url, args.model, cache_prompt, 8)
    cache_second = request(args.url, args.model, cache_prompt, 8)
    after = sample(args.pid)
    decode = [x["timings"].get("predicted_per_second", 0) for x in performance]
    prefill = [x["timings"].get("prompt_per_second", 0) for x in performance]
    elapsed = [x["elapsed_s"] for x in performance]
    output = {"model": args.model, "pid": args.pid, "before": before, "performance": performance,
              "performance_medians": {"decode_tok_s": median(decode), "prefill_tok_s": median(prefill),
                                      "e2e_s": median(elapsed)},
              "cache": {"first": cache_first, "second": cache_second,
                        "compatible": bool(cache_first["text"].strip() and cache_second["text"].strip())},
              "after": after}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"model": args.model, "performance_medians": output["performance_medians"],
                      "cache_compatible": output["cache"]["compatible"]}, indent=2))

if __name__ == "__main__":
    main()
