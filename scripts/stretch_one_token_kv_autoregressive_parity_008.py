#!/usr/bin/env python3
"""LOOM Stretch 008 — one-token KV autoregressive parity.

Official resident Qwen3 control vs LOOM phase-streamed raw weights with persistent
per-layer KVCache state. Prefill a frozen 4-token prompt, select exactly one
argmax token, feed it back through the same caches, and compare post-token logits.

No tokenizer, sampling, multi-token generation, cache quantization, or download.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SOURCE_007B_BLOB = "b08c9b44ae062ee259ab6641575e44c4d7d753e6"
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
POST_TOKEN_OFFSET = 5

MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
POLL_SECONDS = 0.5

CHILD_CODE = r'''
import gc
import hashlib
import importlib.metadata as md
import inspect
import json
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
from mlx_lm.models import qwen3
from mlx_lm.models.base import create_attention_mask
from mlx_lm.models.cache import KVCache, make_prompt_cache
from mlx_lm import models as models_pkg
from mlx_lm.utils import load_model

model_dir = Path(sys.argv[1])
weight_path = Path(sys.argv[2])
config_path = Path(sys.argv[3])
state_path = Path(sys.argv[4])
prompt_token_ids = json.loads(sys.argv[5])
expected_layer_bytes = int(sys.argv[6])
expected_layer_tensors = int(sys.argv[7])
expected_embed_bytes = int(sys.argv[8])
expected_norm_bytes = int(sys.argv[9])
expected_head_bytes = int(sys.argv[10])
expected_kv_total_bytes = int(sys.argv[11])

config = json.loads(config_path.read_text(encoding="utf-8"))
args = qwen3.ModelArgs.from_dict(config)
quant = config["quantization"]


def mem():
    return {
        "active_bytes": int(mx.get_active_memory()),
        "cache_bytes": int(mx.get_cache_memory()),
        "peak_bytes": int(mx.get_peak_memory()),
    }


def save(phase, **extra):
    payload = {"phase": phase, "memory": mem(), **extra}
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("LOOM_CHILD_STATE=" + json.dumps(payload), flush=True)
    return payload


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_sha(module):
    return sha256_file(Path(inspect.getfile(module)))


def select_weights(prefix, strip_prefix=""):
    all_weights = mx.load(str(weight_path))
    selected = {}
    for name, value in all_weights.items():
        if name.startswith(prefix):
            local_name = name[len(strip_prefix):] if strip_prefix else name
            selected[local_name] = value
    del all_weights
    gc.collect()
    return selected


def selected_bytes(selected):
    return sum(int(v.nbytes) for v in selected.values())


def quantize_and_load(module, selected):
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


def build_block(layer_id):
    marker = f"model.layers.{layer_id}."
    selected = select_weights(marker, marker)
    if len(selected) != expected_layer_tensors:
        raise RuntimeError(
            f"layer {layer_id} local tensor count {len(selected)} != {expected_layer_tensors}"
        )
    if selected_bytes(selected) != expected_layer_bytes:
        raise RuntimeError(
            f"layer {layer_id} selected bytes {selected_bytes(selected)} != {expected_layer_bytes}"
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


def cache_snapshot(caches):
    offsets = [int(c.offset) for c in caches]
    nbytes = [int(c.nbytes) for c in caches]
    return {
        "count": len(caches),
        "offsets": offsets,
        "all_offsets_equal": len(set(offsets)) == 1,
        "total_nbytes": sum(nbytes),
        "per_layer_nbytes": nbytes,
    }


def run_streamed_pass(ids, caches, label):
    stage_records = {}

    # Embedding stage.
    embed_pre_active = int(mx.get_active_memory())
    embed_selected = select_weights("model.embed_tokens.", "model.")
    embed_bytes = selected_bytes(embed_selected)
    if embed_bytes != expected_embed_bytes:
        raise RuntimeError(f"embedding selected bytes {embed_bytes} != {expected_embed_bytes}")
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
        "materialize_wall_seconds": round(embed_materialize_wall, 6),
        "forward_wall_seconds": round(embed_forward_wall, 6),
    }
    save(f"stream_{label}_embedding_complete", stage=stage_records["embedding"], cache=cache_snapshot(caches))

    mask = create_attention_mask(h, caches[0])
    cycles = []
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
        save(f"stream_{label}_layer_{layer_id}_complete", cycle=cycle, cache=post_cache)

    # Final RMSNorm.
    norm_pre_active = int(mx.get_active_memory())
    norm_selected = select_weights("model.norm.", "model.")
    norm_bytes = selected_bytes(norm_selected)
    if norm_bytes != expected_norm_bytes:
        raise RuntimeError(f"norm selected bytes {norm_bytes} != {expected_norm_bytes}")
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
        "materialize_wall_seconds": round(norm_materialize_wall, 6),
        "forward_wall_seconds": round(norm_forward_wall, 6),
    }
    save(f"stream_{label}_norm_complete", stage=stage_records["norm"], cache=cache_snapshot(caches))

    # LM head.
    head_pre_active = int(mx.get_active_memory())
    head_selected = select_weights("lm_head.")
    head_bytes = selected_bytes(head_selected)
    if head_bytes != expected_head_bytes:
        raise RuntimeError(f"head selected bytes {head_bytes} != {expected_head_bytes}")
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
        "materialize_wall_seconds": round(head_materialize_wall, 6),
        "forward_wall_seconds": round(head_forward_wall, 6),
    }
    save(f"stream_{label}_head_complete", stage=stage_records["head"], cache=cache_snapshot(caches))

    max_layer_delta = max(c["materialized_delta_bytes"] for c in cycles)
    max_stage_delta = max(
        stage_records["embedding"]["materialized_delta_bytes"],
        max_layer_delta,
        stage_records["norm"]["materialized_delta_bytes"],
        stage_records["head"]["materialized_delta_bytes"],
    )
    return logits, {
        "stages": stage_records,
        "cycles": cycles,
        "max_layer_materialized_delta_bytes": max_layer_delta,
        "max_weight_stage_materialized_delta_bytes": max_stage_delta,
        "total_layer_materialize_wall_seconds": round(total_materialize_wall, 6),
        "total_layer_forward_wall_seconds": round(total_forward_wall, 6),
    }


required_api = [
    "load", "eval", "get_active_memory", "get_cache_memory", "get_peak_memory",
    "reset_peak_memory", "clear_cache",
]
missing_api = [name for name in required_api if not hasattr(mx, name)]
if missing_api:
    save("api_missing", missing_api=missing_api)
    raise SystemExit(4)

versions = {
    "mlx": md.version("mlx"),
    "mlx-lm": md.version("mlx-lm"),
    "transformers": md.version("transformers"),
}

mx.clear_cache()
gc.collect()
mx.reset_peak_memory()
baseline = save(
    "baseline",
    versions=versions,
    qwen3_source_sha256=source_sha(qwen3),
    config={
        "model_type": config.get("model_type"),
        "hidden_size": config.get("hidden_size"),
        "num_hidden_layers": config.get("num_hidden_layers"),
        "vocab_size": config.get("vocab_size"),
        "num_attention_heads": config.get("num_attention_heads"),
        "num_key_value_heads": config.get("num_key_value_heads"),
        "head_dim": config.get("head_dim"),
        "tie_word_embeddings": config.get("tie_word_embeddings"),
        "quantization": quant,
    },
)

# ---------------------------------------------------------------------------
# Resident official control with official prompt cache.
# ---------------------------------------------------------------------------
resident_base_active = int(mx.get_active_memory())
started = time.perf_counter()
resident_model, resident_loaded_config = load_model(model_dir, lazy=False, strict=True)
resident_load_wall = time.perf_counter() - started
resident_post_load_active = int(mx.get_active_memory())
resident_cache = make_prompt_cache(resident_model)
if len(resident_cache) != args.num_hidden_layers:
    raise RuntimeError(f"resident cache count {len(resident_cache)} != {args.num_hidden_layers}")
resident_tokens = make_ids(prompt_token_ids)

started = time.perf_counter()
resident_prompt_logits = resident_model(resident_tokens, cache=resident_cache)
mx.eval(resident_prompt_logits)
resident_prompt_wall = time.perf_counter() - started
resident_cache_after_prompt = cache_snapshot(resident_cache)
resident_prompt_max_abs = float(mx.max(mx.abs(resident_prompt_logits.astype(mx.float32))).item())
resident_next_token = mx.argmax(resident_prompt_logits[:, -1, :], axis=-1).reshape(1, 1).astype(mx.int32)
mx.eval(resident_next_token)
resident_next_token_list = resident_next_token.tolist()
save(
    "resident_prompt_complete",
    cache=resident_cache_after_prompt,
    next_token=resident_next_token_list,
    logits_shape=list(resident_prompt_logits.shape),
    wall_seconds=round(resident_prompt_wall, 6),
)

started = time.perf_counter()
resident_post_token_logits = resident_model(resident_next_token, cache=resident_cache)
mx.eval(resident_post_token_logits)
resident_post_token_wall = time.perf_counter() - started
resident_cache_after_token = cache_snapshot(resident_cache)
resident_post_token_max_abs = float(mx.max(mx.abs(resident_post_token_logits.astype(mx.float32))).item())
resident_post_token_top1 = mx.argmax(resident_post_token_logits[:, -1, :], axis=-1)
mx.eval(resident_post_token_top1)
resident_post_token_top1_list = resident_post_token_top1.tolist()
resident_peak = int(mx.get_peak_memory())
save(
    "resident_post_token_complete",
    cache=resident_cache_after_token,
    post_token_top1=resident_post_token_top1_list,
    logits_shape=list(resident_post_token_logits.shape),
    wall_seconds=round(resident_post_token_wall, 6),
)

resident_materialized_delta = resident_post_load_active - resident_base_active

del resident_model, resident_loaded_config, resident_cache, resident_tokens
gc.collect()
mx.clear_cache()
gc.collect()
resident_after_clear = mem()
save("resident_control_cleared", memory_after_clear=resident_after_clear)

# ---------------------------------------------------------------------------
# Streamed prompt prefill with persistent per-layer KV cache.
# ---------------------------------------------------------------------------
mx.reset_peak_memory()
stream_caches = [KVCache() for _ in range(args.num_hidden_layers)]
stream_prompt_ids = make_ids(prompt_token_ids)
stream_prompt_logits, stream_prompt_record = run_streamed_pass(
    stream_prompt_ids, stream_caches, "prompt"
)
stream_cache_after_prompt = cache_snapshot(stream_caches)
stream_prompt_max_abs = float(mx.max(mx.abs(stream_prompt_logits.astype(mx.float32))).item())
stream_next_token = mx.argmax(stream_prompt_logits[:, -1, :], axis=-1).reshape(1, 1).astype(mx.int32)
mx.eval(stream_next_token)
stream_next_token_list = stream_next_token.tolist()
save(
    "stream_prompt_complete",
    cache=stream_cache_after_prompt,
    next_token=stream_next_token_list,
    logits_shape=list(stream_prompt_logits.shape),
)

# Prompt full-logit parity.
prompt_diff = mx.abs(
    resident_prompt_logits.astype(mx.float32) - stream_prompt_logits.astype(mx.float32)
)
mx.eval(prompt_diff)
prompt_max_abs_diff = float(mx.max(prompt_diff).item())
prompt_mean_abs_diff = float(mx.mean(prompt_diff).item())
prompt_threshold = 1e-5 + 1e-5 * resident_prompt_max_abs
prompt_parity_pass = prompt_max_abs_diff <= prompt_threshold
generated_token_equal = resident_next_token_list == stream_next_token_list

# ---------------------------------------------------------------------------
# Feed exactly the resident-selected token through both persisted cache states.
# Streamed side uses the same fixed continuation input for numerical parity.
# ---------------------------------------------------------------------------
stream_feedback_ids = make_ids(resident_next_token_list)
stream_post_token_logits, stream_token_record = run_streamed_pass(
    stream_feedback_ids, stream_caches, "token"
)
stream_cache_after_token = cache_snapshot(stream_caches)
stream_post_token_max_abs = float(mx.max(mx.abs(stream_post_token_logits.astype(mx.float32))).item())
stream_post_token_top1 = mx.argmax(stream_post_token_logits[:, -1, :], axis=-1)
mx.eval(stream_post_token_top1)
stream_post_token_top1_list = stream_post_token_top1.tolist()

post_diff = mx.abs(
    resident_post_token_logits.astype(mx.float32) - stream_post_token_logits.astype(mx.float32)
)
mx.eval(post_diff)
post_max_abs_diff = float(mx.max(post_diff).item())
post_mean_abs_diff = float(mx.mean(post_diff).item())
post_threshold = 1e-5 + 1e-5 * resident_post_token_max_abs
post_parity_pass = post_max_abs_diff <= post_threshold
post_top1_equal = resident_post_token_top1_list == stream_post_token_top1_list

stream_peak = int(mx.get_peak_memory())
max_stream_stage = max(
    stream_prompt_record["max_weight_stage_materialized_delta_bytes"],
    stream_token_record["max_weight_stage_materialized_delta_bytes"],
)
residency_ratio = (
    resident_materialized_delta / max_stream_stage if max_stream_stage > 0 else None
)

final = {
    "versions": versions,
    "baseline": baseline["memory"],
    "resident": {
        "materialized_delta_bytes": resident_materialized_delta,
        "load_wall_seconds": round(resident_load_wall, 6),
        "prompt_forward_wall_seconds": round(resident_prompt_wall, 6),
        "post_token_forward_wall_seconds": round(resident_post_token_wall, 6),
        "peak_bytes": resident_peak,
        "cache_after_prompt": resident_cache_after_prompt,
        "cache_after_token": resident_cache_after_token,
        "next_token": resident_next_token_list,
        "post_token_top1": resident_post_token_top1_list,
        "after_clear": resident_after_clear,
    },
    "stream_prompt": stream_prompt_record,
    "stream_token": stream_token_record,
    "stream": {
        "cache_after_prompt": stream_cache_after_prompt,
        "cache_after_token": stream_cache_after_token,
        "next_token": stream_next_token_list,
        "post_token_top1": stream_post_token_top1_list,
        "max_weight_stage_materialized_delta_bytes": max_stream_stage,
        "resident_to_max_streamed_stage_ratio": residency_ratio,
        "peak_bytes": stream_peak,
    },
    "prompt_parity": {
        "max_abs_diff": prompt_max_abs_diff,
        "mean_abs_diff": prompt_mean_abs_diff,
        "resident_max_abs": resident_prompt_max_abs,
        "stream_max_abs": stream_prompt_max_abs,
        "threshold": prompt_threshold,
        "pass": prompt_parity_pass,
        "generated_token_equal": generated_token_equal,
    },
    "post_token_parity": {
        "max_abs_diff": post_max_abs_diff,
        "mean_abs_diff": post_mean_abs_diff,
        "resident_max_abs": resident_post_token_max_abs,
        "stream_max_abs": stream_post_token_max_abs,
        "threshold": post_threshold,
        "pass": post_parity_pass,
        "top1_equal": post_top1_equal,
    },
    "expected_kv_total_bytes": expected_kv_total_bytes,
    "final_memory": mem(),
}
print("LOOM_CHILD_COMPLETE=" + json.dumps(final), flush=True)
'''


def utc_now():
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
    if phase.startswith("stream_token"):
        return "stream_token"
    return "other"


def summarize_phase_telemetry(samples: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for sample in samples:
        groups.setdefault(phase_bucket(str(sample.get("phase", ""))), []).append(sample)
    out = {}
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


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source007b = repo / "scripts" / "stretch_phase_streamed_full_logit_parity_007b.py"
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    observed007b = git_blob(source007b, repo)
    observed002 = git_blob(source002, repo)

    print("LOOM Stretch 008 — One-Token KV Autoregressive Parity")
    print(f"Stretch 007B source blob: {observed007b}")
    print(f"Stretch 002 helper blob: {observed002}")
    if observed007b != SOURCE_007B_BLOB or observed002 != SOURCE_002_BLOB:
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
    run_dir = repo / "results-local" / "stretch" / "one-token-kv-autoregressive-parity-008" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / "child-state.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 008 — One-Token KV Autoregressive Parity",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "prompt_token_ids": PROMPT_TOKEN_IDS,
        "prompt_length": PROMPT_LEN,
        "generated_tokens": 1,
        "tokenizer": False,
        "sampling": False,
        "kv_cache": "mlx_lm.models.cache.KVCache",
        "network_download": False,
        "source_007b_blob": observed007b,
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
                f"mean_abs={p.get('mean_abs_diff')} threshold={p.get('threshold')} "
                f"token_equal={p.get('generated_token_equal')}"
            )
        if summary.get("post_token_parity"):
            p = summary["post_token_parity"]
            print(
                f"Post-token parity: pass={p.get('pass')} max_abs={p.get('max_abs_diff')} "
                f"mean_abs={p.get('mean_abs_diff')} threshold={p.get('threshold')} "
                f"top1_equal={p.get('top1_equal')}"
            )
        if summary.get("resident"):
            r = summary["resident"]
            print(f"Resident full-model materialized delta: {r.get('materialized_delta_bytes')} B")
            print(f"Resident generated token: {r.get('next_token')}")
            print(f"Resident cache bytes prompt/token: {r.get('cache_after_prompt',{}).get('total_nbytes')} / {r.get('cache_after_token',{}).get('total_nbytes')} B")
            print(f"Resident cache offsets prompt/token: {sorted(set(r.get('cache_after_prompt',{}).get('offsets',[])))} / {sorted(set(r.get('cache_after_token',{}).get('offsets',[])))}")
        if summary.get("stream"):
            s = summary["stream"]
            print(f"Streamed generated token: {s.get('next_token')}")
            print(f"Streamed cache bytes prompt/token: {s.get('cache_after_prompt',{}).get('total_nbytes')} / {s.get('cache_after_token',{}).get('total_nbytes')} B")
            print(f"Streamed cache offsets prompt/token: {sorted(set(s.get('cache_after_prompt',{}).get('offsets',[])))} / {sorted(set(s.get('cache_after_token',{}).get('offsets',[])))}")
            print(f"Max streamed weight-stage delta: {s.get('max_weight_stage_materialized_delta_bytes')} B")
            print(f"Resident/max-streamed-stage ratio: {s.get('resident_to_max_streamed_stage_ratio')}")
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Phase telemetry: {json.dumps(summary.get('phase_telemetry', {}), sort_keys=True)}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("Resident control: official full Qwen3 + make_prompt_cache")
    print("Streamed path: phase-streamed weights + 36 persistent KVCache objects")
    print(f"Frozen prompt token IDs: {PROMPT_TOKEN_IDS}")
    print("Generation policy: argmax exactly one token, then feed it back through persisted cache")
    print("Tokenizer/sampling/multi-token generation: NONE")
    print(f"Expected allocated KV bytes after prompt: {EXPECTED_KV_TOTAL_BYTES}")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required_paths = [source007b, source002, venv_py, weight, config_path]
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
        str(venv_py), "-c", CHILD_CODE,
        str(model_dir), str(weight), str(config_path), str(state_path),
        json.dumps(PROMPT_TOKEN_IDS),
        str(EXPECTED_LAYER_BYTES), str(EXPECTED_LAYER_TENSORS),
        str(EXPECTED_EMBED_BYTES), str(EXPECTED_NORM_BYTES), str(EXPECTED_HEAD_BYTES),
        str(EXPECTED_KV_TOTAL_BYTES),
    ]
    started = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    guardrail_reason = None
    telemetry_reason = None

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

    stdout, stderr = proc.communicate(timeout=10)
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    summary["child_exit_code"] = proc.returncode
    summary["child_stdout_file"] = str(stdout_path)
    summary["child_stderr_file"] = str(stderr_path)

    if telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
        return finish(4)
    if guardrail_reason:
        summary["classification"] = "PARTIAL_RESOURCE_FAIL"
        summary["failure_reason"] = guardrail_reason
        return finish(5)
    if proc.returncode != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"MLX child exited {proc.returncode}; last_state={helpers.read_json(state_path)!r}"
        return finish(6)

    complete_line = None
    for line in (stdout or "").splitlines():
        if line.startswith("LOOM_CHILD_COMPLETE="):
            complete_line = line.split("=", 1)[1]
    if complete_line is None:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "child completed without LOOM_CHILD_COMPLETE payload"
        return finish(6)
    try:
        child = json.loads(complete_line)
    except json.JSONDecodeError as exc:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"cannot parse child payload: {exc}"
        return finish(6)

    for key in ["resident", "stream_prompt", "stream_token", "stream", "prompt_parity", "post_token_parity"]:
        summary[key] = child[key]
    summary["expected_kv_total_bytes"] = child["expected_kv_total_bytes"]
    summary["child_baseline"] = child["baseline"]
    summary["child_final_memory"] = child["final_memory"]

    # Resident full-model accounting gate.
    resident_delta = int(child["resident"]["materialized_delta_bytes"])
    if abs(resident_delta - EXPECTED_TOTAL_BYTES) > 64 * 1024 * 1024:
        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"
        summary["failure_reason"] = f"resident materialized delta {resident_delta} B not near {EXPECTED_TOTAL_BYTES} B"
        return finish(7)

    # Cache state gates.
    cache_checks = [
        ("resident_prompt", child["resident"]["cache_after_prompt"], PROMPT_LEN),
        ("resident_token", child["resident"]["cache_after_token"], POST_TOKEN_OFFSET),
        ("stream_prompt", child["stream"]["cache_after_prompt"], PROMPT_LEN),
        ("stream_token", child["stream"]["cache_after_token"], POST_TOKEN_OFFSET),
    ]
    for label, cache, expected_offset in cache_checks:
        offsets = cache.get("offsets", [])
        if cache.get("count") != 36 or len(offsets) != 36 or any(int(x) != expected_offset for x in offsets):
            summary["classification"] = "KV_CACHE_OFFSET_FAIL"
            summary["failure_reason"] = f"{label} offsets/count invalid: {cache!r}"
            return finish(8)
        total = int(cache.get("total_nbytes", -1))
        if abs(total - EXPECTED_KV_TOTAL_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "KV_CACHE_SIZE_FAIL"
            summary["failure_reason"] = f"{label} cache bytes {total} not near {EXPECTED_KV_TOTAL_BYTES}"
            return finish(8)

    for side in ["resident", "stream"]:
        prompt_bytes = int(child[side]["cache_after_prompt"]["total_nbytes"])
        token_bytes = int(child[side]["cache_after_token"]["total_nbytes"])
        if token_bytes - prompt_bytes > 1 * 1024 * 1024:
            summary["classification"] = "KV_CACHE_GROWTH_UNEXPECTED"
            summary["failure_reason"] = f"{side} cache grew {token_bytes - prompt_bytes} B below 256-token capacity"
            return finish(8)

    # Weight-stage gates for both streamed passes.
    for pass_name in ["stream_prompt", "stream_token"]:
        record = child[pass_name]
        stages = record["stages"]
        if abs(int(stages["embedding"]["materialized_delta_bytes"]) - EXPECTED_EMBED_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "STREAMED_WEIGHT_STAGE_MISMATCH"
            summary["failure_reason"] = f"{pass_name} embedding materialization mismatch"
            return finish(9)
        if abs(int(stages["norm"]["materialized_delta_bytes"]) - EXPECTED_NORM_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "STREAMED_WEIGHT_STAGE_MISMATCH"
            summary["failure_reason"] = f"{pass_name} norm materialization mismatch"
            return finish(9)
        if abs(int(stages["head"]["materialized_delta_bytes"]) - EXPECTED_HEAD_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "STREAMED_WEIGHT_STAGE_MISMATCH"
            summary["failure_reason"] = f"{pass_name} head materialization mismatch"
            return finish(9)
        cycles = record["cycles"]
        if len(cycles) != 36:
            summary["classification"] = "STREAMED_LAYER_COUNT_FAIL"
            summary["failure_reason"] = f"{pass_name} cycle count {len(cycles)}"
            return finish(9)
        for cycle in cycles:
            if cycle["pre_eval_delta_bytes"] > 32 * 1024 * 1024:
                summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
                summary["failure_reason"] = f"{pass_name} layer {cycle['layer_id']} pre-eval delta {cycle['pre_eval_delta_bytes']}"
                return finish(9)
            if abs(int(cycle["materialized_delta_bytes"]) - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:
                summary["classification"] = "STREAMED_MATERIALIZATION_SIZE_MISMATCH"
                summary["failure_reason"] = f"{pass_name} layer {cycle['layer_id']} materialized {cycle['materialized_delta_bytes']}"
                return finish(9)

    if not child["prompt_parity"]["pass"]:
        summary["classification"] = "PROMPT_KV_NUMERICAL_PARITY_FAIL"
        summary["failure_reason"] = f"prompt max abs diff {child['prompt_parity']['max_abs_diff']} > {child['prompt_parity']['threshold']}"
        return finish(10)
    if not child["prompt_parity"]["generated_token_equal"]:
        summary["classification"] = "GENERATED_TOKEN_MISMATCH"
        summary["failure_reason"] = f"resident token {child['resident']['next_token']} != streamed {child['stream']['next_token']}"
        return finish(10)
    if not child["post_token_parity"]["pass"]:
        summary["classification"] = "POST_TOKEN_KV_NUMERICAL_PARITY_FAIL"
        summary["failure_reason"] = f"post-token max abs diff {child['post_token_parity']['max_abs_diff']} > {child['post_token_parity']['threshold']}"
        return finish(10)

    summary["classification"] = "ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS"
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
