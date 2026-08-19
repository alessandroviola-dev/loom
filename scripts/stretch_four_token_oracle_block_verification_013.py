#!/usr/bin/env python3
"""LOOM Stretch 013 — four-token oracle block verification.

Reconstructs the exact frozen Stretch 012 eight-layer-hotset workload and changes
one scientific factor: sixteen one-token target feedback traversals become four
causal target traversals of four known-correct oracle tokens each. This is an
upper-bound target-verification experiment; there is no real draft model/cost.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_009_BLOB = "3e0780850bb65f9dccf07946f89597fa2e4d17e1"
SOURCE_010_BLOB = "ff3dc83abc6388113fca15594eef6b3ec00ebe50"
SOURCE_011_BLOB = "16125f7eb0b2fb662591e194de0498513a563a6d"
SOURCE_012_BLOB = "8e10660af778655a279f30e7d59785163bc204e3"


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


def replace_exact(text: str, old: str, new: str, expected_count: int, label: str) -> str:
    observed = text.count(old)
    if observed != expected_count:
        raise RuntimeError(
            f"oracle transform failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def replace_span(text: str, start: str, end: str, replacement: str, label: str) -> str:
    if text.count(start) != 1:
        raise RuntimeError(f"oracle transform start invariant failed for {label}: {text.count(start)}")
    start_index = text.index(start)
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"oracle transform end invariant failed for {label}")
    if text.find(end, end_index + len(end)) >= 0:
        raise RuntimeError(f"oracle transform end not unique for {label}")
    return text[:start_index] + replacement + text[end_index + len(end):]


def add_oracle_block_transform(source: str) -> str:
    source = replace_exact(
        source,
        'print("LOOM Stretch 012 — Eight-Layer Persistent Hotset")',
        'print("LOOM Stretch 013 — Four-Token Oracle Block Verification")',
        1,
        "terminal title",
    )
    source = replace_exact(
        source,
        '"experiment": "Stretch 012 — Eight-Layer Persistent Hotset",',
        '"experiment": "Stretch 013 — Four-Token Oracle Block Verification",',
        1,
        "summary title",
    )
    source = replace_exact(
        source,
        '"eight-layer-persistent-hotset-012"',
        '"four-token-oracle-block-verification-013"',
        1,
        "run directory",
    )

    source = replace_exact(
        source,
        "HOTSET_ACTIVE_TOLERANCE = 8 * 1024 * 1024\n",
        "HOTSET_ACTIVE_TOLERANCE = 8 * 1024 * 1024\n"
        "ORACLE_BLOCK_SIZE = 4\n"
        "ORACLE_SEQUENCE = [1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]\n"
        "ORACLE_BLOCK_COUNT = 4\n"
        "ORACLE_BASELINE_012_TOKENS_PER_SECOND = 0.477929\n",
        1,
        "oracle constants",
    )

    source = replace_exact(
        source,
        '    if phase.startswith("stream_token_"):\n        return "stream_tokens"\n',
        '    if phase.startswith("stream_token_") or phase.startswith("stream_oracle_block_"):\n        return "stream_blocks"\n',
        1,
        "phase telemetry bucket",
    )

    child_start = "    stream_token_records = []\n    step_parities = []\n"
    child_end = "    stream_peak = int(mx.get_peak_memory())\n"
    child_replacement = '''    # ------------------------------------------------------------------\n    # Oracle block verification: four target traversals x four oracle tokens.\n    # ------------------------------------------------------------------\n    oracle_sequence = list(ORACLE_SEQUENCE)\n    oracle_sequence_provenance = resident_generated_tokens == oracle_sequence\n    stream_token_records = []\n    step_parities = []\n    stream_generated_tokens = list(oracle_sequence)\n    previous_block_next_prediction = None\n\n    for block_index in range(ORACLE_BLOCK_COUNT):\n        start_index = block_index * ORACLE_BLOCK_SIZE\n        end_index = start_index + ORACLE_BLOCK_SIZE\n        draft_tokens = oracle_sequence[start_index:end_index]\n        ids = make_ids([draft_tokens])\n        stream_logits, pass_record = run_streamed_pass(\n            ids, stream_caches, f"oracle_block_{block_index + 1}"\n        )\n        stream_snap = cache_snapshot(stream_caches)\n\n        # Acceptance predictions are shifted autoregressively. The first token\n        # of block 1 is predicted by prompt logits; later block-first tokens are\n        # predicted by the final position logits of the preceding block.\n        first_prediction = (\n            stream_token1 if block_index == 0 else int(previous_block_next_prediction)\n        )\n        acceptance_predictions = [first_prediction]\n        for local_pos in range(ORACLE_BLOCK_SIZE - 1):\n            pos_logits = stream_logits[:, local_pos:local_pos + 1, :]\n            acceptance_predictions.append(token_value(pos_logits))\n        acceptance = [\n            int(pred) == int(draft)\n            for pred, draft in zip(acceptance_predictions, draft_tokens)\n        ]\n        previous_block_next_prediction = token_value(\n            stream_logits[:, ORACLE_BLOCK_SIZE - 1:ORACLE_BLOCK_SIZE, :]\n        )\n\n        position_parities = []\n        for local_pos in range(ORACLE_BLOCK_SIZE):\n            global_step = start_index + local_pos + 1\n            resident_logits = resident_step_logits[global_step - 1]\n            block_logits = stream_logits[:, local_pos:local_pos + 1, :]\n            resident_max_abs = float(\n                mx.max(mx.abs(resident_logits.astype(mx.float32))).item()\n            )\n            stream_max_abs = float(\n                mx.max(mx.abs(block_logits.astype(mx.float32))).item()\n            )\n            diff = mx.abs(\n                resident_logits.astype(mx.float32) - block_logits.astype(mx.float32)\n            )\n            mx.eval(diff)\n            max_abs_diff = float(mx.max(diff).item())\n            mean_abs_diff = float(mx.mean(diff).item())\n            threshold = 1e-5 + 1e-5 * resident_max_abs\n            resident_predicted_top1 = int(\n                resident_steps[global_step - 1]["predicted_top1"]\n            )\n            stream_predicted_top1 = token_value(block_logits)\n            parity = {\n                "step": global_step,\n                "block": block_index + 1,\n                "block_position": local_pos,\n                "input_token": int(draft_tokens[local_pos]),\n                "max_abs_diff": max_abs_diff,\n                "mean_abs_diff": mean_abs_diff,\n                "resident_max_abs": resident_max_abs,\n                "stream_max_abs": stream_max_abs,\n                "threshold": threshold,\n                "pass": max_abs_diff <= threshold,\n                "resident_predicted_top1": resident_predicted_top1,\n                "stream_predicted_top1": stream_predicted_top1,\n                "top1_equal": resident_predicted_top1 == stream_predicted_top1,\n            }\n            position_parities.append(parity)\n            step_parities.append(parity)\n            del diff\n\n        block_record = {\n            "block": block_index + 1,\n            "step": end_index,\n            "start_step": start_index + 1,\n            "end_step": end_index,\n            "draft_tokens": draft_tokens,\n            "acceptance_predictions": acceptance_predictions,\n            "accepted": acceptance,\n            "accepted_count": sum(1 for value in acceptance if value),\n            "all_accepted": all(acceptance),\n            "next_prediction": int(previous_block_next_prediction),\n            "cache": stream_snap,\n            "position_parities": position_parities,\n            "pass": pass_record,\n        }\n        stream_token_records.append(block_record)\n        save_state(\n            f"stream_oracle_block_{block_index + 1}_complete",\n            block=block_record,\n        )\n\n        for global_step in range(start_index + 1, end_index + 1):\n            resident_step_logits[global_step - 1] = None\n        del ids, stream_logits\n        gc.collect()\n        mx.clear_cache()\n\n    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n'''
    source = replace_span(source, child_start, child_end, child_replacement, "child block loop")

    source = replace_exact(
        source,
        '        "hotset": hotset_record,\n',
        '        "hotset": hotset_record,\n        "oracle_sequence_provenance": oracle_sequence_provenance,\n',
        1,
        "child oracle provenance payload",
    )

    source = replace_exact(
        source,
        '''    for key in [\n        "resident", "stream", "hotset", "prompt_parity", "step_parities",\n        "generated_sequence_equal", "expected_kv_total_bytes",\n    ]:\n''',
        '''    for key in [\n        "resident", "stream", "hotset", "oracle_sequence_provenance",\n        "prompt_parity", "step_parities", "generated_sequence_equal",\n        "expected_kv_total_bytes",\n    ]:\n''',
        1,
        "parent oracle provenance promotion",
    )

    cache_start = "    # Cache gates: prompt then sixteen feedback positions.\n"
    cache_end = "    # Weight-stage gates for prompt and all four feedback passes.\n"
    cache_replacement = '''    # Cache gates: resident remains sequential; streamed target advances by four.\n    err = validate_cache(child["resident"]["prompt_cache"], PROMPT_LEN, "resident_prompt")\n    if err:\n        summary["classification"] = "ORACLE_BLOCK_CACHE_STATE_FAIL"\n        summary["failure_reason"] = err\n        return finish(8)\n    err = validate_cache(child["stream"]["prompt_cache"], PROMPT_LEN, "stream_prompt")\n    if err:\n        summary["classification"] = "ORACLE_BLOCK_CACHE_STATE_FAIL"\n        summary["failure_reason"] = err\n        return finish(8)\n\n    for step in range(1, GENERATED_TOKENS + 1):\n        expected_offset = PROMPT_LEN + step\n        resident_cache = child["resident"]["steps"][step - 1]["cache"]\n        err = validate_cache(resident_cache, expected_offset, f"resident_token_{step}")\n        if err:\n            summary["classification"] = "ORACLE_BLOCK_CACHE_STATE_FAIL"\n            summary["failure_reason"] = err\n            return finish(8)\n\n    block_records = child["stream"]["tokens"]\n    if len(block_records) != ORACLE_BLOCK_COUNT:\n        summary["classification"] = "ORACLE_BLOCK_CACHE_STATE_FAIL"\n        summary["failure_reason"] = f"expected {ORACLE_BLOCK_COUNT} target blocks, got {len(block_records)}"\n        return finish(8)\n    stream_prompt_bytes = int(child["stream"]["prompt_cache"]["total_nbytes"])\n    for block_index, record in enumerate(block_records):\n        expected_offset = PROMPT_LEN + (block_index + 1) * ORACLE_BLOCK_SIZE\n        cache = record["cache"]\n        err = validate_cache(cache, expected_offset, f"stream_oracle_block_{block_index + 1}")\n        if err:\n            summary["classification"] = "ORACLE_BLOCK_CACHE_STATE_FAIL"\n            summary["failure_reason"] = err\n            return finish(8)\n        if int(cache["total_nbytes"]) - stream_prompt_bytes > 1 * 1024 * 1024:\n            summary["classification"] = "KV_CACHE_GROWTH_UNEXPECTED"\n            summary["failure_reason"] = f"oracle block {block_index + 1}: cache grew below 256-position boundary"\n            return finish(8)\n\n    # Weight-stage gates for prompt and all oracle block passes.\n'''
    source = replace_span(source, cache_start, cache_end, cache_replacement, "block cache gates")

    source = replace_exact(
        source,
        '''    if not child["prompt_parity"]["token_equal"]:\n        summary["classification"] = "GENERATED_TOKEN_MISMATCH"\n        summary["failure_reason"] = f"prompt token mismatch: {child['prompt_parity']!r}"\n        return finish(10)\n\n    for parity in child["step_parities"]:\n''',
        '''    if not child["prompt_parity"]["token_equal"]:\n        summary["classification"] = "GENERATED_TOKEN_MISMATCH"\n        summary["failure_reason"] = f"prompt token mismatch: {child['prompt_parity']!r}"\n        return finish(10)\n\n    if not child.get("oracle_sequence_provenance"):\n        summary["classification"] = "ORACLE_SEQUENCE_PROVENANCE_FAIL"\n        summary["failure_reason"] = (\n            f"resident greedy sequence {child['resident']['generated_tokens']} "\n            f"!= frozen oracle {ORACLE_SEQUENCE}"\n        )\n        return finish(10)\n\n    for record in child["stream"]["tokens"]:\n        if not record.get("all_accepted") or int(record.get("accepted_count", 0)) != ORACLE_BLOCK_SIZE:\n            summary["classification"] = "ORACLE_TOKEN_REJECTED"\n            summary["failure_reason"] = f"oracle block rejection: {record!r}"\n            return finish(10)\n\n    if len(child["step_parities"]) != GENERATED_TOKENS:\n        summary["classification"] = "ORACLE_BLOCK_NUMERICAL_PARITY_FAIL"\n        summary["failure_reason"] = f"expected {GENERATED_TOKENS} position parities, got {len(child['step_parities'])}"\n        return finish(10)\n\n    for parity in child["step_parities"]:\n''',
        1,
        "oracle provenance/acceptance gates",
    )

    source = replace_exact(
        source,
        '"MULTI_TOKEN_KV_NUMERICAL_PARITY_FAIL"',
        '"ORACLE_BLOCK_NUMERICAL_PARITY_FAIL"',
        1,
        "oracle numerical fail classification",
    )
    source = replace_exact(
        source,
        '"MULTI_TOKEN_TOP1_MISMATCH"',
        '"ORACLE_BLOCK_TOP1_MISMATCH"',
        1,
        "oracle top1 fail classification",
    )

    # The inherited timing summary now describes target blocks, not individual tokens.
    source = replace_exact(
        source,
        '"logical_streamed_tokens_per_second": round(1.0 / mean_full_pass, 6),',
        '"target_block_traversals_per_second": round(1.0 / mean_full_pass, 6),',
        1,
        "block traversal rate key",
    )
    source = replace_exact(
        source,
        'print(f"Logical streamed tok/s: {t.get(\'logical_streamed_tokens_per_second\')}")',
        'print(f"Target block traversals/s: {t.get(\'target_block_traversals_per_second\')}")',
        1,
        "block traversal rate display",
    )
    source = replace_exact(
        source,
        'print(f"Mean full streamed pass/token: {t.get(\'mean_full_pass_seconds\')} s")',
        'print(f"Mean full target block pass: {t.get(\'mean_full_pass_seconds\')} s")',
        1,
        "block mean display",
    )
    source = replace_exact(
        source,
        'print(f"Median full streamed pass/token: {t.get(\'median_full_pass_seconds\')} s")',
        'print(f"Median full target block pass: {t.get(\'median_full_pass_seconds\')} s")',
        1,
        "block median display",
    )

    io_start = '    try:\n        token_passes = [record["pass"] for record in child["stream"]["tokens"]]\n'
    io_end = '    summary["classification"] = "EIGHT_LAYER_PERSISTENT_HOTSET_PASS"\n'
    io_replacement = '''    try:\n        block_records = child["stream"]["tokens"]\n        block_passes = [record["pass"] for record in block_records]\n        materialize_disk_reads = [\n            sum(int(cycle["io_materialize_delta"]["disk_read_bytes"]) for cycle in record["cycles"])\n            for record in block_passes\n        ]\n        materialize_pageins = [\n            sum(int(cycle["io_materialize_delta"]["pageins"]) for cycle in record["cycles"])\n            for record in block_passes\n        ]\n        build_disk_reads = [\n            sum(int(cycle["io_build_delta"]["disk_read_bytes"]) for cycle in record["cycles"])\n            for record in block_passes\n        ]\n        full_pass_disk_reads = [int(record["io_delta"]["disk_read_bytes"]) for record in block_passes]\n        full_pass_pageins = [int(record["io_delta"]["pageins"]) for record in block_passes]\n        full_pass_walls = [float(record["total_pass_wall_seconds"]) for record in block_passes]\n        if len(block_passes) != ORACLE_BLOCK_COUNT:\n            raise RuntimeError(f"expected {ORACLE_BLOCK_COUNT} block passes, got {len(block_passes)}")\n        if not all(len(record.get("cycles", [])) == 36 for record in block_passes):\n            raise RuntimeError("incomplete oracle block layer records")\n        if not all(int(record.get("accepted_count", 0)) == ORACLE_BLOCK_SIZE for record in block_records):\n            raise RuntimeError("incomplete oracle acceptance")\n\n        accepted_tokens = ORACLE_BLOCK_COUNT * ORACLE_BLOCK_SIZE\n        total_target_block_wall = sum(full_pass_walls)\n        oracle_target_tps = accepted_tokens / total_target_block_wall\n        summary["oracle_block_verification"] = {\n            "oracle_block_size": ORACLE_BLOCK_SIZE,\n            "target_block_traversals": ORACLE_BLOCK_COUNT,\n            "accepted_oracle_tokens": accepted_tokens,\n            "accepted_tokens_per_target_traversal": accepted_tokens / ORACLE_BLOCK_COUNT,\n            "total_target_block_wall_seconds": total_target_block_wall,\n            "wall_seconds_per_accepted_token": total_target_block_wall / accepted_tokens,\n            "oracle_target_verification_tokens_per_second": oracle_target_tps,\n            "stretch_012_logical_tokens_per_second": ORACLE_BASELINE_012_TOKENS_PER_SECOND,\n            "oracle_target_rate_vs_stretch_012_ratio": oracle_target_tps / ORACLE_BASELINE_012_TOKENS_PER_SECOND,\n            "block_full_pass_seconds": full_pass_walls,\n            "block_materialize_seconds": materialize_times,\n            "block_forward_seconds": forward_times,\n        }\n        summary["io_attribution"] = {\n            "darwin_api": "proc_pid_rusage/RUSAGE_INFO_V2",\n            "materialize_disk_read_bytes_per_block": materialize_disk_reads,\n            "materialize_pageins_per_block": materialize_pageins,\n            "build_select_disk_read_bytes_per_block": build_disk_reads,\n            "full_pass_disk_read_bytes_per_block": full_pass_disk_reads,\n            "full_pass_pageins_per_block": full_pass_pageins,\n            "materialize_disk_read_bytes_per_accepted_token": [value / ORACLE_BLOCK_SIZE for value in materialize_disk_reads],\n            "full_pass_disk_read_bytes_per_accepted_token": [value / ORACLE_BLOCK_SIZE for value in full_pass_disk_reads],\n            "mean_full_pass_disk_read_bytes_per_block": statistics.mean(full_pass_disk_reads),\n            "mean_full_pass_disk_read_bytes_per_accepted_token": statistics.mean(full_pass_disk_reads) / ORACLE_BLOCK_SIZE,\n            "mean_materialize_disk_read_bytes_per_block": statistics.mean(materialize_disk_reads),\n            "mean_materialize_disk_read_bytes_per_accepted_token": statistics.mean(materialize_disk_reads) / ORACLE_BLOCK_SIZE,\n        }\n    except Exception as exc:\n        summary["classification"] = "TELEMETRY_FAIL"\n        summary["failure_reason"] = f"incomplete oracle block attribution: {type(exc).__name__}: {exc}"\n        return finish(11)\n\n    summary["classification"] = "FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS"\n'''
    source = replace_span(source, io_start, io_end, io_replacement, "oracle I/O summary")

    display_start = '        if summary.get("io_attribution"):\n'
    display_end = '        print(f"Minimum observed free memory: {summary[\'telemetry\'].get(\'min_memory_free_percent\')}%")\n'
    display_replacement = '''        if summary.get("oracle_block_verification"):\n            ob = summary["oracle_block_verification"]\n            print(f"Oracle block size: {ob.get('oracle_block_size')}")\n            print(f"Target block traversals: {ob.get('target_block_traversals')}")\n            print(f"Accepted oracle tokens: {ob.get('accepted_oracle_tokens')}")\n            print(f"Accepted tokens/target traversal: {ob.get('accepted_tokens_per_target_traversal')}")\n            print(f"Target block walls: {ob.get('block_full_pass_seconds')}")\n            print(f"Target block total wall: {ob.get('total_target_block_wall_seconds')} s")\n            print(f"Wall/accepted token: {ob.get('wall_seconds_per_accepted_token')} s")\n            print(f"Oracle target-verification tok/s: {ob.get('oracle_target_verification_tokens_per_second')}")\n            print(f"Oracle target-rate / Stretch012 ratio: {ob.get('oracle_target_rate_vs_stretch_012_ratio')}")\n        if summary.get("io_attribution"):\n            ioa = summary["io_attribution"]\n            print(f"Materialize disk-read bytes/block: {ioa.get('materialize_disk_read_bytes_per_block')}")\n            print(f"Full-pass disk-read bytes/block: {ioa.get('full_pass_disk_read_bytes_per_block')}")\n            print(f"Materialize bytes/accepted token: {ioa.get('materialize_disk_read_bytes_per_accepted_token')}")\n            print(f"Full-pass bytes/accepted token: {ioa.get('full_pass_disk_read_bytes_per_accepted_token')}")\n            print(f"Mean full-pass bytes/accepted token: {ioa.get('mean_full_pass_disk_read_bytes_per_accepted_token')}")\n        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")\n'''
    source = replace_span(source, display_start, display_end, display_replacement, "oracle terminal display")

    source = replace_exact(
        source,
        'print(f"Generation policy: argmax exactly {GENERATED_TOKENS} tokens")',
        'print(f"Generation policy: resident greedy {GENERATED_TOKENS} tokens; streamed oracle blocks {ORACLE_BLOCK_COUNT}x{ORACLE_BLOCK_SIZE}")',
        1,
        "generation-policy display",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source009 = repo / "scripts" / "stretch_four_token_kv_autoregressive_parity_009.py"
    source010 = repo / "scripts" / "stretch_sixteen_token_autoregressive_stability_010.py"
    source011 = repo / "scripts" / "stretch_materialization_io_attribution_011.py"
    source012 = repo / "scripts" / "stretch_eight_layer_persistent_hotset_012.py"

    observed009 = git_blob(source009, repo)
    observed010 = git_blob(source010, repo)
    observed011 = git_blob(source011, repo)
    observed012 = git_blob(source012, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 013 — Four-Token Oracle Block Verification frozen transform")
        print(f"Stretch 009 source blob: {observed009}")
        print(f"Stretch 010 transform blob: {observed010}")
        print(f"Stretch 011 instrumentation blob: {observed011}")
        print(f"Stretch 012 hotset blob: {observed012}")
    if (
        observed009 != SOURCE_009_BLOB
        or observed010 != SOURCE_010_BLOB
        or observed011 != SOURCE_011_BLOB
        or observed012 != SOURCE_012_BLOB
    ):
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")

    transform010 = load_module(source010, "loom_stretch010_transform")
    instrument011 = load_module(source011, "loom_stretch011_instrument")
    hotset012 = load_module(source012, "loom_stretch012_hotset")

    source = transform010.transformed_source(source009.read_text(encoding="utf-8"))
    source = instrument011.add_io_instrumentation(source)
    source = hotset012.add_hotset_transform(source)
    source = add_oracle_block_transform(source)

    required_fragments = [
        "ORACLE_BLOCK_SIZE = 4",
        "ORACLE_BLOCK_COUNT = 4",
        "FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS",
        "oracle_target_verification_tokens_per_second",
        "stream_oracle_block_",
        "oracle_sequence_provenance",
        "persistent_blocks",
        "HOTSET_LAYER_IDS = tuple(range(8))",
        "proc_pid_rusage",
        "stdout=out_handle",
        "stderr=err_handle",
        "MIN_FREE_PERCENT = 5",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise RuntimeError(f"oracle transformed-source invariant failed; missing {missing}")

    if not is_child:
        print("Frozen Stretch 012 reconstruction: PASS")
        print("Scientific change: 16 one-token target traversals -> 4 x 4-token oracle target blocks ONLY")
        print("Eight-layer persistent hotset: PRESERVED")
        print("Resident sequential control / KV / parity / I/O / safety gates: PRESERVED")
        print("Real draft model: NONE (oracle upper bound)")

    transformed_globals = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
    }
    exec(compile(source, str(source009), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
