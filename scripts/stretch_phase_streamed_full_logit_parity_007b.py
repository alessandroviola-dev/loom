#!/usr/bin/env python3
"""LOOM Stretch 007B — phase-streamed full-logit parity.

Resident control: official mlx_lm.utils.load_model full Qwen3 model.
Streamed path: embedding -> evict -> layers 0..35 one at a time -> final norm
-> LM head. No tokenizer, KV cache, autoregressive generation, or download.
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

SOURCE_001_BLOB = "890444928abd6cc24e7194317c92b36b50fd994b"
SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"
SOURCE_005_BLOB = "8bbfff727a0131c48d4ba71edc8de485182b7fbe"

EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_QUANTIZATION = {"group_size": 64, "bits": 3}
EXPECTED_TOTAL_BYTES = 3_583_928_320
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_EMBED_BYTES = 272_269_312
EXPECTED_EMBED_TENSORS = 3
EXPECTED_NORM_BYTES = 8_192
EXPECTED_NORM_TENSORS = 1
EXPECTED_HEAD_BYTES = 272_269_312
EXPECTED_HEAD_TENSORS = 3
EXPECTED_NON_LAYER_BYTES = 544_546_816
TOKEN_IDS = [[1, 42, 2048, 151935]]

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
from mlx_lm.utils import load_model

model_dir = Path(sys.argv[1])
weight_path = Path(sys.argv[2])
config_path = Path(sys.argv[3])
state_path = Path(sys.argv[4])
token_ids = json.loads(sys.argv[5])
expected_layer_bytes = int(sys.argv[6])
expected_layer_tensors = int(sys.argv[7])
expected_embed_bytes = int(sys.argv[8])
expected_norm_bytes = int(sys.argv[9])
expected_head_bytes = int(sys.argv[10])

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


def make_tokens():
    ids = mx.array(token_ids, dtype=mx.int32)
    mx.eval(ids)
    return ids


required_api = [
    "load",
    "eval",
    "get_active_memory",
    "get_cache_memory",
    "get_peak_memory",
    "reset_peak_memory",
    "clear_cache",
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
        "rms_norm_eps": config.get("rms_norm_eps"),
        "tie_word_embeddings": config.get("tie_word_embeddings"),
        "quantization": quant,
    },
)

# ---------------------------------------------------------------------------
# Resident official control
# ---------------------------------------------------------------------------
resident_base_active = int(mx.get_active_memory())
started = time.perf_counter()
resident_model, resident_loaded_config = load_model(model_dir, lazy=False, strict=True)
resident_load_wall = time.perf_counter() - started
resident_post_load_active = int(mx.get_active_memory())
resident_post_load_cache = int(mx.get_cache_memory())
save(
    "resident_model_loaded",
    base_active_bytes=resident_base_active,
    post_load_active_bytes=resident_post_load_active,
    materialized_delta_bytes=resident_post_load_active - resident_base_active,
    load_wall_seconds=round(resident_load_wall, 6),
)

resident_tokens = make_tokens()
started = time.perf_counter()
resident_logits = resident_model(resident_tokens, cache=None)
mx.eval(resident_logits)
resident_forward_wall = time.perf_counter() - started
resident_peak = int(mx.get_peak_memory())
resident_max_abs = float(mx.max(mx.abs(resident_logits.astype(mx.float32))).item())
resident_top1 = mx.argmax(resident_logits, axis=-1)
mx.eval(resident_top1)
save(
    "resident_forward_complete",
    forward_wall_seconds=round(resident_forward_wall, 6),
    logits_shape=list(resident_logits.shape),
    logits_max_abs=resident_max_abs,
)

del resident_model, resident_loaded_config, resident_tokens
gc.collect()
mx.clear_cache()
gc.collect()
resident_after_clear_active = int(mx.get_active_memory())
resident_after_clear_cache = int(mx.get_cache_memory())
save(
    "resident_control_cleared",
    active_bytes=resident_after_clear_active,
    cache_bytes=resident_after_clear_cache,
)

# ---------------------------------------------------------------------------
# Phase-streamed path
# ---------------------------------------------------------------------------
mx.reset_peak_memory()
stream_base_active = int(mx.get_active_memory())
stream_tokens = make_tokens()

# Stage 1: embedding
embed_pre_active = int(mx.get_active_memory())
embed_selected = select_weights("model.embed_tokens.", "model.")
embed_selected_bytes = selected_bytes(embed_selected)
embed_stage = EmbeddingStage()
quantize_and_load(embed_stage, embed_selected)
embed_pre_eval_active = int(mx.get_active_memory())
started = time.perf_counter()
mx.eval(embed_stage.parameters())
embed_materialize_wall = time.perf_counter() - started
embed_post_materialize_active = int(mx.get_active_memory())
started = time.perf_counter()
h = embed_stage(stream_tokens)
mx.eval(h)
embed_forward_wall = time.perf_counter() - started
del stream_tokens, embed_stage, embed_selected
gc.collect()
mx.clear_cache()
gc.collect()
embed_post_clear_active = int(mx.get_active_memory())
embed_post_clear_cache = int(mx.get_cache_memory())
embedding_stage = {
    "selected_bytes": embed_selected_bytes,
    "pre_active_bytes": embed_pre_active,
    "pre_eval_active_bytes": embed_pre_eval_active,
    "post_materialize_active_bytes": embed_post_materialize_active,
    "post_clear_active_bytes": embed_post_clear_active,
    "post_clear_cache_bytes": embed_post_clear_cache,
    "pre_eval_delta_bytes": embed_pre_eval_active - embed_pre_active,
    "materialized_delta_bytes": embed_post_materialize_active - embed_pre_active,
    "post_clear_delta_bytes": embed_post_clear_active - embed_pre_active,
    "materialize_wall_seconds": round(embed_materialize_wall, 6),
    "forward_wall_seconds": round(embed_forward_wall, 6),
}
save("stream_embedding_complete", stage=embedding_stage)

# Stage 2: all transformer blocks, no KV cache.
mask = create_attention_mask(h, None)
stream_cycles = []
total_layer_materialize_wall = 0.0
total_layer_forward_wall = 0.0
for layer_id in range(args.num_hidden_layers):
    pre_active = int(mx.get_active_memory())
    block, selected = build_block(layer_id)
    pre_eval_active = int(mx.get_active_memory())

    started = time.perf_counter()
    mx.eval(block.parameters())
    materialize_wall = time.perf_counter() - started
    total_layer_materialize_wall += materialize_wall
    post_materialize_active = int(mx.get_active_memory())

    started = time.perf_counter()
    out = block(h, mask, None)
    mx.eval(out)
    forward_wall = time.perf_counter() - started
    total_layer_forward_wall += forward_wall

    old_h = h
    h = out
    del old_h, block, selected
    gc.collect()
    mx.clear_cache()
    gc.collect()
    post_clear_active = int(mx.get_active_memory())
    post_clear_cache = int(mx.get_cache_memory())

    cycle = {
        "layer_id": layer_id,
        "pre_active_bytes": pre_active,
        "pre_eval_active_bytes": pre_eval_active,
        "post_materialize_active_bytes": post_materialize_active,
        "post_clear_active_bytes": post_clear_active,
        "post_clear_cache_bytes": post_clear_cache,
        "pre_eval_delta_bytes": pre_eval_active - pre_active,
        "materialized_delta_bytes": post_materialize_active - pre_active,
        "post_clear_delta_bytes": post_clear_active - pre_active,
        "materialize_wall_seconds": round(materialize_wall, 6),
        "forward_wall_seconds": round(forward_wall, 6),
    }
    stream_cycles.append(cycle)
    save(f"stream_layer_{layer_id}_complete", cycle=cycle)

# Stage 3: final RMSNorm
norm_pre_active = int(mx.get_active_memory())
norm_selected = select_weights("model.norm.", "model.")
norm_selected_bytes = selected_bytes(norm_selected)
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
norm_post_clear_cache = int(mx.get_cache_memory())
norm_stage_record = {
    "selected_bytes": norm_selected_bytes,
    "pre_active_bytes": norm_pre_active,
    "pre_eval_active_bytes": norm_pre_eval_active,
    "post_materialize_active_bytes": norm_post_materialize_active,
    "post_clear_active_bytes": norm_post_clear_active,
    "post_clear_cache_bytes": norm_post_clear_cache,
    "pre_eval_delta_bytes": norm_pre_eval_active - norm_pre_active,
    "materialized_delta_bytes": norm_post_materialize_active - norm_pre_active,
    "post_clear_delta_bytes": norm_post_clear_active - norm_pre_active,
    "materialize_wall_seconds": round(norm_materialize_wall, 6),
    "forward_wall_seconds": round(norm_forward_wall, 6),
}
save("stream_final_norm_complete", stage=norm_stage_record)

# Stage 4: separate LM head
head_pre_active = int(mx.get_active_memory())
head_selected = select_weights("lm_head.")
head_selected_bytes = selected_bytes(head_selected)
head_stage = HeadStage()
quantize_and_load(head_stage, head_selected)
head_pre_eval_active = int(mx.get_active_memory())
started = time.perf_counter()
mx.eval(head_stage.parameters())
head_materialize_wall = time.perf_counter() - started
head_post_materialize_active = int(mx.get_active_memory())
started = time.perf_counter()
stream_logits = head_stage(h)
mx.eval(stream_logits)
head_forward_wall = time.perf_counter() - started
del h, head_stage, head_selected
gc.collect()
mx.clear_cache()
gc.collect()
head_post_clear_active = int(mx.get_active_memory())
head_post_clear_cache = int(mx.get_cache_memory())
head_stage_record = {
    "selected_bytes": head_selected_bytes,
    "pre_active_bytes": head_pre_active,
    "pre_eval_active_bytes": head_pre_eval_active,
    "post_materialize_active_bytes": head_post_materialize_active,
    "post_clear_active_bytes": head_post_clear_active,
    "post_clear_cache_bytes": head_post_clear_cache,
    "pre_eval_delta_bytes": head_pre_eval_active - head_pre_active,
    "materialized_delta_bytes": head_post_materialize_active - head_pre_active,
    "post_clear_delta_bytes": head_post_clear_active - head_pre_active,
    "materialize_wall_seconds": round(head_materialize_wall, 6),
    "forward_wall_seconds": round(head_forward_wall, 6),
}
save("stream_lm_head_complete", stage=head_stage_record)

# Full-logit numerical parity.
diff = mx.abs(resident_logits.astype(mx.float32) - stream_logits.astype(mx.float32))
mx.eval(diff)
max_abs_diff = float(mx.max(diff).item())
mean_abs_diff = float(mx.mean(diff).item())
parity_threshold = 1e-5 + 1e-5 * resident_max_abs
parity_pass = max_abs_diff <= parity_threshold
stream_top1 = mx.argmax(stream_logits, axis=-1)
mx.eval(stream_top1)
resident_top1_list = resident_top1.tolist()
stream_top1_list = stream_top1.tolist()
top1_equal = resident_top1_list == stream_top1_list

max_layer_delta = max(c["materialized_delta_bytes"] for c in stream_cycles)
max_stream_stage_delta = max(
    embedding_stage["materialized_delta_bytes"],
    max_layer_delta,
    norm_stage_record["materialized_delta_bytes"],
    head_stage_record["materialized_delta_bytes"],
)
resident_materialized_delta = resident_post_load_active - resident_base_active
residency_ratio = (
    resident_materialized_delta / max_stream_stage_delta
    if max_stream_stage_delta > 0
    else None
)

final = {
    "versions": versions,
    "baseline": baseline["memory"],
    "resident": {
        "base_active_bytes": resident_base_active,
        "post_load_active_bytes": resident_post_load_active,
        "post_load_cache_bytes": resident_post_load_cache,
        "materialized_delta_bytes": resident_materialized_delta,
        "after_clear_active_bytes": resident_after_clear_active,
        "after_clear_cache_bytes": resident_after_clear_cache,
        "load_wall_seconds": round(resident_load_wall, 6),
        "forward_wall_seconds": round(resident_forward_wall, 6),
        "peak_bytes": resident_peak,
        "logits_shape": list(resident_logits.shape),
        "logits_max_abs": resident_max_abs,
        "top1": resident_top1_list,
    },
    "embedding_stage": embedding_stage,
    "stream_cycles": stream_cycles,
    "layers": {
        "max_materialized_delta_bytes": max_layer_delta,
        "total_materialize_wall_seconds": round(total_layer_materialize_wall, 6),
        "total_forward_wall_seconds": round(total_layer_forward_wall, 6),
    },
    "norm_stage": norm_stage_record,
    "head_stage": head_stage_record,
    "stream": {
        "max_weight_stage_materialized_delta_bytes": max_stream_stage_delta,
        "resident_to_max_streamed_stage_ratio": residency_ratio,
        "logits_shape": list(stream_logits.shape),
        "top1": stream_top1_list,
    },
    "parity": {
        "max_abs_diff": max_abs_diff,
        "mean_abs_diff": mean_abs_diff,
        "resident_max_abs": resident_max_abs,
        "threshold": parity_threshold,
        "pass": parity_pass,
        "top1_equal": top1_equal,
    },
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


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source001 = repo / "scripts" / "stretch_layer_streaming_feasibility_001.py"
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    source005 = repo / "scripts" / "stretch_eight_layer_streamed_forward_scaling_005.py"

    observed001 = git_blob(source001, repo)
    observed002 = git_blob(source002, repo)
    observed005 = git_blob(source005, repo)

    print("LOOM Stretch 007B — Phase-Streamed Full-Logit Parity")
    print(f"Stretch 001 helper blob: {observed001}")
    print(f"Stretch 002 helper blob: {observed002}")
    print(f"Stretch 005 source blob: {observed005}")
    if observed001 != SOURCE_001_BLOB or observed002 != SOURCE_002_BLOB or observed005 != SOURCE_005_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    anatomy = load_module(source001, "loom_stretch001_anatomy")
    helpers = load_module(source002, "loom_stretch002_helpers")

    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "phase-streamed-full-logit-parity-007b" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / "child-state.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 007B — Phase-Streamed Full-Logit Parity",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "token_ids": TOKEN_IDS,
        "kv_cache": False,
        "tokenizer": False,
        "autoregressive_generation": False,
        "network_download": False,
        "source_001_blob": observed001,
        "source_002_blob": observed002,
        "source_005_blob": observed005,
        "disk_before": helpers.disk_snapshot(repo),
    }
    telemetry = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = helpers.disk_snapshot(repo)
        summary["telemetry"] = helpers.summarize_telemetry(telemetry)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        if summary.get("parity"):
            p = summary["parity"]
            print(
                f"Parity: pass={p.get('pass')} max_abs={p.get('max_abs_diff')} "
                f"mean_abs={p.get('mean_abs_diff')} threshold={p.get('threshold')} "
                f"top1_equal={p.get('top1_equal')}"
            )
        if summary.get("resident"):
            print(f"Resident full-model materialized delta: {summary['resident'].get('materialized_delta_bytes')} B")
        if summary.get("embedding_stage"):
            print(f"Embedding materialized delta: {summary['embedding_stage'].get('materialized_delta_bytes')} B")
        if summary.get("layers"):
            print(f"Max transformer-layer materialized delta: {summary['layers'].get('max_materialized_delta_bytes')} B")
        if summary.get("norm_stage"):
            print(f"Final norm selected/materialized: {summary['norm_stage'].get('selected_bytes')} / {summary['norm_stage'].get('materialized_delta_bytes')} B")
        if summary.get("head_stage"):
            print(f"LM-head materialized delta: {summary['head_stage'].get('materialized_delta_bytes')} B")
        if summary.get("stream"):
            print(f"Max streamed weight-stage delta: {summary['stream'].get('max_weight_stage_materialized_delta_bytes')} B")
            print(f"Resident/max-streamed-stage ratio: {summary['stream'].get('resident_to_max_streamed_stage_ratio')}")
            print(f"Resident top1: {summary['resident'].get('top1')}")
            print(f"Streamed top1: {summary['stream'].get('top1')}")
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("Resident control: official full Qwen3 load_model")
    print("Streamed path: embedding -> evict -> layers 0..35 -> norm -> LM head")
    print("Tokenizer/KV/autoregressive generation: NONE")
    print(f"Frozen token IDs: {TOKEN_IDS}")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required_paths = [source001, source002, source005, venv_py, weight, config_path]
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
        summary["failure_reason"] = (
            f"model config/quantization mismatch: config={observed_config!r} "
            f"quantization={config.get('quantization')!r}"
        )
        return finish(2)
    print(f"Model config/quantization: PASS {observed_config} quantization={EXPECTED_QUANTIZATION}")

    try:
        _, tensors = anatomy.catalog_weights(model_dir)
    except Exception as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"cannot catalog safetensors: {type(exc).__name__}: {exc}"
        return finish(2)

    total_bytes = sum(int(t["bytes"]) for t in tensors)
    non_layer = [t for t in tensors if t["layer_id"] is None]
    non_layer_bytes = sum(int(t["bytes"]) for t in non_layer)
    embed = [t for t in non_layer if t["name"].startswith("model.embed_tokens.")]
    norm = [t for t in non_layer if t["name"].startswith("model.norm.")]
    head = [t for t in non_layer if t["name"].startswith("lm_head.")]
    other = [t for t in non_layer if t not in embed and t not in norm and t not in head]
    layout = {
        "total_bytes": total_bytes,
        "non_layer_bytes": non_layer_bytes,
        "embedding": {"tensors": len(embed), "bytes": sum(int(t["bytes"]) for t in embed)},
        "final_norm": {"tensors": len(norm), "bytes": sum(int(t["bytes"]) for t in norm)},
        "lm_head": {"tensors": len(head), "bytes": sum(int(t["bytes"]) for t in head)},
        "other": {"tensors": len(other), "bytes": sum(int(t["bytes"]) for t in other)},
    }
    summary["layout"] = layout
    if not (
        total_bytes == EXPECTED_TOTAL_BYTES
        and non_layer_bytes == EXPECTED_NON_LAYER_BYTES
        and layout["embedding"] == {"tensors": EXPECTED_EMBED_TENSORS, "bytes": EXPECTED_EMBED_BYTES}
        and layout["final_norm"] == {"tensors": EXPECTED_NORM_TENSORS, "bytes": EXPECTED_NORM_BYTES}
        and layout["lm_head"] == {"tensors": EXPECTED_HEAD_TENSORS, "bytes": EXPECTED_HEAD_BYTES}
        and layout["other"] == {"tensors": 0, "bytes": 0}
    ):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"shared-component layout mismatch: {layout!r}"
        return finish(2)
    print(f"Shared-component layout: PASS {layout}")

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
        str(venv_py),
        "-c",
        CHILD_CODE,
        str(model_dir),
        str(weight),
        str(config_path),
        str(state_path),
        json.dumps(TOKEN_IDS),
        str(EXPECTED_LAYER_BYTES),
        str(EXPECTED_LAYER_TENSORS),
        str(EXPECTED_EMBED_BYTES),
        str(EXPECTED_NORM_BYTES),
        str(EXPECTED_HEAD_BYTES),
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

    for key in ["resident", "embedding_stage", "stream_cycles", "layers", "norm_stage", "head_stage", "stream", "parity", "baseline", "final_memory"]:
        summary[key] = child[key]

    resident_delta = int(child["resident"]["materialized_delta_bytes"])
    if abs(resident_delta - EXPECTED_TOTAL_BYTES) > 64 * 1024 * 1024:
        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"
        summary["failure_reason"] = f"resident delta {resident_delta} B not near expected {EXPECTED_TOTAL_BYTES} B"
        return finish(7)

    embed_stage = child["embedding_stage"]
    if embed_stage["selected_bytes"] != EXPECTED_EMBED_BYTES:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"embedding selected payload {embed_stage['selected_bytes']} B"
        return finish(7)
    if embed_stage["pre_eval_delta_bytes"] > 32 * 1024 * 1024:
        summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
        summary["failure_reason"] = f"embedding pre-eval delta {embed_stage['pre_eval_delta_bytes']} B"
        return finish(7)
    if abs(embed_stage["materialized_delta_bytes"] - EXPECTED_EMBED_BYTES) > 2 * 1024 * 1024:
        summary["classification"] = "EMBEDDING_MATERIALIZATION_SIZE_MISMATCH"
        summary["failure_reason"] = f"embedding materialized delta {embed_stage['materialized_delta_bytes']} B"
        return finish(7)
    if embed_stage["post_clear_cache_bytes"] > 4 * 1024 * 1024:
        summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
        summary["failure_reason"] = f"embedding post-clear cache {embed_stage['post_clear_cache_bytes']} B"
        return finish(7)

    for cycle in child["stream_cycles"]:
        if cycle["pre_eval_delta_bytes"] > 32 * 1024 * 1024:
            summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
            summary["failure_reason"] = f"layer {cycle['layer_id']} pre-eval delta {cycle['pre_eval_delta_bytes']} B"
            return finish(7)
        if abs(cycle["materialized_delta_bytes"] - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "STREAMED_MATERIALIZATION_SIZE_MISMATCH"
            summary["failure_reason"] = f"layer {cycle['layer_id']} materialized delta {cycle['materialized_delta_bytes']} B"
            return finish(7)
        if abs(cycle["post_clear_delta_bytes"]) > 4 * 1024 * 1024:
            summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
            summary["failure_reason"] = f"layer {cycle['layer_id']} post-clear delta {cycle['post_clear_delta_bytes']} B"
            return finish(7)
        if cycle["post_clear_cache_bytes"] > 4 * 1024 * 1024:
            summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
            summary["failure_reason"] = f"layer {cycle['layer_id']} post-clear cache {cycle['post_clear_cache_bytes']} B"
            return finish(7)

    norm_stage = child["norm_stage"]
    if norm_stage["selected_bytes"] != EXPECTED_NORM_BYTES:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"final norm selected payload {norm_stage['selected_bytes']} B"
        return finish(7)
    if norm_stage["post_clear_cache_bytes"] > 4 * 1024 * 1024:
        summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
        summary["failure_reason"] = f"final norm post-clear cache {norm_stage['post_clear_cache_bytes']} B"
        return finish(7)

    head_stage = child["head_stage"]
    if head_stage["selected_bytes"] != EXPECTED_HEAD_BYTES:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"LM-head selected payload {head_stage['selected_bytes']} B"
        return finish(7)
    if head_stage["pre_eval_delta_bytes"] > 32 * 1024 * 1024:
        summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
        summary["failure_reason"] = f"LM-head pre-eval delta {head_stage['pre_eval_delta_bytes']} B"
        return finish(7)
    if abs(head_stage["materialized_delta_bytes"] - EXPECTED_HEAD_BYTES) > 2 * 1024 * 1024:
        summary["classification"] = "LM_HEAD_MATERIALIZATION_SIZE_MISMATCH"
        summary["failure_reason"] = f"LM-head materialized delta {head_stage['materialized_delta_bytes']} B"
        return finish(7)
    if head_stage["post_clear_cache_bytes"] > 4 * 1024 * 1024:
        summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
        summary["failure_reason"] = f"LM-head post-clear cache {head_stage['post_clear_cache_bytes']} B"
        return finish(7)

    if child["resident"]["logits_shape"] != [1, 4, 151936] or child["stream"]["logits_shape"] != [1, 4, 151936]:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"unexpected logits shape resident={child['resident']['logits_shape']} stream={child['stream']['logits_shape']}"
        return finish(8)

    if not child["parity"]["pass"]:
        summary["classification"] = "NUMERICAL_PARITY_FAIL"
        summary["failure_reason"] = f"max abs diff {child['parity']['max_abs_diff']} > threshold {child['parity']['threshold']}"
        return finish(8)

    summary["classification"] = "PHASE_STREAMED_FULL_LOGIT_PARITY_PASS"
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
