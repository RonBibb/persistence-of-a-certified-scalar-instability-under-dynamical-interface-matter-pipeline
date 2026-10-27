"""Independent decision/integrity reader; no producer or legacy imports."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone
from math import factorial,comb
import hashlib,json,os
R=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def local(p):return Path(str(p).replace('/Users/ronbibb/','/media/psf/Home/',1))
def main():
    assert os.uname().sysname=='Linux' and os.sched_getaffinity(0)<={4,5}
    result=read(R/'RESULT.json');binding=read(R/'BINDINGS.json');p={x['id']:local(x['path']) for x in binding['inputs']}
    checks={}
    for x in binding['inputs']:checks['input:'+x['id']]=sha(local(x['path']))==x['sha256']
    for x in binding['sources']:checks['source:'+x['path']]=sha(R/x['path'])==x['sha256']
    checks['binding']=sha(R/'BINDINGS.json')==result['binding_sha256']
    D=Q(read(p['seed'])['D']);a=read(p['candidate100']);dense=read(p['dense100']);old=read(p['old_dense'])
    delta=list(map(Q,a['delta_c5_c7']))
    high=(delta[2]+delta[3])/Q(factorial(7))/D**8
    saved=Q(dense['correction'][15]);checks['degree15_nonzero']=high!=0 and saved!=0
    checks['degree15_formula_agrees']=abs(high-saved)<Q(1,10**40)
    midpoint=sum((v*((D/2)**j*((Q(1,2))**(j+1))/factorial(j))*(1 if side==0 else -1)
                  for v,(j,side) in zip(delta,((5,0),(5,1),(7,0),(7,1)))),Q(0))
    checks['direct_shape_midpoint']=midpoint==Q(result['membership_and_bounds']['delta_Phi_at_common_material_midpoint_exact'])
    checks['new_metric_not_gauge_only']=Q(a['delta_A0'])!=0
    checks['original_correction_degree_at_most_11']=len(old['correction'])<=12
    checks['new_degree_exceeds_old_ansatz']=len(dense['correction'])==16
    checks['material_bounds_not_assigned_to_C6']=result['membership_and_bounds']['C4_only_transfer']['applies_to_C6'] is False
    checks['missing_map_bound_not_invented']=result['membership_and_bounds']['C4_only_transfer']['rigorous_inverse_map_error_bound'] is None
    checks['classification']=result['classification']=='STATIC_INITIAL_BRIDGE_INCOMPLETE'
    checks['no_evolution_or_resolve']=result['evolution_steps']==result['new_root_solves']==result['new_metric_solves']==0
    for dps in (80,100):
        z=read(R/f'CHECKPOINT_p{dps}.json');checks[f'level{dps}_checks']=all(z['checks'].values())
        checks[f'level{dps}_positive_J']=Q(z['Jacobian_lower_exact'])>0
        for name,val in [('X_interval','X_Gauss16'),('proper_distance_interval','proper_distance_Gauss16')]:
            lo,hi=map(Q,z[name]['exact']);checks[f'level{dps}_{name}']=lo<=Q(z[val])<=hi
        for name,v in z['errors'].items():checks[f'level{dps}_error_{name}']=abs(Q(v))<=Q(1,10**20)
        ss=[Q(x['s']) for x in z['samples']];checks[f'level{dps}_ordered_inverse']=all(a<b for a,b in zip(ss,ss[1:]))
        checks[f'level{dps}_endpoint_inverse']=abs(ss[0])<=Q(1,10**20) and abs(ss[-1]-D)<=Q(1,10**20)
    for k,v in result['paired'].items():checks['paired_'+k]=abs(Q(v))<=Q(1,10**20)
    out={'utc':datetime.now(timezone.utc).isoformat(),'classification':'VERIFIED_STATIC_HALF_WITH_UNRESOLVED_CONTINUUM_BRIDGE',
      'all_passed':all(checks.values()),'checks':checks,'result_sha256':sha(R/'RESULT.json'),
      'independence':'Separate exact-rational shape/decision and integrity implementation; not a second integration or an independent C6 existence theorem.',
      'partner_scientific_review':'Pending exchanged-packet audit by initial-data owner.'}
    tmp=R/'AUDIT.json.partial'
    with tmp.open('w') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.replace(tmp,R/'AUDIT.json')
    print(json.dumps({'all_passed':out['all_passed'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
    assert out['all_passed']
if __name__=='__main__':main()
