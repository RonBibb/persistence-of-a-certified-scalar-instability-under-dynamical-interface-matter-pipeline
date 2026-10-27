"""Linux-only terminal evidence audit; no underlying scientific checker replay."""
import sys
sys.dont_write_bytecode=True
import os,fcntl,subprocess,json,hashlib,signal,resource,platform,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert sys.platform=='linux'
    signal.alarm(180);resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    L=Path('/tmp/research-20261012-astra-medium');handles=[]
    def take(p):
        f=p.open('a+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(f);return f
    gate=take(L/'admission.lock');assert not any('hold' in p.name.lower() for p in L.iterdir());take(L/'line-L001.lock')
    busy=set()
    for row in subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'],text=True).splitlines()[1:]:
        a=row.split(None,3)
        if len(a)!=4 or int(a[0])==os.getpid():continue
        science=any(s in a[2].lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
        system=any(s in a[3] for s in ('unattended-upgrade','update-manager','check-new-release'))
        if (science and not system) or (float(a[1])>20 and not a[3].startswith('[')):
            try:busy.update(os.sched_getaffinity(int(a[0])))
            except ProcessLookupError:pass
    free=[]
    for c in sorted(os.sched_getaffinity(0)):
        if not (L/f'cpu-{c}.lock').exists():continue
        try:f=take(L/f'cpu-{c}.lock')
        except BlockingIOError:busy.add(c);continue
        if c in busy:f.close()
        else:free.append((c,f))
    assert free and len(busy|{free[0][0]})<=2
    cpu=free[0][0];os.sched_setaffinity(0,{cpu})
    for _,f in free[1:]:f.close()
    gate.close()
    adm=read(HERE/'FINAL_THREE_ADMISSION.json');assert adm['admitted']
    assert str(Path(sys.executable).resolve())==adm['executable_realpath']
    for p,h in adm['sources'].items():assert sha(p)==h,p
    report={}
    for name in ('bridge','exact_consequences','mass_audit'):
        p=ROOT/name;f=read(p/'FROZEN.json');a=read(p/'ADMISSION.json');ex=read(p/'run_EXECUTION.json')
        assert a['admitted'] and sha(p/'FROZEN.json')==a['frozen_sha256']
        for path,h in f['files'].items():assert sha(path)==h,path
        assert ex['exit_code']==0 and ex['child_reaped'] and 'integrity_error' not in ex
        assert ex['post_frozen_files_verified']==len(f['files'])
        assert not list(p.rglob('*FAILURE*.json'))
        assert ex['executable_sha256']==sha(f['executable_realpath'])
        report[name]={'bindings':len(f['files']),'reaped':True,'exit_code':0,'wall_seconds':ex['wall_seconds']}
    p=ROOT/'bridge';r=read(p/'output/RESULT.json');ins=read(p/'INPUTS.json')
    assert r['classification']=='EXACT_BACKGROUND_TO_CURRENT_AB_BRIDGE_VERIFIED'
    assert len(r['gates'])>=30 and all(v is True for v in r['gates'].values())
    assert r['inputs']==ins and r['current_boundary_action_requires_separate_analytic_bridge']
    for k,v in ins.items():assert sha(v['path'])==v['sha256'],k
    assert set(r['details']['primary_exact_model'])==set(r['details']['independent_exact_model'])=={'gamma','m2','v0','v1','lambda_a','lambda_b'}
    assert r['details']['primary_exact_model']==r['details']['independent_exact_model']
    assert len(r['details']['A'])==len(r['details']['D'])==2
    report['bridge'].update(gate_count=len(r['gates']),classification=r['classification'],root_existence_reproved=False)
    p=ROOT/'exact_consequences';r=read(p/'RESULT.json');f=read(p/'FROZEN.json')
    assert r['classification']=='PASS_COMPLETE_SAVED_CONSEQUENCES_LINUX' and r['ode_executed'] is False
    assert [c['case'] for c in r['cases']]==['curvature','openness','stiffness']
    for c in r['cases']:
        n=c['case'];o=read(p/(n+'_producer_OUTPUT.json'));assert o==read(c['historical_result'])
        for role in ('producer','independent'):
            e=read(p/(n+'_'+role+'_EXECUTION.json'));parsed=read(p/(n+'_'+role+'_OUTPUT.json'))
            assert e['returncode']==0 and e['stderr']=='' and json.loads(e['stdout'])==parsed
            assert e['source'] in f['files'] and sha(e['source'])==f['files'][e['source']]
            if role=='independent':assert parsed['status']=='PASS'
    before=read(p/'RUNTIME_START.json');after=read(p/'RUNTIME_END.json')
    assert before['runtime_files']==after['runtime_files']==f['runtime_files'] and after['all_file_hashes_rechecked']
    report['exact_consequences'].update(classification=r['classification'],complete_programs=6,complete_json_reproductions=3)
    p=ROOT/'mass_audit';f=read(p/'FROZEN.json');r=read(p/'RESULT.json');receipt=read(p/'output/AUDITOR_STDOUT.json');old=read(Path(f['packet'])/'INDEPENDENT_AUDIT.json')
    assert r['status']=='CURRENT_LINUX_HISTORICAL_MASS_AUDITOR_VERIFIED' and r['new_ode_solves']==0
    assert r['auditor_stdout_sha256']==sha(p/'output/AUDITOR_STDOUT.json')
    assert receipt['audit_pass'] and receipt['endpoint_certificate'] and receipt['uniform_separation_certificate']
    assert receipt['checkpoint_count']==288 and receipt['native_roundtrips_checked']==11808 and receipt['runtime_libraries_verified']==42
    assert receipt['new_physical_integration_performed'] is False
    for k in ('result_sha256','terminal_sha256','audit_source_sha256','guard','exact_signs'):assert receipt[k]==old[k],k
    assert receipt['audit_source_sha256']==r['original_auditor_sha256']==sha(Path(f['packet'])/'postrun_audit.py')
    before=read(p/'RUNTIME_BEFORE.json');after=read(p/'RUNTIME_AFTER.json');ex=read(p/'run_EXECUTION.json')
    for k in ('pid','executable_realpath','executable_sha256','affinity','python','platform'):assert before[k]==after[k],k
    assert before['pid']==ex['child_pid'] and before['affinity']==[ex['cpu']]
    canonical={str(Path(path).resolve()):h for path,h in f['files'].items()};unbound=[];late=[]
    for phase,v in (('before',before),('after',after)):
        for k,item in v['modules'].items():
            path=str(Path(item['path']).resolve());assert sha(path)==item['sha256']
            if canonical.get(path)!=item['sha256']:unbound.append([phase,'module',k,path])
        for path,h in v['mapped_files'].items():
            assert sha(path)==h
            if canonical.get(str(Path(path).resolve()))!=h:unbound.append([phase,'mapped',path])
    for section in ('modules','mapped_files'):
        for k in set(before[section])&set(after[section]):assert before[section][k]==after[section][k],k
        late += [[section,k] for k in set(after[section])-set(before[section])]
    report['mass_audit'].update(classification=r['status'],checkpoints=288,native_roundtrips=11808,historical_runtime_libraries=42,unbound_runtime_records=unbound,late_imports=late)
    for path,h in adm['sources'].items():assert sha(path)==h,path
    result={'classification':'ACCEPT_ALL_THREE' if not unbound else 'MASS_RUNTIME_COVERAGE_REQUIRES_REVIEW','packets':report,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),'executable':str(Path(sys.executable).resolve()),'executable_sha256':sha(sys.executable),'admission_sha256':sha(HERE/'FINAL_THREE_ADMISSION.json'),'source_sha256':sha(__file__),'scope':'Terminal evidence audit only; no rerun of scientific arithmetic or IVP; historical root and native arithmetic premises remain inherited.'}
    for f in handles:f.close()
    signal.alarm(0);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
