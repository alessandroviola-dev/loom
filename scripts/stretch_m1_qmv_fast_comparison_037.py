#!/usr/bin/env python3
"""Stretch 037 frozen CONTROL vs custom S1_R8 full-model ABBA harness."""
from __future__ import annotations
import json, os, py_compile, re, shutil, statistics, subprocess, sys, time
from datetime import datetime
from pathlib import Path

CANONICAL_LAUNCHER = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
RUNTIME = "scripts/stretch_m1_qmv_fast_runtime_037.py"
FEASIBILITY = "scripts/stretch_m1_qmv_fast_tuning_037_feasibility.py"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED_VERSIONS = {"mlx":"0.31.2","mlx-metal":"0.31.2","mlx-lm":"0.31.3","transformers":"5.12.1"}
EXPECTED_CLASS = "SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS"
RUN_ORDER = ("CONTROL", "S1_R8", "S1_R8", "CONTROL")
ORACLE_TOKENS, BLOCKS, TOTAL_WEIGHTS = 10, 2, 3_583_928_320


def parse_summary(stdout: str) -> Path | None:
    found = re.findall(r"^Summary:\s*(.+summary\.json)\s*$", stdout, re.M)
    return Path(found[-1]) if found else None

def distribution(records: list[dict]) -> dict:
    accepted=sum(r["accepted_tokens"] for r in records); wall=sum(r["total_wall"] for r in records)
    blocks=[x for r in records for x in r["block_walls"]]; cleanup=[x for r in records for x in r["cleanup_walls"]]
    return {"runs":len(records),"accepted_tokens":accepted,"total_target_block_wall_seconds":wall,"pooled_target_verification_tokens_per_second":accepted/wall,"wall_seconds_per_accepted_token":wall/accepted,"median_block_wall_seconds":statistics.median(blocks),"mean_block_wall_seconds":statistics.mean(blocks),"final_cleanup_wall_seconds_per_accepted_token":sum(cleanup)/accepted,"raw_block_walls":blocks,"raw_final_cleanup_walls":cleanup,"minimum_free_memory_percent":min(r["min_free"] for r in records),"peak_swap_mb":max(r["peak_swap"] for r in records),"peak_active_mlx_bytes":max(r["peak_active"] for r in records),"peak_mlx_bytes":max(r["peak_mlx"] for r in records)}

def render_preflight(repo: Path, root: Path) -> dict:
    sys.path.insert(0,str(repo/"scripts"))
    import stretch_m1_qmv_fast_runtime_037 as runtime
    for path in (repo/RUNTIME,repo/FEASIBILITY,repo/"scripts/stretch_m1_qmv_fast_comparison_037.py"): py_compile.compile(str(path),doraise=True)
    control, cf = runtime.render(repo,"control"); treatment, tf = runtime.render(repo,"treatment")
    (root/"control-final.py").write_text(control); (root/"treatment-final.py").write_text(treatment)
    compile(control,str(root/"control-final.py"),"exec"); compile(treatment,str(root/"treatment-final.py"),"exec")
    if not tf["normalized_equal"]: raise RuntimeError("normalized factor diff failed")
    required=("metal_source as __stretch037_metal_source","self.group_size == 64","bits == 3","self.mode == \"affine\"","x_value.shape[-2] == 5","threadgroup=(32, 1, 1)","grid=(32 * 5, n // 8, 1)")
    missing=[x for x in required if x not in treatment]
    if missing: raise RuntimeError(f"static treatment invariant missing {missing}")
    launcher=repo/CANONICAL_LAUNCHER
    if not launcher.is_symlink(): raise RuntimeError("literal venv launcher is not symlink")
    marker={}
    for mode in ("control","treatment"):
        out=root/f"{mode}-no-model.json"; env={**os.environ,"STRETCH037_MODE":mode}
        proc=subprocess.run([str(launcher),str(repo/RUNTIME),"--dispatch-preflight",str(out)],cwd=repo,env=env,capture_output=True,text=True,check=False)
        if proc.returncode or not out.is_file(): raise RuntimeError(f"{mode} no-model dispatch failed: {proc.stderr}")
        marker[mode]=json.loads(out.read_text())
        if marker[mode].get("model_loaded") or marker[mode].get("target_compute_executed") or marker[mode].get("classification")!="STRETCH_037_NO_MODEL_DISPATCH_PASS": raise RuntimeError(f"{mode} no-model marker invalid")
    jit=root/"treatment-jit-preflight.json"; env={**os.environ,"STRETCH037_MODE":"treatment"}
    proc=subprocess.run([str(launcher),str(repo/RUNTIME),"--jit-preflight",str(jit)],cwd=repo,env=env,capture_output=True,text=True,check=False)
    if proc.returncode or not jit.is_file(): raise RuntimeError(f"JIT preflight failed: {proc.stderr}")
    startup=json.loads(jit.read_text())
    if startup.get("kernel_count") != 4 or not all(x.get("exact_equal") for x in startup.get("real_weight_parity",[])): raise RuntimeError("JIT/parity preflight invalid")
    return {"classification":"STRETCH_037_PREFLIGHT_PASS","scientific_run":False,"py_compile":"PASS","control_source_sha256":cf["control_sha256"],"treatment_source_sha256":tf["treatment_sha256"],"normalized_scientific_diff":"PASS: only built-in MLX qmv implementation vs custom S1_R8 injection","static_kernel_invariants":"PASS","literal_launcher":str(launcher),"no_model_dispatch":marker,"runtime_expected":EXPECTED_VERSIONS,"startup":startup,"directory":str(root)}

def main() -> int:
    repo=Path(__file__).resolve().parents[1]
    if sys.argv[1:] == ["--preflight"]:
        root=repo/"results-local/stretch/m1-qmv-fast-tuning-037/preflight"/datetime.now().strftime("%Y%m%d-%H%M%S"); root.mkdir(parents=True)
        try: result=render_preflight(repo,root)
        except Exception as exc:
            (root/"preflight-summary.json").write_text(json.dumps({"classification":"STRETCH_037_PREFLIGHT_FAIL","scientific_run":False,"error":f"{type(exc).__name__}: {exc}"},indent=2)+"\n"); print(f"Classification: STRETCH_037_PREFLIGHT_FAIL\nError: {exc}",file=sys.stderr); return 2
        path=root/"preflight-summary.json"; path.write_text(json.dumps(result,indent=2)+"\n"); print(f"Classification: {result['classification']}\nPreflight summary: {path}"); return 0
    if sys.argv[1:]: print("usage: comparison_037.py [--preflight]",file=sys.stderr); return 2
    root=repo/"results-local/stretch/m1-qmv-fast-tuning-037"/datetime.now().strftime("%Y%m%d-%H%M%S"); root.mkdir(parents=True)
    try: preflight=render_preflight(repo,root/"preflight"); (root/"preflight/preflight-summary.json").write_text(json.dumps(preflight,indent=2)+"\n")
    except Exception as exc:
        (root/"summary.json").write_text(json.dumps({"classification":"M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE","scientific_result":"NONE","failure_reason":f"preflight: {type(exc).__name__}: {exc}"},indent=2)+"\n"); print(f"Classification: M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE\nSummary: {root/'summary.json'}"); return 2
    summary={"experiment":"Stretch 037 built-in MLX qmv_fast vs M1-specific custom S1_R8","classification":"RUNNING","scientific_factor":"built-in MLX affine qmv_fast implementation -> M1-specific custom qmv_fast S1_R8 implementation","run_order":RUN_ORDER,"preflight":preflight,"frozen":"Qwen3-8B 3bit/group64; M5; H36; full persistence; one final cleanup; BF16 KV; MLX 0.31.2","attempts":[],"deliberate_cache_purge":False}
    def save(): (root/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    save(); launcher=repo/CANONICAL_LAUNCHER
    for idx, variant in enumerate(RUN_ORDER,1):
        mode="control" if variant=="CONTROL" else "treatment"; out=root/f"attempt-{idx}-{variant.lower()}-stdout.txt"; err=root/f"attempt-{idx}-{variant.lower()}-stderr.txt"
        started=time.perf_counter(); env={**os.environ,"STRETCH037_MODE":mode}
        with out.open("w") as so, err.open("w") as se: proc=subprocess.run([str(launcher),str(repo/RUNTIME)],cwd=repo,env=env,stdout=so,stderr=se,check=False)
        child_path=parse_summary(out.read_text(errors="replace")); attempt={"attempt":idx,"variant":variant,"returncode":proc.returncode,"wrapper_wall_seconds":time.perf_counter()-started,"stdout":str(out),"stderr":str(err),"child_summary":str(child_path) if child_path else None}
        if not child_path or not child_path.is_file(): summary.update({"classification":"M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE","scientific_result":"NONE","failure_reason":f"attempt {idx}: child summary missing"}); summary["attempts"].append(attempt); save(); return 3
        child=json.loads(child_path.read_text()); attempt["classification"]=child.get("classification")
        # Genuine treatment numerical/oracle failure is scientific FAIL, never rescue.
        scientific_fail=variant=="S1_R8" and child.get("classification") in {"PROMPT_KV_NUMERICAL_PARITY_FAIL","GENERATED_TOKEN_MISMATCH","ORACLE_SEQUENCE_PROVENANCE_FAIL","ORACLE_BLOCK_NUMERICAL_PARITY_FAIL","ORACLE_BLOCK_TOP1_MISMATCH","ORACLE_TOKEN_REJECTED","GENERATED_SEQUENCE_MISMATCH"}
        if scientific_fail:
            summary.update({"classification":"M1_QMV_FAST_TUNING_NUMERICAL_PARITY_FAIL","scientific_result":"VALID_FAIL","failure_reason":child.get("failure_reason")}); summary["attempts"].append(attempt); save(); return 0
        ob=child.get("oracle_block_verification",{}); hot=child.get("hotset",{}); full=child.get("full_weight_persistence",{}); tele=child.get("telemetry",{}); stream=(child.get("stream") or {}).get("tokens") or []
        cleanup=[float((r.get("pass",{}).get("stages",{}).get("shared_stage_cleanup") or {}).get("wall_seconds",-1)) for r in stream]
        custom=None
        final_file=child.get("child_final_file")
        if final_file and Path(final_file).is_file(): custom=json.loads(Path(final_file).read_text()).get("custom_qmv")
        attempt.update({"accepted_tokens":ob.get("accepted_oracle_tokens"),"total_wall":ob.get("total_target_block_wall_seconds"),"block_walls":ob.get("block_full_pass_seconds") or [],"cleanup_walls":cleanup,"min_free":tele.get("min_memory_free_percent"),"peak_swap":tele.get("peak_swap_used_mb"),"peak_active":tele.get("peak_active_memory_bytes",0),"peak_mlx":max([child.get("resident",{}).get("peak_bytes",0),child.get("stream",{}).get("peak_bytes",0)]),"custom_kernel":custom})
        usable=proc.returncode==0 and child.get("classification")==EXPECTED_CLASS and list(hot.get("layer_ids",[]))==list(range(36)) and abs(int(full.get("persistent_total_raw_weight_bytes",0))-TOTAL_WEIGHTS)<=24*1024*1024 and int(ob.get("accepted_oracle_tokens",0))==ORACLE_TOKENS and len(attempt["block_walls"])==BLOCKS and len(cleanup)==BLOCKS and all(x>=0 for x in cleanup)
        if variant=="S1_R8": usable=usable and custom is not None and custom.get("kernel_count")==4 and custom.get("recompilation_count_during_target")==0 and all(x.get("exact_equal") for x in custom.get("real_weight_parity",[]))
        attempt["usable"]=usable; summary["attempts"].append(attempt); save()
        if not usable: summary.update({"classification":"M1_QMV_FAST_TUNING_COMPARISON_INCOMPLETE","scientific_result":"NONE","failure_reason":f"attempt {idx} inherited/provenance/resource gate failed"}); save(); return 4
    control=distribution([x for x in summary["attempts"] if x["variant"]=="CONTROL"]); treatment=distribution([x for x in summary["attempts"] if x["variant"]=="S1_R8"])
    ratio=treatment["pooled_target_verification_tokens_per_second"]/control["pooled_target_verification_tokens_per_second"]
    summary.update({"classification":"M1_QMV_FAST_TUNING_BALANCED_COMPARISON_PASS","scientific_result":"VALID_ABBA","comparison":{"control":control,"s1_r8":treatment,"s1_r8_over_control_ratio":ratio,"percent_gain":(ratio-1)*100,"observed_winner":"S1_R8" if ratio>1 else "CONTROL"}}); save(); print(f"Classification: {summary['classification']}\nCONTROL tok/s: {control['pooled_target_verification_tokens_per_second']}\nS1_R8 tok/s: {treatment['pooled_target_verification_tokens_per_second']}\nRatio: {ratio}\nSummary: {root/'summary.json'}"); return 0
if __name__ == "__main__": raise SystemExit(main())
