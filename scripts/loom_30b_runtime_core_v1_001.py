#!/usr/bin/env python3
"""Minimal tracked runtime core for LOOM 30B interactive v1.

This is the exact external-expert BF16-KV functionality promoted from the
validated local research helpers.  It deliberately imports only the canonical
PACKED backend plus frozen installed MLX/MLX-LM packages.
"""
from __future__ import annotations

import gc
import json
import os
import re
import struct
import time
from pathlib import Path
from typing import Any

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten
from mlx_lm.models.activations import swiglu
from mlx_lm.models.base import scaled_dot_product_attention
from mlx_lm.models.cache import KVCache

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "results-local/moe/models/Qwen3-30B-A3B-MLX-4bit"
LAYERS, TOP_K = 48, 8
EXPERT_BYTES = 2_506_752
PROJS = ("gate_proj", "up_proj", "down_proj")
COMPS = ("weight", "scales", "biases")
DT = {"F16": np.float16, "F32": np.float32, "U32": np.uint32}
EXPERT_RE = re.compile(r"^model\.layers\.(\d+)\.mlp\.switch_mlp\.")


class QLinear(nn.Module):
    def __init__(self, inn: int, out: int) -> None:
        super().__init__()
        self.inn, self.out = inn, out

    def __call__(self, x: Any) -> Any:
        return mx.quantized_matmul(x, self.weight, scales=self.scales, biases=self.biases,
                                   transpose=True, group_size=128, bits=4, mode="affine")


class QEmbedding(nn.Module):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, x: Any) -> Any:
        return mx.dequantize(self.weight[x], scales=self.scales[x], biases=self.biases[x],
                             group_size=128, bits=4, mode="affine")


class Attention(nn.Module):
    def __init__(self, cfg: dict[str, Any]) -> None:
        super().__init__()
        self.n_heads = cfg["num_attention_heads"]
        self.n_kv_heads = cfg["num_key_value_heads"]
        self.scale = cfg["head_dim"] ** -0.5
        self.q_proj, self.k_proj = QLinear(2048, 4096), QLinear(2048, 512)
        self.v_proj, self.o_proj = QLinear(2048, 512), QLinear(4096, 2048)
        self.q_norm = nn.RMSNorm(cfg["head_dim"], eps=cfg["rms_norm_eps"])
        self.k_norm = nn.RMSNorm(cfg["head_dim"], eps=cfg["rms_norm_eps"])
        self.rope = nn.RoPE(cfg["head_dim"], traditional=False, base=cfg["rope_theta"])


class ExternalMoeHook(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.gate = QLinear(2048, 128)
        self.kind = "external_expert_hook_no_expert_parameters"


class Layer(nn.Module):
    def __init__(self, cfg: dict[str, Any]) -> None:
        super().__init__()
        self.self_attn = Attention(cfg)
        self.input_layernorm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"])
        self.post_attention_layernorm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"])
        self.external_moe = ExternalMoeHook()


class Backbone(nn.Module):
    def __init__(self, cfg: dict[str, Any]) -> None:
        super().__init__()
        self.embed_tokens = QEmbedding()
        self.layers = [Layer(cfg) for _ in range(cfg["num_hidden_layers"])]
        self.norm = nn.RMSNorm(2048, eps=cfg["rms_norm_eps"])
        self.lm_head = QLinear(2048, cfg["vocab_size"])


def classify(name: str) -> tuple[str, int | None]:
    if name.startswith("model.embed_tokens."):
        return "embedding", None
    if name.startswith("lm_head."):
        return "lm_head", None
    if name.startswith("model.norm."):
        return "final_norm", None
    match = re.match(r"model\.layers\.(\d+)\.(.*)", name)
    if not match:
        return "other", None
    layer, rest = int(match.group(1)), match.group(2)
    if EXPERT_RE.match(name):
        return "routed_expert", layer
    if rest.startswith("mlp.gate."):
        return "router", layer
    if rest.startswith("self_attn.") and ".q_norm." not in rest and ".k_norm." not in rest:
        return "attention", layer
    if rest.startswith("self_attn.") or rest.startswith("input_layernorm.") or rest.startswith("post_attention_layernorm."):
        return "layer_norm", layer
    return "other", layer


def headers() -> dict[str, tuple[Path, int, dict[str, Any]]]:
    output = {}
    for path in sorted(MODEL.glob("*.safetensors")):
        with path.open("rb") as handle:
            size = struct.unpack("<Q", handle.read(8))[0]
            output[path.name] = (path, 8 + size, json.loads(handle.read(size)))
    return output


def inventory(header_map: dict[str, tuple[Path, int, dict[str, Any]]]) -> list[dict[str, Any]]:
    records = []
    for shard, (_, base, header) in header_map.items():
        for name, metadata in header.items():
            if name == "__metadata__":
                continue
            start, end = map(int, metadata["data_offsets"])
            category, layer = classify(name)
            records.append({"name": name, "shape": metadata["shape"], "dtype": metadata["dtype"],
                            "stored_bytes": end - start, "source_shard": shard,
                            "payload_offset": base + start, "layer": layer, "category": category})
    return sorted(records, key=lambda row: row["name"])


def raw(record: dict[str, Any], _reads: list[Any]) -> np.ndarray:
    fd = os.open(MODEL / record["source_shard"], os.O_RDONLY)
    try:
        payload = os.pread(fd, record["stored_bytes"], record["payload_offset"])
    finally:
        os.close(fd)
    if len(payload) != record["stored_bytes"]:
        raise RuntimeError("short exact read " + record["name"])
    return np.frombuffer(payload, dtype=DT[record["dtype"]]).reshape(record["shape"]).copy()


def path_module(backbone: Backbone, name: str) -> tuple[Any, str]:
    if name.startswith("model.embed_tokens."):
        return backbone.embed_tokens, name.rsplit(".", 1)[1]
    if name.startswith("lm_head."):
        return backbone.lm_head, name.rsplit(".", 1)[1]
    if name.startswith("model.norm."):
        return backbone.norm, "weight"
    match = re.match(r"model\.layers\.(\d+)\.(.*)", name)
    if not match:
        raise KeyError(name)
    layer, rest = backbone.layers[int(match.group(1))], match.group(2)
    if rest.startswith("self_attn."):
        suffix = rest[len("self_attn."):]
        return getattr(layer.self_attn, suffix.split(".")[0]), suffix.rsplit(".", 1)[1]
    if rest.startswith("input_layernorm.") or rest.startswith("post_attention_layernorm."):
        return getattr(layer, rest.split(".")[0]), "weight"
    if rest.startswith("mlp.gate."):
        return layer.external_moe.gate, rest.rsplit(".", 1)[1]
    raise KeyError(name)


class BF16KVCache(KVCache):
    """Canonical contiguous MLX KV cache with explicit BF16 K/V materialization."""
    def update_and_fetch(self, keys: Any, values: Any) -> tuple[Any, Any]:
        return super().update_and_fetch(keys.astype(mx.bfloat16), values.astype(mx.bfloat16))


def load_backbone(cfg: dict[str, Any], included: list[dict[str, Any]]) -> Backbone:
    backbone = Backbone(cfg)
    for record in included:
        host = raw(record, [])
        array = mx.array(host)
        mx.eval(array)
        module, key = path_module(backbone, record["name"])
        setattr(module, key, array)
        del host, array
    gc.collect()
    mx.clear_cache()
    gc.collect()
    return backbone


def catalog(records: list[dict[str, Any]]) -> dict[tuple[int, str, str], dict[str, Any]]:
    output = {}
    for record in records:
        if record["category"] == "routed_expert":
            tail = record["name"].split(".switch_mlp.", 1)[1].split(".")
            output[(record["layer"], tail[0], tail[1])] = record
    if len(output) != LAYERS * 9:
        raise RuntimeError(f"expert catalog expected 432 component tensors, got {len(output)}")
    return output


def route(gate: Any, x: Any) -> tuple[Any, Any, Any]:
    logits = gate(x)
    probabilities = mx.softmax(logits, axis=-1, precise=True)
    ids = mx.argpartition(probabilities, kth=-TOP_K, axis=-1)[..., -TOP_K:]
    weights = mx.take_along_axis(probabilities, ids, axis=-1)
    weights /= mx.sum(weights, axis=-1, keepdims=True)
    return logits, ids, weights


def attention_with_bf16_cache(attention: Attention, x: Any, mask: Any, cache: BF16KVCache) -> Any:
    batch, length, _ = x.shape
    queries, keys, values = attention.q_proj(x), attention.k_proj(x), attention.v_proj(x)
    queries = attention.q_norm(queries.reshape(batch, length, attention.n_heads, -1)).transpose(0, 2, 1, 3)
    keys = attention.k_norm(keys.reshape(batch, length, attention.n_kv_heads, -1)).transpose(0, 2, 1, 3)
    values = values.reshape(batch, length, attention.n_kv_heads, -1).transpose(0, 2, 1, 3)
    queries, keys = attention.rope(queries, offset=cache.offset), attention.rope(keys, offset=cache.offset)
    keys, values = cache.update_and_fetch(keys, values)
    output = scaled_dot_product_attention(queries, keys, values, cache=cache, scale=attention.scale, mask=mask)
    return attention.o_proj(output.transpose(0, 2, 1, 3).reshape(batch, length, -1))


def direct_expert(x: Any, weights: dict[str, Any]) -> Any:
    def projection(name: str, value: Any) -> Any:
        return mx.quantized_matmul(value, weights[name + ".weight"], scales=weights[name + ".scales"],
                                   biases=weights[name + ".biases"], transpose=True, group_size=128,
                                   bits=4, mode="affine")
    return projection("down_proj", swiglu(projection("gate_proj", x), projection("up_proj", x)))


def ownership(backbone: Backbone) -> dict[str, Any]:
    leaves = tree_flatten(backbone.parameters())
    routed = [(path, value) for path, value in leaves
              if "expert" in ".".join(map(str, path)).lower() or "switch_mlp" in ".".join(map(str, path)).lower()]
    return {"backbone_parameter_tensor_count": len(leaves), "routed_expert_tensor_count": len(routed),
            "routed_expert_logical_bytes": sum(int(value.nbytes) for _, value in routed), "pass": not routed}
