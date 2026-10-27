"""One prospectively bounded Dirichlet-limit bisection; no rescue tuning."""
import sys, time, traceback, os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import finite_test as f
r=f.r

def authenticate():
    gate=r.read(ROOT/'DIRICHLET_GATE.json')
    r.need(gate['decision']=='APPROVED_FOR_ONE_BOUNDED_EXECUTION','DIRICHLET_GATE')
    for name,digest in gate['frozen_hashes'].items(): r.need(r.sha(ROOT/name)==digest,'DIRICHLET_GATE_HASH:'+name)
    for name,digest in r.read(ROOT/'DIRICHLET_BINDINGS.json')['files'].items(): r.need(r.sha(ROOT/name)==digest,'DIRICHLET_SOURCE_HASH:'+name)
    return r.authenticate()

def main():
    out=ROOT/'output_dirichlet'; out.mkdir(exist_ok=True)
    r.need(not any((out/name).exists() for name in ('STARTED.json','RESULT.json','FAILURE.json')),'REFUSE_RETRY')
    spec=r.read(ROOT/'DIRICHLET_SPEC.json'); bracket=tuple(map(Q,spec['initial_mu'])); started=time.monotonic(); attempts=[]
    try:
        flint=authenticate(); flint.ctx.prec=spec['bits']; flint.ctx.threads=1
        r.put(out/'STARTED.json',{'utc':r.now(),'pid':os.getpid(),'gate_sha256':r.sha(ROOT/'DIRICHLET_GATE.json')})
        controls=r.semantic_controls(); binding=r.read(ROOT/'inputs/central_bindings.json'); endpoint_records={}
        for engine in ('primary','independent'):
            r.need(r.load_engine(engine).algebra_controls()['pass'],'ENGINE_ALGEBRA_CONTROL')
            for label,expected,mass in [('finite_lower',1,bracket[0]),('high',-1,bracket[1])]:
                source=r.read(ROOT/('output/'+label+'_'+engine+'.json'))
                r.need(Q(source['mu_exact'])==mass,'ENDPOINT_MASS')
                r.need(r.sign(r.interval(source['event']['f']))==expected,'ENDPOINT_SIGN')
                endpoint_records[label+'_'+engine]=source['event']['f']
        reason='ATTEMPT_BUDGET'
        for attempt in range(1,spec['max_attempts']+1):
            if bracket[1]-bracket[0]<=Q(spec['target_width']): reason='TARGET_REACHED'; break
            mid=sum(bracket)/2; entry={'attempt':attempt,'before':list(map(str,bracket)),'midpoint_exact':str(mid),'engine_results':{}}
            attempts.append(entry); signs=[]
            for engine in ('primary','independent'):
                label=f'mid_{attempt:02d}'; record=f.flow(engine,mid,binding,spec,out,label,started)
                sig=r.sign(r.interval(record['event']['f'])); signs.append(sig)
                path=label+'_'+engine+'.json'; entry['engine_results'][engine]={'path':path,'sha256':r.sha(out/path),'sign':sig}
                if sig==0: reason='ZERO_CONTAINING_MIDPOINT'; break
            if 0 in signs: entry['admitted']=False; break
            if signs[0]!=signs[1]: entry['admitted']=False; reason='ENGINE_SIGN_DISAGREEMENT'; break
            bracket=(mid,bracket[1]) if signs[0]>0 else (bracket[0],mid)
            entry.update(admitted=True,after=list(map(str,bracket)))
        width=bracket[1]-bracket[0]; target=width<=Q(spec['target_width'])
        if target: reason='TARGET_REACHED'
        original=tuple(map(Q,r.read(ROOT/'inputs/narrowing_result.json')['mu_bracket']))
        first=r.read(ROOT/'output/RESULT.json'); r.need(first['classification']=='FINITE_RESPONSE_AND_GLOBAL_BRANCH','FIRST_RESULT')
        q=Q(first['eta100_mu_bracket'][0]); displacement=Q(first['strict_displacement_lower_exact'])
        total=(bracket[0]-original[1],bracket[1]-original[0]); remaining=bracket[1]-q
        r.need(total[1]>0 and remaining>0,'GAIN_DENOMINATOR_POSITIVE')
        fraction=displacement/total[1]
        useful=target and total[1]<Q(spec['max_total_gain_upper'])
        result={'status':'COMPLETE_PENDING_INDEPENDENT_REVIEW','classification':'QUANTIFIED_SATURATION' if useful else 'RETAINED_WIDE',
          'stop_reason':reason,'mu_D_bracket':list(map(str,bracket)),'width_exact':str(width),'target_pass':target,
          'total_gain_strict_bounds':list(map(str,total)),'remaining_gain_strict_bounds':['0',str(remaining)],
          'achieved_fraction_strict_lower':str(fraction),'attempts':attempts,'initial_endpoint_records':endpoint_records,
          'controls':controls,'elapsed_seconds':time.monotonic()-started,'finished_utc':r.now()}
        r.put(out/'RESULT.json',result); print(__import__('json').dumps(result,indent=2))
    except BaseException as e:
        r.put(out/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','utc':r.now(),'error':repr(e),'traceback':traceback.format_exc(),
            'last_admitted_bracket':list(map(str,bracket)),'attempts':attempts,'elapsed_seconds':time.monotonic()-started})
        raise
if __name__=='__main__': main()
