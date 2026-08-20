#!/usr/bin/env python3
"""LOOM Stretch 029 — fused gate+up quantized projection treatment.

Reuses the canonical Stretch 027 SINGLE_PASS target architecture and changes one
scientific factor only: Qwen3 MLP gate_proj + up_proj are fused into one persistent
3-bit/group64 quantized projection per transformer layer. The fused arrays replace
rather than supplement the two original persistent projection parameter sets.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_027_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_027_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"
SOURCE_026_PATH = Path("scripts/stretch_full_persistent_shared_batched_cleanup_026.py")
SOURCE_026_BLOB = "6926e1b1b9a851f23d88ba6b1f1023e13336098a"
SOURCE_025_PATH = Path("scripts/stretch_full_persistent_batched_cleanup_025.py")
SOURCE_025_BLOB = "5ca3572f3269899e7c3fc23b9e136381ce864d99"
SOURCE_FIX1_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")
SOURCE_FIX1_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"
SOURCE_BROKEN_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py")
SOURCE_BROKEN_BLOB = "8c263e7be15441581e481e6f41cbd16f87d4df4b"
SOURCE_H36_PATH = Path("scripts/stretch_five_token_h36_hotset_variant_022.py")
SOURCE_H36_BLOB = "9111dde483206a774a9fe5426522dab6e77cecca"
SOURCE_017_PATH = Path("scripts/stretch_five_token_oracle_block_confirmation_017.py")
SOURCE_017_BLOB = "6171440736badf5150297f9c8945209fe49d0826"
SOURCE_013_PATH = Path("scripts/stretch_four_token_oracle_block_verification_013.py")
SOURCE_013_BLOB = "deeb0339294162f38cd4522d2890b6a0c728f96e"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 029 gate-up fusion transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def inject_fusion_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch027_apply_single_pass_cleanup(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError("Stretch 029 wrapper invariant failed: Stretch 027 callback missing")
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch029_apply_gate_up_fusion(source)\n",
        1,
    )


def add_gate_up_fusion(source: str) -> str:
    source = source.replace(
        "LOOM Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
        "LOOM Stretch 029 — Gate+Up Quantized Fusion",
    )
    source = source.replace(
        "Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
        "Stretch 029 — Gate+Up Quantized Fusion",
    )
    source = source.replace(
        "five-token-h36-full-persistent-single-pass-cleanup-027",
        "gate-up-quantized-fusion-029-fused",
    )

    build_anchor = '''    def build_block(layer_id: int):\n        if layer_id in persistent_blocks:\n            return persistent_blocks[layer_id], None\n'''
    classes = '''    class FusedGateUpMLP(qwen3.MLP):\n        def __init__(self, dim, hidden_dim):\n            super().__init__(dim, hidden_dim)\n            self._loom_gate_up_ready = False\n\n        def finalize_gate_up_fusion(self):\n            gate = self.gate_proj\n            up = self.up_proj\n            required = ("weight", "scales")\n            if not all(hasattr(gate, name) and hasattr(up, name) for name in required):\n                raise RuntimeError("gate/up are not quantized before fusion")\n            if (\n                int(gate.group_size) != int(up.group_size)\n                or int(gate.bits) != int(up.bits)\n                or str(gate.mode) != str(up.mode)\n            ):\n                raise RuntimeError("gate/up quantization configuration mismatch")\n\n            gate_rows = int(gate.weight.shape[0])\n            up_rows = int(up.weight.shape[0])\n            if gate_rows != up_rows:\n                raise RuntimeError(f"gate/up output rows differ: {gate_rows} vs {up_rows}")\n\n            fused_weight = mx.concatenate([gate.weight, up.weight], axis=0)\n            fused_scales = mx.concatenate([gate.scales, up.scales], axis=0)\n            gate_biases = getattr(gate, "biases", None)\n            up_biases = getattr(up, "biases", None)\n            if (gate_biases is None) != (up_biases is None):\n                raise RuntimeError("gate/up affine quantization bias presence mismatch")\n            fused_biases = (\n                mx.concatenate([gate_biases, up_biases], axis=0)\n                if gate_biases is not None else None\n            )\n\n            self.gate_up_weight = fused_weight\n            self.gate_up_scales = fused_scales\n            self.gate_up_biases = fused_biases\n            self.gate_up_group_size = int(gate.group_size)\n            self.gate_up_bits = int(gate.bits)\n            self.gate_up_mode = str(gate.mode)\n            self.gate_up_split_rows = gate_rows\n\n            # Drop the two original module references before materializing the fused\n            # representation. The concat graph still owns its inputs until mx.eval.\n            self.gate_proj = None\n            self.up_proj = None\n            del gate, up\n            if fused_biases is None:\n                mx.eval(self.gate_up_weight, self.gate_up_scales)\n            else:\n                mx.eval(self.gate_up_weight, self.gate_up_scales, self.gate_up_biases)\n            self._loom_gate_up_ready = True\n\n        def rewrite_selected_to_fused_views(self, selected):\n            if not self._loom_gate_up_ready:\n                raise RuntimeError("gate/up fusion not finalized")\n            n = self.gate_up_split_rows\n            replacements = {\n                "mlp.gate_proj.weight": self.gate_up_weight[:n],\n                "mlp.up_proj.weight": self.gate_up_weight[n:],\n                "mlp.gate_proj.scales": self.gate_up_scales[:n],\n                "mlp.up_proj.scales": self.gate_up_scales[n:],\n            }\n            if self.gate_up_biases is not None:\n                replacements.update({\n                    "mlp.gate_proj.biases": self.gate_up_biases[:n],\n                    "mlp.up_proj.biases": self.gate_up_biases[n:],\n                })\n            for key, value in replacements.items():\n                if key not in selected:\n                    raise RuntimeError(f"selected tensor missing during fusion rewrite: {key}")\n                selected[key] = value\n\n        def fused_payload_bytes(self):\n            total = int(self.gate_up_weight.nbytes) + int(self.gate_up_scales.nbytes)\n            if self.gate_up_biases is not None:\n                total += int(self.gate_up_biases.nbytes)\n            return total\n\n        def __call__(self, x):\n            if not self._loom_gate_up_ready:\n                raise RuntimeError("gate/up fused projection used before finalization")\n            fused = mx.quantized_matmul(\n                x,\n                self.gate_up_weight,\n                scales=self.gate_up_scales,\n                biases=self.gate_up_biases,\n                transpose=True,\n                group_size=self.gate_up_group_size,\n                bits=self.gate_up_bits,\n                mode=self.gate_up_mode,\n            )\n            gate, up = mx.split(fused, 2, axis=-1)\n            return self.down_proj(qwen3.swiglu(gate, up))\n\n    class FusedGateUpTransformerBlock(qwen3.TransformerBlock):\n        def __init__(self, block_args):\n            super().__init__(block_args)\n            self.mlp = FusedGateUpMLP(block_args.hidden_size, block_args.intermediate_size)\n\n    def build_block(layer_id: int):\n        if layer_id in persistent_blocks:\n            return persistent_blocks[layer_id], None\n'''
    source = replace_once(source, build_anchor, classes, "fused MLP classes")

    source = replace_once(
        source,
        "        block = qwen3.TransformerBlock(args)\n",
        "        block = FusedGateUpTransformerBlock(args)\n",
        "fused transformer construction",
    )
    source = replace_once(
        source,
        '''        block.load_weights(list(selected.items()), strict=True)\n        block.eval()\n        return block, selected\n''',
        '''        block.load_weights(list(selected.items()), strict=True)\n        block.mlp.finalize_gate_up_fusion()\n        block.mlp.rewrite_selected_to_fused_views(selected)\n        if selected_bytes(selected) != EXPECTED_LAYER_BYTES:\n            raise RuntimeError(\n                f"layer {layer_id} fused selected bytes {selected_bytes(selected)} != {EXPECTED_LAYER_BYTES}"\n            )\n        block.eval()\n        return block, selected\n''',
        "finalize fused gate-up after strict load",
    )

    shared_ready_anchor = '    save_state("stream_shared_persistence_ready", shared_persistence=shared_persistence_record)\n'
    fusion_record = '''    save_state("stream_shared_persistence_ready", shared_persistence=shared_persistence_record)\n\n    fused_layer_payloads = []\n    fused_layer_ids = []\n    for fused_layer_id in HOTSET_LAYER_IDS:\n        fused_mlp = persistent_blocks[fused_layer_id].mlp\n        if not isinstance(fused_mlp, FusedGateUpMLP) or not fused_mlp._loom_gate_up_ready:\n            raise RuntimeError(f"persistent layer {fused_layer_id} gate/up fusion missing")\n        fused_layer_ids.append(int(fused_layer_id))\n        fused_layer_payloads.append(int(fused_mlp.fused_payload_bytes()))\n    gate_up_fusion_record = {\n        "policy": "single_quantized_matmul_gate_up",\n        "layer_ids": fused_layer_ids,\n        "layer_count": len(fused_layer_ids),\n        "per_layer_fused_payload_bytes": fused_layer_payloads,\n        "all_payloads_equal": len(set(fused_layer_payloads)) == 1,\n        "steady_state_duplicate_gate_up_modules": False,\n        "group_size": int(quant["group_size"]),\n        "bits": int(quant["bits"]),\n        "mode": quant.get("mode", "affine"),\n    }\n    save_state("stream_gate_up_fusion_ready", gate_up_fusion=gate_up_fusion_record)\n'''
    source = replace_once(source, shared_ready_anchor, fusion_record, "fusion provenance record")

    source = replace_once(
        source,
        '        "shared_persistence": shared_persistence_record,\n',
        '        "shared_persistence": shared_persistence_record,\n        "gate_up_fusion": gate_up_fusion_record,\n',
        "child fusion payload",
    )
    source = replace_once(
        source,
        '        "resident", "stream", "hotset", "shared_persistence", "oracle_sequence_provenance",\n',
        '        "resident", "stream", "hotset", "shared_persistence", "gate_up_fusion", "oracle_sequence_provenance",\n',
        "parent fusion payload promotion",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    paths = {
        "s027": repo / SOURCE_027_PATH,
        "s026": repo / SOURCE_026_PATH,
        "s025": repo / SOURCE_025_PATH,
        "fix1": repo / SOURCE_FIX1_PATH,
        "broken": repo / SOURCE_BROKEN_PATH,
        "h36": repo / SOURCE_H36_PATH,
        "s017": repo / SOURCE_017_PATH,
        "s013": repo / SOURCE_013_PATH,
    }
    expected = {
        "s027": SOURCE_027_BLOB,
        "s026": SOURCE_026_BLOB,
        "s025": SOURCE_025_BLOB,
        "fix1": SOURCE_FIX1_BLOB,
        "broken": SOURCE_BROKEN_BLOB,
        "h36": SOURCE_H36_BLOB,
        "s017": SOURCE_017_BLOB,
        "s013": SOURCE_013_BLOB,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}

    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"
    if not is_child:
        print("LOOM Stretch 029 — Gate+Up Quantized Fusion")
        for key in ["s027", "s026", "s025", "fix1", "broken", "h36", "s017", "s013"]:
            print(f"{key} blob: {observed[key]}")
    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: gate_proj + up_proj two quantized matmuls -> one fused quantized matmul ONLY")
        print("Fused packed payload replaces original gate/up persistent modules; no per-forward concat")
        print("M5 / H36 / full weights / single cleanup / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    s027 = load_module(paths["s027"], "loom_stretch027_transform_for_029")
    s026 = load_module(paths["s026"], "loom_stretch026_transform_for_029")
    s025 = load_module(paths["s025"], "loom_stretch025_transform_for_029")
    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_029")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_029")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_029")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_029")

    wrapper = h36.transformed_013_wrapper(paths["s013"].read_text(encoding="utf-8"), stretch017)
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = s026.inject_shared_cleanup_callback(wrapper)
    wrapper = s027.inject_single_pass_callback(wrapper)
    wrapper = inject_fusion_callback(wrapper)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch027_apply_single_pass_cleanup(source)",
        "__stretch029_apply_gate_up_fusion(source)",
        "single_quantized_matmul_gate_up",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 029 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": s026.add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        "__stretch029_apply_gate_up_fusion": add_gate_up_fusion,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
