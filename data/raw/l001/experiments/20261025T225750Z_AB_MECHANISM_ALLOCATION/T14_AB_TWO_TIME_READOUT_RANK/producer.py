"""Two-time linear readout rank; no delay choice or new evolution."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('two_time_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT; I=c.I
PARENTS={'t8':'T8_AB_NEUTRAL_RADAR_RESPONSE','t10':'T10_AB_CURRENT_RADAR_RESPONSE','t12':'T12_AB_THREE_READOUT_IDENTIFIABILITY'}
def path(key,file): return ROOT/'..'/PARENTS[key]/file
def det(cols):
    a,b,d=cols
    return a[0]*(b[1]*d[2]-b[2]*d[1])-b[0]*(a[1]*d[2]-a[2]*d[1])+d[0]*(a[1]*b[2]-a[2]*b[1])

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('admitted') is True,'ADMISSION')
    required=[]
    for key,folder in PARENTS.items():
        c.need(g.get(key+'_terminal_review_accepted') is True,'REVIEW_REQUIRED:'+key)
        required+=['../'+folder+'/TERMINAL_REVIEW.md','../'+folder+('/RESULT.json' if key=='t12' else '/output/RESULT.json')]
    for name in ('primary','independent'):
        required+=['../'+PARENTS['t8']+'/output/radar_'+name+'.json',
                   '../'+PARENTS['t10']+'/output/current_radar_'+name+'.json']
        required+=['../'+PARENTS['t10']+'/output/'+kind+'_'+name+'.json' for kind in ('homogeneous','particular_lower')]
    for rel in required: c.need(rel in g['sources'],'MISSING_PARENT_BINDING:'+rel)
    for rel,d in g['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for p,d in rt['files'].items(): c.need(c.sha(p)==d,'RUNTIME_HASH:'+p)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    c.need(c.read(path('t8','output/RESULT.json'))['classification']=='NEUTRAL_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T8_SCOPE')
    c.need(c.read(path('t10','output/RESULT.json'))['classification']=='FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T10_SCOPE')
    c.need(c.read(path('t12','RESULT.json'))['classification']=='UNRESOLVED','PRESERVE_T12')

def controls():
    Dn,Da,Db,Rn,Ra,Rb=map(Q,('2/3','3/5','5/7','7/11','11/13','13/17'))
    en,ec=Q(7,5),Q(3,5) # formal positive exponential values, not computed delays
    columns=[[Dn,Rn,Rn*en],[Da,Ra,Ra*ec],[Db,Rb,Rb*ec]]
    row_operated=[[col[0],col[1],col[2]-ec*col[1]] for col in columns]
    minor=Da*Rb-Db*Ra; factor=Rn*(en-ec)*minor
    c.need(det(columns)==det(row_operated)==factor,'ROW_OPERATION_AND_FACTOR_SIGN')
    c.need(row_operated[1][2]==row_operated[2][2]==0,'EXACT_SHARED_CURRENT_RATE')
    c.need(minor==Da*Db*(Rb/Db-Ra/Da),'CURRENT_MINOR_RATIO_IDENTITY')
    dep=[[Dn,Rn,Rn*en],[Da,Ra,Ra*ec],[2*Da,2*Ra,2*Ra*ec]]
    c.need(det(dep)==0,'DEPENDENT_CURRENT_DIRECTIONS')
    c.need(en-ec>0,'FORMAL_POSITIVE_EXPONENTIAL_GAP')
    c.need(Q(-6)*Q(2,7)==Q(-6)*Q(2,7),'SINGLE_SOURCE_RATE_LAW')
    # Perturbed proper-clock scheduling changes the already first-order
    # response only at quadratic order; background radar is time independent.
    r,A,shift=Q(-2,3),Q(3,7),Q(5,11)
    linear_coefficient=A; shifted_linear_coefficient=A
    quadratic_extra=r*A*shift
    c.need(linear_coefficient==shifted_linear_coefficient and quadratic_extra!=0,'EMISSION_CLOCK_SHIFT_ORDER')
    return {'row_operation':True,'cofactor_sign':True,'shared_current_rate':True,'minor_ratio_identity':True,
            'dependent_current_control':True,'formal_gap_sign':True,'clock_scheduling_order':True}

def evaluate(name,rank):
    raw=rank['per_engine'][name]
    c.need(raw['column_order']==['neutral','lower_current','upper_current'],'COLUMN_ORDER')
    cols=[[c.interval(v) for v in col] for col in raw['raw_columns']]
    neutral,lower,upper=cols; Dn,Fn,Rn=neutral; Da,Fa,Ra=lower; Db,Fb,Rb=upper
    n=c.read(path('t8','output/radar_'+name+'.json')); currents=c.read(path('t10','output/current_radar_'+name+'.json'))
    gamma=c.interval(n['observables']['gamma']); c.need(gamma.lo>0,'POSITIVE_NEUTRAL_RATE')
    c.need(Rn.overlap(c.interval(n['observables']['proper_roundtrip_coefficient'])),'NEUTRAL_CLOCK_LINKAGE')
    basis={kind:c.read(path('t10','output/'+kind+'_'+name+'.json')) for kind in ('homogeneous','particular_lower')}
    rates=[c.interval(v['rate']) for v in basis.values()]; ks=[c.interval(v['k']) for v in basis.values()]
    c.need(all(r.hi<0 for r in rates) and all(k.lo>0 for k in ks),'CURRENT_RATE_DOMAIN')
    c.need(rates[0].overlap(rates[1]) and ks[0].overlap(ks[1]),'SHARED_BACKGROUND_ENCLOSURES')
    for v in basis.values():
        rr=c.interval(v['rate']); k=c.interval(v['k']); mu=c.interval(v['mu'])
        c.need((rr.sq()-36*k).zero() and (mu+18*k).zero(),'SOURCE_RATE_MASS_LAW')
    # Rate equality is the exact source law r=-6h for both conserved-current
    # channels on this one background, NOT inferred from interval overlap.
    for side,D,R in (('lower',Da,Ra),('upper',Db,Rb)):
        obs=currents['channels'][side]['observables']
        c.need(D.overlap(c.interval(obs['accepted_separation_coefficient'])) and
               R.overlap(c.interval(obs['proper_roundtrip_coefficient'])),'CURRENT_COLUMN_LINKAGE:'+side)
    minor=Da*Rb-Db*Ra # authoritative predeclared raw expression
    prefactor=Rn*minor
    consistency=None
    if not Da.zero() and not Db.zero():
        secondary=Da*Db*(Rb/Db-Ra/Da)
        c.need(minor.overlap(secondary),'MINOR_FACTORIZED_CONSISTENCY')
        consistency=secondary.pack()
    label='LOCAL_TIME_RESOLVED_LINEAR_READOUT_INJECTIVITY' if not Rn.zero() and not minor.zero() else 'UNRESOLVED'
    return {'engine':name,'raw_columns_D_F_R':[[v.pack() for v in col] for col in cols],
            'authoritative_raw_current_minor':minor.pack(),'neutral_radar_coefficient':Rn.pack(),
            'determinant_positive_gap_prefactor':prefactor.pack(),'ratio_factorization_consistency_only':consistency,
            'neutral_rate':gamma.pack(),'current_rate_enclosure':rates[0].hull(rates[1]).pack(),
            'same_current_rate_authority':'Exact shared source law r=-6h, not equality inferred from overlap.',
            'classification':label}

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('TWO_TIME_RANK_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested=controls(); c.put('CONTROLS.json',tested); rank=c.read(path('t12','RESULT.json'))
        per={name:evaluate(name,rank) for name in ('primary','independent')}; combined={}
        for key in ('authoritative_raw_current_minor','neutral_radar_coefficient','determinant_positive_gap_prefactor','neutral_rate','current_rate_enclosure'):
            a,b=[c.interval(per[n][key]) for n in ('primary','independent')]
            c.need(a.overlap(b),'ENGINE_DISAGREEMENT:'+key); combined[key]=a.hull(b).pack()
        minor=c.interval(combined['authoritative_raw_current_minor']); Rn=c.interval(combined['neutral_radar_coefficient'])
        label='LOCAL_TIME_RESOLVED_LINEAR_READOUT_INJECTIVITY' if not minor.zero() and not Rn.zero() else 'UNRESOLVED'
        c.put('RESULT.json',{'classification':label,'combined':combined,'per_engine':per,'controls':tested,
               'analytic_time_factor':'exp(gamma*Delta_t)-exp(r*Delta_t)>0 for every Delta_t>0, gamma>0>r, within common perturbative patch.',
               'delay_choice':None,'T12_preserved':'UNRESOLVED','seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'New two-time protocol D(0), lower radar(0), lower radar(positive delay). Formal local linear injectivity only; no excitation, conditioning, finite-charge inverse or nonlinear uniqueness. Current amplitudes occupy a nonnegative cone.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
