#!/usr/bin/env python3
"""Read-only P407 late-state bulk/wall diagnostic; no evolution or correction."""
from pathlib import Path
import datetime, hashlib, importlib, json, os, sys, time
import numpy as np

ROOT=Path(__file__).resolve().parent
CUTOFF=datetime.datetime(2026,10,1,11,34,37,tzinfo=datetime.timezone.utc)
P407=Path('/home/parallels/research-runs/protocol407-r2-qualified-h-g10-eh-future-extension-2026-09-09')
P400=Path('/home/parallels/research-runs/protocol400-same-lineage-g10-future-extension-2026-09-08')
P395=Path('/home/parallels/research-runs/protocol395-same-lineage-g10-future-archive-2026-09-08')
ACADEMIC=Path('/home/parallels/protocol240-runtime/Academic2')
VISUAL=Path('/home/parallels/protocol240-runtime/Visual4')
LEGACY=ACADEMIC/'brane-horizon-phase-structure'
CANDIDATE=Path('/home/parallels/research-runs/protocol404-r4-bound-current-project-source-2026-09-09')
BRANCH1=Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/01-horizon-core/boundary-compatibility-20261001T093524Z')
P9=BRANCH1.parent/'constraint-audit-20261001T003447Z'
OUT=ROOT/'o4r1-output'
RIND=(35,36); ZIND=(0,1,2,4,124,126,127,128)
STATES={
 512:(P400/'candidate-output/evolution/G10_future_step0512.npz',0.008),
 1152:(Path('/media/psf/T7/research-runs/protocol407-r2-qualified-h-g10-eh-future-extension-2026-09-09/units/evolution-block-0004.npz'),0.018),
 1792:(Path('/media/psf/T7/research-runs/protocol407-r2-qualified-h-g10-eh-future-extension-2026-09-09/units/evolution-block-0008.npz'),0.028),
}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def plain(v):
 if isinstance(v,np.ndarray):
  return v.astype(float).tolist() if v.dtype.kind=='f' else v.tolist()
 if isinstance(v,np.floating): return float(v)
 if isinstance(v,np.integer): return int(v)
 if isinstance(v,np.bool_): return bool(v)
 raise TypeError(type(v).__name__)
def atomic_json(path,value):
 path=Path(path); tmp=path.with_name('.'+path.name+'.tmp')
 if path.exists() or tmp.exists(): raise RuntimeError('refusing overwrite '+str(path))
 with tmp.open('x') as f:
  json.dump(value,f,indent=2,sort_keys=True,default=plain,allow_nan=False); f.flush(); os.fsync(f.fileno())
 os.replace(tmp,path); fd=os.open(path.parent,os.O_RDONLY); os.fsync(fd); os.close(fd)
def reference(path):
 path=Path(path); return {'path':str(path),'sha256':sha(path),'byte_count':path.stat().st_size}

def load_contract():
 c=json.loads((ROOT/'O4_CONTRACT.json').read_text())
 if c['schema']!='o4-p407-late-compatibility-contract-v1': raise RuntimeError('contract schema')
 if sha(P407/'authority/freeze_record.json')!=c['p407_authority_sha256']: raise RuntimeError('P407 authority changed')
 for item in c['bound_files']:
  p=Path(item['path'])
  if not p.is_file() or sha(p)!=item['sha256']: raise RuntimeError('bound file changed: '+str(p))
 return c

def raw_acceleration(native,einstein,q,first,second,radius,H,Hd,mass):
 jets=native.regular_so3_perturbation_jets(float(radius),q,first,second)
 solved=einstein.solve_reduced_einstein_two_scalar_acceleration(
  jets['metric'],jets['metric_first'],jets['metric_second'],jets['phi'],jets['phi_first'],jets['phi_second'],
  jets['chi'],jets['chi_first'],jets['chi_second'],H,Hd,mass_squared=float(mass),potential_offset=-6.,kappa5_squared=1.)
 return native._pack_acceleration(solved['metric_acceleration'],solved['phi_acceleration'],solved['chi_acceleration'],float(radius))

def main():
 if datetime.datetime.now(datetime.timezone.utc)>=CUTOFF: raise RuntimeError('immutable no-new-test cutoff')
 contract=load_contract(); OUT.mkdir(exist_ok=False)
 atomic_json(OUT/'START.json',{'started_utc':now(),'contract':reference(ROOT/'O4_CONTRACT.json'),'cutoff_utc':CUTOFF.isoformat()})
 sys.path.insert(0,str(BRANCH1/'code')); import common_acceleration as ca
 sys.path.insert(0,str(P407)); import protocol404_kernel_adapter as adapter
 authority=json.loads((P407/'authority/freeze_record.json').read_text())
 p400,context,_,_=adapter.load_context(P400,P395,ACADEMIC,VISUAL,LEGACY,CANDIDATE,authority)
 candidate=adapter.candidate_acceleration_module(CANDIDATE,LEGACY,authority)
 bundle=context['bundles']['G10']; switch=adapter.KernelSwitch(bundle,candidate); switch.select('qualified-batched')
 rhs=bundle.rhs_by_mode[adapter.MODE]
 forcing_names=('tangential_tracefree_wall_forcing','tangential_flux_wall_forcing','physical_metric_wall_forcing','scalar_wall_forcing')
 if rhs.boundary_closure_mode!='legacy_wall_axis_outer' or not rhs.batched_open_bulk or any(getattr(rhs,n) is not None for n in forcing_names):
  raise RuntimeError('active kernel contract differs')
 einstein=sys.modules['bhps.linearized_gh_einstein_scalar']; z=bundle.geometry['z']; r=bundle.geometry['r']; bg=bundle.geometry['background']; mass=bundle.geometry['mass_squared']
 D=candidate.derivative_matrix(np.asarray(z,float),1,7); D=D.toarray() if hasattr(D,'toarray') else np.asarray(D)
 results=[]; arrays={}
 for step,(path,tval) in STATES.items():
  with np.load(path,allow_pickle=False) as f: state={k:np.ascontiguousarray(f[k]) for k in ('q','v','source','memory')}
  expected=contract['states'][str(step)]['array_sha256']
  for k,a in state.items():
   if hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()!=expected[k]: raise RuntimeError(f'state {step} {k} differs')
  stage=context['runner'].reconstruct_driver_stage(bundle,adapter.MODE,float(tval),tuple(state[k] for k in ('q','v','source','memory')),capture=True)
  if not stage['finite']: raise RuntimeError(f'nonfinite stage {step}')
  q,v,a,H,Ht,Htt=(stage[k] for k in ('q','v','acceleration','source','source_time','source_second_time'))
  first,second=candidate.reduced_state_jets(q,v,z,r,7); gauge=candidate.StageRegularGaugeSource(H,Ht,z,r,7)
  wall=ca.wall_rows(q,v,a,H,Ht,Htt,z,r,bg,D)
  arrays[f'{step}_acceleration']=a; arrays[f'{step}_source_time']=Ht; arrays[f'{step}_source_second_time']=Htt
  points=[]
  for i in ZIND:
   for j in RIND:
    hs,hd=gauge.at(i,j,float(tval)); sec=second[:,:,i,j].copy(); sec[0,0]=a[i,j]
    raw=raw_acceleration(candidate,einstein,q[i,j],first[:,i,j],sec,r[j],hs,hd,mass)
    saved=ca.bulk_point(q[i,j],first[:,i,j],sec,a[i,j],r[j],hs,hd,candidate,einstein)
    counter=ca.bulk_point(q[i,j],first[:,i,j],sec,raw,r[j],hs,hd,candidate,einstein)
    def view(x):
     t=float(x['Tll']); return {'Tll':t,'projections':x['projections'],'normalized_projections':x['projections']/t if t else None,'scalar_equations':x['scalar_equations'],'reduced9_max':float(np.max(np.abs(x['reduced9']))),'physical_E_max':float(np.max(np.abs(x['physical_Einstein']))),'gauge_constraint':x['gauge_constraint'],'tensor_closure_max':float(np.max(np.abs(x['tensor_closure'])))}
    points.append({'i':i,'j':j,'z':float(z[i]),'r':float(r[j]),'saved':view(saved),'raw_bulk_counterfactual':view(counter),'saved_minus_raw_acceleration_max':float(np.max(np.abs(a[i,j]-raw)))})
  wall_summary={}
  for wi,name in enumerate(('lower','upper')):
   vals=[]
   for j in RIND:
    i=0 if wi==0 else len(z)-1; hs,hd=gauge.at(i,j,float(tval)); sec=second[:,:,i,j].copy(); sec[0,0]=a[i,j]
    saved=ca.bulk_point(q[i,j],first[:,i,j],sec,a[i,j],r[j],hs,hd,candidate,einstein); t=float(saved['Tll'])
    vals.append({'j':j,'r':float(r[j]),'E_ll':float(saved['projections'][3]),'T_ll':t,'E_ll_over_T_ll':float(saved['projections'][3]/t) if t else None,'chi_wave_residual':float(saved['scalar_equations'][1]),'wall_raw2':wall['raw2'][wi,j],'wall_normalized2':wall['normalized2'][wi,j]})
   wall_summary[name]=vals
  results.append({'h_step':step,'time':tval,'state_payload':reference(path),'stage_diagnostic_finite':bool(stage['diagnostic']['finite']),'wall':wall_summary,'points':points})
  atomic_json(OUT/f'CHECKPOINT_H{step}.json',results[-1])
 np.savez_compressed(OUT/'arrays.npz',**arrays)
 record={'schema':'o4-p407-late-compatibility-result-v1','classification':'MEASURED-P407-LATE-COMPATIBILITY__INTERPRETATION-REQUIRED','started_utc':json.loads((OUT/'START.json').read_text())['started_utc'],'completed_utc':now(),'contract':reference(ROOT/'O4_CONTRACT.json'),'active_kernel':{'kind':'qualified-batched','boundary_closure_mode':rhs.boundary_closure_mode,'batched_open_bulk':bool(rhs.batched_open_bulk),'optional_wall_forcings':{n:getattr(rhs,n) for n in forcing_names}},'results':results,'arrays':reference(OUT/'arrays.npz'),'scope':'Fixed-state diagnostic. Raw bulk acceleration is counterfactual. No evolution, correction, state mutation, continuum inference, or event-horizon inference.'}
 atomic_json(OUT/'O4_RESULT.json',record); print(json.dumps({'classification':record['classification'],'result':str(OUT/'O4_RESULT.json')},sort_keys=True))

if __name__=='__main__': main()
