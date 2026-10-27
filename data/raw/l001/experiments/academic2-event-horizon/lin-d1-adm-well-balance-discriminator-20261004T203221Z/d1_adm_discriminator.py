#!/usr/bin/env python3
"""D1 ADM equilibrium well-balance and direct-refinement discriminator."""

from __future__ import annotations

import argparse, datetime as dt, hashlib, importlib.util, json, math, os, sys, time
from pathlib import Path
from typing import Any
import numpy as np

A_GRIDS=((65,121),(97,181),(129,241));B_NX=(129,193,257,385,513);B_NR=241;STENCIL=7;GATE=5e-5

def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def atomic_json(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n');os.replace(tmp,path)
def status(output,phase,detail,started): atomic_json(output/'STATUS.json',{'schema':'lin-d1-adm-status-v1','started_utc':started,'updated_utc':utc(),'phase':phase,'detail':detail,'pid':os.getpid()})
def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError(f'cannot import {path}')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def verify_bindings(root,here):
    b=json.loads((here/'BINDINGS.json').read_text());out=[]
    for item in b['parents']+b['production_sources']:
        actual=sha256(root/item['path'])
        if actual!=item['sha256']: raise RuntimeError(f"binding changed: {item['path']} {actual}")
        out.append({'path':item['path'],'sha256':actual,'role':item.get('role','production_source')})
    return out
def maximum(x): return float(np.max(np.abs(np.asarray(x,dtype=float))))
def observed_order(c,f,cn,fn):
    return None if c<=0 or f<=0 or c==f else float(math.log(c/f)/math.log((fn-1)/(cn-1)))

def raw_adm_arrays(fields,metric_acceleration,scalar_acceleration):
    zero=np.zeros_like(fields['psi'])
    metric=metric_acceleration(fields['x'],fields['r'],fields['psi'],fields['a'],fields['b'],fields['c'],fields['phi'],zero,zero,0.41,stencil_width=STENCIL,lapse=fields['alpha'])
    scalar=scalar_acceleration(fields['x'],fields['r'],fields['psi'],fields['a'],fields['b'],fields['c'],fields['phi'],0.41,lapse=fields['alpha'],stencil_width=STENCIL)
    return {name:np.asarray(metric[name]) for name in ('zz','radial','transverse','zr')}|{'phi':np.asarray(scalar)}

def difference_record(candidate,baseline,metric_acceleration,scalar_acceleration):
    ca=raw_adm_arrays(candidate,metric_acceleration,scalar_acceleration);ba=raw_adm_arrays(baseline,metric_acceleration,scalar_acceleration)
    q=candidate['q'];r=candidate['r'];scales={'zz':max(1.,maximum(q[:,:,6])),'radial':max(1.,maximum(q[:,:,3]+r[None,:]**2*q[:,:,4])),
        'transverse':max(1.,maximum(q[:,:,3])),'zr':1.,'phi':max(1.,maximum(candidate['phi']))}
    by={name:maximum(ca[name]-ba[name])/scales[name] for name in scales}
    return {'by_component':by,'maximum_normalized':max(by.values()),'finite':all(np.all(np.isfinite(ca[n]-ba[n])) for n in scales)}

def coherent_perturbation(fields,k,cscale):
    result={key:(value.copy() if isinstance(value,np.ndarray) else value) for key,value in fields.items()}
    shape=np.sin(math.pi*(fields['x'][:,None]-1.)/(math.e-1.))*np.exp(-(fields['r'][None,:]/6.)**2);factor=1.+1e-6*shape
    result['psi']=fields['psi']*factor;result['alpha']=fields['alpha']*factor
    w2=result['psi']**2;f=1.-k*fields['r'][None,:]**2;q=fields['q'].copy()
    q[:,:,2]=-w2*f;q[:,:,3]=w2;q[:,:,4]=w2*k/f;q[:,:,6]=w2*cscale*cscale;result['q']=q
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    root=args.root.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True);here=Path(__file__).resolve().parent;started=utc();clock=time.monotonic()
    result={'schema':'lin-d1-adm-discriminator-result-v1','status':'RUNNING','classification':None,'started_utc':started,
            'contract_sha256':sha256(here/'CONTRACT.md'),'bindings_sha256':sha256(here/'BINDINGS.json'),
            'claim_boundary':['One finite-resolution D1 equilibrium only.','No continuum, stability, P16, collapse, parent-child, or causal inference.']}
    try:
        status(output,'AUTHENTICATION','verifying frozen parents and operators',started);result['bindings_verified']=verify_bindings(root,here)
        prior=import_file('adm_prior',root/'branches/02-event-horizon/lin-d1-cauchy-background-admission-20261004T172121Z/d1_background_admission.py')
        curvature=import_file('adm_curvature',root/'branches/02-event-horizon/lin-d1-curvature-well-balance-discriminator-20261004T190608Z/d1_curvature_discriminator.py')
        wall=import_file('adm_wall',root/'branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-20261004T200437Z/d1_wall_discriminator.py')
        adapter=import_file('adm_adapter',root/'branches/02-event-horizon/lin-d1-wall-well-balance-discriminator-r1-20261004T201152Z/d1_wall_discriminator_r1.py')
        gauge=import_file('adm_gauge',root/'branches/02-event-horizon/lin-d1-gauge-well-balance-discriminator-20261004T202200Z/d1_gauge_discriminator.py')
        source_root=root/'branches/01-horizon-core/formation-mechanism-20260930T171423Z/frozen-project/src';sys.path.insert(0,str(source_root))
        from bhps.adm_corner import _axisymmetric_derivatives
        from bhps.anisotropic_geometry import anisotropic_metric_acceleration,anisotropic_scalar_acceleration,axisymmetric_diagonal_geometry
        from bhps.gw_slice_high_order_solver import derivative_matrix
        from bhps.linearized_gh_einstein_scalar import metric_geometry_from_jets
        from bhps.nonlinear_regular_so3_evolution import NativeRegularSO3RHS,StageRegularGaugeSource,apply_outer_source_sommerfeld,compact_wall_position_residuals,gauge_constraint_summary,outer_sommerfeld_position_residuals,reduced_state_jets,regular_so3_outward_radial_speed
        from bhps.regular_so3_gh_reduction import regular_so3_perturbation_jets
        CompatibleStage=adapter.compatible_stage_source_class(StageRegularGaugeSource)
        production={'derivatives':_axisymmetric_derivatives,'axisymmetric_diagonal_geometry':axisymmetric_diagonal_geometry,'anisotropic_metric_acceleration':anisotropic_metric_acceleration,
          'anisotropic_scalar_acceleration':anisotropic_scalar_acceleration,'derivative_matrix':derivative_matrix,'metric_geometry_from_jets':metric_geometry_from_jets,
          'NativeRegularSO3RHS':NativeRegularSO3RHS,'StageRegularGaugeSource':CompatibleStage,'apply_outer_source_sommerfeld':apply_outer_source_sommerfeld,
          'compact_wall_position_residuals':compact_wall_position_residuals,'gauge_constraint_summary':gauge_constraint_summary,'outer_sommerfeld_position_residuals':outer_sommerfeld_position_residuals,
          'reduced_state_jets':reduced_state_jets,'regular_so3_outward_radial_speed':regular_so3_outward_radial_speed,'regular_so3_perturbation_jets':regular_so3_perturbation_jets}
        root_record=prior.solve_representative_root();sample,length,cscale=prior.make_profile(root_record);result['representative_root']={'a':root_record['a'],'D':root_record['D'],'L':length,'k':root_record['k']}
        saved_corrected_adm=curvature.corrected_adm_record;a_fields=[];a_levels=[]
        status(output,'PRODUCER_A','evaluating D1 equilibrium ADM well-balance',started)
        for nx,nr in A_GRIDS:
            fields=prior.represented_fields(nx,nr,sample,root_record['k'],cscale);a_fields.append(fields)
            raw=saved_corrected_adm(fields,root_record,axisymmetric_diagonal_geometry,anisotropic_metric_acceleration,anisotropic_scalar_acceleration)
            wb=difference_record(fields,fields,anisotropic_metric_acceleration,anisotropic_scalar_acceleration)
            a_levels.append({'grid':[nx,nr],'curvature_corrected_raw':raw,'equilibrium_well_balanced':wb})
        perturb=coherent_perturbation(a_fields[-1],root_record['k'],cscale)
        control=difference_record(perturb,a_fields[-1],anisotropic_metric_acceleration,anisotropic_scalar_acceleration)
        a_gates={'background':a_levels[-1]['equilibrium_well_balanced']['maximum_normalized']<=GATE,'generic_finite':control['finite'],'generic_nonzero':control['maximum_normalized']>1e-12}
        result['producer_A']={'levels':a_levels,'perturbation_control':{'amplitude':1e-6,**control},'gates':a_gates,'passed':all(a_gates.values())}
        status(output,'PRODUCER_B','evaluating unchanged curvature-corrected ADM refinement',started);b_levels=[]
        for nx in B_NX:
            fields=prior.represented_fields(nx,B_NR,sample,root_record['k'],cscale)
            record=saved_corrected_adm(fields,root_record,axisymmetric_diagonal_geometry,anisotropic_metric_acceleration,anisotropic_scalar_acceleration)
            b_levels.append({'grid':[nx,B_NR],**record});status(output,'PRODUCER_B',f'completed {nx}x{B_NR}',started)
        orders=[{'from_Nx':l['grid'][0],'to_Nx':r['grid'][0],'order':observed_order(l['maximum_normalized'],r['maximum_normalized'],l['grid'][0],r['grid'][0])} for l,r in zip(b_levels[:-1],b_levels[1:])]
        passing=[i for i,x in enumerate(b_levels) if x['maximum_normalized']<=GATE]
        b_gates={'finest':b_levels[-1]['maximum_normalized']<=GATE,'monotone':all(r['maximum_normalized']<l['maximum_normalized'] for l,r in zip(b_levels[:-1],b_levels[1:])),
                 'last_order':orders[-1]['order'] is not None and 2<=orders[-1]['order']<=6,'two_consecutive':len(passing)>=2 and passing[-2:]==[len(b_levels)-2,len(b_levels)-1]}
        result['producer_B']={'levels':b_levels,'orders':orders,'passing_indices':passing,'gates':b_gates,'passed':all(b_gates.values()),'scope':'ADM-only diagnostic'}
        if result['producer_A']['passed']:
            baseline={(len(f['x']),len(f['r'])):f for f in a_fields}
            def wall_wb(position,z,r,background,stencil_width=7,radial_buffer=7): return wall.summarize_wall_difference(position,baseline[(len(z),len(r))]['q'],z,r,background,derivative_matrix,radial_buffer)
            def gauge_wb(position,velocity,t,rhs,radial_cut=None,gauge_source=None):
                base=baseline[(len(rhs.z),len(rhs.r))]
                if np.array_equal(position,base['q']) and np.count_nonzero(velocity)==0 and t==0.: return {'global_relative':0.,'maximum_local_relative':0.,'maximum_absolute':0.,'finite':True}
                c=gauge.gauge_arrays(position,velocity,t,rhs,reduced_state_jets,regular_so3_perturbation_jets,metric_geometry_from_jets,gauge_source)
                b=gauge.gauge_arrays(base['q'],base['v'],0.,rhs,reduced_state_jets,regular_so3_perturbation_jets,metric_geometry_from_jets,gauge_source)
                return gauge.summarize_constraints(c[0]-b[0],c[1],c[2],rhs.r,radial_cut)
            def adm_wb(fields,root_rec,axis_geometry,metric_acc,scalar_acc): return difference_record(fields,baseline[(len(fields['x']),len(fields['r']))],metric_acc,scalar_acc)
            admitted=dict(production);admitted['compact_wall_position_residuals']=wall_wb;admitted['gauge_constraint_summary']=gauge_wb;curvature.corrected_adm_record=adm_wb
            admission=curvature.complete_admission('A',a_fields,prior,root_record,admitted,output,started);result['producer_A']['complete_admission']={k:v for k,v in admission.items() if k!='evolution_inputs'}
            if admission['passed']:
                evolution=curvature.run_evolution('A',a_fields[-2:],prior,admitted,root_record,output,started);result['short_evolution']=evolution
                result['classification']='D1_ADM_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS' if evolution['passed'] else 'D1_ADM_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED'
            else: result['classification']='D1_ADM_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_'+str(admission.get('first_failed_gate','UNKNOWN')).upper()
        else: result['classification']='D1_ADM_WELL_BALANCE_TECHNICAL_INCOMPLETE'
        result['status']='COMPLETE';finest=a_fields[-1];np.savez_compressed(output/'EVIDENCE.npz',x=finest['x'],r=finest['r'],q=finest['q'],source=finest['source'],A=finest['profile']['A'],H=finest['profile']['H'],phi=finest['profile']['phi'],U=finest['profile']['U'],k=np.asarray(root_record['k']),cscale=np.asarray(cscale))
    except Exception as error: result['status']='INCOMPLETE';result['classification']='D1_ADM_WELL_BALANCE_TECHNICAL_INCOMPLETE';result['error']=repr(error)
    result['completed_utc']=utc();result['wall_seconds']=time.monotonic()-clock;atomic_json(output/'RESULT.json',result)
    terminal={'schema':'lin-d1-adm-terminal-v1','status':result['status'],'classification':result['classification'],'result_sha256':sha256(output/'RESULT.json'),'evidence_sha256':sha256(output/'EVIDENCE.npz') if (output/'EVIDENCE.npz').exists() else None,'completed_utc':result['completed_utc']}
    atomic_json(output/'TERMINAL.json',terminal);status(output,'TERMINAL',str(result['classification']),started);print(json.dumps({'status':result['status'],'classification':result['classification'],'wall_seconds':result['wall_seconds']},indent=2))
if __name__=='__main__': main()
