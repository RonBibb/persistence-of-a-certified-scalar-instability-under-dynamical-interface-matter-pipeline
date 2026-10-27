"""Exact saved-record susceptibility calculation for selected neutral AB mode.

No ODE integration. Interval endpoints and automatic derivative controls use
Fraction; all executable calculation is restricted to admitted Linux runtime.
"""
import hashlib, json, os, platform, signal, sys, time, traceback
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.set_int_max_str_digits(0)  # Bound scientific Fraction records may exceed the display digit limit.

def need(ok,why):
    if not ok: raise RuntimeError(why)
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def put(name,obj):
    p=ROOT/name; t=p.with_suffix(p.suffix+'.tmp')
    need(not p.exists() and not t.exists(),'NO_OVERWRITE:'+name)
    with t.open('x') as f: json.dump(obj,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.link(t,p); t.unlink()

class I:
    def __init__(self,a,b=None):
        self.lo=Q(a); self.hi=Q(a if b is None else b); need(self.lo<=self.hi,'INTERVAL_ORDER')
    @staticmethod
    def cast(x): return x if isinstance(x,I) else I(x)
    def __add__(self,o):
        o=I.cast(o); return I(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self): return I(-self.hi,-self.lo)
    def __sub__(self,o): return self+-I.cast(o)
    def __rsub__(self,o): return I.cast(o)+-self
    def __mul__(self,o):
        o=I.cast(o); v=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]; return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=I.cast(o); need(not o.zero(),'ZERO_DENOMINATOR'); return self*I(1/o.hi,1/o.lo)
    def __rtruediv__(self,o): return I.cast(o)/self
    def sq(self):
        return I(0 if self.zero() else min(self.lo*self.lo,self.hi*self.hi),max(self.lo*self.lo,self.hi*self.hi))
    def zero(self): return self.lo<=0<=self.hi
    def overlap(self,o): return self.lo<=o.hi and o.lo<=self.hi
    def hull(self,o): return I(min(self.lo,o.lo),max(self.hi,o.hi))
    def pack(self): return {'exact_bounds':[str(self.lo),str(self.hi)]}

class Dual:
    """Exact forward differentiation, independent of hand derivative formulas."""
    def __init__(self,v,d=0): self.v,self.d=Q(v),Q(d)
    @staticmethod
    def cast(o): return o if isinstance(o,Dual) else Dual(o)
    def __add__(self,o):
        o=Dual.cast(o); return Dual(self.v+o.v,self.d+o.d)
    __radd__=__add__
    def __neg__(self): return Dual(-self.v,-self.d)
    def __sub__(self,o): return self+-Dual.cast(o)
    def __rsub__(self,o): return Dual.cast(o)+-self
    def __mul__(self,o):
        o=Dual.cast(o); return Dual(self.v*o.v,self.d*o.v+self.v*o.d)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=Dual.cast(o); need(o.v!=0,'DUAL_ZERO_DENOMINATOR')
        return Dual(self.v/o.v,(self.d*o.v-self.v*o.d)/(o.v*o.v))
    def __rtruediv__(self,o): return Dual.cast(o)/self

def interval(r): return I(*r['exact_bounds'])

def gamma_expression(k,b,w,e,mu,A): return k+b*e*e-b*b*e*e/(w+b-mu/A)

def analytic_derivatives(k,b,w,e,mu,A):
    # For Fraction or interval arithmetic; ordinary repeated products suffice
    # in exact point controls, but interval squares below use .sq explicitly.
    d=w+b-mu/A
    sq=lambda x:x.sq() if isinstance(x,I) else x*x
    return {'kappa':I(1) if isinstance(A,I) else Q(1),
            'beta':sq(e)*sq(w-mu/A)/sq(d),
            'omega_squared':sq(b)*sq(e)/sq(d),
            'eta':2*b*e*(1-b/d),
            'mu':-sq(b)*sq(e)/(A*sq(d))}

def controls(cfg):
    count=0
    for A in map(Q,cfg['control_A']):
        for b in map(Q,cfg['control_beta']):
            for e in map(Q,cfg['control_eta']):
                vals={'kappa':Q(20),'beta':b,'omega_squared':Q(cfg['control_omega_squared']),
                      'eta':e,'mu':Q(cfg['control_mu'])}
                expected=analytic_derivatives(vals['kappa'],b,vals['omega_squared'],e,vals['mu'],A)
                for target in vals:
                    z={k:Dual(v,k==target) for k,v in vals.items()}
                    got=gamma_expression(z['kappa'],z['beta'],z['omega_squared'],z['eta'],z['mu'],A).d
                    need(got==expected[target],'DUAL_DERIVATIVE:'+target); count+=1
    # Independent interval predicates and crossing-zero square.
    need(I(-2,3).sq().lo==0 and I(-2,3).sq().hi==9,'SQUARE_CONTROL')
    try: I(1)/I(-1,1)
    except RuntimeError as e: need(str(e)=='ZERO_DENOMINATOR','WRONG_CONTROL_REJECTION')
    else: raise RuntimeError('ACCEPTED_ZERO_DENOMINATOR')
    mu=Q(-1,1000); k=Q(3,10000)
    need(gamma_expression(Q(20),Q(1),Q(1),Q(1),mu,Q(1,4))!=
         gamma_expression(Q(20),Q(1),Q(1),Q(1),mu+4*k,Q(1,4)),'SHIFTED_MASS_MUTATION')
    # Exact normalization: P=A² f² and u=beta eta f/d imply -PΓ_mu=A u².
    A=Q(1,4); f=Q(3,7); b=Q(3,2); e=Q(-1); w=Q(1); d=w+b-mu/A
    gm=analytic_derivatives(Q(20),b,w,e,mu,A)['mu']; u=b*e*f/d
    need(-A*A*f*f*gm==A*u*u,'WALL_NORM_IDENTITY_CONTROL')
    return {'dual_derivative_checks':count,'five_formulas_exact':True,'cross_zero_square':True,
            'zero_denominator_rejected':True,'shifted_mass_mutation_rejected':True,'wall_norm_identity':True}

def authenticate(cfg):
    need(sys.platform=='linux','LINUX_ONLY')
    gate=read(ROOT/'ADMISSION.json'); need(gate.get('admitted') is True,'ADMISSION')
    need(gate.get('t2_terminal_review_accepted') is True,'T2_TERMINAL_REVIEW_NOT_ACCEPTED')
    for rel,digest in gate['sources'].items(): need(sha(ROOT/rel)==digest,'SOURCE_HASH:'+rel)
    for rel in [cfg['t2']+'/output/RESULT.json',cfg['t2']+'/output/strip_primary.json',
                cfg['t2']+'/output/strip_independent.json',cfg['t2_review']]:
        need(rel in gate['sources'],'MISSING_BOUND_T2_SOURCE:'+rel)
    rt=read(ROOT/'RUNTIME_BINDINGS.json')
    need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for p,digest in rt['files'].items(): need(sha(p)==digest,'RUNTIME_HASH:'+p)
    need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')

def evaluate(strip,mu,cfg):
    need(strip['beta']==1 and strip['all_cell_checks_pass'] is True,'SELECTED_STRIP_REQUIRED')
    need(strip['mu_bounds']==[str(mu.lo),str(mu.hi)],'MASS_STRIP_BINDING')
    ob={k:interval(v) for k,v in strip['observables'].items()}
    Z=ob['Zext']; ZA=ob['Zg']+ob['Zs']; need(Z.lo>0 and ZA.lo>0,'POSITIVE_KINETIC_NORM')
    selected={k:I(v) for k,v in cfg['selected'].items()}
    lower=strip['lower_event']; upper=strip['event']
    walls={
        'lower':{'A':interval(lower['a_squared']),'f':interval(lower['f']),'u':interval(lower['u']),'Gamma':interval(lower['Gamma']),'d':interval(lower['d'])},
        'upper':{'A':interval(upper['a_squared_b']),'f':interval(upper['f_b']),'u':interval(upper['u_b']),'Gamma':interval(upper['Gamma_b']),'d':interval(upper['d_b'])}}
    total_mu=I(0); direct_wall_norm=I(0); results={}
    for label,wall in walls.items():
        A,f=wall['A'],wall['f']; need(A.lo>0,'POSITIVE_WALL_METRIC')
        k,b,w,e=[selected[t] for t in ('kappa','beta','omega_squared','eta')]
        d=w+b-mu/A; need(d.lo>0 and d.overlap(wall['d']),'OSCILLATOR_DENOMINATOR')
        G=gamma_expression(k,b,w,e,mu,A); need(G.overlap(wall['Gamma']),'EFFECTIVE_HESSIAN_BINDING')
        u=b*e*f/d; need(u.overlap(wall['u']),'OSCILLATOR_TRACE_BINDING')
        dg=analytic_derivatives(k,b,w,e,mu,A)
        P=A.sq()*f.sq(); total_mu+=P*dg['mu']; direct_wall_norm+=A*wall['u'].sq()
        vals={p:P*dg[p]/Z for p in cfg['parameters']}
        results[label]={'susceptibilities':{p:v.pack() for p,v in vals.items()},
                        'Gamma_derivatives':{p:v.pack() for p,v in dg.items()},
                        'a4_f_squared':P.pack(),'wall_scalar_trace_excludes_zero':not f.zero()}
    denominator=ZA-total_mu
    need(denominator.lo>0 and denominator.overlap(Z) and (denominator-Z).zero(),'IMPLICIT_DENOMINATOR_IDENTITY')
    need(direct_wall_norm.overlap(ob['Zw']) and (direct_wall_norm+total_mu).zero(),'WALL_NORM_IDENTITY')
    ratios={}; omitted=[]
    for p in cfg['parameters']:
        a=interval(results['lower']['susceptibilities'][p]); b=interval(results['upper']['susceptibilities'][p])
        if a.zero(): omitted.append(p)
        else: ratios[p]=(b/a).pack()
    return {'walls':results,'upper_over_lower_ratios':ratios,'omitted_ratios':omitted,
            'implicit_denominator':denominator.pack(),'Zext':Z.pack(),'ZA':ZA.pack(),
            'norm_identity_residual':(denominator-Z).pack(),'direct_wall_norm':direct_wall_norm.pack()}

def main():
    need(not any((ROOT/n).exists() for n in ('RESULT.json','FAILURE.json','STARTED.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('HARD_PRODUCER_CAP_900_SECONDS')))
        signal.alarm(900)
        cfg=read(ROOT/'CONFIG.json'); authenticate(cfg); put('STARTED.json',{'utc':now(),'pid':os.getpid(),'admission_sha256':sha(ROOT/'ADMISSION.json')})
        tested=controls(cfg); put('CONTROLS.json',tested)
        t2=ROOT/cfg['t2']; accepted=read(t2/'output/RESULT.json')
        need(accepted['classification'] in ('SELECTED_NEUTRAL_MODE_CHARACTERIZED','SELECTED_NEUTRAL_MODE_SEPARATION_INCONCLUSIVE'),'T2_COMPLETE_SELECTED_MODE')
        mu=I(*accepted['mu_bracket']); need(mu.hi<0,'NEGATIVE_MASS')
        per={name:evaluate(read(t2/'output'/('strip_'+name+'.json')),mu,cfg) for name in ('primary','independent')}
        combined={}; ratios={}; omitted=[]
        for wall in ('lower','upper'):
            combined[wall]={}
            for p in cfg['parameters']:
                a=interval(per['primary']['walls'][wall]['susceptibilities'][p]); b=interval(per['independent']['walls'][wall]['susceptibilities'][p])
                need(a.overlap(b),'ENGINE_SUSCEPTIBILITY_DISAGREEMENT:'+wall+':'+p)
                combined[wall][p]=a.hull(b).pack()
        for p in cfg['parameters']:
            if all(p in per[name]['upper_over_lower_ratios'] for name in per):
                a=interval(per['primary']['upper_over_lower_ratios'][p]); b=interval(per['independent']['upper_over_lower_ratios'][p])
                need(a.overlap(b),'ENGINE_RATIO_DISAGREEMENT:'+p); ratios[p]=a.hull(b).pack()
            else: omitted.append(p)
        positive=all(interval(combined[w][p]).lo>0 for w in combined for p in cfg['parameters'])
        put('RESULT.json',{'classification':'SELECTED_NEUTRAL_LOCAL_SUSCEPTIBILITIES_EVALUATED',
            'mu_bracket':accepted['mu_bracket'],'selected':cfg['selected'],'per_engine':per,
            'combined':combined,'upper_over_lower_ratios':ratios,'omitted_ratios':omitted,
            'all_eight_derivatives_strictly_positive':positive,'controls':tested,
            'scope':'Local background-preserving neutral selected-action eigenvalue derivatives; not charged evolution or finite stabilization threshold',
            'seconds':time.monotonic()-begun,'utc':now()})
    except BaseException as e:
        put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
