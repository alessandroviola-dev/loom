#!/usr/bin/env python3
"""Stretch 041: post-promotion current bottleneck re-attribution (investigation only).

Renders the promoted S1_R8 + deferred-cleanup source, performs no comparison
or treatment, and writes one canonical and one broad-stage profiled diagnostic
plus synchronized isolated real-payload measurements.
"""
from __future__ import annotations

import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LAUNCHER = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
EXPECTED = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
RUNTIME = "scripts/stretch_m1_qmv_fast_runtime_037.py"
S038 = "scripts/stretch_s1r8_deferred_cleanup_comparison_038.py"
CONTROL_SHA = "9f94787f7a002a8da95e8352f134eac11f1b072b9363fe600dcac1122080a54c"
S1R8_SHA = "82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3"
INJECTION_SHA = "a086806a314d387770dac54e9140b9526bf7fe9097819f449bba17b7fc1f3ad4"
TOTAL_WEIGHTS = 3_583_928_320
CANONICAL_CYCLES = 6
PROFILED_CYCLES = 4
WARMUPS = 40
SAMPLES = 120


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def one(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"STRETCH041 anchor {label!r} expected once, found {text.count(old)}")
    return text.replace(old, new, 1)


def host() -> dict:
    pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
    free = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
    swap = re.search(r"used = ([0-9.,]+)([MG])", swap_text)
    if not free or not swap:
        raise RuntimeError("STRETCH041_HOST_TELEMETRY_UNAVAILABLE")
    used = float(swap.group(1).replace(",", ".")) * (1024 if swap.group(2) == "G" else 1)
    return {"free_memory_percent": int(free.group(1)), "swap_used_mb": used, "sampled_at_utc": datetime.now(timezone.utc).isoformat()}


def child_extension() -> str:
    # This executes after the inherited resident/oracle work, exactly as the
    # promoted 038 constituent did. The inherited work is excluded warmup.
    return r'''    # Stretch 041 diagnostic extension: no treatment and no cadence change.
    import statistics as __s041_statistics
    globals()["__s041_profiles"] = []
    globals()["__s041_payloads"] = {}
    globals()["__s041_profile_enabled"] = False
    __s041_profiles, __s041_payloads = globals()["__s041_profiles"], globals()["__s041_payloads"]

    def __s041_eval(value):
        if isinstance(value, tuple): mx.eval(*value)
        else: mx.eval(value)
        return value

    class __s041ProfiledTransformerBlock(qwen3.TransformerBlock):
        def __init__(self, block_args, layer_id):
            super().__init__(block_args); self.__s041_layer_id = int(layer_id)
        def __call__(self, x, mask=None, cache=None):
            if not globals()["__s041_profile_enabled"]:
                return super().__call__(x, mask, cache)
            rec = {"layer": self.__s041_layer_id}
            def stage(name, fn):
                t = time.perf_counter(); value = fn()
                if isinstance(value, tuple): mx.eval(*value)
                else: mx.eval(value)
                rec[name] = time.perf_counter() - t; return value
            n1 = stage("input_rmsnorm", lambda: self.input_layernorm(x))
            q, k, v = stage("qkv_projection", lambda: (self.self_attn.q_proj(n1), self.self_attn.k_proj(n1), self.self_attn.v_proj(n1)))
            B, L, _ = x.shape
            q = stage("q_norm_layout", lambda: self.self_attn.q_norm(q.reshape(B,L,self.self_attn.n_heads,-1)).transpose(0,2,1,3))
            k = stage("k_norm_layout", lambda: self.self_attn.k_norm(k.reshape(B,L,self.self_attn.n_kv_heads,-1)).transpose(0,2,1,3))
            v = stage("v_layout", lambda: v.reshape(B,L,self.self_attn.n_kv_heads,-1).transpose(0,2,1,3))
            q, k = stage("rope", lambda: (self.self_attn.rope(q, offset=cache.offset), self.self_attn.rope(k, offset=cache.offset)))
            k, v = stage("kv_cache_update", lambda: cache.update_and_fetch(k, v))
            a = stage("sdpa", lambda: qwen3.scaled_dot_product_attention(q,k,v,cache=cache,scale=self.self_attn.scale,mask=mask))
            oi = stage("attention_layout", lambda: a.transpose(0,2,1,3).reshape(B,L,-1))
            ao = stage("attention_output_projection", lambda: self.self_attn.o_proj(oi))
            h = stage("residual_1", lambda: x + ao)
            n2 = stage("post_attention_rmsnorm", lambda: self.post_attention_layernorm(h))
            g, u = stage("gate_up_projection", lambda: (self.mlp.gate_proj(n2), self.mlp.up_proj(n2)))
            z = stage("swiglu", lambda: qwen3.swiglu(g,u))
            d = stage("down_projection", lambda: self.mlp.down_proj(z))
            out = stage("residual_2", lambda: h + d)
            if self.__s041_layer_id in (0,18,35) and self.__s041_layer_id not in globals()["__s041_payloads"]:
                globals()["__s041_payloads"][self.__s041_layer_id] = {"block": self, "input": x, "n1": n1, "q":q, "k":k, "v":v, "o_input":oi, "n2":n2, "gate":g, "up":u, "swiglu":z, "h":h}
            globals()["__s041_profiles"].append(rec)
            return out

    # Switch the existing materializer to this identical-layout class. It is
    # dormant during canonical cycles, so it does not alter their graph.
    __s041_original_build_block = build_block
    def build_block(layer_id):
        if layer_id in persistent_blocks: return persistent_blocks[layer_id], None
        marker = f"model.layers.{layer_id}."; selected = select_weights(marker, marker)
        if len(selected) != EXPECTED_LAYER_TENSORS or selected_bytes(selected) != EXPECTED_LAYER_BYTES: raise RuntimeError("STRETCH041 layer payload invariant")
        block = __s041ProfiledTransformerBlock(args, layer_id)
        def class_predicate(path, leaf): return hasattr(leaf, "to_quantized") and f"{path}.scales" in selected
        nn.quantize(block, group_size=quant["group_size"], bits=quant["bits"], mode=quant.get("mode","affine"), class_predicate=class_predicate)
        block.load_weights(list(selected.items()), strict=True); block.eval(); return block, selected

    def __s041_mem():
        return {"mlx_active_bytes":int(mx.get_active_memory()), "mlx_peak_bytes":int(mx.get_peak_memory()), "mlx_cache_bytes":int(mx.get_cache_memory()) if hasattr(mx,"get_cache_memory") else None, **__import__("json").loads(__import__("subprocess").run(["/usr/sbin/sysctl","-n","vm.swapusage"],text=True,capture_output=True).stdout and "{}")}
    def __s041_host():
        p=subprocess.run(["memory_pressure"],text=True,capture_output=True,check=False).stdout; m=__import__("re").search(r"System-wide memory free percentage:\s*(\d+)%",p)
        s=subprocess.run(["sysctl","-n","vm.swapusage"],text=True,capture_output=True,check=False).stdout; n=__import__("re").search(r"used = ([0-9.,]+)([MG])",s)
        return {"free_memory_percent":int(m.group(1)),"swap_used_mb":float(n.group(1).replace(",","."))*(1024 if n.group(2)=="G" else 1),**__s041_mem()}
    def __s041_rows(logits,start,prompt,previous,draft):
        predictions=[prompt if start==0 else previous]+[token_value(logits[:,p:p+1,:]) for p in range(ORACLE_BLOCK_SIZE-1)]; rows=[]
        for p,expected in enumerate(draft):
            r=resident_step_logits[start+p]; t=logits[:,p:p+1,:]; delta=mx.abs(r.astype(mx.float32)-t.astype(mx.float32)); mx.eval(delta)
            maximum=float(mx.max(delta).item()); threshold=1e-5+1e-5*float(mx.max(mx.abs(r.astype(mx.float32))).item()); top=token_value(t)
            rows.append({"accepted":int(predictions[p])==int(expected),"logits_pass":maximum<=threshold,"top1_equal":int(resident_steps[start+p]["predicted_top1"])==top}); del delta
        return rows, token_value(logits[:,ORACLE_BLOCK_SIZE-1:ORACLE_BLOCK_SIZE,:])
    def __s041_cycle(kind, ordinal):
        global __stretch038_cleanup_enabled, __stretch038_before_cleanup, __s041_profile_enabled
        caches=[KVCache() for _ in range(args.num_hidden_layers)]; __stretch038_cleanup_enabled=False; __stretch038_before_cleanup=None; __s041_profile_enabled=False
        pi=make_ids(prompt_token_ids); pl,_=run_streamed_pass(pi,caches,f"s041_prompt_{kind}_{ordinal}"); pt=token_value(pl); pd=mx.abs(resident_prompt_logits.astype(mx.float32)-pl.astype(mx.float32)); mx.eval(pd)
        if pt!=token1 or float(mx.max(pd).item())>1e-5+1e-5*resident_prompt_max_abs: raise RuntimeError("STRETCH041 prompt parity")
        del pi,pl,pd; before=__s041_host(); blocks=[]; prior=None; __s041_profile_enabled=(kind=="PROFILED"); started=time.perf_counter()
        for i in range(2):
            ids=make_ids([oracle_sequence[i*5:i*5+5]]); __stretch038_cleanup_enabled=(i==1); ps=time.perf_counter(); logits,p=run_streamed_pass(ids,caches,f"s041_{kind}_{ordinal}_{i}"); pe=time.perf_counter()
            rows,prior=__s041_rows(logits,i*5,pt,prior,oracle_sequence[i*5:i*5+5]); blocks.append({"pass_wall_seconds":p["total_pass_wall_seconds"],"outer_wall_seconds":pe-ps,"cleanup":p["stages"]["shared_stage_cleanup"],"rows":rows}); del ids,logits
        finished=time.perf_counter(); __s041_profile_enabled=False; __stretch038_cleanup_enabled=True
        rows=[r for b in blocks for r in b["rows"]]; after=__s041_host(); ok=len(rows)==10 and all(r["accepted"] and r["logits_pass"] and r["top1_equal"] for r in rows)
        if not ok: raise RuntimeError("STRETCH041 target correctness")
        return {"kind":kind,"ordinal":ordinal,"target_wall_seconds":finished-started,"wall_per_token_seconds":(finished-started)/10,"blocks":blocks,"before":before,"after":after,"accepted_tokens":10,"full_weight_persistence_bytes":hotset_record["materialized_delta_bytes"]+shared_persistence_record["materialized_delta_bytes"]}
    __s041_result={"canonical":[],"profiled":[],"isolated":{},"warmups":40,"samples":120}
    for i in range(1,7): __s041_result["canonical"].append(__s041_cycle("CANONICAL",i))
    for i in range(1,5): __s041_result["profiled"].append(__s041_cycle("PROFILED",i))
    def __s041_quantiles(v):
        v=sorted(v); return {"median_seconds":__s041_statistics.median(v),"p25_seconds":v[int(.25*(len(v)-1))],"p75_seconds":v[int(.75*(len(v)-1))]}
    def __s041_bench(name, fn):
        for _ in range(40): y=fn(); mx.eval(y)
        xs=[]
        for _ in range(120): t=time.perf_counter(); y=fn(); mx.eval(y); xs.append(time.perf_counter()-t)
        __s041_result["isolated"][name]=__s041_quantiles(xs)
    # Captured intermediates are outputs from actual profile-path M5 blocks.
    for lid,p in __s041_payloads.items():
        b=p["block"]; a=b.self_attn; m=b.mlp
        __s041_bench(f"layer{lid}.q_proj",lambda p=p,a=a:a.q_proj(p["n1"]))
        __s041_bench(f"layer{lid}.k_proj",lambda p=p,a=a:a.k_proj(p["n1"]))
        __s041_bench(f"layer{lid}.v_proj",lambda p=p,a=a:a.v_proj(p["n1"]))
        __s041_bench(f"layer{lid}.o_proj",lambda p=p,a=a:a.o_proj(p["o_input"]))
        __s041_bench(f"layer{lid}.gate_proj",lambda p=p,m=m:m.gate_proj(p["n2"]))
        __s041_bench(f"layer{lid}.up_proj",lambda p=p,m=m:m.up_proj(p["n2"]))
        __s041_bench(f"layer{lid}.down_proj",lambda p=p,m=m:m.down_proj(p["swiglu"]))
        __s041_bench(f"layer{lid}.input_rmsnorm",lambda p=p,b=b:b.input_layernorm(p["input"]))
        __s041_bench(f"layer{lid}.post_rmsnorm",lambda p=p,b=b:b.post_attention_layernorm(p["h"]))
        __s041_bench(f"layer{lid}.residual_add",lambda p=p:p["input"]+p["h"])
        __s041_bench(f"layer{lid}.swiglu",lambda p=p:qwen3.swiglu(p["gate"],p["up"]))
    __s041_bench("final_norm",lambda: persistent_shared["norm"](__s041_payloads[35]["h"]))
    __s041_bench("lm_head",lambda: persistent_shared["head"](__s041_payloads[35]["h"]))
    __s041_result["profile_records"]=__s041_profiles
    __s041_result["lm_head"]={"class":type(persistent_shared["head"].lm_head).__name__,"weight_shape":list(persistent_shared["head"].lm_head["weight"].shape),"weight_dtype":str(persistent_shared["head"].lm_head["weight"].dtype),"bits":getattr(persistent_shared["head"].lm_head,"bits",None),"group_size":getattr(persistent_shared["head"].lm_head,"group_size",None),"mode":getattr(persistent_shared["head"].lm_head,"mode",None),"m5_eligible_for_s1r8":False}
    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens
    stream_peak = int(mx.get_peak_memory())
'''


def render(repo: Path) -> tuple[str, dict]:
    sys.path.insert(0, str(repo / "scripts"))
    import stretch_s1r8_deferred_cleanup_comparison_038 as s038
    source, info = s038.render_final(repo, "TREATMENT")
    p = info["promoted_s1_r8"]
    if (p["control_sha256"], p["treatment_sha256"], p["injection_sha256"], p["normalized_equal"]) != (CONTROL_SHA, S1R8_SHA, INJECTION_SHA, True):
        raise RuntimeError(f"STRETCH041 promoted source changed: {p}")
    # Insert the profiled class before build_block; replacement extension follows.
    anchor = "    def build_block(layer_id: int):\n"
    injected = child_extension()
    # child_extension contains both class and experiment; split at its build switch comment.
    class_part, extension = injected.split("    # Switch the existing materializer", 1)
    source = one(source, anchor, class_part + anchor, "profile class")
    source = one(source, "        block = qwen3.TransformerBlock(args)\n", "        block = __s041ProfiledTransformerBlock(args, layer_id)\n", "profile block construction")
    extension = "    # Switch the existing materializer" + extension
    # Its redundant build_block override is not needed after replacing construction.
    left = extension.index("    def __s041_mem()")
    extension = extension[left:]
    start = source.index("    # Stretch 038 scientific constituent.")
    end_marker = "    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n"
    end = source.index(end_marker, start) + len(end_marker)
    source = source[:start] + extension + source[end:]
    source = one(source, '        "stretch038": __stretch038_result,\n', '        "stretch041": __s041_result,\n', "result payload")
    return source, {"rendered_sha256": digest(source), "promoted": p}


def parse_summary(stdout: str) -> Path | None:
    found = re.findall(r"^Summary:\s*(.+summary\.json)\s*$", stdout, re.M)
    return Path(found[-1]) if found else None


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    root = repo / "results-local/stretch/current-bottleneck-attribution-041" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    root.mkdir(parents=True, exist_ok=False)
    summary = {"classification":"RUNNING", "investigation_only":True, "no_treatment":True, "no_abba":True, "source":{}}
    try:
        py_compile.compile(str(Path(__file__)), doraise=True)
        launch = repo / LAUNCHER
        if not launch.is_symlink(): raise RuntimeError("STRETCH041 canonical launcher missing")
        observed = json.loads(subprocess.check_output([str(launch),"-c","import importlib.metadata as m,json;print(json.dumps({x:m.version(x) for x in ('mlx','mlx-metal','mlx-lm','transformers')}))"], text=True))
        if observed != EXPECTED: raise RuntimeError(f"STRETCH041 runtime mismatch {observed}")
        ready = host(); summary["host_before"] = ready
        if ready["free_memory_percent"] < 5 or ready["swap_used_mb"] > 5600: raise RuntimeError("STRETCH041 resource abort")
        source, provenance = render(repo); generated = root / "stretch041-current.py"; generated.write_text(source); compile(source,str(generated),"exec")
        summary["source"] = {**provenance,"runtime_versions":observed,"runtime_script_blob":subprocess.check_output(["git","rev-parse",f"HEAD:{RUNTIME}"],cwd=repo,text=True).strip(),"stretch038_blob":subprocess.check_output(["git","rev-parse",f"HEAD:{S038}"],cwd=repo,text=True).strip()}
        proc=subprocess.run([str(launch),str(generated)],cwd=repo,env={**os.environ,"LOOM_REPO":str(repo),"STRETCH038_RUN_DIR":str(root)},text=True,capture_output=True,check=False)
        (root/"stdout.txt").write_text(proc.stdout); (root/"stderr.txt").write_text(proc.stderr); child=parse_summary(proc.stdout); final=root/"child-final.json"
        summary.update({"child_returncode":proc.returncode,"child_summary":str(child) if child else None,"child_final":str(final) if final.is_file() else None})
        if child and child.is_file(): shutil.copy2(child,root/"child-summary.json")
        if proc.returncode or not final.is_file(): raise RuntimeError("STRETCH041 child failed or payload absent")
        payload=json.loads(final.read_text()); result=payload.get("stretch041")
        if not result: raise RuntimeError("STRETCH041 payload absent")
        if any(x["full_weight_persistence_bytes"]!=TOTAL_WEIGHTS or x["accepted_tokens"]!=10 for x in result["canonical"]+result["profiled"]): raise RuntimeError("STRETCH041 invariant failure")
        summary.update({"classification":"STRETCH_041_CURRENT_BOTTLENECK_MAP_COMPLETE","result":result,"custom_qmv":payload.get("custom_qmv"),"mlx_peak_bytes":payload.get("stream_peak")})
    except Exception as exc:
        summary.update({"classification":"STRETCH_041_ATTRIBUTION_INCOMPLETE","error":f"{type(exc).__name__}: {exc}"})
    (root/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(f"Classification: {summary['classification']}\nSummary: {root/'summary.json'}")
    return 0 if summary["classification"].endswith("COMPLETE") else 2

if __name__ == "__main__": raise SystemExit(main())
