#!/usr/bin/env python3
"""Exact frozen-segmentation Q4 baseline replay; no BF16 target or network path."""
from __future__ import annotations

import gc
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx
import numpy as np

import loom_30b_moe_dflash_target_interface_001 as oracle
import loom_30b_moe_first_greedy_generation_001 as target
import loom_dflash_greedy_e2e_001 as dflash

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "results-local/moe/models/Qwen3-30B-A3B-MLX-4bit"
TRACE = ROOT / "results-local/moe/routing-cache-trace-001/20260824T090555Z/generations.json"
CORPUS = ROOT / "results-local/research/dflash-masked-reference-parity-001/20260824T142830Z"
FREEZE = ROOT / "results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z"
PREFLIGHT = ROOT / "results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z"
OUTROOT = ROOT / "results-local/research/dflash-q4-baseline-segmentation-replay-repair-001"
TAPS = (1, 12, 23, 34, 45)
ORDER = ("P3_t01", "P1_t32", "P2_t16")
EXPECTED = {
    "P1_t32": {"rank": 3, "target": 326},
    "P2_t16": {"rank": 3, "target": 994},
    "P3_t01": {"rank": 2, "target": 1620},
}


def utc_id(): return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
def raw_sha(a): return hashlib.sha256(np.ascontiguousarray(np.asarray(a)).tobytes()).hexdigest()
def file_sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()
def dump(p, x): Path(p).write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")


def clone_cache(cache):
    """Verbatim frozen-continuation clone: BF16 cache values remain BF16-exact."""
    copied = []
    for source in cache:
        item = target.BF16KVCache()
        keys, values = source.state
        item.state = (mx.array(np.array(keys.astype(mx.float32)), dtype=mx.bfloat16),
                      mx.array(np.array(values.astype(mx.float32)), dtype=mx.bfloat16))
        copied.append(item)
    mx.eval(*(x.keys for x in copied), *(x.values for x in copied))
    return copied


def offsets(cache): return [int(x.offset) for x in cache]
def all_offsets(cache, n): return len(cache) == target.LAYERS and offsets(cache) == [n] * target.LAYERS


def selected_states():
    selected = {x["state_id"]: x for x in json.loads((PREFLIGHT / "selected-states.json").read_text())["selected_states"]}
    corpus = {x["state_id"]: x for x in json.loads((CORPUS / "corpus.json").read_text())["states"]}
    decisions = json.loads((FREEZE / "target-continuation-reference.json").read_text())["decisions"]
    decision_by_state = {}
    for x in decisions: decision_by_state.setdefault(x["state_id"], []).append(x)
    traces = {x["prompt_id"]: x for x in json.loads(TRACE.read_text())["runs"]}
    out = []
    for sid in ORDER:
        meta, frozen = selected[sid], corpus[sid]
        rows = sorted(decision_by_state[sid], key=lambda x: int(x["continuation_position"]))
        pos, base_len = int(meta["continuation_position"]), int(meta["base_prefix_length"])
        trace = traces[meta["prompt_id"]]
        prompt = list(map(int, trace["prompt_token_ids"]))
        base_decode = [int(x["output_token_id"]) for x in trace["generation"]["records"][:int(meta["state_token_index"]) - 1]]
        continuation = [int(x["target_token_id"]) for x in rows[:pos - 1]]
        ids = prompt + base_decode + continuation
        portable = hashlib.sha256(",".join(map(str, ids)).encode()).hexdigest()
        if (len(rows) != 7 or [int(x["continuation_position"]) for x in rows] != list(range(1, 8))
                or len(prompt) + len(base_decode) != base_len or len(ids) != int(meta["replay_input_length_at_selected_decision"])
                or portable != meta["input_token_ids_sha256"] or continuation[-1] != int(meta["anchor_token_id"])
                or int(rows[pos - 1]["target_token_id"]) != EXPECTED[sid]["target"]):
            raise RuntimeError(f"FROZEN_INPUT_OR_SEGMENTATION_PROVENANCE_FAIL: {sid}")
        out.append({"state_id": sid, "meta": meta, "frozen": frozen, "rows": rows,
                    "prompt": prompt, "base_decode": base_decode, "continuation": continuation,
                    "ids": ids, "input_sha256": portable,
                    "expected_logit_sha256": rows[pos - 1]["logits_sha256"],
                    "retained_taps": CORPUS / frozen["tap_file"],
                    "retained_dflash": ROOT / meta["retained_full_logits_source"]})
    return out


def collect(forward):
    return {layer: np.asarray(forward["taps"][layer]).astype(np.float32, copy=True)[0] for layer in TAPS}


def replay_one(state, out):
    cfg = json.loads((MODEL / "config.json").read_text())
    records = target.bb.inventory(target.bb.headers())
    included = [x for x in records if x["category"] != "routed_expert"]
    if len(included) != 919 or sum(x["stored_bytes"] for x in included) != target.BACKBONE_BYTES:
        raise RuntimeError("Q4_BACKBONE_INVENTORY_FAIL")
    sources, backbone = target.catalog(records), target.load_backbone(cfg, included)
    ownership_before = target.ownership(backbone)
    cache = [target.BF16KVCache() for _ in range(target.LAYERS)]
    histories = {layer: [] for layer in TAPS}
    forwards, base = [], None
    try:
        # Original freeze producer: one prompt prefill, then one cached decode per trace token.
        for index, segment in enumerate([state["prompt"]] + [[x] for x in state["base_decode"]]):
            current = oracle.external_forward(backbone, sources, segment, cache, f"Q4_REPLAY_BASE_{index}", capture_taps=True)
            forwards.append(current)
            captured = collect(current)
            for layer in TAPS: histories[layer].append(captured[layer])
            if index == len(state["base_decode"]): base = current
        base_len = int(state["meta"]["base_prefix_length"])
        base_taps = np.stack([np.concatenate(histories[layer], axis=0) for layer in TAPS])
        retained = np.load(state["retained_taps"], allow_pickle=False)
        retained_taps = retained["taps"]
        frozen_state_gate = (base_taps.shape == retained_taps.shape and base_taps.dtype == retained_taps.dtype
                             and bool(np.array_equal(base_taps, retained_taps))
                             and int(retained["anchor_token_id"]) == int(state["frozen"]["anchor_token_id"])
                             and all_offsets(cache, base_len))
        if not frozen_state_gate: raise RuntimeError(f"FROZEN_Q4_STATE_RECONSTRUCTION_FAIL: {state['state_id']}")
        if int(np.argmax(base["logits"][0, -1])) != state["continuation"][0]:
            raise RuntimeError(f"FROZEN_BRANCH_FIRST_TOKEN_FAIL: {state['state_id']}")
        boundary_offsets = offsets(cache)
        branch = clone_cache(cache)
        clone_offsets = offsets(branch)
        clone_gate = all_offsets(branch, base_len)
        current = base
        # Exact freeze branch: continuation inputs are separate one-token cached decodes.
        for index, token in enumerate(state["continuation"], 1):
            current = oracle.external_forward(backbone, sources, [token], branch, f"Q4_REPLAY_CONTINUATION_{index}", capture_taps=True)
            forwards.append(current)
            captured = collect(current)
            for layer in TAPS: histories[layer].append(captured[layer])
        full_taps = np.stack([np.concatenate(histories[layer], axis=0) for layer in TAPS])
        final_logits = np.asarray(current["logits"][0, -1], dtype=np.float32)
        final_sha = raw_sha(final_logits)
        final_len = len(state["ids"])
        # Unchanged DFlash run on the exactly recovered frozen base taps, at the frozen continuation row.
        drafter = dflash.Drafter()
        debug = drafter.propose_debug(base_taps, int(state["frozen"]["anchor_token_id"]))
        dlogits = np.asarray(debug["logits"], dtype=np.float32)[0, 1:8]
        ref = np.load(state["retained_dflash"], allow_pickle=False)
        ref_logits, ref_rows = ref["logits"][0, 1:8], ref["draft_ids"]
        pos = int(state["meta"]["continuation_position"])
        target_id = EXPECTED[state["state_id"]]["target"]
        mapping = np.asarray(drafter.target_ids_by_draft_row, dtype=np.int64)
        inverse = np.full(151936, -1, dtype=np.int64); inverse[mapping] = np.arange(mapping.size, dtype=np.int64)
        target_row = int(inverse[target_id])
        rank = int(1 + np.count_nonzero(dlogits[pos - 1] > dlogits[pos - 1, target_row]))
        proposal_row = int(np.argmax(dlogits[pos - 1])); proposal = int(mapping[proposal_row])
        # Frozen evidence commits discrete draft rows/proposals and ranks, not these full
        # intermediate DFlash float arrays; retain bitwise comparison diagnostically only.
        dflash_gate = (bool(np.array_equal(debug["draft_ids"], ref_rows))
                       and target_row == int(state["meta"]["target_draft_row"]) and rank == EXPECTED[state["state_id"]]["rank"]
                       and proposal_row == int(ref_rows[pos - 1]))
        del drafter
        ownership_after = target.ownership(backbone)
        report = {
            "state_id": state["state_id"],
            "input": {"ids_exact": state["ids"], "portable_csv_sha256": state["input_sha256"],
                      "canonical_int64_raw_sha256": raw_sha(np.asarray(state["ids"], dtype=np.int64))},
            "segmentation": {"segments": [len(state["prompt"])] + [1] * (len(state["base_decode"]) + len(state["continuation"])),
                "base_prefill_length": len(state["prompt"]), "base_cached_decode_count": len(state["base_decode"]),
                "frozen_kv_boundary_offset": base_len, "branch_cached_decode_token_ids": state["continuation"],
                "final_anchor_selector": [0, -1], "final_anchor_token_id": state["continuation"][-1],
                "cache_class": "BF16KVCache", "cache_offsets_at_boundary": boundary_offsets,
                "cache_offsets_after_clone": clone_offsets, "cache_offsets_final": offsets(branch)},
            "final_logits": {"dtype": str(final_logits.dtype), "shape": list(final_logits.shape),
                "expected_raw_sha256": state["expected_logit_sha256"], "observed_raw_sha256": final_sha,
                "exact": final_sha == state["expected_logit_sha256"]},
            "frozen_base_taps": {"retained_file_sha256": file_sha(state["retained_taps"]), "shape": list(base_taps.shape),
                "dtype": str(base_taps.dtype), "bitwise_exact": frozen_state_gate},
            "dflash": {"unchanged_drafter_full_32k_logits_bitwise_exact_to_frozen": bool(np.array_equal(dlogits, ref_logits)),
                "corrected_decode": "target_id = draft_row + d2t[draft_row]", "frozen_target_id": target_id,
                "target_draft_row": target_row, "corrected_frozen_target_rank": rank, "expected_rank": EXPECTED[state["state_id"]]["rank"],
                "proposal_draft_row": proposal_row, "proposal_target_id": proposal, "frozen_proposal_draft_row": int(ref_rows[pos - 1]),
                "gate": dflash_gate},
            "integrity": {"finite": bool(np.isfinite(final_logits).all()) and bool(np.isfinite(full_taps).all()),
                "all_final_expert_live_zero": all(int(x["final_logical_expert_live_bytes"]) == 0 for x in forwards),
                "no_routed_expert_leak": ownership_before["pass"] and ownership_after["pass"]},
            "gates": {"frozen_state_taps_bitwise_exact": frozen_state_gate, "cached_bf16_kv_boundary_exact": clone_gate,
                "final_cache_offset_exact": all_offsets(branch, final_len), "final_logit_sha256_exact": final_sha == state["expected_logit_sha256"],
                "dflash_frozen_rank_and_proposal_exact": dflash_gate},
        }
        np.savez_compressed(out / "q4-target.npz", taps=full_taps, base_taps=base_taps, logits=final_logits,
                            input_token_ids=np.asarray(state["ids"], dtype=np.int64), tap_layers_1_based=np.asarray(TAPS, dtype=np.int32))
        dump(out / "q4-baseline.json", report)
        if not all(report["gates"].values()) or not all(report["integrity"].values()):
            raise RuntimeError(f"Q4_BASELINE_REPLAY_OR_PROVENANCE_FAIL: {state['state_id']}")
        return full_taps, final_logits, report
    finally:
        del backbone
        gc.collect(); mx.clear_cache()


def main():
    out = OUTROOT / utc_id(); out.mkdir(parents=True, exist_ok=False)
    states, completed, failure = selected_states(), [], None
    try:
        for state in states:
            state_out = out / state["state_id"]; state_out.mkdir()
            _, _, report = replay_one(state, state_out)
            completed.append(report)
    except Exception as exc:
        failure = {"type": type(exc).__name__, "error": str(exc)}
    gates = [x for report in completed for x in report["gates"].values()]
    summary = {"checkpoint": "LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001",
        "classification": "Q4_BASELINE_SEGMENTATION_REPAIR_PASS" if failure is None and len(completed) == 3 and all(gates) else "Q4_BASELINE_SEGMENTATION_REPAIR_FAIL",
        "completed_states": [x["state_id"] for x in completed], "states": completed, "failure": failure,
        "restrictions": {"q4_target_forward_count": sum(1 + len(next(s for s in states if s['state_id'] == r['state_id'])['base_decode']) + len(next(s for s in states if s['state_id'] == r['state_id'])['continuation']) for r in completed),
            "bf16_target_forward_count": 0, "network_requests": 0, "network_bytes": 0, "downloads": 0, "e2e_runs": 0,
            "proof": "This Q4-only executable imports no BF16 store/probe/fetch client and has no network API, URL, subprocess, or BF16-target-forward call path."},
        "runtime": {"python": sys.executable, "platform": platform.platform(), "mlx": mx.__version__}, "evidence_directory": str(out)}
    dump(out / "summary.json", summary)
    print(json.dumps({"classification": summary["classification"], "evidence": str(out)}, indent=2))
    if failure is not None: raise RuntimeError(failure["error"])


if __name__ == "__main__": main()
