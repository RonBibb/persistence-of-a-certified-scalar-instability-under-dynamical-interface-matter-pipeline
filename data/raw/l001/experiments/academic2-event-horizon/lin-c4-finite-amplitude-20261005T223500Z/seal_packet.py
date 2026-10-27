"""Seal independently accepted finite-amplitude evidence; no IVP kernels."""
import hashlib,json,os,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path

root=Path(sys.argv[1]).resolve()
assert root.name=='lin-c4-finite-amplitude-20261005T223500Z'
guard='3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x):
    assert not p.exists(),str(p)
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.uncommitted-',dir=p.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(x,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);p.chmod(0o444)

binding=read(root/'BINDINGS.json');assert sha(root/'BINDINGS.json')==guard
assert read(root/'FREEZE_RECORD.json')['guard']==guard
for label in ('sources','reviews','inputs'):
    for n,h in binding[label].items():assert sha(root/n)==h,(label,n)
for n,h in {binding['runtime']['executable']:binding['runtime']['executable_sha256'],**binding['runtime']['libraries']}.items():
    assert sha(Path(n))==h,('runtime',n)
producer=read(root/'output/RESULT.json');terminal=read(root/'output/TERMINAL.json')
audit=read(root/'INDEPENDENT_AUDIT.json')
classification='BOTH_SIGNED_FINITE_AMPLITUDE_C4_SAMPLES_CERTIFIED'
assert producer['guard']==terminal['guard']==audit['guard']==guard
assert producer['classification']==audit['scientific_classification']==classification
assert audit['overall']=='PASS' and audit['both_signed_certificates_accepted'] is True and audit['inputs_unchanged'] is True
assert audit['audit_source_sha256']==sha(root/'postrun_audit.py')
assert terminal['result_sha256']==audit['graph_terminal_evidence_sha256']==sha(root/'output/RESULT.json')
assert sorted(audit['accepted_cases'])==['negative','positive']
assert producer['return_codes']=={'negative':0,'positive':0}
for name in ('source','zero','positive','negative'):
    t=read(root/'output'/name/'TERMINAL.json')
    assert t['guard']==guard and t['status']=='COMPLETE'
    assert t['result_sha256']==sha(root/'output'/name/'RESULT.json')
assert not list((root/'output').rglob('FAILURE.json'))
processes=[s.strip() for s in subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines()
           if str(root/'runner.py')+' ' in s]
assert not processes,processes
utc=datetime.now(timezone.utc).isoformat()
save(root/'FINAL_LIVENESS.json',{'utc':utc,'guard':guard,'matching_producer_processes':processes,
                               'scope':'Only this finite-amplitude packet; unrelated jobs untouched.'})
artifacts=['output/RESULT.json','output/TERMINAL.json','INDEPENDENT_AUDIT.json','POSTRUN_REVIEW.md',
           'postrun_audit.py','RESULT_REPORT.md','FINAL_LIVENESS.json']
result={'status':'COMPLETE','classification':classification,'guard':guard,'independently_accepted':True,
        'evidence_class':'COMPUTER_ASSISTED_FINITE_AMPLITUDE_INITIAL_DATA_EXISTENCE_AND_UNIQUENESS',
        'epsilon_samples':['1/200000','-1/200000'],'connected_amplitude_interval_certified':False,
        'exact_family':'Central D1 final three-variable C7 plus fifth-jet preparation with original physical mode and walls',
        'unknown_box_half_widths':binding['config']['radii'],
        'checkpoint_count':audit['checkpoint_count'],'native_ball_count':audit['native_ball_count'],
        'validated_cells':audit['source']['cells']+16365+sum(sum(v['phase_cells'].values()) for v in audit['cases'].values()),
        'case_seconds':{n:v['elapsed_seconds'] for n,v in audit['cases'].items()},
        'limits':['No connected epsilon interval certificate','No all-order compatibility',
                  'No hyperbolic spacetime existence theorem or time evolution','No horizon or child-universe result'],
        'physical_evolution_launched':False,'successor_launched':False,'live_numerical_processes':[],
        'artifacts':{n:sha(root/n) for n in artifacts},'sealed_utc':utc}
save(root/'RESULT.json',result)
paths=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name not in ('RUN.lock','GRAPH.lock')]
assert not any('__pycache__' in p.parts or '.uncommitted-' in p.name for p in paths)
entries=[]
for p in paths:
    p.chmod(0o444);entries.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)})
save(root/'MANIFEST.json',{'classification':classification,'entries':entries,'sealed_utc':utc,
                         'exclusions':['MANIFEST.json self-reference','Unlocked RUN.lock and GRAPH.lock files']})
assert all(sha(root/e['path'])==e['sha256'] for e in read(root/'MANIFEST.json')['entries'])
print(json.dumps({'status':'SEALED','classification':classification,'guard':guard,'files':len(entries),
                  'result_sha256':sha(root/'RESULT.json'),'manifest_sha256':sha(root/'MANIFEST.json')},indent=2))
