#!/usr/bin/env python3
"""LOOM Stretch 015 — eight-token divergence attribution.

Diagnostic successor to the valid Stretch 014 numerical-parity failure.
Preserves the frozen MLX/model stack and tests whether M=8 changes the numerical
result of the actual quantized layer-0 projections and block-internal stages
relative to M=1/M=4. No MLX upgrade, no model change, no performance claim.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SOURCE_014_BLOB = "6d7afd43969e752a7cce39ae474d7054ccc7edd8"
SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_QUANTIZATION = {"group_size": 64, "bits": 3}
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_EMBED_BYTES = 272_269_312
PROMPT_TOKEN_IDS = [1, 42, 2048, 151935]
ORACLE_PREFIX_8 = [1, 374, 264, 4647, 1483, 304, 279, 1809]
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
MAX_SWAP_MB = 5600.0


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


def child_main(argv: list[str]) -> int:
    # Imports intentionally live in the frozen venv child only.
    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm.models import qwen3
    from mlx_lm.models.activations import swiglu
    from mlx_lm.models.base import create_attention_mask, scaled_dot_product_attention
    from mlx_lm.models.cache import KVCache

    model_dir = Path(argv[0])
    weight_path = Path(argv[1])
    config_path = Path(argv[2])
    output_path = Path(argv[3])

    config = json.loads(config_path.read_text(encoding="utf-8"))
    args = qwen3.ModelArgs.from_dict(config)
    quant = config["quantization"]

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

    def build_block(layer_id: int):
        marker = f"model.layers.{layer_id}."
        selected = select_weights(marker, marker)
        if len(selected) != EXPECTED_LAYER_TENSORS:
            raise RuntimeError(
                f"layer {layer_id} tensor count {len(selected)} != {EXPECTED_LAYER_TENSORS}"
            )
        if selected_bytes(selected) != EXPECTED_LAYER_BYTES:
            raise RuntimeError(
                f"layer {layer_id} selected bytes {selected_bytes(selected)} != {EXPECTED_LAYER_BYTES}"
            )
        block = qwen3.TransformerBlock(args)
        quantize_and_load(block, selected)
        mx.eval(block.parameters())
        return block, selected

    def capture_seq(arr, seq_axis: int):
        if seq_axis == 1:
            view = arr[:, 0:1, ...]
        elif seq_axis == 2:
            view = arr[:, :, 0:1, ...]
        else:
            raise ValueError(seq_axis)
        out = (view + mx.zeros_like(view)).astype(mx.float32).reshape(-1)
        mx.eval(out)
        return out

    def metrics(a, b) -> dict:
        diff = mx.abs(a - b)
        mx.eval(diff)
        max_abs = float(mx.max(diff).item())
        mean_abs = float(mx.mean(diff).item())
        return {
            "max_abs_diff": max_abs,
            "mean_abs_diff": mean_abs,
            "exact": max_abs == 0.0,
            "elements": int(a.size),
        }

    def compare_three(vectors: dict[int, object]) -> dict:
        return {
            "m1_vs_m4": metrics(vectors[1], vectors[4]),
            "m1_vs_m8": metrics(vectors[1], vectors[8]),
            "m4_vs_m8": metrics(vectors[4], vectors[8]),
        }

    started = time.perf_counter()

    # Actual frozen-token embeddings; this keeps the probe tied to the workload
    # while still comparing identical first-row inputs across M values.
    embed_selected = select_weights("model.embed_tokens.", "model.")
    if selected_bytes(embed_selected) != EXPECTED_EMBED_BYTES:
        raise RuntimeError(
            f"embedding bytes {selected_bytes(embed_selected)} != {EXPECTED_EMBED_BYTES}"
        )
    embed_stage = EmbeddingStage()
    quantize_and_load(embed_stage, embed_selected)
    mx.eval(embed_stage.parameters())
    prompt_ids = mx.array([PROMPT_TOKEN_IDS], dtype=mx.int32)
    oracle_ids = mx.array([ORACLE_PREFIX_8], dtype=mx.int32)
    prompt_h = embed_stage(prompt_ids)
    oracle_h8 = embed_stage(oracle_ids)
    mx.eval(prompt_h, oracle_h8)
    del embed_stage, embed_selected, prompt_ids, oracle_ids
    gc.collect()
    mx.clear_cache()

    block, block_selected = build_block(0)

    # ------------------------------------------------------------------
    # A. Direct QuantizedLinear M-shape probes.
    # Same first-row input; only the number of rows passed to the kernel changes.
    # ------------------------------------------------------------------
    hidden_probe8 = block.input_layernorm(oracle_h8)
    mx.eval(hidden_probe8)

    intermediate_total = 8 * args.intermediate_size
    intermediate_probe8 = (
        ((mx.arange(intermediate_total, dtype=mx.int32) % 257).astype(mx.float32) - 128.0)
        / 64.0
    ).reshape(1, 8, args.intermediate_size).astype(mx.bfloat16)
    mx.eval(intermediate_probe8)

    projection_modules = {
        "q_proj": (block.self_attn.q_proj, hidden_probe8),
        "k_proj": (block.self_attn.k_proj, hidden_probe8),
        "v_proj": (block.self_attn.v_proj, hidden_probe8),
        "o_proj": (block.self_attn.o_proj, hidden_probe8),
        "gate_proj": (block.mlp.gate_proj, hidden_probe8),
        "up_proj": (block.mlp.up_proj, hidden_probe8),
        "down_proj": (block.mlp.down_proj, intermediate_probe8),
    }

    projection_tests = {}
    projection_order = list(projection_modules)
    for name, (module, probe8) in projection_modules.items():
        vectors = {}
        for m in (1, 4, 8):
            y = module(probe8[:, :m, :])
            vectors[m] = capture_seq(y, 1)
            del y
        projection_tests[name] = compare_three(vectors)
        del vectors

    # ------------------------------------------------------------------
    # B. Layer-0 internal trace with the real 4-token prompt in an ordinary
    # BF16 KVCache, reproducing the causal offset used by Stretch 014.
    # ------------------------------------------------------------------
    trace_order = [
        "input_layernorm",
        "q_proj",
        "k_proj",
        "v_proj",
        "q_norm",
        "k_norm",
        "q_rope",
        "k_rope",
        "sdpa",
        "o_proj",
        "attention_residual",
        "post_attention_layernorm",
        "gate_proj",
        "up_proj",
        "swiglu",
        "down_proj",
        "block_out",
    ]

    def trace_for_m(m: int) -> tuple[dict, dict]:
        cache = KVCache()
        prompt_mask = create_attention_mask(prompt_h, cache)
        prompt_out = block(prompt_h, prompt_mask, cache)
        mx.eval(prompt_out, cache.keys, cache.values)
        if int(cache.offset) != len(PROMPT_TOKEN_IDS):
            raise RuntimeError(f"prompt cache offset {cache.offset} != 4")

        x = oracle_h8[:, :m, :]
        mask = create_attention_mask(x, cache)
        traces = {}

        norm = block.input_layernorm(x)
        traces["input_layernorm"] = capture_seq(norm, 1)

        attn = block.self_attn
        B, L, _ = norm.shape
        q_raw = attn.q_proj(norm)
        k_raw = attn.k_proj(norm)
        v_raw = attn.v_proj(norm)
        traces["q_proj"] = capture_seq(q_raw, 1)
        traces["k_proj"] = capture_seq(k_raw, 1)
        traces["v_proj"] = capture_seq(v_raw, 1)

        queries = attn.q_norm(q_raw.reshape(B, L, attn.n_heads, -1)).transpose(0, 2, 1, 3)
        keys = attn.k_norm(k_raw.reshape(B, L, attn.n_kv_heads, -1)).transpose(0, 2, 1, 3)
        values = v_raw.reshape(B, L, attn.n_kv_heads, -1).transpose(0, 2, 1, 3)
        traces["q_norm"] = capture_seq(queries, 2)
        traces["k_norm"] = capture_seq(keys, 2)

        rope_offset = int(cache.offset)
        queries = attn.rope(queries, offset=rope_offset)
        keys = attn.rope(keys, offset=rope_offset)
        traces["q_rope"] = capture_seq(queries, 2)
        traces["k_rope"] = capture_seq(keys, 2)

        keys_all, values_all = cache.update_and_fetch(keys, values)
        mx.eval(keys_all, values_all)
        sdpa = scaled_dot_product_attention(
            queries,
            keys_all,
            values_all,
            cache=cache,
            scale=attn.scale,
            mask=mask,
        )
        traces["sdpa"] = capture_seq(sdpa, 2)

        attn_concat = sdpa.transpose(0, 2, 1, 3).reshape(B, L, -1)
        o = attn.o_proj(attn_concat)
        traces["o_proj"] = capture_seq(o, 1)
        h = x + o
        traces["attention_residual"] = capture_seq(h, 1)

        post = block.post_attention_layernorm(h)
        traces["post_attention_layernorm"] = capture_seq(post, 1)
        gate = block.mlp.gate_proj(post)
        up = block.mlp.up_proj(post)
        traces["gate_proj"] = capture_seq(gate, 1)
        traces["up_proj"] = capture_seq(up, 1)
        sw = swiglu(gate, up)
        traces["swiglu"] = capture_seq(sw, 1)
        down = block.mlp.down_proj(sw)
        traces["down_proj"] = capture_seq(down, 1)
        out = h + down
        traces["block_out"] = capture_seq(out, 1)
        mx.eval(out)

        state = {
            "m": m,
            "prompt_offset": 4,
            "final_offset": int(cache.offset),
            "expected_final_offset": 4 + m,
            "kv_nbytes": int(cache.nbytes),
        }
        return traces, state

    traces_by_m = {}
    cache_states = {}
    for m in (1, 4, 8):
        traces_by_m[m], cache_states[m] = trace_for_m(m)

    trace_comparisons = {}
    for stage in trace_order:
        vectors = {m: traces_by_m[m][stage] for m in (1, 4, 8)}
        trace_comparisons[stage] = compare_three(vectors)

    first_projection_m4_m8 = next(
        (
            name
            for name in projection_order
            if not projection_tests[name]["m4_vs_m8"]["exact"]
        ),
        None,
    )
    first_trace_m4_m8 = next(
        (
            stage
            for stage in trace_order
            if not trace_comparisons[stage]["m4_vs_m8"]["exact"]
        ),
        None,
    )
    first_trace_m1_m4 = next(
        (
            stage
            for stage in trace_order
            if not trace_comparisons[stage]["m1_vs_m4"]["exact"]
        ),
        None,
    )

    if first_projection_m4_m8 is not None:
        classification = "QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED"
    elif first_trace_m4_m8 is not None:
        classification = "BLOCK_INTERNAL_SHAPE_DEPENDENCE_CONFIRMED"
    else:
        classification = "LAYER0_M8_DIVERGENCE_NOT_REPRODUCED"

    final = {
        "experiment": "Stretch 015 — Eight-Token Divergence Attribution",
        "classification": classification,
        "model_dir": str(model_dir),
        "quantization": quant,
        "prompt_token_ids": PROMPT_TOKEN_IDS,
        "oracle_prefix_8": ORACLE_PREFIX_8,
        "layer": 0,
        "m_values": [1, 4, 8],
        "projection_tests": projection_tests,
        "trace_order": trace_order,
        "trace_comparisons": trace_comparisons,
        "first_projection_m4_m8": first_projection_m4_m8,
        "first_trace_m4_m8": first_trace_m4_m8,
        "first_trace_m1_m4": first_trace_m1_m4,
        "cache_states": cache_states,
        "peak_active_bytes": int(mx.get_peak_memory()),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }
    output_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Classification: {classification}")
    print(f"First direct QuantizedLinear M4/M8 divergence: {first_projection_m4_m8}")
    print(f"First layer-0 trace M4/M8 divergence: {first_trace_m4_m8}")
    print(f"First layer-0 trace M1/M4 divergence: {first_trace_m1_m4}")
    for name in projection_order:
        p = projection_tests[name]["m4_vs_m8"]
        print(
            f"Projection {name} M4/M8: exact={p['exact']} "
            f"max_abs={p['max_abs_diff']} mean_abs={p['mean_abs_diff']}"
        )
    for stage in trace_order:
        p = trace_comparisons[stage]["m4_vs_m8"]
        print(
            f"Trace {stage} M4/M8: exact={p['exact']} "
            f"max_abs={p['max_abs_diff']} mean_abs={p['mean_abs_diff']}"
        )
    print(f"Peak MLX memory: {final['peak_active_bytes']} B")
    print(f"Child summary: {output_path}")

    del block, block_selected
    gc.collect()
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main(sys.argv[2:])

    repo = Path(__file__).resolve().parents[1]
    source014 = repo / "scripts" / "stretch_eight_token_oracle_block_verification_014.py"
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    observed014 = git_blob(source014, repo)
    observed002 = git_blob(source002, repo)

    print("LOOM Stretch 015 — Eight-Token Divergence Attribution")
    print(f"Stretch 014 runner blob: {observed014}")
    print(f"Stretch 002 helper blob: {observed002}")
    if observed014 != SOURCE_014_BLOB or observed002 != SOURCE_002_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Scientific question: locate first M=4 vs M=8 numerical divergence")
    print("Frozen runtime/model/quantization: UNCHANGED")
    print("MLX upgrade / strict mode / threshold relaxation: NONE")

    helpers = load_module(source002, "loom_stretch002_helpers")
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "eight-token-divergence-attribution-015" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    child_summary = run_dir / "child-summary.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 015 — Eight-Token Divergence Attribution",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "source_014_blob": observed014,
        "source_002_blob": observed002,
        "disk_before": helpers.disk_snapshot(repo),
    }

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = helpers.disk_snapshot(repo)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        child = summary.get("child") or {}
        if child:
            print(f"First direct QuantizedLinear M4/M8 divergence: {child.get('first_projection_m4_m8')}")
            print(f"First layer-0 trace M4/M8 divergence: {child.get('first_trace_m4_m8')}")
            print(f"First layer-0 trace M1/M4 divergence: {child.get('first_trace_m1_m4')}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required = [source014, source002, venv_py, weight, config_path]
    if not all(path.is_file() for path in required):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required frozen source/venv/model/config path missing"
        return finish(2)

    version_proc = subprocess.run(
        [
            str(venv_py),
            "-c",
            "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    try:
        versions = json.loads(version_proc.stdout.strip())
    except Exception:
        versions = {}
    summary["versions"] = versions
    if versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {versions!r}"
        return finish(2)
    print(f"Version lock: PASS {versions}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    observed_quant = config.get("quantization")
    summary["quantization"] = observed_quant
    if observed_quant != EXPECTED_QUANTIZATION:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"quantization mismatch: {observed_quant!r}"
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
    observed_config = {key: config.get(key) for key in expected_config}
    summary["model_config"] = observed_config
    if observed_config != expected_config:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"model config mismatch: {observed_config!r}"
        return finish(2)
    print(f"Model config/quantization: PASS {observed_config} quantization={observed_quant}")

    try:
        names, layer_bytes = helpers.selected_layer_from_header(weight, 0)
    except Exception as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"layer 0 provenance recovery failed: {type(exc).__name__}: {exc}"
        return finish(2)
    if len(names) != EXPECTED_LAYER_TENSORS or layer_bytes != EXPECTED_LAYER_BYTES:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"layer 0 provenance mismatch: tensors={len(names)} bytes={layer_bytes}"
        return finish(2)
    print("Layer-0 provenance: PASS")

    host_samples = []
    for index in range(HOST_GATE_SAMPLES):
        sample = helpers.system_sample()
        host_samples.append(sample)
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
            time.sleep(0.5)
    summary["host_samples"] = host_samples
    print("Host-state gate: PASS")

    cmd = [
        str(venv_py),
        str(Path(__file__).resolve()),
        "--child",
        str(model_dir),
        str(weight),
        str(config_path),
        str(child_summary),
    ]
    proc = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    summary["child_returncode"] = proc.returncode

    if proc.returncode != 0 or not child_summary.is_file():
        summary["classification"] = "HARNESS_OR_CHILD_FAIL"
        summary["failure_reason"] = (
            f"child returncode={proc.returncode}; child_summary_exists={child_summary.is_file()}"
        )
        return finish(4)

    try:
        child = json.loads(child_summary.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "HARNESS_OR_CHILD_FAIL"
        summary["failure_reason"] = f"cannot parse child summary: {type(exc).__name__}: {exc}"
        return finish(4)

    summary["child"] = child
    summary["classification"] = child.get("classification")

    print(proc.stdout, end="" if proc.stdout.endswith("\n") or not proc.stdout else "\n")
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
