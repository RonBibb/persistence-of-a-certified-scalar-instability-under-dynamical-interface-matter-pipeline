"""Seal this bounded research round after scientific review; no numerical solve."""
import datetime,hashlib,json,os
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
    p=Path(p)
    if p.exists():raise RuntimeError('refusing overwrite '+str(p))
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n');os.replace(temp,p)

if (HERE/'TERMINAL.json').exists():raise RuntimeError('round already sealed')
b=read(HERE/'SPECTRUM_R1_BINDINGS.json')
for p,h in b['source'].items():
    if sha(HERE/p)!=h:raise RuntimeError('source mismatch '+p)
for n,v in b['inputs'].items():
    if sha(HERE/v['path'])!=v['sha256']:raise RuntimeError('input mismatch '+n)
r2=read(HERE/'audit/R2_POSTRUN_AUDIT.json');frozen=read(HERE/'audit/r2_frozen/POSTRUN_AUDIT.json');branch=read(HERE/'audit/branch/RESULT.json')
science=read(HERE/'spectrum-r1/RESULT.json');terminal=read(HERE/'spectrum-r1/TERMINAL.json');cp=read(HERE/'spectrum-r1/CHECKPOINT.json')
if sha(HERE/'spectrum-r1/RESULT.json')!=terminal['result_sha256']:raise RuntimeError('spectrum terminal mismatch')
guard=sha(HERE/'SPECTRUM_R1_BINDINGS.json')
if not all(x['guard']==guard for x in [science,terminal,cp]):raise RuntimeError('spectrum guards mismatch')
for n,rec in cp['completed'].items():
    if sha(HERE/'spectrum-r1'/rec['receipt'])!=rec['receipt_sha256'] or sha(HERE/'spectrum-r1'/rec['arrays'])!=rec['arrays_sha256']:raise RuntimeError('case mismatch '+n)
review=read(HERE/'audit/INDEPENDENT_POSTRUN.json')
for p,h in review['source_and_input_sha256'].items():
    if sha(p)!=h:raise RuntimeError('reviewed source/input changed '+p)
if not review['inputs_unchanged']:raise RuntimeError('review detected input mutation')
if r2['status']!='PASS' or frozen['status']!='PASS' or branch['status']!='COMPLETE':raise RuntimeError('prerequisite audit not complete')
if science['status']!='UNRESOLVED' or science['completed_cases']!=2:raise RuntimeError('report/result disagreement')
if review['classification']!='INDEPENDENT_DIAGNOSIS_CONFIRMS_FROZEN_GATE_FAILURE':raise RuntimeError('independent diagnosis disagrees')
if not all(x['pass'] for x in review['conformal_replays']):raise RuntimeError('independent coordinate replay unresolved')
if not (HERE/'RESULT_REPORT.md').is_file():raise RuntimeError('final interpretation missing')
fine=read(HERE/'spectrum-r1/center_fine.json');coarse=read(HERE/'spectrum-r1/center_coarse.json')
result={'schema':'lin-r2-stability-round-v1','workflow_status':'COMPLETE','classification':'STATIC_NEIGHBORHOOD_VALIDATED_CENTRAL_MODE_REPRODUCED_PARAMETER_STABILITY_QUALIFICATION_INCOMPLETE','static_certificate':'RIGOROUS_WITHIN_DECLARED_REDUCED_STATIC_PROBLEM','branch_link':'NUMERICAL_ACTION_PROVENANCE_INVARIANTS_AND_FULL_PROFILE_AGREEMENT','central_growing_mode':'PREVIOUSLY_ACCEPTED_NUMERICAL_EVIDENCE_INDEPENDENTLY_REPRODUCED; NOT_RIGOROUSLY_ENCLOSED','new_nine_point_test_status':science['status'],'completed_cases':2,'uncomputed_cases':16,'central_coarse_accepted':coarse['accepted'],'central_fine_accepted':fine['accepted'],'central_mu':fine['mu'],'paired_mass_difference':abs(fine['mu']-coarse['mu']),'legacy_mass_difference':fine['central_comparison']['mass_difference'],'fine_metric_check':fine['independent_checks'][1]['background']['direct_metric'],'unchanged_metric_gate':1e-8,'result_sha256':terminal['result_sha256'],'independent_review_sha256':sha(HERE/'audit/INDEPENDENT_POSTRUN.json'),'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'no_rigorous_spectral_or_global_causal_claim':True,'manuscript_changed':False,'prior_packets_changed':False}
write(HERE/'RESULT.json',result)
manifest={'schema':'bounded-round-manifest-v1','files':{str(p.relative_to(HERE)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file() and p not in [HERE/'MANIFEST.json',HERE/'TERMINAL.json']}}
write(HERE/'MANIFEST.json',manifest)
write(HERE/'TERMINAL.json',{'workflow_status':'COMPLETE','scientific_test_status':'UNRESOLVED','classification':result['classification'],'result_sha256':sha(HERE/'RESULT.json'),'manifest_sha256':sha(HERE/'MANIFEST.json'),'completed_utc':result['ended_utc']})
for p in HERE.rglob('*'):
    if p.is_file():p.chmod(0o444)
print(json.dumps({'workflow_status':'COMPLETE','scientific_test_status':'UNRESOLVED','files':len(manifest['files']),'result_sha256':sha(HERE/'RESULT.json'),'manifest_sha256':sha(HERE/'MANIFEST.json')},sort_keys=True))
