"""Remote oscillator-plus-W energy sector and exact scalar exchange."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); return v
c=module('energy_common',ROOT/'common.py'); c.ROOT=ROOT
T10=ROOT/'../T10_AB_CURRENT_RADAR_RESPONSE'; T15=ROOT/'../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'; T16=ROOT/'../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION'

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); gate=c.read(ROOT/'ADMISSION.json')
    c.need(gate.get('admitted') is True,'ADMISSION')
    for key in ('t10','t15','t16'): c.need(gate.get(key+'_terminal_review_accepted') is True,'PARENT_REVIEW:'+key)
    for rel,digest in gate['sources'].items(): c.need(c.sha(ROOT/rel)==digest,'SOURCE_HASH:'+rel)
    required=['../T10_AB_CURRENT_RADAR_RESPONSE/basis.py','../T10_AB_CURRENT_RADAR_RESPONSE/TERMINAL_REVIEW.md',
              '../T10_AB_CURRENT_RADAR_RESPONSE/output/RESULT.json','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py',
              '../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/RESULT.json','../T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/TERMINAL_REVIEW.md',
              '../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION/RESULT.json','../T16_AB_REMOTE_WALL_OSCILLATOR_BACKREACTION/TERMINAL_REVIEW.md']
    required+=['../T10_AB_CURRENT_RADAR_RESPONSE/output/current_radar_'+e+'.json' for e in ('primary','independent')]
    for rel in required: c.need(rel in gate['sources'],'MISSING_PARENT:'+rel)
    c.need(c.sha(ROOT/'polynomial_helper.py')==c.sha(T15/'producer.py'),'POLYNOMIAL_HELPER_IDENTITY')
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'] and platform.python_version()==rt['python_version'],'RUNTIME')
    for path,digest in rt['files'].items(): c.need(c.sha(path)==digest,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(T15/'RESULT.json')['classification']=='EULERIAN_QUADRATIC_BULK_SOURCES_QUALIFIED','HELPER_ACCEPTANCE')

def identity():
    a=module('energy_polynomial_helper',ROOT/'polynomial_helper.py')
    a.NAMES=('f','chi','k','E'); a.N=4; a.ZERO=(0,)*4
    f,x,k,E=[a.variable(i) for i in range(4)]
    K=18*k*E*E*x*x; W=(x*x+(x-f)*(x-f))/2; rho=K+W
    decay=-12*rho; expansion=6*K; work=-6*f*(f-x)
    row=(2+18*k*E*E)*x-f
    balance=decay+expansion-work
    c.need((balance+6*x*row).iszero(),'EXACT_OSCILLATOR_ENERGY_IDENTITY')
    mutated={'work_sign':decay+expansion+work,'missing_expansion_loss':decay-work,'missing_kinetic_half':-12*(2*K+W)+12*K-work}
    checks={}
    for name,value in mutated.items():
        difference=value+6*x*row
        c.need(not difference.iszero(),'MUTATION_NOT_DETECTED:'+name); checks[name]=difference.pack()
    return {'variables':list(a.NAMES),'K':K.pack(),'W':W.pack(),'rho_oscillator_sector':rho.pack(),
            'decay_scaled_by_hE':decay.pack(),'expansion_scaled_by_hE':expansion.pack(),
            'scalar_work_scaled_by_hE':work.pack(),'oscillator_row':row.pack(),
            'balance_residual':balance.pack(),'identity':'balance_residual=-6*chi*oscillator_row',
            'mutation_differences':checks}

def evaluate(engine,remote):
    data=c.read(T10/'output'/('current_radar_'+engine+'.json'))['full_forced_assembly']
    k=c.interval(data['k']); c.need(k.lo>0,'POSITIVE_K'); out={}
    for source,wallname in (('lower','upper'),('upper','lower')):
        channel=data['channels'][source]; w={key:c.interval(value) for key,value in channel['walls'][wallname].items()}
        c.need(w['n'].lo==w['n'].hi==w['xi'].lo==w['xi'].hi==0,'REMOTE_ZERO_CURRENT_AND_GRAPH')
        E,f,x=w['E'],w['f'],w['chi']; c.need(E.lo>0,'POSITIVE_WARP')
        d=2+18*k*E.sq(); c.need(d.overlap(w['d']),'OSCILLATOR_DENOMINATOR_LINKAGE')
        row=d*x-f; c.need(row.zero(),'OSCILLATOR_ROW_CONSISTENCY')
        K=18*k*E.sq()*x.sq(); W=(x.sq()+(x-f).sq())/2; rho=K+W
        decay=-12*rho; expansion=6*K; work=-6*f*(f-x)
        residual=decay+expansion-work; c.need(residual.zero() and residual.overlap(-6*x*row),'ENERGY_BALANCE_CONSISTENCY')
        old=c.interval(remote['per_engine'][engine][source+'_to_'+wallname]['oscillator_half_rho_plus_p_coefficient'])
        c.need(K.overlap(old),'T16_KINETIC_STRESS_LINKAGE')
        scale=c.interval(channel['source_wall_a6']).sq(); c.need(scale.lo>0,'POSITIVE_DENSITY_SCALE')
        values={'kinetic_energy':K,'coupled_potential_energy':W,'oscillator_sector_energy':rho,
                'proper_time_energy_decay_divided_by_hE':decay,'expansion_loss_divided_by_hE':expansion,
                'scalar_work_divided_by_hE':work,'balance_consistency_only':residual,
                'energy_per_source_proper_density_squared':scale*rho,
                'scalar_work_divided_by_hE_per_source_proper_density_squared':scale*work}
        out[source+'_to_'+wallname]={key:value.pack() for key,value in values.items()}
    return out

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('ENERGY_EXCHANGE_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        proof=identity(); c.put('ENERGY_IDENTITY.json',proof)
        old=c.read(T16/'RESULT.json'); per={e:evaluate(e,old) for e in ('primary','independent')}; combined={}
        for direction in ('lower_to_upper','upper_to_lower'):
            values={}
            for key in per['primary'][direction]:
                if key.endswith('consistency_only'): continue
                a,b=[c.interval(per[e][direction][key]) for e in ('primary','independent')]
                c.need(a.overlap(b),'ENGINE_DISAGREEMENT:'+direction+':'+key); values[key]=a.hull(b).pack()
            rho=c.interval(values['oscillator_sector_energy']); work=c.interval(values['scalar_work_divided_by_hE'])
            values['classification']='POSITIVE_REMOTE_OSCILLATOR_ENERGY_AND_NEGATIVE_SCALAR_WORK' if rho.lo>0 and work.hi<0 else 'UNRESOLVED'
            combined[direction]=values
        label='POSITIVE_REMOTE_OSCILLATOR_ENERGY_AND_NEGATIVE_SCALAR_WORK' if all(v['classification']=='POSITIVE_REMOTE_OSCILLATOR_ENERGY_AND_NEGATIVE_SCALAR_WORK' for v in combined.values()) else 'UNRESOLVED'
        c.put('RESULT.json',{'classification':label,'combined':combined,'per_engine':per,
             'identity_sha256':c.sha(ROOT/'ENERGY_IDENTITY.json'),'seconds':time.monotonic()-begun,'utc':c.now(),
             'scope':'Quadratic oscillator kinetic plus coupled W sector at remote uncharged wall, not total wall energy including tau(Phi). Known decaying analytic branch; no turn-on, energy propagation speed, full n2 geometry or excitation claim.'})
    except BaseException as exc:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc(),'utc':c.now()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
