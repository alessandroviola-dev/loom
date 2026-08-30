#!/usr/bin/env python3
"""Frozen WP2 A/B/C server benchmark.  It never modifies the frozen corpus."""
from __future__ import annotations
import argparse, json, os, re, statistics, subprocess, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
CLI=ROOT/'scripts/loom-context'
CASES=json.loads((ROOT/'benchmarks/context-intelligence-wp2/frozen-cases.json').read_text())['cases']

def corpus(case):
    target=case['target']; kind=case['class']
    if kind=='verbose_logs': return '\n'.join(['2026-08-30 INFO worker=7 progress=ok']*6+[f'2026-08-30 FATAL failing_path={target} errno=42']+['2026-08-30 WARNING retryable background noise']*6)
    if kind=='repository_search': return '\n'.join([f'{target}:66: selected canonical result path']+[f'scripts/noise_{i}.py:{i}: unrelated search occurrence' for i in range(1,12)])
    if kind=='structured_json': return json.dumps({'source_commit':target,'model_sha256':'c5d08e67dc535b9c00aa8c27535239b89cb18026e7f10d4184b65adfe8036251','records':[{'id':f'noise-{i}','status':'unrelated','nested':{'value':i}} for i in range(8)]},indent=2)
    if kind=='code_read': return '\n'.join(['# generated helper']+[f'noise_value_{i} = {i}' for i in range(20)]+['def selected_policy():','    return "S32"']+[f'other_value_{i} = {i}' for i in range(20)])
    if kind=='diff': return '\n'.join(['diff --git a/.pi/settings b/.pi/settings','--- a/.pi/settings','+++ b/.pi/settings','@@ -1,2 +1,3 @@',f'+export {target}']+[f' unchanged context {i}' for i in range(18)])
    if kind=='earlier_project_decision': return '\n'.join(['historical narrative unrelated to runtime selection']*6+['Decision: canonical S32 median decode is 5.596 tok/s; S24 is rollback.']+['historical narrative unrelated to runtime selection']*6)
    return ''

def rss_swap():
    pid=(ROOT/'results-local/runtime-productization-wp1/live/llama-server.pid').read_text().strip()
    rss=int(subprocess.check_output(['ps','-o','rss=','-p',pid],text=True).strip() or 0)*1024
    swap=subprocess.check_output(['sysctl','-n','vm.swapusage'],text=True).strip()
    return {'server_rss_bytes':rss,'swapusage':swap}

def pack(payload, query, memory):
    import tempfile
    with tempfile.NamedTemporaryFile('w',suffix='.json',delete=False) as f:
        json.dump(payload,f); path=f.name
    try:
        cmd=[str(CLI),'pack-payload','--input',path,'--query',query,'--budget','120']+([] if memory else ['--no-memory'])
        started=time.perf_counter(); result=subprocess.run(cmd,text=True,capture_output=True,check=True); elapsed=(time.perf_counter()-started)*1000
        out=json.loads(result.stdout); out['accounting']['host_wall_ms']=round(elapsed,3); return out
    finally: os.unlink(path)

def request(payload):
    data=json.dumps({**payload,'model':'loom-deep-30b-s32','max_tokens':16,'temperature':0,'stream':False,'enable_thinking':False}).encode()
    started=time.perf_counter()
    try:
        with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:18080/v1/chat/completions',data=data,headers={'Content-Type':'application/json'}),timeout=180) as response: out=json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'provider HTTP {error.code}: {error.read().decode(errors="replace")}') from error
    return out,round((time.perf_counter()-started)*1000,3)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    (out/'frozen-cases.json').write_text((ROOT/'benchmarks/context-intelligence-wp2/frozen-cases.json').read_text())
    results=[]; before=rss_swap()
    # Fixed interleaving prevents one arm receiving all warm or cold requests.
    arms=[('A','baseline',None),('B','packer_only',False),('C','combined',True)]
    for ci,case in enumerate(CASES):
        raw=corpus(case)
        base={'messages':([{'role':'user','content':raw}] if raw else [])+[{'role':'user','content':case['query']}]}
        order=arms[ci%3:]+arms[:ci%3]
        for arm,label,memory in order:
            if arm=='A': payload=base; accounting={'bypassed':True,'tokens_before':0,'tokens_after':0,'saved':0,'host_wall_ms':0,'selected':0,'deferred':0,'recovery_refs':[]}
            else:
                packed=pack(base,case['query'],memory); payload=packed['payload']; accounting=packed['accounting']
            response,e2e=request(payload)
            answer=response['choices'][0]['message']['content']; usage=response.get('usage',{}); timings=response.get('timings',{})
            item={'case_id':case['id'],'class':case['class'],'arm':arm,'label':label,'expected':case['expected'],'answer':answer,'success':case['expected'].lower() in answer.lower(),'provider_prompt_tokens':usage.get('prompt_tokens'),'completion_tokens':usage.get('completion_tokens'),'prefill_ms':timings.get('prompt_ms'),'e2e_ms':e2e,'decode_tok_s':timings.get('predicted_per_second'),'accounting':accounting}
            results.append(item); (out/f'{case["id"]}-{arm}.json').write_text(json.dumps({'payload':payload,'response':response,'result':item},indent=2))
    after=rss_swap()
    summary={'benchmark_version':'1.0.0','cases':len(CASES),'results':results,'resource_before':before,'resource_after':after}
    for arm in 'ABC':
        items=[x for x in results if x['arm']==arm]; summary[arm]={'successes':sum(x['success'] for x in items),'total':len(items),'median_prompt_tokens':statistics.median(x['provider_prompt_tokens'] for x in items),'median_prefill_ms':statistics.median(x['prefill_ms'] for x in items),'median_e2e_ms':statistics.median(x['e2e_ms'] for x in items),'median_decode_tok_s':statistics.median(x['decode_tok_s'] for x in items),'median_host_wall_ms':statistics.median(x['accounting'].get('host_wall_ms',0) for x in items)}
    heavy=[x for x in results if x['class']!='small_noop']
    for arm in 'BC':
        paired=[]
        for x in heavy:
            a=next(y for y in heavy if y['case_id']==x['case_id'] and y['arm']=='A')
            if x['arm']==arm: paired.append((a['provider_prompt_tokens']-x['provider_prompt_tokens'])/a['provider_prompt_tokens'])
        summary[arm]['heavy_median_provider_input_reduction']=statistics.median(paired)
    summary['A']['noop_prompt_tokens']=next(x['provider_prompt_tokens'] for x in results if x['case_id']=='noop' and x['arm']=='A')
    for arm in 'BC': summary[arm]['noop_prompt_tokens']=next(x['provider_prompt_tokens'] for x in results if x['case_id']=='noop' and x['arm']==arm)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
