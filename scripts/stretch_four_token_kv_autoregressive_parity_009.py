#!/usr/bin/env python3
"""LOOM Stretch 009 — four-token KV autoregressive parity.

Resident official Qwen3 vs LOOM phase-streamed raw weights with 36 persistent
ordinary BF16 KVCache objects. Frozen prompt, deterministic argmax, exactly four
feedback tokens. Progress/final child payloads are file-backed to avoid the
captured-stdout pipe stall diagnosed in Stretch 008.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import platform
import statistics
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

SOURCE_008_BLOB = "03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf"
SOURCE_008_PIPEFIX_BLOB = "8b2ce5902d3ed45c9120273fab415fe67a026d4a"
SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"

EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_QUANTIZATION = {"group_size": 64, "bits": 3}
EXPECTED_TOTAL_BYTES = 3_583_928_320
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_EMBED_BYTES = 272_269_312
EXPECTED_NORM_BYTES = 8_192
EXPECTED_HEAD_BYTES = 272_269_312
EXPECTED_KV_TOTAL_BYTES = 37_748_736
PROMPT_TOKEN_IDS = [[1, 42, 2048, 151935]]
PROMPT_LEN = 4
GENERATED_TOKENS = 4
FINAL_OFFSET = PROMPT_LEN + GENERATED_TOKENS

MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
POLL_SECONDS = 0.5


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_bucket(phase: str) -> str:
    if phase == "host_gate":
        return "host_gate"
    if phase.startswith("resident_"):
        return "resident"
    if phase.startswith("stream_prompt"):
        return "stream_prompt"
    if phase.startswith("stream_token_"):
        return "stream_tokens"
    return "other"


def summarize_phase_telemetry(samples: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for sample in samples:
        groups.setdefault(phase_bucket(str(sample.get("phase", ""))), []).append(sample)
    out: dict[str, dict] = {}
    for key, rows in groups.items():
        frees = [r.get("memory_free_percent") for r in rows if r.get("memory_free_percent") is not None]
        swaps = [r.get("swap_used_mb") for r in rows if r.get("swap_used_mb") is not None]
        rss = [r.get("child_rss_mb") for r in rows if r.get("child_rss_mb") is not None]
        out[key] = {
            "samples": len(rows),
            "min_memory_free_percent": min(frees) if frees else None,
            "peak_swap_used_mb": max(swaps) if swaps else None,
            "peak_child_rss_mb": max(rss) if rss else None,
        }
    return out


def child_main(argv: list[str]) -> int:
    # Imports intentionally live inside child mode so the parent remains a
    # standard-library watchdog process.
    import importlib.metadata as md
    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm.models import qwen3
    from mlx_lm.models.base import create_attention_mask
    from mlx_lm.models.cache import KVCache, make_prompt_cache
    from mlx_lm.utils import load_model

    if len(argv) != 6:
        raise RuntimeError(f"child expected 6 args, got {len(argv)}")

    model_dir = Path(argv[0])
    weight_path = Path(argv[1])
    config_path = Path(argv[2])
    state_path = Path(argv[3])
    final_path = Path(argv[4])
    prompt_token_ids = json.loads(argv[5])

    config = json.loads(config_path.read_text(encoding="utf-8"))
    args = qwen3.ModelArgs.from_dict(config)
    quant = config["quantization"]

    def mem() -> dict:
        return {
            "active_bytes": int(mx.get_active_memory()),
            "cache_bytes": int(mx.get_cache_memory()),
            "peak_bytes": int(mx.get_peak_memory()),
        }

    def save_state(phase: str, **extra) -> dict:
        payload = {"phase": phase, "memory": mem(), **extra}
        state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload

    def select_weights(prefix: str, strip_prefix: str = "") -> dict:
        all_weights = mx.load(str(weight_path))
        selected = {}
        for name, value in all_weights.items():
            if name.startswith(prefix):
                local_name = name[len(strip_prefix):] if strip_prefix else name
                selected[local_name] = value
        del all_weights
        gc.collect()
        return selected

    def selected_bytes(selected: dict) -> int:
        return sum(int(v.nbytes) for v in selected.values())

    def quantize_and_load(module, selected: dict):
        def class_predicate(path, leaf):
            return hasattr(leaf, "to_quantized") and f"{path}.scales" in selected

        nn.quantize(
            module,
            group_size=quant["group_size"],
            bits=quant["bits"],
            mode=quant.get("mode", "affine"),
            class_predicate=class_predicate,
        )
        module.load_weights(list(selected.items()), strict=True)
        module.eval()
        return module

    class EmbeddingStage(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed_tokens = nn.Embedding(args.vocab_size, args.hidden_size)

        def __call__(self, ids):
            return self.embed_tokens(ids)

    class NormStage(nn.Module):
        def __init__(self):
            super().__init__()
            self.norm = nn.RMSNorm(args.hidden_size, eps=args.rms_norm_eps)

        def __call__(self, x):
            return self.norm(x)

    class HeadStage(nn.Module):
        def __init__(self):
            super().__init__()
            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)

        def __call__(self, x):
            return self.lm_head(x)

    def build_block(layer_id: int):
        marker = f"model.layers.{layer_id}."
        selected = select_weights(marker, marker)
        if len(selected) != EXPECTED_LAYER_TENSORS:
            raise RuntimeError(
                f"layer {layer_id} local tensor count {len(selected)} != {EXPECTED_LAYER_TENSORS}"
            )
        layer_bytes = selected_bytes(selected)
        if layer_bytes != EXPECTED_LAYER_BYTES:
            raise RuntimeError(
                f"layer {layer_id} selected bytes {layer_bytes} != {EXPECTED_LAYER_BYTES}"
            )
        block = qwen3.TransformerBlock(args)

        def class_predicate(path, leaf):
            return hasattr(leaf, "to_quantized") and f"{path}.scales" in selected

        nn.quantize(
            block,
            group_size=quant["group_size"],
            bits=quant["bits"],
            mode=quant.get("mode", "affine"),
            class_predicate=class_predicate,
        )
        block.load_weights(list(selected.items()), strict=True)
        block.eval()
        return block, selected

    def make_ids(values):
        ids = mx.array(values, dtype=mx.int32)
        mx.eval(ids)
        return ids

    def token_value(logits) -> int:
        token = mx.argmax(logits[:, -1, :], axis=-1).astype(mx.int32)
        mx.eval(token)
        return int(token.item())

    def cache_snapshot(caches) -> dict:
        offsets = [int(c.offset) for c in caches]
        nbytes = [int(c.nbytes) for c in caches]
        return {
            "count": len(caches),
            "offsets": offsets,
            "all_offsets_equal": len(set(offsets)) == 1,
            "total_nbytes": sum(nbytes),
            "per_layer_nbytes": nbytes,
        }

    def run_streamed_pass(ids, caches, label: str):
        pass_started = time.perf_counter()
        stage_records: dict[str, dict] = {}

        # Embedding.
        embed_pre_active = int(mx.get_active_memory())
        embed_selected = select_weights("model.embed_tokens.", "model.")
        embed_bytes = selected_bytes(embed_selected)
        if embed_bytes != EXPECTED_EMBED_BYTES:
            raise RuntimeError(f"embedding selected bytes {embed_bytes} != {EXPECTED_EMBED_BYTES}")
        embed_stage = EmbeddingStage()
        quantize_and_load(embed_stage, embed_selected)
        embed_pre_eval_active = int(mx.get_active_memory())
        started = time.perf_counter()
        mx.eval(embed_stage.parameters())
        embed_materialize_wall = time.perf_counter() - started
        embed_post_materialize_active = int(mx.get_active_memory())
        started = time.perf_counter()
        h = embed_stage(ids)
        mx.eval(h)
        embed_forward_wall = time.perf_counter() - started
        del embed_stage, embed_selected
        gc.collect()
        mx.clear_cache()
        gc.collect()
        embed_post_clear_active = int(mx.get_active_memory())
        stage_records["embedding"] = {
            "selected_bytes": embed_bytes,
            "pre_active_bytes": embed_pre_active,
            "pre_eval_active_bytes": embed_pre_eval_active,
            "post_materialize_active_bytes": embed_post_materialize_active,
            "post_clear_active_bytes": embed_post_clear_active,
            "pre_eval_delta_bytes": embed_pre_eval_active - embed_pre_active,
            "materialized_delta_bytes": embed_post_materialize_active - embed_pre_active,
            "post_clear_delta_bytes": embed_post_clear_active - embed_pre_active,
            "materialize_wall_seconds": round(embed_materialize_wall, 6),
            "forward_wall_seconds": round(embed_forward_wall, 6),
        }
        save_state(f"stream_{label}_embedding_complete", stage=stage_records["embedding"], cache=cache_snapshot(caches))

        # Transformer body with persistent per-layer cache.
        mask = create_attention_mask(h, caches[0])
        cycles: list[dict] = []
        total_materialize_wall = 0.0
        total_forward_wall = 0.0

        for layer_id in range(args.num_hidden_layers):
            pre_active = int(mx.get_active_memory())
            pre_cache = cache_snapshot(caches)
            block, selected = build_block(layer_id)
            pre_eval_active = int(mx.get_active_memory())

            started = time.perf_counter()
            mx.eval(block.parameters())
            materialize_wall = time.perf_counter() - started
            total_materialize_wall += materialize_wall
            post_materialize_active = int(mx.get_active_memory())

            started = time.perf_counter()
            out = block(h, mask, caches[layer_id])
            mx.eval(out)
            forward_wall = time.perf_counter() - started
            total_forward_wall += forward_wall

            old_h = h
            h = out
            del old_h, block, selected
            gc.collect()
            mx.clear_cache()
            gc.collect()
            post_clear_active = int(mx.get_active_memory())
            post_cache = cache_snapshot(caches)

            cycle = {
                "layer_id": layer_id,
                "pre_active_bytes": pre_active,
                "pre_eval_active_bytes": pre_eval_active,
                "post_materialize_active_bytes": post_materialize_active,
                "post_clear_active_bytes": post_clear_active,
                "pre_eval_delta_bytes": pre_eval_active - pre_active,
                "materialized_delta_bytes": post_materialize_active - pre_active,
                "post_clear_delta_bytes": post_clear_active - pre_active,
                "cache_total_before_bytes": pre_cache["total_nbytes"],
                "cache_total_after_bytes": post_cache["total_nbytes"],
                "layer_cache_offset_after": int(caches[layer_id].offset),
                "layer_cache_nbytes_after": int(caches[layer_id].nbytes),
                "materialize_wall_seconds": round(materialize_wall, 6),
                "forward_wall_seconds": round(forward_wall, 6),
            }
            cycles.append(cycle)
            save_state(f"stream_{label}_layer_{layer_id}_complete", cycle=cycle, cache=post_cache)

        # Final RMSNorm.
        norm_pre_active = int(mx.get_active_memory())
        norm_selected = select_weights("model.norm.", "model.")
        norm_bytes = selected_bytes(norm_selected)
        if norm_bytes != EXPECTED_NORM_BYTES:
            raise RuntimeError(f"norm selected bytes {norm_bytes} != {EXPECTED_NORM_BYTES}")
        norm_stage = NormStage()
        quantize_and_load(norm_stage, norm_selected)
        norm_pre_eval_active = int(mx.get_active_memory())
        started = time.perf_counter()
        mx.eval(norm_stage.parameters())
        norm_materialize_wall = time.perf_counter() - started
        norm_post_materialize_active = int(mx.get_active_memory())
        started = time.perf_counter()
        norm_out = norm_stage(h)
        mx.eval(norm_out)
        norm_forward_wall = time.perf_counter() - started
        old_h = h
        h = norm_out
        del old_h, norm_stage, norm_selected
        gc.collect()
        mx.clear_cache()
        gc.collect()
        norm_post_clear_active = int(mx.get_active_memory())
        stage_records["norm"] = {
            "selected_bytes": norm_bytes,
            "pre_active_bytes": norm_pre_active,
            "pre_eval_active_bytes": norm_pre_eval_active,
            "post_materialize_active_bytes": norm_post_materialize_active,
            "post_clear_active_bytes": norm_post_clear_active,
            "pre_eval_delta_bytes": norm_pre_eval_active - norm_pre_active,
            "materialized_delta_bytes": norm_post_materialize_active - norm_pre_active,
            "post_clear_delta_bytes": norm_post_clear_active - norm_pre_active,
            "materialize_wall_seconds": round(norm_materialize_wall, 6),
            "forward_wall_seconds": round(norm_forward_wall, 6),
        }
        save_state(f"stream_{label}_norm_complete", stage=stage_records["norm"], cache=cache_snapshot(caches))

        # LM head.
        head_pre_active = int(mx.get_active_memory())
        head_selected = select_weights("lm_head.")
        head_bytes = selected_bytes(head_selected)
        if head_bytes != EXPECTED_HEAD_BYTES:
            raise RuntimeError(f"head selected bytes {head_bytes} != {EXPECTED_HEAD_BYTES}")
        head_stage = HeadStage()
        quantize_and_load(head_stage, head_selected)
        head_pre_eval_active = int(mx.get_active_memory())
        started = time.perf_counter()
        mx.eval(head_stage.parameters())
        head_materialize_wall = time.perf_counter() - started
        head_post_materialize_active = int(mx.get_active_memory())
        started = time.perf_counter()
        logits = head_stage(h)
        mx.eval(logits)
        head_forward_wall = time.perf_counter() - started
        del h, head_stage, head_selected
        gc.collect()
        mx.clear_cache()
        gc.collect()
        head_post_clear_active = int(mx.get_active_memory())
        stage_records["head"] = {
            "selected_bytes": head_bytes,
            "pre_active_bytes": head_pre_active,
            "pre_eval_active_bytes": head_pre_eval_active,
            "post_materialize_active_bytes": head_post_materialize_active,
            "post_clear_active_bytes": head_post_clear_active,
            "pre_eval_delta_bytes": head_pre_eval_active - head_pre_active,
            "materialized_delta_bytes": head_post_materialize_active - head_pre_active,
            "post_clear_delta_bytes": head_post_clear_active - head_pre_active,
            "materialize_wall_seconds": round(head_materialize_wall, 6),
            "forward_wall_seconds": round(head_forward_wall, 6),
        }
        save_state(f"stream_{label}_head_complete", stage=stage_records["head"], cache=cache_snapshot(caches))

        max_layer_delta = max(c["materialized_delta_bytes"] for c in cycles)
        max_stage_delta = max(
            stage_records["embedding"]["materialized_delta_bytes"],
            max_layer_delta,
            stage_records["norm"]["materialized_delta_bytes"],
            stage_records["head"]["materialized_delta_bytes"],
        )
        return logits, {
            "label": label,
            "stages": stage_records,
            "cycles": cycles,
            "max_layer_materialized_delta_bytes": max_layer_delta,
            "max_weight_stage_materialized_delta_bytes": max_stage_delta,
            "total_layer_materialize_wall_seconds": round(total_materialize_wall, 6),
            "total_layer_forward_wall_seconds": round(total_forward_wall, 6),
            "total_pass_wall_seconds": round(time.perf_counter() - pass_started, 6),
        }

    versions = {
        "mlx": md.version("mlx"),
        "mlx-lm": md.version("mlx-lm"),
        "transformers": md.version("transformers"),
    }

    required_api = [
        "load", "eval", "get_active_memory", "get_cache_memory", "get_peak_memory",
        "reset_peak_memory", "clear_cache",
    ]
    missing_api = [name for name in required_api if not hasattr(mx, name)]
    if missing_api:
        raise RuntimeError(f"required MLX API missing: {missing_api}")

    mx.clear_cache()
    gc.collect()
    mx.reset_peak_memory()
    baseline = save_state("baseline", versions=versions)

    # ------------------------------------------------------------------
    # Resident official control.
    # ------------------------------------------------------------------
    resident_base_active = int(mx.get_active_memory())
    started = time.perf_counter()
    resident_model, resident_loaded_config = load_model(model_dir, lazy=False, strict=True)
    resident_load_wall = time.perf_counter() - started
    resident_post_load_active = int(mx.get_active_memory())
    resident_materialized_delta = resident_post_load_active - resident_base_active
    resident_cache = make_prompt_cache(resident_model)
    if len(resident_cache) != args.num_hidden_layers:
        raise RuntimeError(f"resident cache count {len(resident_cache)} != {args.num_hidden_layers}")
    save_state("resident_model_loaded", materialized_delta_bytes=resident_materialized_delta)

    resident_prompt_ids = make_ids(prompt_token_ids)
    started = time.perf_counter()
    resident_prompt_logits = resident_model(resident_prompt_ids, cache=resident_cache)
    mx.eval(resident_prompt_logits)
    resident_prompt_wall = time.perf_counter() - started
    resident_prompt_cache = cache_snapshot(resident_cache)
    resident_prompt_max_abs = float(mx.max(mx.abs(resident_prompt_logits.astype(mx.float32))).item())
    token1 = token_value(resident_prompt_logits)
    resident_generated_tokens = [token1]
    save_state(
        "resident_prompt_complete",
        cache=resident_prompt_cache,
        generated_token=token1,
        wall_seconds=round(resident_prompt_wall, 6),
    )

    resident_step_logits = []
    resident_steps = []
    current_token = token1
    for step in range(1, GENERATED_TOKENS + 1):
        ids = make_ids([[current_token]])
        started = time.perf_counter()
        logits = resident_model(ids, cache=resident_cache)
        mx.eval(logits)
        wall = time.perf_counter() - started
        snap = cache_snapshot(resident_cache)
        predicted_top1 = token_value(logits)
        resident_step_logits.append(logits)
        resident_steps.append(
            {
                "step": step,
                "input_token": current_token,
                "predicted_top1": predicted_top1,
                "cache": snap,
                "forward_wall_seconds": round(wall, 6),
            }
        )
        save_state(
            f"resident_token_{step}_complete",
            input_token=current_token,
            predicted_top1=predicted_top1,
            cache=snap,
            wall_seconds=round(wall, 6),
        )
        if step < GENERATED_TOKENS:
            current_token = predicted_top1
            resident_generated_tokens.append(current_token)

    resident_peak = int(mx.get_peak_memory())
    del resident_model, resident_loaded_config, resident_cache, resident_prompt_ids
    gc.collect()
    mx.clear_cache()
    gc.collect()
    resident_after_clear = mem()
    save_state("resident_control_cleared", memory_after_clear=resident_after_clear)

    # ------------------------------------------------------------------
    # Streamed prompt + four feedback passes.
    # ------------------------------------------------------------------
    mx.reset_peak_memory()
    stream_caches = [KVCache() for _ in range(args.num_hidden_layers)]
    stream_prompt_ids = make_ids(prompt_token_ids)
    stream_prompt_logits, stream_prompt_record = run_streamed_pass(
        stream_prompt_ids, stream_caches, "prompt"
    )
    stream_prompt_cache = cache_snapshot(stream_caches)
    stream_prompt_max_abs = float(mx.max(mx.abs(stream_prompt_logits.astype(mx.float32))).item())
    stream_token1 = token_value(stream_prompt_logits)
    stream_generated_tokens = [stream_token1]

    prompt_diff = mx.abs(
        resident_prompt_logits.astype(mx.float32) - stream_prompt_logits.astype(mx.float32)
    )
    mx.eval(prompt_diff)
    prompt_max_abs_diff = float(mx.max(prompt_diff).item())
    prompt_mean_abs_diff = float(mx.mean(prompt_diff).item())
    prompt_threshold = 1e-5 + 1e-5 * resident_prompt_max_abs
    prompt_parity = {
        "max_abs_diff": prompt_max_abs_diff,
        "mean_abs_diff": prompt_mean_abs_diff,
        "resident_max_abs": resident_prompt_max_abs,
        "stream_max_abs": stream_prompt_max_abs,
        "threshold": prompt_threshold,
        "pass": prompt_max_abs_diff <= prompt_threshold,
        "resident_token": token1,
        "stream_token": stream_token1,
        "token_equal": token1 == stream_token1,
    }
    save_state("stream_prompt_complete", cache=stream_prompt_cache, parity=prompt_parity)

    del stream_prompt_ids, stream_prompt_logits, prompt_diff
    gc.collect()
    mx.clear_cache()

    stream_token_records = []
    step_parities = []

    for step in range(1, GENERATED_TOKENS + 1):
        common_input_token = resident_generated_tokens[step - 1]
        ids = make_ids([[common_input_token]])
        stream_logits, pass_record = run_streamed_pass(
            ids, stream_caches, f"token_{step}"
        )
        stream_snap = cache_snapshot(stream_caches)
        stream_predicted_top1 = token_value(stream_logits)

        resident_logits = resident_step_logits[step - 1]
        resident_max_abs = float(mx.max(mx.abs(resident_logits.astype(mx.float32))).item())
        stream_max_abs = float(mx.max(mx.abs(stream_logits.astype(mx.float32))).item())
        diff = mx.abs(resident_logits.astype(mx.float32) - stream_logits.astype(mx.float32))
        mx.eval(diff)
        max_abs_diff = float(mx.max(diff).item())
        mean_abs_diff = float(mx.mean(diff).item())
        threshold = 1e-5 + 1e-5 * resident_max_abs
        resident_predicted_top1 = int(resident_steps[step - 1]["predicted_top1"])
        parity = {
            "step": step,
            "input_token": common_input_token,
            "max_abs_diff": max_abs_diff,
            "mean_abs_diff": mean_abs_diff,
            "resident_max_abs": resident_max_abs,
            "stream_max_abs": stream_max_abs,
            "threshold": threshold,
            "pass": max_abs_diff <= threshold,
            "resident_predicted_top1": resident_predicted_top1,
            "stream_predicted_top1": stream_predicted_top1,
            "top1_equal": resident_predicted_top1 == stream_predicted_top1,
        }
        step_parities.append(parity)
        stream_token_records.append(
            {
                "step": step,
                "input_token": common_input_token,
                "predicted_top1": stream_predicted_top1,
                "cache": stream_snap,
                "pass": pass_record,
            }
        )
        save_state(
            f"stream_token_{step}_complete",
            cache=stream_snap,
            parity=parity,
        )

        if step < GENERATED_TOKENS:
            stream_generated_tokens.append(stream_predicted_top1)

        resident_step_logits[step - 1] = None
        del ids, stream_logits, diff
        gc.collect()
        mx.clear_cache()

    stream_peak = int(mx.get_peak_memory())
    max_stream_stage = max(
        [stream_prompt_record["max_weight_stage_materialized_delta_bytes"]]
        + [r["pass"]["max_weight_stage_materialized_delta_bytes"] for r in stream_token_records]
    )
    residency_ratio = (
        resident_materialized_delta / max_stream_stage if max_stream_stage > 0 else None
    )

    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens

    final = {
        "ok": True,
        "versions": versions,
        "baseline": baseline["memory"],
        "resident": {
            "materialized_delta_bytes": resident_materialized_delta,
            "load_wall_seconds": round(resident_load_wall, 6),
            "prompt_forward_wall_seconds": round(resident_prompt_wall, 6),
            "peak_bytes": resident_peak,
            "prompt_cache": resident_prompt_cache,
            "generated_tokens": resident_generated_tokens,
            "steps": resident_steps,
            "after_clear": resident_after_clear,
        },
        "stream": {
            "prompt": stream_prompt_record,
            "prompt_cache": stream_prompt_cache,
            "generated_tokens": stream_generated_tokens,
            "tokens": stream_token_records,
            "max_weight_stage_materialized_delta_bytes": max_stream_stage,
            "resident_to_max_streamed_stage_ratio": residency_ratio,
            "peak_bytes": stream_peak,
        },
        "prompt_parity": prompt_parity,
        "step_parities": step_parities,
        "generated_sequence_equal": generated_sequence_equal,
        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,
        "final_memory": mem(),
    }
    final_path.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    save_state(
        "child_complete",
        generated_sequence_equal=generated_sequence_equal,
        resident_generated_tokens=resident_generated_tokens,
        stream_generated_tokens=stream_generated_tokens,
    )
    return 0


def child_entry(argv: list[str]) -> int:
    final_path = Path(argv[4]) if len(argv) >= 5 else None
    state_path = Path(argv[3]) if len(argv) >= 4 else None
    try:
        return child_main(argv)
    except Exception as exc:
        payload = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        if final_path is not None:
            try:
                final_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            except Exception:
                pass
        if state_path is not None:
            try:
                state_path.write_text(
                    json.dumps({"phase": "child_exception", "error": payload["error"]}, indent=2) + "\n",
                    encoding="utf-8",
                )
            except Exception:
                pass
        return 90


def validate_cache(cache: dict, expected_offset: int, label: str) -> str | None:
    offsets = cache.get("offsets", [])
    if cache.get("count") != 36 or len(offsets) != 36:
        return f"{label}: cache count/offset length invalid"
    if any(int(x) != expected_offset for x in offsets):
        return f"{label}: expected all offsets {expected_offset}, got {sorted(set(offsets))}"
    total = int(cache.get("total_nbytes", -1))
    if abs(total - EXPECTED_KV_TOTAL_BYTES) > 1 * 1024 * 1024:
        return f"{label}: cache bytes {total} not near {EXPECTED_KV_TOTAL_BYTES}"
    return None


def validate_streamed_pass(record: dict, label: str) -> str | None:
    stages = record.get("stages", {})
    for stage_name, expected in [
        ("embedding", EXPECTED_EMBED_BYTES),
        ("norm", EXPECTED_NORM_BYTES),
        ("head", EXPECTED_HEAD_BYTES),
    ]:
        stage = stages.get(stage_name, {})
        observed = int(stage.get("materialized_delta_bytes", -10**18))
        if abs(observed - expected) > 1 * 1024 * 1024:
            return f"{label}: {stage_name} materialized delta {observed} not near {expected}"
    cycles = record.get("cycles", [])
    if len(cycles) != 36:
        return f"{label}: expected 36 layer cycles, got {len(cycles)}"
    for cycle in cycles:
        pre_eval = int(cycle.get("pre_eval_delta_bytes", 10**18))
        materialized = int(cycle.get("materialized_delta_bytes", -10**18))
        if pre_eval > 32 * 1024 * 1024:
            return f"{label}: layer {cycle.get('layer_id')} pre-eval delta {pre_eval} >32 MiB"
        if abs(materialized - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:
            return f"{label}: layer {cycle.get('layer_id')} materialized {materialized} not near {EXPECTED_LAYER_BYTES}"
    return None


def parent_main() -> int:
    repo = Path(__file__).resolve().parents[1]
    script_path = Path(__file__).resolve()
    source008 = repo / "scripts" / "stretch_one_token_kv_autoregressive_parity_008.py"
    source008_pipefix = repo / "scripts" / "stretch_one_token_kv_autoregressive_parity_008_pipefix.py"
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"

    observed008 = git_blob(source008, repo)
    observed_pipefix = git_blob(source008_pipefix, repo)
    observed002 = git_blob(source002, repo)

    print("LOOM Stretch 009 — Four-Token KV Autoregressive Parity")
    print(f"Stretch 008 scientific source blob: {observed008}")
    print(f"Stretch 008 pipefix blob: {observed_pipefix}")
    print(f"Stretch 002 helper blob: {observed002}")
    if (
        observed008 != SOURCE_008_BLOB
        or observed_pipefix != SOURCE_008_PIPEFIX_BLOB
        or observed002 != SOURCE_002_BLOB
    ):
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    helpers = load_module(source002, "loom_stretch002_helpers")
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "four-token-kv-autoregressive-parity-009" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / "child-state.json"
    final_path = run_dir / "child-final.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 009 — Four-Token KV Autoregressive Parity",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "prompt_token_ids": PROMPT_TOKEN_IDS,
        "prompt_length": PROMPT_LEN,
        "generated_tokens": GENERATED_TOKENS,
        "final_expected_offset": FINAL_OFFSET,
        "kv_cache": "mlx_lm.models.cache.KVCache",
        "tokenizer": False,
        "sampling": False,
        "network_download": False,
        "source_008_blob": observed008,
        "source_008_pipefix_blob": observed_pipefix,
        "source_002_blob": observed002,
        "disk_before": helpers.disk_snapshot(repo),
    }
    telemetry: list[dict] = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = helpers.disk_snapshot(repo)
        summary["telemetry"] = helpers.summarize_telemetry(telemetry)
        summary["phase_telemetry"] = summarize_phase_telemetry(telemetry)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        if summary.get("prompt_parity"):
            p = summary["prompt_parity"]
            print(
                f"Prompt parity: pass={p.get('pass')} max_abs={p.get('max_abs_diff')} "
                f"mean_abs={p.get('mean_abs_diff')} token_equal={p.get('token_equal')}"
            )
        if summary.get("step_parities"):
            for p in summary["step_parities"]:
                print(
                    f"Token step {p.get('step')}: pass={p.get('pass')} "
                    f"max_abs={p.get('max_abs_diff')} mean_abs={p.get('mean_abs_diff')} "
                    f"top1_equal={p.get('top1_equal')}"
                )
        if summary.get("resident") and summary.get("stream"):
            print(f"Resident generated sequence: {summary['resident'].get('generated_tokens')}")
            print(f"Streamed generated sequence: {summary['stream'].get('generated_tokens')}")
            print(f"Generated sequence equal: {summary.get('generated_sequence_equal')}")
            print(f"Resident full-model materialized delta: {summary['resident'].get('materialized_delta_bytes')} B")
            print(f"Max streamed weight-stage delta: {summary['stream'].get('max_weight_stage_materialized_delta_bytes')} B")
            print(f"Resident/max-streamed-stage ratio: {summary['stream'].get('resident_to_max_streamed_stage_ratio')}")
            print(f"Resident cache offsets final: {sorted(set(summary['resident']['steps'][-1]['cache']['offsets']))}")
            print(f"Streamed cache offsets final: {sorted(set(summary['stream']['tokens'][-1]['cache']['offsets']))}")
            print(f"KV bytes final resident/streamed: {summary['resident']['steps'][-1]['cache']['total_nbytes']} / {summary['stream']['tokens'][-1]['cache']['total_nbytes']} B")
        if summary.get("per_token_timing"):
            t = summary["per_token_timing"]
            print(f"Stream token layer-materialize walls: {t.get('layer_materialize_seconds')}")
            print(f"Stream token layer-forward walls: {t.get('layer_forward_seconds')}")
            print(f"Mean layer-materialize/token: {t.get('mean_layer_materialize_seconds')} s")
            print(f"Mean layer-forward/token: {t.get('mean_layer_forward_seconds')} s")
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Phase telemetry: {json.dumps(summary.get('phase_telemetry', {}), sort_keys=True)}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("Resident control: official full Qwen3 + make_prompt_cache")
    print("Streamed path: phase-streamed weights + 36 persistent ordinary KVCache objects")
    print(f"Frozen prompt token IDs: {PROMPT_TOKEN_IDS}")
    print(f"Generation policy: argmax exactly {GENERATED_TOKENS} tokens")
    print(f"Expected cache offsets: 4 -> 5 -> 6 -> 7 -> {FINAL_OFFSET}")
    print(f"Expected allocated KV bytes throughout: {EXPECTED_KV_TOTAL_BYTES}")
    print("Child transport: file-backed state/final/stdout/stderr (no captured verbose pipe)")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required_paths = [script_path, source008, source008_pipefix, source002, venv_py, weight, config_path]
    if not all(p.is_file() for p in required_paths):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required frozen source/venv/model/config path missing"
        return finish(2)

    versions_result = helpers.run(
        [
            str(venv_py),
            "-c",
            "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo,
        timeout=30,
    )
    try:
        versions = json.loads(versions_result.get("stdout", "").strip())
    except Exception:
        versions = {}
    summary["versions"] = versions
    if versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {versions!r}"
        return finish(2)
    print(f"Version lock: PASS {versions}")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"cannot parse config.json: {type(exc).__name__}: {exc}"
        return finish(2)

    expected_config = {
        "model_type": "qwen3",
        "hidden_size": 4096,
        "num_hidden_layers": 36,
        "vocab_size": 151936,
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "head_dim": 128,
        "rms_norm_eps": 1e-6,
        "tie_word_embeddings": False,
    }
    observed_config = {k: config.get(k) for k in expected_config}
    summary["model_config"] = observed_config
    summary["quantization"] = config.get("quantization")
    if observed_config != expected_config or config.get("quantization") != EXPECTED_QUANTIZATION:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"model config/quantization mismatch: {observed_config!r} {config.get('quantization')!r}"
        return finish(2)
    print(f"Model config/quantization: PASS {observed_config} quantization={EXPECTED_QUANTIZATION}")

    for layer_id in range(36):
        try:
            names, layer_bytes = helpers.selected_layer_from_header(weight, layer_id)
        except Exception as exc:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = f"layer {layer_id} header recovery failed: {type(exc).__name__}: {exc}"
            return finish(2)
        if len(names) != EXPECTED_LAYER_TENSORS or layer_bytes != EXPECTED_LAYER_BYTES:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = f"layer {layer_id} provenance mismatch"
            return finish(2)
    print("Transformer layer provenance: PASS 36/36")

    for index in range(HOST_GATE_SAMPLES):
        sample = helpers.system_sample()
        sample["phase"] = "host_gate"
        telemetry.append(sample)
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        print(f"Host sample {index + 1}/{HOST_GATE_SAMPLES}: free={free}% swap={swap} MB")
        if free is None or swap is None:
            summary["classification"] = "TELEMETRY_FAIL"
            summary["failure_reason"] = "required host telemetry unavailable"
            return finish(3)
        if free < HOST_GATE_FREE_PERCENT or swap > MAX_SWAP_MB:
            summary["classification"] = "HOST_STATE_NOT_READY"
            summary["failure_reason"] = f"host state outside launch gate: free={free}% swap={swap} MB"
            return finish(3)
        if index + 1 < HOST_GATE_SAMPLES:
            time.sleep(1.0)
    print("Host-state gate: PASS")

    cmd = [
        str(venv_py), str(script_path), "--child",
        str(model_dir), str(weight), str(config_path), str(state_path), str(final_path),
        json.dumps(PROMPT_TOKEN_IDS),
    ]

    guardrail_reason = None
    telemetry_reason = None
    started = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as out_handle, stderr_path.open("w", encoding="utf-8") as err_handle:
        proc = subprocess.Popen(
            cmd,
            cwd=repo,
            stdout=out_handle,
            stderr=err_handle,
            text=True,
        )
        while proc.poll() is None:
            sample = helpers.system_sample(proc.pid)
            state = helpers.read_json(state_path) or {}
            sample["phase"] = state.get("phase", "child_starting")
            sample["elapsed_seconds"] = round(time.perf_counter() - started, 3)
            telemetry.append(sample)
            free = sample.get("memory_free_percent")
            swap = sample.get("swap_used_mb")
            if free is None or swap is None:
                telemetry_reason = "required runtime memory/swap telemetry unavailable"
                helpers.terminate(proc)
                break
            if free < MIN_FREE_PERCENT:
                guardrail_reason = f"memory free {free}% < {MIN_FREE_PERCENT}%"
                helpers.terminate(proc)
                break
            if swap > MAX_SWAP_MB:
                guardrail_reason = f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB"
                helpers.terminate(proc)
                break
            time.sleep(POLL_SECONDS)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            helpers.terminate(proc)
            proc.wait(timeout=10)

    summary["child_exit_code"] = proc.returncode
    summary["child_stdout_file"] = str(stdout_path)
    summary["child_stderr_file"] = str(stderr_path)
    summary["child_final_file"] = str(final_path)

    if telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
        return finish(4)
    if guardrail_reason:
        summary["classification"] = "PARTIAL_RESOURCE_FAIL"
        summary["failure_reason"] = guardrail_reason
        return finish(5)

    child = helpers.read_json(final_path)
    if proc.returncode != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"child exited {proc.returncode}; final={child!r}; state={helpers.read_json(state_path)!r}"
        return finish(6)
    if not isinstance(child, dict) or not child.get("ok"):
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"missing/invalid child-final payload: {child!r}"
        return finish(6)

    for key in [
        "resident", "stream", "prompt_parity", "step_parities",
        "generated_sequence_equal", "expected_kv_total_bytes",
    ]:
        summary[key] = child[key]
    summary["child_baseline"] = child.get("baseline")
    summary["child_final_memory"] = child.get("final_memory")

    resident_delta = int(child["resident"]["materialized_delta_bytes"])
    if abs(resident_delta - EXPECTED_TOTAL_BYTES) > 64 * 1024 * 1024:
        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"
        summary["failure_reason"] = f"resident delta {resident_delta} B not near {EXPECTED_TOTAL_BYTES}"
        return finish(7)

    # Cache gates: prompt then four feedback positions.
    err = validate_cache(child["resident"]["prompt_cache"], PROMPT_LEN, "resident_prompt")
    if err:
        summary["classification"] = "KV_CACHE_STATE_FAIL"
        summary["failure_reason"] = err
        return finish(8)
    err = validate_cache(child["stream"]["prompt_cache"], PROMPT_LEN, "stream_prompt")
    if err:
        summary["classification"] = "KV_CACHE_STATE_FAIL"
        summary["failure_reason"] = err
        return finish(8)

    for step in range(1, GENERATED_TOKENS + 1):
        expected_offset = PROMPT_LEN + step
        resident_cache = child["resident"]["steps"][step - 1]["cache"]
        stream_cache = child["stream"]["tokens"][step - 1]["cache"]
        for label, cache in [(f"resident_token_{step}", resident_cache), (f"stream_token_{step}", stream_cache)]:
            err = validate_cache(cache, expected_offset, label)
            if err:
                summary["classification"] = "KV_CACHE_STATE_FAIL"
                summary["failure_reason"] = err
                return finish(8)
            prompt_bytes = int(
                child["resident"]["prompt_cache"]["total_nbytes"]
                if label.startswith("resident")
                else child["stream"]["prompt_cache"]["total_nbytes"]
            )
            if int(cache["total_nbytes"]) - prompt_bytes > 1 * 1024 * 1024:
                summary["classification"] = "KV_CACHE_GROWTH_UNEXPECTED"
                summary["failure_reason"] = f"{label}: cache grew below 256-position boundary"
                return finish(8)

    # Weight-stage gates for prompt and all four feedback passes.
    err = validate_streamed_pass(child["stream"]["prompt"], "stream_prompt")
    if err:
        summary["classification"] = "STREAMED_WEIGHT_STAGE_FAIL"
        summary["failure_reason"] = err
        return finish(9)
    for token_record in child["stream"]["tokens"]:
        err = validate_streamed_pass(token_record["pass"], f"stream_token_{token_record['step']}")
        if err:
            summary["classification"] = "STREAMED_WEIGHT_STAGE_FAIL"
            summary["failure_reason"] = err
            return finish(9)

    if not child["prompt_parity"]["pass"]:
        summary["classification"] = "PROMPT_KV_NUMERICAL_PARITY_FAIL"
        summary["failure_reason"] = f"prompt parity failed: {child['prompt_parity']!r}"
        return finish(10)
    if not child["prompt_parity"]["token_equal"]:
        summary["classification"] = "GENERATED_TOKEN_MISMATCH"
        summary["failure_reason"] = f"prompt token mismatch: {child['prompt_parity']!r}"
        return finish(10)

    for parity in child["step_parities"]:
        if not parity["pass"]:
            summary["classification"] = "MULTI_TOKEN_KV_NUMERICAL_PARITY_FAIL"
            summary["failure_reason"] = f"step {parity['step']} numerical parity failed: {parity!r}"
            return finish(10)
        if not parity["top1_equal"]:
            summary["classification"] = "MULTI_TOKEN_TOP1_MISMATCH"
            summary["failure_reason"] = f"step {parity['step']} top1 mismatch: {parity!r}"
            return finish(10)

    if not child["generated_sequence_equal"]:
        summary["classification"] = "GENERATED_SEQUENCE_MISMATCH"
        summary["failure_reason"] = (
            f"resident {child['resident']['generated_tokens']} != "
            f"streamed {child['stream']['generated_tokens']}"
        )
        return finish(10)

    materialize_times = [
        float(r["pass"]["total_layer_materialize_wall_seconds"])
        for r in child["stream"]["tokens"]
    ]
    forward_times = [
        float(r["pass"]["total_layer_forward_wall_seconds"])
        for r in child["stream"]["tokens"]
    ]
    summary["per_token_timing"] = {
        "layer_materialize_seconds": materialize_times,
        "layer_forward_seconds": forward_times,
        "mean_layer_materialize_seconds": round(statistics.mean(materialize_times), 6),
        "median_layer_materialize_seconds": round(statistics.median(materialize_times), 6),
        "mean_layer_forward_seconds": round(statistics.mean(forward_times), 6),
        "median_layer_forward_seconds": round(statistics.median(forward_times), 6),
    }

    summary["classification"] = "FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS"
    return finish(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        raise SystemExit(child_entry(sys.argv[2:]))
    raise SystemExit(parent_main())
