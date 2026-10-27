"""Package an independently accepted terminal certificate; no physical kernels."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]).resolve()
assert root.name=='lin-c4-local-certificate-r1-20261005T221400Z'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,data):
    assert not p.exists(),str(p)
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.uncommitted-',dir=p.parent)
    with os.fdopen(fd,'w') as f:
        json.dump(data,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p);p.chmod(0o444)
binding=read(root/'BINDINGS.json');guard=sha(root/'BINDINGS.json')
assert guard=='233defdff9efcaef4e2c0b427af22776b85c94c233894a7da16e3a9936cf2cdc'
assert read(root/'FREEZE_RECORD.json')['binding_sha256']==guard
for group in ('source','reviews'):
    for name,digest in binding[group].items():assert sha(root/name)==digest,name
for record in binding['inputs'].values():assert sha(root/record['path'])==record['sha256'],record['path']
producer=read(root/'output/RESULT.json');terminal=read(root/'output/TERMINAL.json')
audit=read(root/'INDEPENDENT_AUDIT.json')
assert audit['status']=='PASS' and audit['qualitative_accepted'] is True and audit['radius_accepted'] is True
assert audit['guard']==producer['guard']==terminal['guard']==guard
assert terminal['result_sha256']==audit['result_sha256']==sha(root/'output/RESULT.json')
assert audit['auditor_source_sha256']==sha(root/'postrun_audit.py')
assert audit['independently_recomputed_classification']==producer['classification']==terminal['classification']
assert producer['status']==terminal['status']=='COMPLETE'
assert producer['qualitative_certificate'] is True and producer['quantitative_radius_certificate'] is True
assert audit['inputs_unchanged'] is True and audit['checkpoint_count']==96
assert audit['physical_kernel_imported_or_run'] is False
assert not (root/'output/FAILURE.json').exists()
processes=[line.strip() for line in subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines()
           if str(root/'runner.py')+' run ' in line]
assert not processes,processes
utc=datetime.now(timezone.utc).isoformat()
save(root/'FINAL_LIVENESS.json',{'checked_utc':utc,'scope':'This packet interval producer only',
     'matching_numerical_processes':processes,'terminal_status':'COMPLETE','guard':guard})
artifacts=['output/RESULT.json','output/TERMINAL.json','INDEPENDENT_AUDIT.json',
           'POSTRUN_REVIEW.md','postrun_audit.py','RESULT_REPORT.md','FINAL_LIVENESS.json']
result={'status':'COMPLETE','classification':producer['classification'],
        'evidence_class':'ANALYTIC_LOCAL_EXISTENCE_WITH_INTERVAL_COUPLED_JACOBIAN_AND_EXPLICIT_COMPLEX_MAJORANTS',
        'guard':guard,'independently_accepted':True,'qualitative_certificate':True,
        'quantitative_radius_certificate':True,'amplitude_radius':'2^-9216',
        'physical_run_seconds':producer['elapsed_seconds'],'validated_cells':audit['total_validated_cells'],
        'checkpoint_count':audit['checkpoint_count'],'sample_amplitudes_included':False,
        'scope':'Exact central final three-variable constraint family, physical-mode tangent, wall compatibility through fourth time order.',
        'limits':['No finite-amplitude sample inclusion','No all-order compatibility',
                  'No spacetime evolution existence or nonlinear fate theorem','No horizon or child-universe claim'],
        'technical_predecessor':'../lin-c4-local-certificate-20261005T214000Z',
        'evolution_launched':False,'successor_launched':False,'live_numerical_processes':[],
        'artifacts':{name:sha(root/name) for name in artifacts},'sealed_utc':utc}
save(root/'RESULT.json',result)
paths=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name!='RUN.lock']
assert not any('.uncommitted-' in p.name or '__pycache__' in p.parts for p in paths)
entries=[]
for p in paths:
    p.chmod(0o444)
    entries.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)})
save(root/'MANIFEST.json',{'classification':producer['classification'],'entries':entries,'sealed_utc':utc,
     'exclusions':['MANIFEST.json (self-reference)','output/RUN.lock (unlocked advisory-lock file)']})
assert all(sha(root/e['path'])==e['sha256'] for e in read(root/'MANIFEST.json')['entries'])
print(json.dumps({'status':'SEALED','files':len(entries),'guard':guard,
     'result_sha256':sha(root/'RESULT.json'),'manifest_sha256':sha(root/'MANIFEST.json'),
     'live_numerical_processes':processes},indent=2))
