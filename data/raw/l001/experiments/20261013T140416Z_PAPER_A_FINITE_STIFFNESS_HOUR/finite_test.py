"""Frozen six-flow upper-Hessian test; no numerical search or retries."""
import json, os, sys, time, traceback
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import inherited_runner as r
r.ROOT=ROOT

def flow(engine,mu,binding,spec,out,label,started):
    from flint import arb,fmpq
    mod=r.load_engine(engine); begun=time.monotonic(); cfg=binding['config']; D=tuple(map(Q,cfg['D']))
    h=fmpq(2,spec['steps'][engine]); Dlo,Dhi=map(fmpq,cfg['D']); A=mod.interval(*map(fmpq,cfg['A']))
    y,par=mod.initial(A,arb(fmpq(str(mu))),binding['model_exact'])
    r.need(par['k'].lower()>0 and (arb(fmpq(str(mu)))+4*par['k']).upper()<0,'FLOW_SECTOR')
    n=(D[1]*spec['steps'][engine]/2).__ceil__(); rows=[]; hulls={}; maxpicard=0
    def pack(x):
        lo,hi=mod.bounds(x); return {'exact_bounds':[str(lo),str(hi)]}
    for j in range(n):
        if j%64==0:
            deadline=datetime.fromisoformat(r.read(ROOT/'AUTHORITY.json')['hard_deadline_utc'].replace('Z','+00:00')).timestamp()-spec['deadline_reserve_seconds']
            r.need(time.time()<deadline,'ABSOLUTE_PRODUCTION_DEADLINE')
            r.need(time.monotonic()-begun<spec['flow_seconds_max'],'FLOW_TIME_BUDGET')
            r.need(time.monotonic()-started<spec['production_seconds_max'],'TOTAL_TIME_BUDGET')
        s=j*h; y,cell=mod.step(y,h,par); geo=mod.geometry(cell,par)
        r.need(all(v.is_finite() for v in y+list(geo.values())),'NONFINITE_FLOW')
        r.need(geo['constraint'].lower()<=0<=geo['constraint'].upper(),'CONSTRAINT_ESCAPE')
        r.need(geo['first_integral'].lower()<=0<=geo['first_integral'].upper(),'FIRST_INTEGRAL_ESCAPE')
        r.need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY')
        maxpicard=max(maxpicard,cell['picard_iterations'])
        if s+h>=Dlo and s<=Dhi:
            a=max(fmpq(0),Dlo-s); b=min(h,Dhi-s); v=mod.range_on_cell(cell,a,b)
            vals={'R0':mod.determinant(v,par),'f':v[6 if engine=='primary' else 5]}
            for key,value in vals.items():
                r.need(value.is_finite(),'NONFINITE_EVENT'); hulls[key]=value if key not in hulls else mod.hull(hulls[key],value)
            rows.append({'index':j,'lo_exact':str(s+a),'hi_exact':str(s+b),**{key:pack(value) for key,value in vals.items()}})
    r.event_cover(rows,D)
    result={'label':label,'engine':engine,'mu_exact':str(mu),'event':{key:pack(value) for key,value in hulls.items()},'event_cover':rows,
      'cells':n,'steps':spec['steps'][engine],'all_cell_checks_pass':True,'max_picard_iterations':maxpicard,
      'elapsed_seconds':time.monotonic()-begun,'finished_utc':r.now(),'source_sha256':r.sha(ROOT/('engine/'+engine+'_interval.py'))}
    r.put(out/(label+'_'+engine+'.json'),result); print(json.dumps({'completed':label,'engine':engine}),flush=True); return result

def assess(records,spec):
    eta=Q(spec['eta']); answer={}
    for engine in ('primary','independent'):
        events={label:{key:r.interval(value) for key,value in records[engine][label]['event'].items()} for label in spec['mass_points']}
        vals={}
        for label,event in events.items():
            vals[label]={'R_eta100':r.record(r.add(event['R0'],r.scale(event['f'],eta/2))),
                         'R_eta_uniform':r.record(r.add(event['R0'],r.mul(event['f'],(Q(0),eta/2))))}
        allfinite=events['low']['R0'][0]>0 and events['low']['f'][0]>0
        uniform=r.interval(vals['low']['R_eta_uniform'])[0]>0 and r.interval(vals['high']['R_eta_uniform'])[1]<0
        shifted=r.interval(vals['finite_lower']['R_eta100'])[0]>0 and r.interval(vals['high']['R_eta100'])[1]<0
        answer[engine]={'derived':vals,'all_finite_lower_witness':allfinite,'uniform_strip_endpoints':uniform,'finite_displacement':shifted}
    full=all(x['all_finite_lower_witness'] and x['uniform_strip_endpoints'] and x['finite_displacement'] for x in answer.values())
    qualitative=all(x['all_finite_lower_witness'] for x in answer.values())
    narrow=r.read(ROOT/'inputs/narrowing_result.json'); old=tuple(map(Q,narrow['mu_bracket']))
    gap=Q(spec['mass_points']['finite_lower'])-old[1]
    r.need(gap==Q(3,16000000),'PROSPECTIVE_DISPLACEMENT_GAP')
    return {'engines':answer,'classification':'FINITE_RESPONSE_AND_GLOBAL_BRANCH' if full else 'GLOBAL_BRANCH_ONLY' if qualitative else 'INCOMPLETE',
      'eta_interval':['0',str(eta)],'eta100_mu_bracket':[spec['mass_points']['finite_lower'],spec['mass_points']['high']] if full else None,
      'strict_displacement_lower_exact':str(gap) if full else None,'initial_mu_bracket':list(map(str,old)),
      'all_finite_branch_numerical_premise_pass':qualitative,'quantitative_pass':full}

def main():
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    r.need(not any((out/name).exists() for name in ('STARTED.json','RESULT.json','FAILURE.json')),'REFUSE_RETRY')
    started=time.monotonic(); records={}; spec=r.read(ROOT/'TEST_SPEC.json')
    try:
        flint=r.authenticate(); flint.ctx.prec=spec['bits']; flint.ctx.threads=1
        r.put(out/'STARTED.json',{'utc':r.now(),'pid':os.getpid(),'gate_sha256':r.sha(ROOT/'INDEPENDENT_GATE.json')})
        controls=r.semantic_controls(); binding=r.read(ROOT/'inputs/central_bindings.json')
        for engine in ('primary','independent'):
            r.need(r.load_engine(engine).algebra_controls()['pass'],'ENGINE_ALGEBRA_CONTROL'); records[engine]={}
            for label,mu in spec['mass_points'].items(): records[engine][label]=flow(engine,Q(mu),binding,spec,out,label,started)
        result=assess(records,spec)
        result.update(status='COMPLETE_PENDING_INDEPENDENT_REVIEW',finished_utc=r.now(),elapsed_seconds=time.monotonic()-started,controls=controls,
          source_records={engine:{label:{'path':label+'_'+engine+'.json','sha256':r.sha(out/(label+'_'+engine+'.json'))} for label in records[engine]} for engine in records})
        r.put(out/'RESULT.json',result); print(json.dumps(result,indent=2))
    except BaseException as e:
        r.put(out/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','utc':r.now(),'error':repr(e),'traceback':traceback.format_exc(),'elapsed_seconds':time.monotonic()-started})
        raise
if __name__=='__main__': main()
