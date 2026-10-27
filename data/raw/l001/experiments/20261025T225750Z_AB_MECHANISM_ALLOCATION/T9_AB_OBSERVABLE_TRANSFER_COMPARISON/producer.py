"""Compare two physical readout ratios, not modes or excitation amplitudes."""
import importlib.util, os, platform, signal, sys, time, traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('transfer_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT
I=c.I
PARENTS={'t4':'../T4_AB_FIRST_CURRENT','t6':'../T6_AB_MINIMUM_SEPARATION_TRANSFER','t7':'../T7_AB_MINIMUM_PARTITION'}

def classify(d):
    return 'RESOLVED_TRANSFER_DIFFERENCE' if not d.zero() else 'TRANSFER_DIFFERENCE_UNRESOLVED'

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY')
    gate=c.read(ROOT/'ADMISSION.json'); c.need(gate.get('admitted') is True,'ADMISSION')
    required=[]
    for key,path in PARENTS.items():
        c.need(gate.get(key+'_terminal_review_accepted') is True,'PARENT_REVIEW:'+key)
        required += [path+'/TERMINAL_REVIEW.md',path+'/output/RESULT.json']
    for engine in ('primary','independent'):
        required += [PARENTS['t4']+'/output/assembled_'+engine+'.json',PARENTS['t6']+'/output/turn_'+engine+'.json',PARENTS['t7']+'/output/partition_'+engine+'.json']
    for rel in required: c.need(rel in gate['sources'],'MISSING_BINDING:'+rel)
    for rel,digest in gate['sources'].items(): c.need(c.sha(ROOT/rel)==digest,'SOURCE_HASH:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,digest in rt['files'].items(): c.need(c.sha(path)==digest,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    expected={'t4':'FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED','t6':'NEUTRAL_MINIMUM_SEPARATION_TRANSFER_ENCLOSED','t7':'FIRST_CURRENT_PHYSICAL_MINIMUM_PARTITION_ENCLOSED'}
    for key,want in expected.items(): c.need(c.read(ROOT/PARENTS[key]/'output/RESULT.json')['classification']==want,'PARENT_SCOPE:'+key)

def controls():
    a,b,scale=Q(-5,7),Q(3,11),Q(17,19)
    c.need(a/b==(scale*a)/(scale*b),'SCALE_CANCELLATION')
    k,n=a/b,Q(-2,3); c.need(k/n-1==(k-n)/n,'RELATIVE_DIFFERENCE')
    c.need(classify(I(1,2)-I(3,4))=='RESOLVED_TRANSFER_DIFFERENCE','DISJOINT_CONTROL')
    c.need(classify(I(1,2)-I(2,3))=='TRANSFER_DIFFERENCE_UNRESOLVED','TOUCHING_CONTROL')
    c.need(classify(I(1,3)-I(2,4))=='TRANSFER_DIFFERENCE_UNRESOLVED','OVERLAP_CONTROL')
    try: I(1)/I(-1,1)
    except RuntimeError as exc: c.need(str(exc)=='ZERO_DENOMINATOR','ZERO_REJECTION')
    else: raise RuntimeError('ZERO_DENOMINATOR_ACCEPTED')
    return {'scale_cancellation':True,'relative_difference_identity':True,'disjoint_touching_overlap':True,'zero_denominator_rejection':True}

def evaluate(engine):
    a=c.read(ROOT/PARENTS['t4']/'output'/('assembled_'+engine+'.json'))
    b=c.read(ROOT/PARENTS['t7']/'output'/('partition_'+engine+'.json'))
    n=c.read(ROOT/PARENTS['t6']/'output'/('turn_'+engine+'.json'))
    c.need(n['f_minimum_excludes_zero'],'NEUTRAL_DENOMINATOR')
    kn=c.interval(n['deltaD_over_deltaPhi_min']); c.need(not kn.zero(),'NEUTRAL_RATIO_NONZERO')
    out={}
    for channel in ('lower','upper'):
        old=a['channels'][channel]; obs=b['channels'][channel]['observables']
        total=c.interval(old['coefficient_total']); f=c.interval(obs['minimum_scalar_value'])
        c.need(not f.zero(),'CURRENT_MINIMUM_DENOMINATOR:'+channel)
        c.need(total.overlap(c.interval(obs['parent_total'])),'SAME_CURRENT_TOTAL')
        ki=total/f; diff=ki-kn; rel=ki/kn-1
        proper=c.interval(old['proper_density_coefficient_total'])/c.interval(obs['proper_density_minimum_scalar_value'])
        c.need(ki.overlap(proper),'DENSITY_NORMALIZATION:'+channel)
        out[channel]={key:value.pack() for key,value in {'current_ratio':ki,'neutral_ratio':kn,'difference':diff,'relative_difference':rel,'proper_density_ratio':proper}.items()}
    return out

def main():
    c.need(not any((ROOT/p).exists() for p in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    start=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('TRANSFER_COMPARISON_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested)
        per={e:evaluate(e) for e in ('primary','independent')}; combined={}
        for channel in ('lower','upper'):
            row={}
            for key in per['primary'][channel]:
                a=c.interval(per['primary'][channel][key]); b=c.interval(per['independent'][channel][key])
                c.need(a.overlap(b),'ENGINE_OVERLAP:'+channel+':'+key); row[key]=a.hull(b).pack()
            row['classification']=classify(c.interval(row['difference'])); combined[channel]=row
        c.put('RESULT.json',{'classification':'TWO_OBSERVABLE_TRANSFER_COMPARISON_COMPLETED','per_engine':per,'combined':combined,'controls':tested,'seconds':time.monotonic()-start,'utc':c.now(),'scope':'One ratio of two readouts across distinct temporal and boundary contracts. Overlap is unresolved distinction, not equality, mode alignment, excitation or nonlinear causation.'})
    except BaseException as exc:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(exc),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
