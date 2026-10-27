#!/usr/bin/env python3
"""Read-only provenance/scope checker; never recomputes a scientific flow."""
from pathlib import Path
from fractions import Fraction
import datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    counts={};errors=[]
    def check(p,h,category):
        counts[category]=counts.get(category,0)+1
        if not p.is_file() or sha(p)!=h:errors.append({'category':category,'path':str(p)})
    inputs=json.loads((R/'INPUTS.json').read_text())
    for e in inputs['files']:
        check(Path(e['source']),e['sha256'],'original_sources');check(R/e['snapshot'],e['sha256'],'input_snapshots')
    for n in ['PRELAUNCH_CANDIDATE.json','PRELAUNCH_CANDIDATE_v2.json','action_review/fraction_verifier/FRACTION_VERIFIER_CANDIDATE_v1.json','AUDIT_CANDIDATE.json','TERMINAL_CANDIDATE.json']:
        if not (R/n).exists():errors.append({'missing_candidate':n});continue
        for p,h in json.loads((R/n).read_text())['files'].items():check(R/p,h,'candidate_bindings')
    admission=json.loads((R/'NUMERICAL_ADMISSION.json').read_text())
    if not admission['admitted'] or admission['scientific_acceptance']:errors.append({'invalid_interval_admission':True})
    check(R/admission['candidate'],admission['candidate_sha256'],'interval_admitted_candidate')
    for p,h in admission['executable_bindings'].items():check(R/p,h,'interval_executable_bindings')
    for p,h in admission['review_receipts'].items():
        check(R/p,h,'interval_prelaunch_receipts');a=json.loads((R/p).read_text())
        if a['candidate_sha256']!=admission['candidate_sha256'] or a.get('decision',a.get('verdict'))!='PASS_PRELAUNCH':errors.append({'invalid_interval_receipt':p})
    pointer=R/'certificate/LATEST.json';pt=json.loads(pointer.read_text());check(R/'certificate'/pt['path'],pt['sha256'],'immutable_interval_payload');state=json.loads((R/'certificate'/pt['path']).read_text())
    fp=hashlib.sha256(json.dumps(state['guard'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if fp!=state['fingerprint']:errors.append({'interval_fingerprint_mismatch':True})
    for p,h in state['guard']['files'].items():check(R/p,h,'interval_guard_files')
    check(R/'certificate/CONTROLS.json',state['control_sha256'],'synthetic_controls')
    last=0
    for ch in state['completed_chunks']:
        check(R/'certificate'/ch['path'],ch['sha256'],'interval_chunks')
        if ch['start']!=last or ch['end']<=last:errors.append({'chunk_inventory_mismatch':ch['path']})
        last=ch['end']
    if last!=state['completed_cells'] or last!=16365:errors.append({'interval_count_mismatch':last})
    numerical=json.loads((R/'certificate/RESULTS.json').read_text())
    if not numerical['complete'] or not all(numerical['gates'].values()) or not numerical['certified_K_at_least_half_S'] or numerical['fingerprint']!=fp:errors.append({'interval_gate_or_summary_mismatch':True})
    if Fraction(numerical['strict_Delta_upper_rational'])>=Fraction(1,2):errors.append({'nonpositive_certificate_margin':True})
    va=json.loads((R/'FRACTION_VERIFIER_ADMISSION.json').read_text());check(R/va['candidate'],va['candidate_sha256'],'fraction_admitted_candidate')
    if not va['admitted'] or va['expected_final_pointer_sha256']!=sha(pointer):errors.append({'fraction_admission_mismatch':True})
    for p,h in va['review_receipts'].items():
        check(R/p,h,'fraction_prelaunch_receipts');a=json.loads((R/p).read_text())
        if a['candidate_sha256']!=va['candidate_sha256'] or not a.get('decision',a.get('verdict','')).startswith('PASS'):errors.append({'invalid_fraction_receipt':p})
    vr=json.loads((R/'fraction_verification_v1/VERIFICATION_RESULT.json').read_text())
    if vr['status']!='PASS_EXACT_FRACTION_SAVED_CERTIFICATE_AND_COARSE_GATES' or not vr['complete'] or not vr['certified_half_S_gate'] or vr['verified_cells']!=16365 or vr['gates']!=numerical['gates']:errors.append({'fraction_verification_incomplete':True})
    check(pointer,vr['pointer_sha256'],'fraction_verified_pointer');check(R/'certificate'/pt['path'],vr['payload_sha256'],'fraction_verified_payload');check(R/'certificate/RESULTS.json',vr['producer_result_sha256'],'fraction_verified_result');check(R/'FRACTION_VERIFIER_ADMISSION.json',vr['admission_sha256'],'fraction_execution_admission')
    if vr['verifier_candidate_sha256']!=va['candidate_sha256']:errors.append({'fraction_candidate_mismatch':True})
    if vr['verified_chunks']!=state['completed_chunks']:errors.append({'fraction_chunk_inventory_mismatch':True})
    recovery=json.loads((R/'RECOVERY_CONTROL_RESULT.json').read_text())
    if recovery['status']!='PASS' or not recovery['immutable_full_state_corruption_rejected_before_cell']:errors.append({'recovery_control_failed':True})
    for n in ['certificate','recovery_replay']:check(R/n/recovery['continued_chunk'],recovery['continued_chunk_sha256'],'fresh_process_replay')
    for an,cn in [('AUDIT_ACCEPTANCE.json','AUDIT_CANDIDATE.json'),('TERMINAL_ACCEPTANCE.json','TERMINAL_CANDIDATE.json')]:
        if not (R/an).exists():errors.append({'missing_acceptance':an});continue
        a=json.loads((R/an).read_text());check(R/cn,a['candidate_sha256'],'accepted_candidates')
        if not a['accepted']:errors.append({'acceptance_not_pass':an})
        for p,h in a['review_receipts'].items():check(R/p,h,'accepted_review_receipts')
        if 'report_sha256' in a:check(R/'CONTINUUM_CERTIFICATE_RESULT.md',a['report_sha256'],'accepted_report')
    cp=subprocess.run([sys.executable,str(R/'proof_state.py'),'verify'],capture_output=True,text=True)
    if cp.returncode:errors.append({'proof_checkpoint_failure':cp.stderr})
    else:counts['proof_checkpoint_bound_artifacts']=json.loads(cp.stdout)['artifact_count']
    prior=Path(inputs['predecessor']);cp=subprocess.run([sys.executable,str(prior/'verify_integrity.py')],capture_output=True,text=True);inherited={}
    if cp.returncode:errors.append({'predecessor_failure':cp.stdout,'stderr':cp.stderr})
    else:
        inherited=json.loads(cp.stdout)
        if not inherited['pass']:errors.append({'predecessor_failure':inherited})
    if (R/'FINAL_MANIFEST.json').exists():
        m=json.loads((R/'FINAL_MANIFEST.json').read_text());excluded=set(m['excluded']);expected={e['path'] for e in m['files']}
        actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and str(p.relative_to(R)) not in excluded}
        if expected!=actual:errors.append({'sealed_inventory_difference':sorted(expected^actual)})
        for e in m['files']:check(R/e['path'],e['sha256'],'sealed_files')
        if (R/'FINAL_SEAL.json').exists():check(R/'FINAL_MANIFEST.json',json.loads((R/'FINAL_SEAL.json').read_text())['manifest_sha256'],'manifest_seal')
        else:errors.append({'missing':'FINAL_SEAL.json'})
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operation':'Read-only accepted-scope, documentary provenance and checkpoint verification; no new scientific computation','pass':not errors,'counts':counts,'inherited_verification':inherited,'mismatches':errors}
if __name__=='__main__':
    d=verify();print(json.dumps(d,indent=2));raise SystemExit(0 if d['pass'] else 1)
