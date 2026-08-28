#!/usr/bin/env python3
"""LOOM Qwen3-30B-A3B Q4 interactive terminal chat (greedy, PACKED only)."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mlx.core as mx
import numpy as np
from mlx_lm.models.base import create_attention_mask
from mlx_lm.tokenizer_utils import load as load_tokenizer

import loom_30b_moe_expert_major_backend_001 as packed
import loom_30b_runtime_core_v1_001 as core

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "results-local/moe/models/Qwen3-30B-A3B-MLX-4bit"
CONTRACT = ROOT / "results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/runtime-contract.json"
LAYERS, TOP_K, EOS = core.LAYERS, core.TOP_K, 151645
EXPERT_BYTES = core.EXPERT_BYTES
ORDER = tuple((projection, component) for projection in core.PROJS for component in core.COMPS)


def now() -> float:
    return time.perf_counter()


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * q
    lo, hi = math.floor(index), math.ceil(index)
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (index - lo)


def shell(argv: list[str]) -> str:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception as exc:
        return f"UNAVAILABLE: {exc!r}"


def swap_mib(text: str) -> float | None:
    import re
    match = re.search(r"used = ([0-9.,]+)M", text)
    return float(match.group(1).replace(",", ".")) if match else None


def memory_snapshot(label: str) -> dict[str, Any]:
    try:
        rss = int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())], text=True).strip()) * 1024
    except Exception:
        rss = None
    swap = shell(["sysctl", "-n", "vm.swapusage"])
    pressure = shell(["memory_pressure"])
    return {
        "label": label,
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "rss_bytes": rss,
        "rss_peak_ru_maxrss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "swap_MiB": swap_mib(swap),
        "swapusage": swap,
        "memory_pressure": pressure,
        "unsafe_memory_pressure": "CRITICAL" in pressure.upper(),
        "mlx_active_bytes": int(mx.get_active_memory()),
        "mlx_peak_bytes": int(mx.get_peak_memory()),
        "mlx_cache_bytes": int(mx.get_cache_memory()),
    }


def component_specs(sources: dict[tuple[int, str, str], dict[str, Any]]) -> dict[int, list[tuple[Any, ...]]]:
    """The exact nine-component Q4 order expected by PackedExpertBackend."""
    specs: dict[int, list[tuple[Any, ...]]] = {}
    for layer in range(LAYERS):
        rows, total = [], 0
        for projection, component in ORDER:
            record = sources[(layer, projection, component)]
            count = record["stored_bytes"] // 128
            rows.append((projection, component, record, count, total))
            total += count
        if total != EXPERT_BYTES:
            raise RuntimeError(f"canonical Q4 component geometry mismatch at layer {layer}")
        specs[layer] = rows
    return specs


def logit_sha(logits: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(logits, dtype=np.float32).tobytes()).hexdigest()


def routing_at_last(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"layer": row["layer"], "expert_ids": row["topk_ids"][0][-1]} for row in rows]


class Runtime:
    """Exact external top-8 Q4 path with no SOURCE branch or expert cache."""

    def __init__(self) -> None:
        started = now()
        self.tokenizer = load_tokenizer(MODEL)
        config = json.loads((MODEL / "config.json").read_text())
        records = core.inventory(core.headers())
        included = [record for record in records if record["category"] != "routed_expert"]
        if len(included) != 919:
            raise RuntimeError("resident backbone selection mismatch")
        self.sources = core.catalog(records)
        self.specs = component_specs(self.sources)
        mx.clear_cache()
        mx.reset_peak_memory()
        self.backbone = core.load_backbone(config, included)
        ownership = core.ownership(self.backbone)
        if not ownership["pass"]:
            raise RuntimeError("routed expert tensors are resident")
        self.backend = packed.PackedExpertBackend(CONTRACT, mx, core.DT, time.perf_counter_ns)
        if self.backend.name != "PACKED" or self.backend.persistent_cache or self.backend.source_fallback:
            raise RuntimeError("PACKED-only/no-cache contract violated")
        self.stop_ids, self.assistant_close = self._validate_chat_controls()
        self.messages: list[dict[str, str]] = []
        self.cache = [core.BF16KVCache() for _ in range(LAYERS)]
        # Tokens already represented in cache.  The current final generated token
        # deliberately remains unprocessed until the next decode/turn boundary.
        self.processed_ids: list[int] = []
        self.pending_token: int | None = None
        self.ready_wall_seconds = now() - started

    def reset(self) -> None:
        self.messages.clear()
        self.cache = [core.BF16KVCache() for _ in range(LAYERS)]
        self.processed_ids.clear()
        self.pending_token = None
        mx.clear_cache()

    def close(self) -> None:
        if getattr(self, "backend", None) is not None:
            self.backend.close()
        if getattr(self, "backbone", None) is not None:
            del self.backbone
        gc.collect()
        mx.clear_cache()

    def assert_policy(self) -> dict[str, Any]:
        own = core.ownership(self.backbone)
        return {
            "backend": self.backend.name,
            "source_fallback_count": int(self.backend.fallback_count),
            "persistent_expert_payload_cache": bool(self.backend.persistent_cache),
            "resident_routed_expert_tensor_count": own["routed_expert_tensor_count"],
            "resident_routed_expert_bytes": own["routed_expert_logical_bytes"],
            "pass": self.backend.name == "PACKED" and self.backend.fallback_count == 0 and not self.backend.persistent_cache and own["pass"],
        }

    def forward(self, token_ids: list[int], phase: str) -> dict[str, Any]:
        """Canonical Qwen external forward; a serial transient expert per route."""
        if not token_ids:
            raise RuntimeError("empty forward")
        started = now()
        embedded = self.backbone.embed_tokens(mx.array([token_ids], dtype=mx.int32))
        mx.eval(embedded)
        mask = create_attention_mask(embedded, self.cache[0])
        routes: list[dict[str, Any]] = []
        expert_requests_before = self.backend.requests
        for layer_no, layer in enumerate(self.backbone.layers):
            hidden = embedded + core.attention_with_bf16_cache(layer.self_attn, layer.input_layernorm(embedded), mask, self.cache[layer_no])
            normalized = layer.post_attention_layernorm(hidden)
            mx.eval(hidden, normalized)
            router_logits, selected, route_weights = core.route(layer.external_moe.gate, normalized)
            mx.eval(router_logits, selected, route_weights)
            ids = np.asarray(selected).astype(int)
            route_weights_np = np.asarray(route_weights).copy()
            outputs = []
            for position in range(normalized.shape[1]):
                serial = []
                for expert_id in ids[0, position].tolist():
                    weights, _, calls = self.backend.load_weights(layer_no, int(expert_id), self.specs)
                    if calls != 1:
                        raise RuntimeError("PACKED expert read contract violated")
                    output = core.direct_expert(normalized[:, position:position + 1, :], weights)
                    mx.eval(output)
                    detached = mx.array(np.array(output))
                    mx.eval(detached)
                    serial.append(detached)
                    del weights, output
                stacked = mx.stack(serial, axis=-2)
                moe = (stacked * route_weights[:, position:position + 1, :, None]).sum(axis=-2)
                mx.eval(moe)
                outputs.append(moe)
                del serial, stacked, moe
            moe_output = mx.concatenate(outputs, axis=1)
            next_hidden = hidden + moe_output
            mx.eval(next_hidden)
            routes.append({"layer": layer_no, "topk_ids": ids.tolist(), "topk_weights": route_weights_np.tolist()})
            del outputs, moe_output, hidden, normalized, router_logits, selected, route_weights
            mx.clear_cache()
            embedded = next_hidden
        normalized = self.backbone.norm(embedded)
        mx.eval(normalized)
        logits = self.backbone.lm_head(normalized)
        mx.eval(logits)
        logits_np = np.asarray(logits).copy()
        del embedded, normalized, logits
        if not bool(np.isfinite(logits_np).all()):
            raise RuntimeError("non-finite final logits")
        return {
            "phase": phase,
            "input_token_ids": list(map(int, token_ids)),
            "wall_seconds": now() - started,
            "logits": logits_np,
            "final_logits_float32_sha256": logit_sha(logits_np[0, -1]),
            "routing": routes,
            "routing_last_position": routing_at_last(routes),
            "expert_requests": self.backend.requests - expert_requests_before,
        }

    def _template(self, messages: list[dict[str, str]], *, generation: bool) -> list[int]:
        return list(map(int, self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=generation, enable_thinking=False)))

    def _validate_chat_controls(self) -> tuple[frozenset[int], tuple[int, ...]]:
        """Mechanically bind the frozen template terminator to tokenizer stop semantics."""
        stop_ids = frozenset(map(int, getattr(self.tokenizer, "eos_token_ids", [])))
        assistant_empty = self._template([{"role": "assistant", "content": ""}], generation=False)
        if len(assistant_empty) < 2 or assistant_empty[-2:] != [EOS, 198]:
            raise RuntimeError("incompatible frozen assistant terminator template")
        if stop_ids != frozenset({EOS}) or assistant_empty[-2] not in stop_ids:
            raise RuntimeError("incompatible tokenizer eos/assistant-terminator semantics")
        user_empty = self._template([{"role": "user", "content": ""}], generation=False)
        user_generation = self._template([{"role": "user", "content": ""}], generation=True)
        if not user_generation[:len(user_empty)] == user_empty or len(user_generation) == len(user_empty):
            raise RuntimeError("incompatible frozen user/generation template controls")
        return stop_ids, tuple(assistant_empty[-2:])

    def template_ids(self, messages: list[dict[str, str]]) -> tuple[str, list[int]]:
        kwargs = {"add_generation_prompt": True, "enable_thinking": False}
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, **kwargs)
        return text, self._template(messages, generation=True)

    def _next_turn_suffix(self, user_text: str, target_ids: list[int]) -> list[int]:
        """Derive assistant-close + user + generation controls without transcript scanning."""
        user_only = [{"role": "user", "content": user_text}]
        user_frame = self._template(user_only, generation=False)
        user_generation = self._template(user_only, generation=True)
        if user_generation[:len(user_frame)] != user_frame or len(user_generation) <= len(user_frame):
            raise RuntimeError("frozen chat-template user/generation suffix mismatch")
        suffix = list(self.assistant_close) + user_generation
        if target_ids[-len(user_generation):] != user_generation:
            raise RuntimeError("full template does not end in canonical user/generation suffix")
        return suffix

    def _prefill_for_turn(self, user_text: str, target_ids: list[int]) -> tuple[dict[str, Any], dict[str, Any]]:
        """Advance only original KV IDs plus mechanically derived next-turn controls."""
        if not self.processed_ids:
            suffix = target_ids
            result = self.forward(suffix, "INITIAL_PREFILL")
            mechanics = {"state_reused": False, "processed_prior_tokens": 0, "new_tokens_processed": len(suffix), "full_target_tokens": len(target_ids), "mechanism": "initial canonical chat-template prefill", "full_transcript_reprefill": False}
        else:
            boundary = self._next_turn_suffix(user_text, target_ids)
            suffix = ([] if self.pending_token is None else [self.pending_token]) + boundary
            if not suffix:
                raise RuntimeError("missing incremental chat suffix")
            result = self.forward(suffix, "INCREMENTAL_TURN_PREFILL")
            mechanics = {"state_reused": True, "processed_prior_tokens": len(self.processed_ids), "new_tokens_processed": len(suffix), "full_target_tokens": len(target_ids), "mechanism": "original pending assistant token plus mechanically derived assistant-close/user/generation suffix", "canonical_reencoding_token_count": len(target_ids), "full_transcript_reprefill": False}
        self.processed_ids.extend(suffix)
        self.pending_token = None
        return result, mechanics

    def generate_turn(self, user_text: str, max_tokens: int, emit: bool = False) -> dict[str, Any]:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        submitted = now()
        turn_messages = [*self.messages, {"role": "user", "content": user_text}]
        formatted, target_ids = self.template_ids(turn_messages)
        prefill, mechanics = self._prefill_for_turn(user_text, target_ids)
        generated: list[int] = []
        visible_ids: list[int] = []
        records: list[dict[str, Any]] = []
        emitted_segments: list[str] = []
        flush_overheads: list[float] = []
        detokenizer = self.tokenizer.detokenizer  # mlx-lm 0.31.3 returns a fresh stateful instance.
        detokenizer.reset()
        first_available = now()
        token_id = int(np.argmax(prefill["logits"][0, -1]))
        ttft = first_available - submitted
        # This spans submit, canonical templating, incremental prefill, and argmax.
        for index in range(max_tokens):
            if index == 0:
                token, source, forward = token_id, "PREFILL_FINAL_POSITION", prefill
            else:
                forward = self.forward([generated[-1]], "DECODE")
                token, source = int(np.argmax(forward["logits"][0, -1])), "ONE_POSITION_DECODE"
            generated.append(token)
            if token in self.stop_ids:
                records.append({"token_index": index + 1, "output_token_id": token, "decoded_fragment": "", "emission_source": source, "forward_wall_seconds": forward["wall_seconds"], "final_logits_float32_sha256": forward["final_logits_float32_sha256"], "routing_last_position": forward["routing_last_position"], "flush_overhead_seconds": 0.0, "suppressed_stop_token": True})
                break
            visible_ids.append(token)
            detokenizer.add_token(token)
            fragment = detokenizer.last_segment
            emitted_segments.append(fragment)
            flush_start = now()
            if emit and fragment:
                print(fragment, end="", flush=True)
            flush_overhead = now() - flush_start
            flush_overheads.append(flush_overhead)
            records.append({"token_index": index + 1, "output_token_id": token, "decoded_fragment": fragment, "emission_source": source, "forward_wall_seconds": forward["wall_seconds"], "final_logits_float32_sha256": forward["final_logits_float32_sha256"], "routing_last_position": forward["routing_last_position"], "flush_overhead_seconds": flush_overhead, "suppressed_stop_token": False})
            if index + 1 < max_tokens:
                # The next forward materializes this exact generated ID in KV.
                self.processed_ids.append(token)
        eos = bool(generated and generated[-1] in self.stop_ids)
        detokenizer.finalize()
        fragment = detokenizer.last_segment
        emitted_segments.append(fragment)
        flush_start = now()
        if emit and fragment:
            print(fragment, end="", flush=True)
        flush_overheads.append(now() - flush_start)
        self.pending_token = None if eos else generated[-1]
        text = detokenizer.text
        normal_decode = self.tokenizer.decode(visible_ids, skip_special_tokens=False)
        if text != normal_decode:
            raise RuntimeError("stateful streamed text differs from normal final decode")
        self.messages = [*turn_messages, {"role": "assistant", "content": text}]
        decode_walls = [row["forward_wall_seconds"] for row in records[1:]]
        return {
            "user": user_text,
            "formatted_chat_text": formatted,
            "input_token_ids": target_ids,
            "input_token_count": len(target_ids),
            "generated_token_ids": generated,
            "visible_generated_token_ids": visible_ids,
            "generated_text": text,
            "normal_final_decode": normal_decode,
            "streamed_text": "".join(emitted_segments),
            "output_tokens": len(generated),
            "eos_reached": eos,
            "ttft_seconds": ttft,
            "prefill_wall_seconds": prefill["wall_seconds"],
            "decode_tok_s": len(decode_walls) / sum(decode_walls) if decode_walls and sum(decode_walls) else None,
            "decode_walls_seconds": decode_walls,
            "p50_decode_wall_seconds": percentile(decode_walls, .5),
            "p95_decode_wall_seconds": percentile(decode_walls, .95),
            "flush_p95_seconds": percentile(flush_overheads, .95),
            "streamed_before_completion": bool(emit and len(visible_ids) > 1),
            "state_reuse": mechanics,
            "records": records,
            "policy": self.assert_policy(),
        }


def chat(max_tokens: int) -> int:
    runtime = Runtime()
    print("LOOM Qwen3-30B-A3B Q4 interactive chat. /reset, /exit")
    try:
        while True:
            try:
                line = input("\nYou> ")
            except EOFError:
                print()
                break
            if line.strip() == "/exit":
                break
            if line.strip() == "/reset":
                runtime.reset()
                print("Conversation reset.")
                continue
            if not line.strip():
                continue
            print("Assistant> ", end="", flush=True)
            result = runtime.generate_turn(line, max_tokens, emit=True)
            print()
            if not result["policy"]["pass"]:
                raise RuntimeError("runtime policy violation")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        runtime.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="LOOM Q4 PACKED-only interactive terminal chat")
    parser.add_argument("--max-tokens", type=int, default=256, help="greedy maximum generated tokens per turn")
    args = parser.parse_args()
    return chat(args.max_tokens)


if __name__ == "__main__":
    raise SystemExit(main())
