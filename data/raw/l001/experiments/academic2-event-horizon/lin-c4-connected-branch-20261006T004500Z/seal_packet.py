"""Publish independently audited interval-branch evidence; no IVP imports."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone

root=Path(sys.argv[1]).resolve()
assert root.name=='lin-c4-connected-branch-20261006T004500Z'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def publish(p,x):
    assert not p.exists(),str(p)
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.uncommitted-',dir=p.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(x,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);p.chmod(0o444)

b=read(root/'BINDINGS.json');guard=sha(root/'BINDINGS.json')
assert read(root/'FREEZE_RECORD.json')['guard']==guard
for group in ('sources','reviews','inputs'):
    for n,h in b[group].items():assert sha(root/n)==h,(group,n)
for n,h in {b['runtime']['executable']:b['runtime']['executable_sha256'],**b['runtime']['libraries']}.items():assert sha(Path(n))==h,n
p=read(root/'output/RESULT.json');t=read(root/'output/TERMINAL.json');a=read(root/'INDEPENDENT_AUDIT.json')
assert p['guard']==t['guard']==a['guard']==guard
assert a['overall']=='PASS' and a['inputs_unchanged'] is True
assert a['audit_source_sha256']==sha(root/'postrun_audit.py')
assert t['result_sha256']==a['graph_terminal_evidence_sha256']==sha(root/'output/RESULT.json')
label=a['scientific_classification']
if a['connected_interval_certified']:
    assert p['coverage']['full'] and label=='CONNECTED_SIGNED_C4_BRANCH_CERTIFIED'
else:assert label in ('PARTIAL_INTERVAL_C4_COVER','NO_CONNECTED_INTERVAL_CERTIFICATE')
live=[s.strip() for s in subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines() if str(root/'runner.py')+' ' in s]
assert not live,live
utc=datetime.now(timezone.utc).isoformat()
publish(root/'FINAL_LIVENESS.json',{'utc':utc,'matching_producer_processes':live,'scope':'This connected-branch packet only; unrelated research untouched.'})
artifacts=['output/RESULT.json','output/TERMINAL.json','INDEPENDENT_AUDIT.json','postrun_audit.py',
           'POSTRUN_REVIEW.md','RESULT_REPORT.md','FINAL_LIVENESS.json']
publish(root/'RESULT.json',{'status':'COMPLETE','classification':label,'guard':guard,'independently_accepted':True,
    'evidence_class':'COMPUTER_ASSISTED_UNIFORM_INITIAL_DATA_EXISTENCE_AND_UNIQUENESS',
    'connected_interval_certified':a['connected_interval_certified'],'requested_interval':b['config']['epsilon_interval'],
    'coverage':p['coverage'],'accepted_tiles':p['accepted_tiles'],'unresolved_tiles':p['unresolved_tiles'],
    'evaluated_nodes':len(p['completed']),'checkpoint_count':a['checkpoint_count'],'native_ball_count':a['native_ball_count'],
    'endpoint_identity':a['endpoint_identity'],'zero_local_reconciliation':a['zero_local_reconciliation'],
    'live_numerical_processes':live,'no_automatic_successor':True,'physical_evolution_launched':False,
    'limits':['Initial data with retained fourth-time wall compatibility only','No uniqueness outside the common correction box',
              'No all-order compatibility or hyperbolic spacetime-existence theorem','No time evolution, horizon or child-universe outcome'],
    'artifacts':{n:sha(root/n) for n in artifacts},'sealed_utc':utc})
entries=[]
for pth in sorted(root.rglob('*')):
    if not pth.is_file() or pth.name in ('GRAPH.lock','RUN.lock'):continue
    assert '__pycache__' not in pth.parts and '.uncommitted-' not in pth.name,str(pth)
    pth.chmod(0o444);entries.append({'path':str(pth.relative_to(root)),'bytes':pth.stat().st_size,'sha256':sha(pth)})
publish(root/'MANIFEST.json',{'classification':label,'entries':entries,'sealed_utc':utc,
    'exclusions':['MANIFEST.json self reference','Unlocked GRAPH.lock and RUN.lock']})
assert all(sha(root/e['path'])==e['sha256'] for e in read(root/'MANIFEST.json')['entries'])
print(json.dumps({'status':'SEALED','classification':label,'files':len(entries),'result_sha256':sha(root/'RESULT.json'),
                  'manifest_sha256':sha(root/'MANIFEST.json')},indent=2))
