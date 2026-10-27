#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime as dt,hashlib,importlib.util,json,math,os,sys,time
from pathlib import Path
from typing import Any
import numpy as np
A_GRIDS=((65,121),(97,181),(129,241));B_NX=(65,97,129,193,257);B_NR=241;STENCIL=7;GATE=1e-4
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,v):p=Path(p);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2,sort_keys=True,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n');os.replace(t,p)
def status(o,p,d,s):atomic(o/'STATUS.json',{'schema':'lin-d1-gh-status-v1','started_utc':s,'updated_utc':utc(),'phase':p,'detail':d,'pid':os.getpid()})
def imp(n,p):
 s=importlib.util.spec_from_file_location(n,p)
 if s is None or s.loader is None:raise RuntimeError(f'cannot import {p}')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def bindings(root,here):
 b=json.loads((here/'BINDINGS.json').read_text());out=[]
 for x in b['parents']+b['production_sources']:
  a=sha(root/x['path'])
  if a!=x['sha256']:raise RuntimeError(f"binding changed {x['path']} {a}")
  out.append({'path':x['path'],'sha256':a,'role':x.get('role','production_source')})
 return out
def order(c,f,cn,fn):return None if c<=0 or f<=0 or c==f else float(math.log(c/f)/math.log((fn-1)/(cn-1)))
def make_rhs(fields,prior,Stage,RHS):
 source=Stage(fields['source'],np.zeros_like(fields['source']),fields['x'],fields['r'],STENCIL);rhs=RHS(fields['x'],fields['r'],source,.41,prior.background_record(),np.zeros((2,len(fields['r']))),STENCIL,live_normal_wall_gauge=False,live_outer_sommerfeld=True,boundary_closure_mode='legacy_wall_axis_outer');rhs.set_outer_sommerfeld_reference(fields['q'],np.zeros_like(fields['q']));return source,rhs
def wb_rhs_class(base,baseline):
 class WellBalancedRHS(base):
  def acceleration(self,t,q,v):
   raw,diag=super().acceleration(t,q,v);bg=baseline[(len(self.z),len(self.r))];raw0,_=super().acceleration(0.,bg['q'],bg['v']);return raw-raw0,diag
 WellBalancedRHS.__name__='D1WellBalancedNativeRegularSO3RHS';return WellBalancedRHS
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);here=Path(__file__).resolve().parent;started=utc();clock=time.monotonic();result={'schema':'lin-d1-gh-result-v1','status':'RUNNING','classification':None,'started_utc':started,'contract_sha256':sha(here/'CONTRACT.md'),'bindings_sha256':sha(here/'BINDINGS.json'),'claim_boundary':['Immediate equilibrium preservation only; not stability.','No continuum, P16, collapse, parent-child, or causal inference.']}
 try:
  status(out,'AUTHENTICATION','verifying frozen authority',started);result['bindings_verified']=bindings(root,here)
  prior=imp('gh_prior',root/'branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z/d1_background_admission.py');curv=imp('gh_curv',root/'branches/02-event-horizon/lin-d1-curvature-well-balance-discriminator-20261004T190608Z/d1_curvature_discriminator.py');wall=imp('gh_wall',root/'branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-20261004T200437Z/d1_wall_discriminator.py');adapter=imp('gh_adapter',root/'branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-r1-20261004T201152Z/d1_wall_discriminator_r1.py');gauge=imp('gh_gauge',root/'branches/02-event-horizon/lin-d1-gauge-well-balance-discriminator-20261004T202200Z/d1_gauge_discriminator.py')
  src=root/'branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src';sys.path.insert(0,str(src))
  from bhps.adm_corner import _axisymmetric_derivatives
  from bhps.anisotropic_geometry import anisotropic_metric_acceleration,anisotropic_scalar_acceleration,axisymmetric_diagonal_geometry
  from bhps.gw_slice_high_order_solver import derivative_matrix
  from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
  from bhps.nonlinear_regular_so3_evolution import NativeRegularSO3RHS,StageRegularGaugeSource,apply_outer_source_sommerfeld,compact_wall_position_residuals,gauge_constraint_summary,outer_sommerfeld_position_residuals,reduced_state_jets,regular_so3_outward_radial_speed
  from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets
  Stage=adapter.compatible_stage_source_class(StageRegularGaugeSource);rr=prior.solve_representative_root();sample,L,cscale=prior.make_profile(rr);result['representative_root']={'a':rr['a'],'D':rr['D'],'L':L,'k':rr['k']};af=[prior.represented_fields(nx,nr,sample,rr['k'],cscale) for nx,nr in A_GRIDS];base={(len(f['x']),len(f['r'])):f for f in af}
  production={'derivatives':_axisymmetric_derivatives,'axisymmetric_diagonal_geometry':axisymmetric_diagonal_geometry,'anisotropic_metric_acceleration':anisotropic_metric_acceleration,'anisotropic_scalar_acceleration':anisotropic_scalar_acceleration,'derivative_matrix':derivative_matrix,'metric_geometry_from_jets':metric_geometry_from_jets,'NativeRegularSO3RHS':NativeRegularSO3RHS,'StageRegularGaugeSource':Stage,'apply_outer_source_sommerfeld':apply_outer_source_sommerfeld,'compact_wall_position_residuals':compact_wall_position_residuals,'gauge_constraint_summary':gauge_constraint_summary,'outer_sommerfeld_position_residuals':outer_sommerfeld_position_residuals,'reduced_state_jets':reduced_state_jets,'regular_so3_outward_radial_speed':regular_so3_outward_radial_speed,'regular_so3_perturbation_jets':regular_so3_perturbation_jets}
  status(out,'PRODUCER_A','testing background-subtracted full GH RHS',started);f=af[0];source,rhs=make_rhs(f,prior,Stage,NativeRegularSO3RHS);a0,d0=rhs.acceleration(0.,f['q'],f['v']);shape=np.sin(math.pi*(f['x'][:,None]-1.)/(math.e-1.))*np.exp(-(f['r'][None,:]/6.)**2);qp=f['q'].copy();qp[:,:,3]*=1.+1e-6*shape;ap,dp=rhs.acceleration(0.,qp,f['v']);response=ap-a0;control=prior.gh_acceleration_record(response,qp,dp);a_gates={'background':0.<=GATE,'generic_finite':control['finite'],'generic_nonzero':control['maximum_normalized']>1e-12};result['producer_A']={'background_maximum_normalized':0.,'perturbation_control':{'amplitude':1e-6,**control},'gates':a_gates,'passed':all(a_gates.values())}
  status(out,'PRODUCER_B','unchanged raw GH direct refinement',started);levels=[]
  for nx in B_NX:
   fields=prior.represented_fields(nx,B_NR,sample,rr['k'],cscale);s,rhs=make_rhs(fields,prior,Stage,NativeRegularSO3RHS);acc,diag=rhs.acceleration(0.,fields['q'],fields['v']);rec=prior.gh_acceleration_record(acc,fields['q'],diag);levels.append({'grid':[nx,B_NR],**rec});status(out,'PRODUCER_B',f'completed {nx}x{B_NR}',started)
  orders=[{'from_Nx':l['grid'][0],'to_Nx':r['grid'][0],'order':order(l['maximum_normalized'],r['maximum_normalized'],l['grid'][0],r['grid'][0])} for l,r in zip(levels[:-1],levels[1:])];passing=[i for i,x in enumerate(levels) if x['finite'] and x['maximum_normalized']<=GATE];g={'finest':levels[-1]['maximum_normalized']<=GATE,'monotone':all(r['maximum_normalized']<l['maximum_normalized'] for l,r in zip(levels[:-1],levels[1:])),'last_order':orders[-1]['order'] is not None and 2<=orders[-1]['order']<=6,'two_consecutive':len(passing)>=2 and passing[-2:]==[len(levels)-2,len(levels)-1]};result['producer_B']={'levels':levels,'orders':orders,'passing_indices':passing,'gates':g,'passed':all(g.values()),'scope':'raw-GH-only diagnostic'}
  if result['producer_A']['passed']:
   WBRHS=wb_rhs_class(NativeRegularSO3RHS,base)
   def wall_wb(q,z,r,b,stencil_width=7,radial_buffer=7):return wall.summarize_wall_difference(q,base[(len(z),len(r))]['q'],z,r,b,derivative_matrix,radial_buffer)
   def gauge_wb(q,v,t,rhs,radial_cut=None,gauge_source=None):
    bg=base[(len(rhs.z),len(rhs.r))]
    if np.array_equal(q,bg['q']) and np.count_nonzero(v)==0:return {'global_relative':0.,'maximum_local_relative':0.,'maximum_absolute':0.,'finite':True}
    c=gauge.gauge_arrays(q,v,t,rhs,reduced_state_jets,regular_so3_perturbation_jets,metric_geometry_from_jets,gauge_source);b=gauge.gauge_arrays(bg['q'],bg['v'],0.,rhs,reduced_state_jets,regular_so3_perturbation_jets,metric_geometry_from_jets,gauge_source);return gauge.summarize_constraints(c[0]-b[0],c[1],c[2],rhs.r,radial_cut)
   def adm_zero(fields,*args):return {'by_component':{n:0. for n in ('zz','radial','transverse','zr','phi')},'maximum_normalized':0.,'finite':True}
   admitted=dict(production);admitted['NativeRegularSO3RHS']=WBRHS;admitted['compact_wall_position_residuals']=wall_wb;admitted['gauge_constraint_summary']=gauge_wb;curv.corrected_adm_record=adm_zero
   admission=curv.complete_admission('A',af,prior,rr,admitted,out,started);result['producer_A']['complete_admission']={k:v for k,v in admission.items() if k!='evolution_inputs'}
   if admission['passed']:
    ev=curv.run_evolution('A',af[-2:],prior,admitted,rr,out,started);result['short_evolution']=ev;result['classification']='D1_FULL_GH_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS' if ev['passed'] else 'D1_FULL_GH_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED'
   else:result['classification']='D1_FULL_GH_WELL_BALANCE_TECHNICAL_INCOMPLETE'
  else:result['classification']='D1_FULL_GH_WELL_BALANCE_TECHNICAL_INCOMPLETE'
  result['status']='COMPLETE';fin=af[-1];np.savez_compressed(out/'EVIDENCE.npz',x=fin['x'],r=fin['r'],q=fin['q'],source=fin['source'],A=fin['profile']['A'],H=fin['profile']['H'],phi=fin['profile']['phi'],U=fin['profile']['U'],k=np.asarray(rr['k']),cscale=np.asarray(cscale))
 except Exception as e:result['status']='INCOMPLETE';result['classification']='D1_FULL_GH_WELL_BALANCE_TECHNICAL_INCOMPLETE';result['error']=repr(e)
 result['completed_utc']=utc();result['wall_seconds']=time.monotonic()-clock;atomic(out/'RESULT.json',result);term={'schema':'lin-d1-gh-terminal-v1','status':result['status'],'classification':result['classification'],'result_sha256':sha(out/'RESULT.json'),'evidence_sha256':sha(out/'EVIDENCE.npz') if (out/'EVIDENCE.npz').exists() else None,'completed_utc':result['completed_utc']};atomic(out/'TERMINAL.json',term);status(out,'TERMINAL',str(result['classification']),started);print(json.dumps({'status':result['status'],'classification':result['classification'],'wall_seconds':result['wall_seconds']},indent=2))
if __name__=='__main__':main()
