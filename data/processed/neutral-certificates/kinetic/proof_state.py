#!/usr/bin/env python3
"""Atomic proof metadata only; no scientific numerical runner."""
from pathlib import Path
import json,hashlib,os,sys,datetime
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
    t=p.with_name(p.name+'.tmp')
    with t.open('w') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(t,p)
    fd=os.open(str(p.parent),os.O_RDONLY);os.fsync(fd);os.close(fd)
def fingerprint():
    d=json.loads((R/'INPUTS.json').read_text());h={n:sha(R/n) for n in ['CHECK_PLAN.md','INPUTS.json','proof_state.py']}
    for e in d['files']:
        assert sha(Path(e['source']))==e['sha256'],e['source']
        assert sha(R/e['snapshot'])==e['sha256'],e['snapshot']
        h[e['snapshot']]=e['sha256']
    return hashlib.sha256(json.dumps(h,sort_keys=True).encode()).hexdigest(),h
def recover():
    p=json.loads((R/'checkpoints/latest.json').read_text());c=R/'checkpoints'/p['path'];assert sha(c)==p['sha256']
    d=json.loads(c.read_text());fp,h=fingerprint();assert fp==d['fingerprint'] and h==d['bound_hashes']
    for n,v in d['artifact_hashes'].items():assert sha(R/n)==v,n
    return d
def commit():
    seq=recover()['sequence']+1 if (R/'checkpoints/latest.json').exists() else 1
    fp,h=fingerprint();s=json.loads((R/'state.json').read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    d={'sequence':seq,'utc':now,'fingerprint':fp,'bound_hashes':h,'state':s,'artifact_hashes':{n:sha(R/n) for n in s['completed_artifacts']},'numerical_RNG_state':'not applicable; hand analysis only'}
    n=f'checkpoint_{seq:03d}.json';atomic(R/'checkpoints'/n,d);atomic(R/'checkpoints/latest.json',{'path':n,'sha256':sha(R/'checkpoints'/n)})
    atomic(R/'progress.json',{'utc':now,'status':s['status'],'current_unit':s['current_unit'],'completed_units':s['completed_units'],'total_units':4,'last_durable_checkpoint':n,'fingerprint':fp,'block_maximum':'2026-10-19T16:03:42Z','scientific_classification':'SEPARATE_FROM_CHECKPOINT'})
    return d
if __name__=='__main__':
    d=commit() if sys.argv[1]=='commit' else recover()
    print(json.dumps({'sequence':d['sequence'],'fingerprint':d['fingerprint'],'artifact_count':len(d['artifact_hashes']),'state':d['state']['status']}))
