#!/usr/bin/env python3
"""Mandatory absolute-deadline supervisor and exact recovery controls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parent
DEADLINE=datetime.datetime.fromisoformat('2026-10-19T16:03:42+00:00')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc)
def atomic(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp')
    with tmp.open('w') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
def invoke(script,out,count,tag,success=True):
    limit=(DEADLINE-now()).total_seconds()-2
    if limit<=0:raise TimeoutError('Absolute deadline; no child launched')
    cmd=[sys.executable,'-B',str(script),'--output',str(out),'--max-chunks',str(count)];logs=ROOT/'execution_logs';logs.mkdir(exist_ok=True)
    r={'tag':tag,'command':cmd,'started_utc':now().isoformat(),'absolute_deadline':DEADLINE.isoformat()}
    try:
        with (logs/(tag+'.stdout')).open('w') as so,(logs/(tag+'.stderr')).open('w') as se:
            cp=subprocess.run(cmd,stdout=so,stderr=se,timeout=limit,check=False)
        r.update(returncode=cp.returncode,finished_utc=now().isoformat(),status='PASS' if (cp.returncode==0)==success else 'FAILURE')
    except BaseException as exc:
        r.update(finished_utc=now().isoformat(),status='FAILURE',error=str(exc));atomic(logs/(tag+'.json'),r);raise
    atomic(logs/(tag+'.json'),r)
    if r['status']!='PASS':raise RuntimeError('Unexpected child result '+tag)
    if not success:
        f=json.loads((out/'FAILURE.json').read_text())
        if f['stage']['stage'] not in ['input_guard','checkpoint_integrity']:raise RuntimeError('Guard failed after science had started')
    return r

def controls():
    names=['recovery_base','certificate','recovery_replay','recovery_corrupt','recovery_changed_source']
    if any((ROOT/n).exists() for n in names) or (ROOT/'RECOVERY_CONTROL_RESULT.json').exists():raise RuntimeError('Require fresh outputs; never silently overwrite controls')
    base,prod,replay,bad,clone=[ROOT/n for n in names];script=ROOT/'certificate_runner.py'
    invoke(script,base,1,'01_initial_256_cell_checkpoint')
    for d in [prod,replay,bad]:shutil.copytree(base,d)
    invoke(script,prod,1,'02_fresh_resume_A')
    state=json.loads((prod/'LATEST.json').read_text());row=state['completed_chunks'][1]
    orphan=replay/row['path'];orphan.parent.mkdir(exist_ok=True);orphan.write_bytes(b'invalid uncommitted cell chunk');orphan.with_name(orphan.name+'.tmp').write_bytes(b'invalid partial write')
    invoke(script,replay,1,'03_fresh_resume_B_partial_orphan')
    if sha(prod/row['path'])!=sha(replay/row['path']):raise RuntimeError('Fresh-process continued cell chunk not byte exact')
    first=json.loads((bad/'LATEST.json').read_text())['completed_chunks'][0];(bad/first['path']).write_bytes(b'corrupt committed cell chunk')
    invoke(script,bad,1,'04_committed_chunk_corruption',False)
    clone.mkdir();shutil.copytree(ROOT/'inputs',clone/'inputs')
    adm=json.loads((ROOT/'NUMERICAL_ADMISSION.json').read_text())
    for n in adm['executable_bindings']:
        dest=clone/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dest)
    shutil.copy2(ROOT/'NUMERICAL_ADMISSION.json',clone/'NUMERICAL_ADMISSION.json')
    with (clone/'certificate_runner.py').open('a') as f:f.write('\n# Intentional changed-source rejection control.\n')
    invoke(clone/'certificate_runner.py',clone/'rejected_output',1,'05_changed_source_rejection',False)
    d={'utc':now().isoformat(),'status':'PASS','fresh_process_continuation_byte_equal':True,'continued_chunk':row['path'],'continued_chunk_sha256':sha(prod/row['path']),'continued_cells':256,'partial_orphan_never_accepted':True,'committed_chunk_corruption_rejected_before_cell':True,'changed_source_rejected_before_controls_or_background':True,'unique_primary_cells_completed':512,'total_physical_cell_evaluations_in_controls':768,'duplicate_physical_cells':256,'synthetic_control_runs':1,'main_output':'certificate','scientific_acceptance':'SEPARATE'}
    atomic(ROOT/'RECOVERY_CONTROL_RESULT.json',d);return d

def main():
    a=json.loads((ROOT/'NUMERICAL_ADMISSION.json').read_text())
    if not a['admitted']:raise RuntimeError('No independent prelaunch admission')
    for n,h in a['executable_bindings'].items():
        if sha(ROOT/n)!=h:raise RuntimeError('Changed admitted executable/plan/input')
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['controls','production']);args=ap.parse_args()
    if args.phase=='controls':r=controls()
    else:
        if json.loads((ROOT/'RECOVERY_CONTROL_RESULT.json').read_text())['status']!='PASS':raise RuntimeError('No passed recovery controls')
        invoke(ROOT/'certificate_runner.py',ROOT/'certificate',10000,'06_full_background_continuation');r=json.loads((ROOT/'certificate/RESULTS.json').read_text())
    print(json.dumps({k:v for k,v in r.items() if k not in ['whole_collar_state_bounds','whole_collar_coefficient_bounds','D_event_state_bounds','upper_wall_residual_rectangle_enclosures']},indent=2))
if __name__=='__main__':
    try:main()
    except BaseException as exc:
        atomic(ROOT/'HARNESS_FAILURE.json',{'utc':now().isoformat(),'type':type(exc).__name__,'error':str(exc),'scientific_classification':'OPERATIONAL_FAILURE_NOT_SIGN_RESULT'});raise
