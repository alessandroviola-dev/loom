#!/usr/bin/env python3
"""REALGEN 001: exact-target greedy M1 autoregressive generation baseline.

This is deliberately an operational baseline, not an optimization experiment.
It uses the ordinary MLX/MLX-LM Qwen3 model at M=1 with BF16 KV.  It does not
inject Stretch-037 S1_R8 (whose exact source identity is M=5-only), use an
oracle continuation, a drafter, lookahead, prompt lookup, Medusa, or sampling.

Usage (from repository root):
  results-local/mlx/venv-mlx-lm-0.31.3/bin/python \
    scripts/loom_real_generation_baseline_001.py
"""
from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import os
import re
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load
from mlx_lm.generate import generate_step
from mlx_lm.models import cache as mlx_cache

REPO = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO / "results-local/mlx/models/Qwen3-8B-3bit"
CANONICAL_PREFIX = REPO / "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
MAX_GENERATED_TOKENS = 128
CLEANUP_INTERVAL = 10
RESULT_ROOT = REPO / "results-local/realgen/real-generation-baseline-001"

# Frozen, non-sensitive, representative prompt set.  The system message and
# target tokenizer chat template are fixed for every item.
PROMPTS = (
    {
        "id": "chat_01",
        "category": "ordinary_assistant_chat",
        "user": "Explain in two short paragraphs why clear error messages improve a command-line tool.",
    },
    {
        "id": "chat_02",
        "category": "ordinary_assistant_chat",
        "user": "Give a practical three-step plan for preparing a healthy vegetarian lunch on a busy weekday.",
    },
    {
        "id": "code_01",
        "category": "coding_software",
        "user": "Write a Python function named normalize_email that trims whitespace, lowercases the domain, and raises ValueError when @ is missing. Include two examples.",
    },
    {
        "id": "code_02",
        "category": "coding_software",
        "user": "In TypeScript, show a small retry wrapper for an async function. Stop after three attempts and preserve the final error.",
    },
    {
        "id": "reasoning_01",
        "category": "reasoning_technical",
        "user": "A service receives 240 requests per minute and each worker handles 18 requests per minute. Calculate the minimum whole number of workers needed, then state one operational caveat.",
    },
    {
        "id": "reasoning_02",
        "category": "reasoning_technical",
        "user": "Compare a mutex and a semaphore for protecting shared resources. Give one appropriate use case for each and one common mistake.",
    },
)
SYSTEM_MESSAGE = "You are a helpful assistant. Answer clearly and directly."


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def host_snapshot() -> dict[str, Any]:
    pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
    free_match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
    swap_match = re.search(r"used = ([0-9.,]+)([MG])", swap_text)
    if not free_match or not swap_match:
        raise RuntimeError("REALGEN_001_HOST_TELEMETRY_UNAVAILABLE")
    swap_mb = float(swap_match.group(1).replace(",", ".")) * (1024.0 if swap_match.group(2) == "G" else 1.0)
    # Darwin ru_maxrss is bytes; it is intentionally diagnostic only.
    rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return {
        "sampled_at_utc": datetime.now(timezone.utc).isoformat(),
        "free_memory_percent": int(free_match.group(1)),
        "swap_used_mb": swap_mb,
        "mlx_active_bytes": int(mx.get_active_memory()),
        "mlx_peak_bytes": int(mx.get_peak_memory()),
        "mlx_cache_bytes": int(mx.get_cache_memory()) if hasattr(mx, "get_cache_memory") else None,
        "process_max_rss_bytes_diagnostic": rss,
    }


def assert_host_ready(snapshot: dict[str, Any]) -> None:
    if snapshot["free_memory_percent"] < 60 or snapshot["swap_used_mb"] > 5600:
        raise RuntimeError(
            "REALGEN_001_NOT_STARTED_HOST_NOT_READY "
            f"free={snapshot['free_memory_percent']}% swap={snapshot['swap_used_mb']:.2f}MB"
        )


def assert_runtime() -> dict[str, str]:
    observed = {name: importlib.metadata.version(name) for name in EXPECTED}
    if Path(sys.prefix) != CANONICAL_PREFIX or observed != EXPECTED:
        raise RuntimeError(f"REALGEN_001_RUNTIME_MISMATCH prefix={sys.prefix} versions={observed}")
    return observed


def template_tokens(tokenizer: Any, user: str) -> list[int]:
    messages = [{"role": "system", "content": SYSTEM_MESSAGE}, {"role": "user", "content": user}]
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, enable_thinking=False)
    return [int(x) for x in ids]


def token_id(value: mx.array) -> int:
    mx.eval(value)
    return int(value.item())


def greedy_reference(model: Any, token_ids: list[int], eos_ids: set[int]) -> list[int]:
    """Ordinary supported MLX-LM generate_step reference, excluded from timing."""
    output: list[int] = []
    sampler = lambda logits: mx.argmax(logits, axis=-1)
    for token, _logprobs in generate_step(mx.array(token_ids), model, max_tokens=MAX_GENERATED_TOKENS, sampler=sampler):
        current = int(token)
        output.append(current)
        if current in eos_ids or len(output) >= MAX_GENERATED_TOKENS:
            break
    return output


def m1_dispatch_audit(model: Any, token_ids: list[int]) -> dict[str, Any]:
    """Observe ordinary built-in QuantizedLinear M1 calls without changing outputs."""
    original = nn.QuantizedLinear.__call__
    seen: dict[tuple[int, int], int] = {}

    def audited(self: Any, x: mx.array) -> mx.array:
        if x.ndim >= 2 and int(x.shape[-2]) == 1:
            packed = self["weight"]
            bits = int(self.bits)
            key = ((int(packed.shape[1]) * 32) // bits, int(packed.shape[0]))
            seen[key] = seen.get(key, 0) + 1
        return original(self, x)

    nn.QuantizedLinear.__call__ = audited
    try:
        cache = mlx_cache.make_prompt_cache(model)
        # Process all but the final prompt token, then one true M1 prediction.
        prompt = mx.array(token_ids)
        if prompt.size > 1:
            model(prompt[:-1][None], cache=cache)
            mx.eval([c.state for c in cache])
        logits = model(prompt[-1:][None], cache=cache)
        next_token = mx.argmax(logits[:, -1, :], axis=-1)
        token_id(next_token)
    finally:
        nn.QuantizedLinear.__call__ = original
    return {
        "dynamic_m1_quantized_linear_shapes_k_to_n": [
            {"K": key[0], "N": key[1], "calls": calls} for key, calls in sorted(seen.items())
        ],
        "dynamic_observation": "All observed calls delegated to the original built-in QuantizedLinear.__call__; no S1_R8 injection was installed.",
    }


def direct_greedy(model: Any, token_ids: list[int], eos_ids: set[int], timed: bool) -> dict[str, Any]:
    """Minimal real M1 loop: prompt -> predict -> commit -> KV -> predict.

    The final predicted token is a committed output but, as in normal generation,
    is not fed through the model after an EOS/length stop.  All earlier output
    tokens are fed as M1 inputs and update the BF16 KV cache.
    """
    cache = mlx_cache.make_prompt_cache(model)
    prompt = mx.array(token_ids)
    prefill_started = time.perf_counter()
    while prompt.size > 1:
        n = int(prompt.size - 1)
        model(prompt[:n][None], cache=cache)
        mx.eval([c.state for c in cache])
        prompt = prompt[n:]
    prefill_finished = time.perf_counter()

    generated: list[int] = []
    latencies: list[float] = []
    cleanup_events: list[dict[str, Any]] = []
    generation_started = time.perf_counter()
    first_token_at: float | None = None
    current = prompt
    eos = False

    while len(generated) < MAX_GENERATED_TOKENS:
        before = time.perf_counter()
        logits = model(current[None], cache=cache)
        next_value = mx.argmax(logits[:, -1, :], axis=-1)
        next_id = token_id(next_value)
        after = time.perf_counter()
        if first_token_at is None:
            first_token_at = after
        latencies.append(after - before)
        generated.append(next_id)

        if len(generated) % CLEANUP_INTERVAL == 0:
            cleanup_started = time.perf_counter()
            gc.collect()
            mx.clear_cache()
            gc.collect()
            cleanup_events.append({"after_committed_generated_token": len(generated), "wall_seconds": time.perf_counter() - cleanup_started})

        if next_id in eos_ids:
            eos = True
            break
        current = mx.array([next_id], dtype=mx.uint32)

    generation_finished = time.perf_counter()
    if first_token_at is None:
        raise RuntimeError("REALGEN_001_NO_GENERATED_TOKEN")
    prefill_wall = prefill_finished - prefill_started
    generation_wall = generation_finished - generation_started
    end_to_end = prefill_finished - prefill_started + generation_wall
    cleanup_wall = sum(event["wall_seconds"] for event in cleanup_events)
    forward_wall = sum(latencies)
    return {
        "generated_token_ids": generated,
        "generated_tokens": len(generated),
        "eos": eos,
        "prompt_prefill_wall_seconds": prefill_wall,
        "time_to_first_generated_token_seconds": first_token_at - prefill_started,
        "generation_only_wall_seconds": generation_wall,
        "generation_forward_only_wall_seconds_excluding_cleanup": forward_wall,
        "end_to_end_wall_seconds": end_to_end,
        "generation_tokens_per_second": len(generated) / generation_wall,
        "end_to_end_output_tokens_per_second": len(generated) / end_to_end,
        "prefill_tokens_per_second": len(token_ids) / prefill_wall,
        "per_token_latency_seconds": latencies,
        "per_token_latency_distribution_seconds": {
            "min": min(latencies),
            "p50": median(latencies),
            "p95": sorted(latencies)[max(0, int(0.95 * (len(latencies) - 1)))],
            "max": max(latencies),
        },
        "cleanup_events": cleanup_events,
        "cleanup_wall_seconds": cleanup_wall,
        "timed": timed,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    generated = sum(x["benchmark"]["generated_tokens"] for x in results)
    generation_wall = sum(x["benchmark"]["generation_only_wall_seconds"] for x in results)
    end_to_end_wall = sum(x["benchmark"]["end_to_end_wall_seconds"] for x in results)
    cleanup_wall = sum(x["benchmark"]["cleanup_wall_seconds"] for x in results)
    rates = [x["benchmark"]["generation_tokens_per_second"] for x in results]
    return {
        "total_generated_tokens": generated,
        "total_generation_only_wall_seconds": generation_wall,
        "total_end_to_end_wall_seconds": end_to_end_wall,
        "pooled_generation_tokens_per_second": generated / generation_wall,
        "pooled_end_to_end_output_tokens_per_second": generated / end_to_end_wall,
        "median_per_prompt_generation_tokens_per_second": median(rates),
        "total_cleanup_wall_seconds": cleanup_wall,
    }


def main() -> int:
    started = time.perf_counter()
    run_dir = RESULT_ROOT / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {"classification": "RUNNING", "experiment": "REALGEN 001", "no_oracle": True, "greedy": True, "temperature": 0, "sampling_disabled": True, "speculative_decoding": False, "drafter": False, "prompt_lookup": False, "medusa": False, "lookahead": False, "s1_r8_at_m1": "INELIGIBLE: exact Stretch-037 injection guards x.shape[-2] == 5", "cleanup_policy": "Operational baseline translation: gc.collect() -> mx.clear_cache() -> gc.collect() after each 10 committed generated tokens; not a new promoted scientific cadence."}
    try:
        versions = assert_runtime()
        host_before = host_snapshot()
        summary["host_before"] = host_before
        assert_host_ready(host_before)

        load_started = time.perf_counter()
        model, tokenizer = load(str(MODEL_DIR), lazy=False)
        model.eval()
        mx.eval(model.parameters())
        load_finished = time.perf_counter()

        tokenizer_files = {name: sha256_file(MODEL_DIR / name) for name in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")}
        tokenizer_info = {
            "class": type(tokenizer._tokenizer).__name__,
            "model_dir": str(MODEL_DIR),
            "tokenizer_files_sha256": tokenizer_files,
            "base_vocab_size": int(tokenizer.vocab_size),
            "effective_vocab_size_from_config": 151936,
            "bos_token": tokenizer.bos_token,
            "bos_token_id": None,
            "config_bos_token_id": 151643,
            "eos_token": tokenizer.eos_token,
            "eos_token_ids": sorted(int(x) for x in tokenizer.eos_token_ids),
            "chat_template_sha256": hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
            "chat_template_used": True,
            "special_tokens_map_sha256": tokenizer_files["special_tokens_map.json"],
        }
        eos_ids = set(int(x) for x in tokenizer.eos_token_ids)
        prompt_records = [{**prompt, "token_ids": template_tokens(tokenizer, prompt["user"])} for prompt in PROMPTS]

        # Separate, excluded warmup: model is loaded, Metal kernels compile, and
        # an M1 BF16-KV path is exercised. No cache purge is performed afterwards.
        warmup_started = time.perf_counter()
        warmup = direct_greedy(model, prompt_records[0]["token_ids"], eos_ids, timed=False)
        warmup_finished = time.perf_counter()
        dispatch = m1_dispatch_audit(model, prompt_records[0]["token_ids"])

        results: list[dict[str, Any]] = []
        all_snapshots: list[dict[str, Any]] = [host_snapshot()]
        for prompt in prompt_records:
            before = host_snapshot()
            if before["free_memory_percent"] < 5 or before["swap_used_mb"] > 5600:
                raise RuntimeError(f"REALGEN_001_RUNTIME_ABORT free={before['free_memory_percent']}% swap={before['swap_used_mb']:.2f}MB")
            reference_ids = greedy_reference(model, prompt["token_ids"], eos_ids)
            benchmark = direct_greedy(model, prompt["token_ids"], eos_ids, timed=True)
            if benchmark["generated_token_ids"] != reference_ids:
                raise RuntimeError(
                    f"REALGEN_BASELINE_CORRECTNESS_FAIL prompt={prompt['id']} "
                    f"reference={reference_ids} driver={benchmark['generated_token_ids']}"
                )
            after = host_snapshot()
            all_snapshots.extend([before, after])
            if after["free_memory_percent"] < 5 or after["swap_used_mb"] > 5600:
                raise RuntimeError(f"REALGEN_001_RUNTIME_ABORT free={after['free_memory_percent']}% swap={after['swap_used_mb']:.2f}MB")
            results.append({
                "id": prompt["id"],
                "category": prompt["category"],
                "user_prompt": prompt["user"],
                "post_template_token_count": len(prompt["token_ids"]),
                "post_template_token_ids": prompt["token_ids"],
                "reference_generated_token_ids": reference_ids,
                "reference_correctness": "EXACT_PASS",
                "benchmark": benchmark,
                "resource_before": before,
                "resource_after": after,
            })

        aggregate = summarize(results)
        min_free = min(s["free_memory_percent"] for s in all_snapshots)
        peak_swap = max(s["swap_used_mb"] for s in all_snapshots)
        peak_mlx = max(s["mlx_peak_bytes"] for s in all_snapshots)
        final_resource = host_snapshot()
        run_payload = {
            "classification": "REALGEN_001_BASELINE_COMPLETE",
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime": {"versions": versions, "python_prefix": sys.prefix, "device": mx.device_info(), "model": "Qwen3-8B", "quantization": "affine 3-bit/group64", "dtype": "BF16", "kv": "ordinary BF16 KV", "M": 1, "m1_qmv_path": "ordinary built-in MLX qmv_fast", "s1_r8": "not injected; exact source identity is M=5 only"},
            "tokenizer": tokenizer_info,
            "prompt_template": {"system": SYSTEM_MESSAGE, "add_generation_prompt": True, "enable_thinking": False},
            "dispatch_audit": dispatch,
            "startup_and_warmup": {"model_load_and_materialization_wall_seconds": load_finished - load_started, "warmup_wall_seconds": warmup_finished - warmup_started, "warmup_generated_tokens": warmup["generated_tokens"], "warmup_excluded_from_timing": True, "startup_total_wall_seconds": time.perf_counter() - started},
            "cleanup_policy": summary["cleanup_policy"],
            "prompts": results,
            "aggregate": aggregate,
            "resources": {"minimum_free_memory_percent": min_free, "peak_swap_used_mb": peak_swap, "peak_mlx_bytes": peak_mlx, "final": final_resource},
            "correctness": {"all_prompts_exact_generated_token_id_match": True, "reference_path": "ordinary supported mlx_lm.generate_step greedy argmax", "driver_path": "minimal direct model M1 loop with mlx_lm BF16 prompt cache"},
        }
        (run_dir / "summary.json").write_text(json.dumps(run_payload, indent=2) + "\n")
        summary.update({"classification": "REALGEN_001_BASELINE_COMPLETE", "summary": str(run_dir / "summary.json"), "aggregate": aggregate})
    except Exception as exc:
        summary.update({"classification": "REALGEN_001_NOT_STARTED_HOST_NOT_READY" if str(exc).startswith("REALGEN_001_NOT_STARTED_HOST_NOT_READY") else "REALGEN_001_INCOMPLETE", "error": f"{type(exc).__name__}: {exc}"})
    (run_dir / "run-status.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Classification: {summary['classification']}\nSummary: {summary.get('summary', run_dir / 'run-status.json')}")
    return 0 if summary["classification"] == "REALGEN_001_BASELINE_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
