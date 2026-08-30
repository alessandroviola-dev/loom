#!/usr/bin/env python3
"""Frozen, deterministic WP3-R2 local model evaluation (no prompt treatment)."""
from __future__ import annotations
import argparse, json, re, subprocess, time
from pathlib import Path
from statistics import median
from urllib.request import Request, urlopen


def post(url, body):
    r = Request(url.rstrip('/') + '/v1/chat/completions', data=json.dumps(body).encode(), headers={'Content-Type':'application/json'}, method='POST')
    with urlopen(r, timeout=900) as response: return json.loads(response.read())
def command(*args):
    try: return subprocess.check_output(args, text=True).strip()
    except Exception: return 'unavailable'
def degenerate(text):
    t=text.strip()
    return len(t)<3 or (bool(t) and max(t.count(c) for c in set(t))/len(t)>.5)
def capability(item, text):
    x=text.lower(); i=item['id']
    if i=='b02':
        try: return json.loads(re.search(r'\{.*?\}',text,re.S).group(0))=={'a':1,'b':2}
        except Exception: return False
    if i=='b04': return 'def add' in x and 'return' in x
    if i=='b05': return text.strip()=='323'
    if i=='b06': return all(w in x for w in ('red','green','blue'))
    return len(text.strip())>=12 and not degenerate(text)
def disposition(item, text):
    x=text.lower()
    return not degenerate(text) and all(v in x for v in item['required'])
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--frozen',type=Path,required=True); ap.add_argument('--controls',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--url',required=True); ap.add_argument('--pid',type=int,required=True); ap.add_argument('--model',required=True); ap.add_argument('--sets',default='target_heldout,benign,disposition'); args=ap.parse_args()
    frozen=json.loads(args.frozen.read_text()); controls=json.loads(args.controls.read_text()); markers=tuple(frozen['scoring']['refusal_markers']); requested=args.sets.split(',')
    datasets={'target_heldout':frozen['target_heldout'],'benign':frozen['benign'],'disposition':controls['items']}; rows=[]
    for set_name in requested:
        for item in datasets[set_name]:
            body={'model':args.model,'messages':[{'role':'system','content':frozen['chat']['system']},{'role':'user','content':item['prompt']}], 'temperature':frozen['chat']['temperature'],'top_p':frozen['chat']['top_p'],'seed':frozen['chat']['seed'],'max_tokens':frozen['chat']['max_tokens'],'stream':False}
            start=time.monotonic(); response=post(args.url,body); elapsed=time.monotonic()-start; text=response['choices'][0]['message']['content'] or ''; lower=text.lower()
            row={'set':set_name,'id':item['id'],'elapsed_s':elapsed,'text':text,'refusal':any(m in lower for m in markers),'degenerate':degenerate(text),'capability_pass':capability(item,text) if set_name=='benign' else None,'disposition_pass':disposition(item,text) if set_name=='disposition' else None,'timings':response.get('timings',{}),'rss_kib':command('ps','-o','rss=','-p',str(args.pid)),'swap':command('sysctl','vm.swapusage')}; rows.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ('text','swap')}),flush=True)
    summary={}
    for set_name in requested:
        got=[r for r in rows if r['set']==set_name]
        summary[set_name]={'n':len(got),'refusal_count':sum(r['refusal'] for r in got),'degenerate_count':sum(r['degenerate'] for r in got),'capability_success':sum(bool(r['capability_pass']) for r in got) if set_name=='benign' else None,'disposition_success':sum(bool(r['disposition_pass']) for r in got) if set_name=='disposition' else None,'elapsed_median_s':median(r['elapsed_s'] for r in got),'decode_tok_s_median':median(r['timings'].get('predicted_per_second',0) for r in got),'prompt_tok_s_median':median(r['timings'].get('prompt_per_second',0) for r in got)}
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps({'model':args.model,'sets':summary,'rows':rows},indent=2)+'\n'); print(json.dumps({'summary':summary},indent=2))
if __name__=='__main__': main()
