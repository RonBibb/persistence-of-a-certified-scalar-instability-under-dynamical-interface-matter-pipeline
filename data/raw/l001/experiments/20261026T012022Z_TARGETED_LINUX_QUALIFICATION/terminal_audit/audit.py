"""Linux-only terminal coverage/provenance audit. Read-only; stdout JSON."""
import sys
sys.dont_write_bytecode=True
import datetime,fcntl,gzip,hashlib,json,os,platform,resource,signal,subprocess
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
KIN=ROOT.parent/'kinetic'
RESEARCH=Path('/media/psf/Home/Research')
OLD=RESEARCH/'papers/ab-bridge-feasibility/20261019_continuum_kinetic_143342'
def need(x,msg):
    if not x:raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    need(sys.platform=='linux','LINUX_ONLY')
    signal.alarm(180);resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    locks=Path('/tmp/research-20261012-astra-medium')
    gate=(locks/'admission.lock').open('r+');fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
    need(not any('hold' in x.name.lower() for x in locks.iterdir()),'HOLD')
    line=(locks/'line-L001.lock').open('a+');fcntl.flock(line,fcntl.LOCK_EX|fcntl.LOCK_NB)
    free=[];busy=set()
    for row in subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'],text=True).splitlines()[1:]:
        fields=row.split(None,3)
        if len(fields)!=4:continue
        pid,pct,comm,args=fields
        if int(pid)==os.getpid():continue
        science=any(s in comm.lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
        system=any(s in args for s in ('unattended-upgrade','update-manager','check-new-release'))
        if (science and not system) or (float(pct)>20 and not args.startswith('[')):
            try:busy.update(os.sched_getaffinity(int(pid)))
            except ProcessLookupError:pass
    for cpu in sorted(os.sched_getaffinity(0)):
        p=locks/f'cpu-{cpu}.lock'
        if not p.exists():continue
        f=p.open('r+')
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:f.close();busy.add(cpu);continue
        if cpu in busy:f.close()
        else:free.append((cpu,f))
    need(bool(free) and len(busy|{free[0][0]})<=2,'AGGREGATE_CPU_CAP')
    cpu,lease=free[0]
    for _,f in free[1:]:f.close()
    os.sched_setaffinity(0,{cpu});gate.close()
    adm=read(ROOT/'ADMISSION.json')
    need(adm['admitted'] is True,'ADMISSION')
    need(str(Path(sys.executable).resolve())==adm['executable_realpath'],'AUDITOR_INTERPRETER')
    for p,h in adm['sources'].items():need(sha(p)==h,'AUDIT_BINDING:'+p)
    kadmin=read(KIN/'ADMISSION.json');frozen=read(KIN/'FROZEN.json')
    need(kadmin['admitted'] is True and sha(KIN/'FROZEN.json')==kadmin['frozen_sha256'],'KINETIC_ADMISSION')
    for p,h in frozen['files'].items():need(sha(p)==h,'KINETIC_FROZEN:'+p)
    execution=read(KIN/'run_EXECUTION.json');result=read(KIN/'RESULT.json')
    before=read(KIN/'RUNTIME_BEFORE.json');after=read(KIN/'RUNTIME_AFTER.json')
    check=read(KIN/'output/VERIFICATION_RESULT.json')
    need(execution['exit_code']==0 and execution['child_reaped'] is True,'EXECUTION')
    need(execution.get('post_frozen_files_verified')==len(frozen['files']) and 'integrity_error' not in execution,'POST_BINDINGS')
    need(not list(KIN.glob('*FAILURE*.json')) and not list((KIN/'output').glob('*FAILURE*.json')),'FAILURE_PRESENT')
    need(result['status']=='PASS_COMPLETE_LINUX_KINETIC_WITNESS' and result['new_ode_solves']==0,'RESULT')
    need(check['status']=='PASS_EXACT_FRACTION_SAVED_CERTIFICATE_AND_COARSE_GATES','CHECKER_STATUS')
    need(check['complete'] is True and check['verified_cells']==check['total_cells']==result['verified_cells']==16365,'COMPLETE_COVERAGE')
    need(all(check['gates'].values()) and check['certified_half_S_gate'] is True and check['new_background_or_response_solves']==0,'CHECKER_GATES')
    need(result['verifier_result_sha256']==sha(KIN/'output/VERIFICATION_RESULT.json'),'RESULT_BINDING')
    source=OLD/'action_review/fraction_verifier/verify_saved_certificate.py'
    need(result['historical_checker_sha256']==sha(source),'UNCHANGED_CHECKER')
    for key in ('pid','executable','executable_sha256','affinity','python','platform'):
        need(before[key]==after[key],'RUNTIME_CHANGED:'+key)
    need(before['pid']==execution['child_pid'] and before['affinity']==[execution['cpu']],'WORKER_IDENTITY')
    need(str(Path(before['executable']).resolve())==frozen['executable_realpath'],'WORKER_INTERPRETER')
    need(before['executable_sha256']==execution['executable_sha256']==frozen['files'][frozen['executable_realpath']],'EXECUTABLE_HASH')
    canonical={str(Path(p).resolve()):h for p,h in frozen['files'].items()}
    unbound=[];late=[]
    for name,record in (('before',before),('after',after)):
        for module,item in record['modules'].items():
            p=str(Path(item['path']).resolve());h=item['sha256']
            if canonical.get(p)!=h:unbound.append([name,'module',module,p,h])
            need(sha(p)==h,'CURRENT_MODULE:'+p)
        for p,h in record['mapped_files'].items():
            resolved=str(Path(p).resolve())
            if canonical.get(resolved)!=h:unbound.append([name,'mapped',resolved,h])
            need(sha(p)==h,'CURRENT_MAPPED:'+p)
    for section in ('modules','mapped_files'):
        for name in set(before[section])&set(after[section]):need(before[section][name]==after[section][name],'COMMON_RUNTIME_CHANGED:'+name)
        late += [[section,name] for name in set(after[section])-set(before[section])]
    pointer=read(OLD/'certificate/LATEST.json')
    need(sha(OLD/'certificate/LATEST.json')==check['pointer_sha256'],'POINTER')
    payload=OLD/'certificate'/pointer['path'];state=read(payload)
    need(sha(payload)==pointer['sha256']==check['payload_sha256'],'PAYLOAD')
    need(sha(OLD/'certificate/RESULTS.json')==check['producer_result_sha256'],'PRODUCER_RESULT')
    need(len(check['verified_chunks'])==len(state['completed_chunks']),'CHUNK_COUNT')
    index=0;t=Q(0);Dhi=Q(state['D_hi']);step=Q(1,8192)
    for c,v in zip(state['completed_chunks'],check['verified_chunks']):
        need(c['path']==v['path'] and c['sha256']==v['sha256'] and c['start']==v['start']==index,'CHUNK_IDENTITY')
        p=OLD/'certificate'/c['path'];need(sha(p)==c['sha256'],'CHUNK_HASH')
        cells=json.loads(gzip.decompress(p.read_bytes()))
        need(len(cells)==c['end']-c['start'] and len(cells)>0,'CHUNK_LENGTH')
        for cell in cells:
            h=Q(cell['h']);need(cell['index']==index and Q(cell['s'])==t and h==min(step,Dhi-t) and h>0,'CELL_COVER')
            index+=1;t+=h
        need(index==v['end']==c['end'],'CHUNK_END')
    need(index==state['completed_cells']==state['total_cells']==16365 and t==Dhi==Q(state['s']),'COMPLETE_DOMAIN')
    oldcheck=read(OLD/'fraction_verification_v1/VERIFICATION_RESULT.json')
    for key in ('status','complete','gates','verified_cells','total_cells','verified_chunks','pointer_sha256','payload_sha256','producer_result_sha256','certified_half_S_gate','new_background_or_response_solves'):
        need(check[key]==oldcheck[key],'HISTORICAL_MATH_RESULT:'+key)
    for p,h in adm['sources'].items():need(sha(p)==h,'FINAL_AUDIT_BINDING:'+p)
    classification='ACCEPT_COMPLETE_LINUX_KINETIC_WITNESS' if not unbound else 'RUNTIME_COVERAGE_UNRESOLVED'
    report={'classification':classification,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'audit_cpu':cpu,
        'auditor_pid':os.getpid(),'auditor_python':sys.version,'auditor_executable':str(Path(sys.executable).resolve()),'auditor_executable_sha256':sha(sys.executable),'auditor_affinity':sorted(os.sched_getaffinity(0)),
        'auditor_source_sha256':sha(__file__),'audit_admission_sha256':sha(ROOT/'ADMISSION.json'),'audit_bindings_checked':len(adm['sources']),
        'kinetic_frozen_files_checked':len(frozen['files']),'verified_cell_inventory':index,'chunk_count':len(check['verified_chunks']),
        'complete_checker_pass':True,'historical_mathematical_fields_equal':True,'runtime_common_identities_equal':True,'late_imports':late,'unbound_runtime_records':unbound,
        'worker_reaped':True,'new_ode_solves':0,'induction_reexecuted_by_terminal_auditor':False,
        'scope':'Terminal provenance/coverage review of complete independent historical checker; root existence remains inherited.'}
    lease.close();line.close();signal.alarm(0);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
