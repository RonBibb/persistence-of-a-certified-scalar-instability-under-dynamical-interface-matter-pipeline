"""Independent general-rate quadratic qualification; execution Linux only.

Uses the authenticated sparse polynomial algebra, not candidate source code,
to extract S6 and prove the scaled Q4 identity modulo the two constraints.
Finite rational fixtures qualify engine recurrence and wall reconstruction;
they are not physical trajectories or a continuum solution certificate.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

DEGREE = 5

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

class Jet:
    def __init__(self, value=0):
        if isinstance(value, (list, tuple)):
            self.a = tuple((list(value)+[Q(0)]*(DEGREE+1))[:DEGREE+1])
        else:
            self.a = (Q(value),)+(Q(0),)*DEGREE
    @staticmethod
    def cast(v): return v if isinstance(v, Jet) else Jet(v)
    def __add__(self, v): return Jet([a+b for a,b in zip(self.a,self.cast(v).a)])
    __radd__ = __add__
    def __neg__(self): return Jet([-a for a in self.a])
    def __sub__(self, v): return self+-self.cast(v)
    def __rsub__(self, v): return self.cast(v)+-self
    def __mul__(self, v):
        b=self.cast(v).a
        return Jet([sum((self.a[i]*b[n-i] for i in range(n+1)),Q(0)) for n in range(DEGREE+1)])
    __rmul__ = __mul__
    def __truediv__(self, v): return Jet([a/Q(v) for a in self.a])
    def __pow__(self, n):
        ans=Jet(1)
        for _ in range(n): ans=ans*self
        return ans

def evaluate(poly, values):
    ans=Jet(0)
    for powers, coefficient in poly.t.items():
        term=Jet(coefficient)
        for value,power in zip(values,powers):
            if power: term=term*value**power
        ans=ans+term
    return ans

def prepare(root):
    """Load inherited import dependencies before the pinned runtime snapshot."""
    root=Path(root)
    parent=root.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
    load(parent/'producer.py','growing_prepare_sparse')
    former=root.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
    for name in ('primary','independent'):
        load(former/(name+'.py'),'growing_prepare_'+name)

def run(root):
    assert sys.platform=='linux', 'LINUX_ONLY'
    from flint import ctx
    ctx.prec=768
    root=Path(root)
    former=root.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
    frozen=json.loads((former/'FROZEN.json').read_text())['files']
    tdir=root.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
    for path in (tdir/'producer.py',tdir/'common.py',former/'primary.py',former/'independent.py'):
        assert str(path) in frozen, 'MISSING_INHERITED_PIN:'+str(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==frozen[str(path)], 'INHERITED_SOURCE_CHANGED:'+str(path)
    t=load(tdir/'producer.py','growing_control_sparse')
    t.NAMES=('g','H','T','Phi','e','p','f','m2','h','rate')
    t.N=len(t.NAMES);t.ZERO=(0,)*t.N
    g,H,T,Phi,e,p,f,m,h,r=[t.variable(i) for i in range(t.N)]
    mu1=-r*(r+3*h);mu2=-2*r*(2*r+3*h)
    Tp=m*Phi-4*H*T;Hp=-T*T/3-h*h*e
    u=-2*H*p-T*f/3
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+(12*H*T-4*m*Phi)*p
    for key,value in dict(g=g,H=H,T=T,Phi=Phi,e=e,p=p,f=f,m=m,h=h,R=r,
                          mu1=mu1,mu2=mu2,Tp=Tp,Hp=Hp,u=u,gp=gp).items():
        setattr(t,key,value)
    t.DERIV=(gp,Hp,Tp,T,-2*H*e,u,g,t.P(0),t.P(0),t.P(0))
    gates={}
    def gate(name,value):
        gates[name]=bool(value)
        assert value,name
    rows=t.original_sources();direct={k:v.a[2] for k,v in rows.items()}
    expected={'T':r*r*(6*p*p+f*f),'M':r*(2*p*u+f*g/3),
              'K':(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p,
              'R':6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2
                  -e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)}
    bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
    first=T*g-Tp*f+(2*T*T-3*(mu1+4*h*h)*e)*p
    for key,row in rows.items():
        gate('S6_zero_'+key,(row.a[0]-(bg if key=='R' else t.P(0))).iszero())
        gate('S6_linear_'+key,(row.a[1]-(-first if key=='R' else t.P(0))).iszero())
        gate('S6_quadratic_'+key,(direct[key]-expected[key]).iszero())
    gate('background_constraint_preserved',t.ds(bg).iszero())
    gate('linear_constraint_preserved',(t.ds(first)+4*H*first).iszero())
    L=2*(2*r-h)
    cscaled=-r*(6*p*p+f*f)
    spscaled=H*cscaled-L*(p*u+f*g/6)
    scscaled=12*H*spscaled-(12*H*H-T*T)*cscaled+L*direct['R']
    sgscaled=T*t.ds(cscaled)+2*m*Phi*cscaled-6*T*spscaled-L*direct['K']
    D=2*T*T-3*(mu2+4*h*h)*e
    compatibility=t.ds(scscaled)+4*H*scscaled-T*sgscaled-D*spscaled
    gate('coprime_constraint_leads',all(min(a,b)==0 for a,b in zip(max(first.t),max(bg.t))))
    multipliers,remainder=t.divide(compatibility,[first,bg])
    gate('Q4_general_rate_scaled_identity',remainder.iszero())
    gate('Q2_trace_divisor_scaled',(r*cscaled+direct['T']).iszero())
    gate('Q2_mixed_divisor_scaled',(2*r*(spscaled-H*cscaled)+L*direct['M']).iszero())
    polys=(spscaled,sgscaled,scscaled,cscaled)
    engines=[load(root/'primary.py','growing_test_primary'),load(root/'independent.py','growing_test_independent')]
    old=[load(former/'primary.py','growing_old_primary'),load(former/'independent.py','growing_old_independent')]
    def contains(engine,ball,q):
        lo,hi=engine.bounds(ball)
        return Q(str(lo))<=q<=Q(str(hi))
    def parameters(rate):
        hh=Q(1,10)
        return dict(m2=Q(2,5),h=hh,k=hh*hh,rate=rate,mu1=-rate*(rate+3*hh),
                    mu2=-2*rate*(2*rate+3*hh),c_factor=rate/(2*(2*rate-hh)),
                    radial_v2=12*hh*hh-3*rate*rate-18*hh*rate,radial_f2=rate*rate/2)
    def sources(y,pars):
        if not pars.get('forcing',True): return [Jet(0)]*4
        W,HH,phi,TT,EE,v,ff,gg,*_=y
        values=(gg,HH,TT,phi,EE*EE,v,ff,Jet(pars['m2']),Jet(pars['h']),Jet(pars['rate']))
        return [evaluate(poly,values)/(2*(2*pars['rate']-pars['h'])) for poly in polys]
    def rhs(y,pars):
        W,HH,phi,TT,EE,v,ff,gg,vp,fp,gp,vh,fh,gh=y
        sp,sg,_,_=sources(y,pars);mass=pars['m2']
        def mode(a,b,c,mu):
            return [-2*HH*a-TT*b/3,c,-4*HH*c+(mass-mu*EE*EE+2*TT*TT)*b+(12*HH*TT-4*mass*phi)*a]
        second=mode(vp,fp,gp,pars['mu2']);second[0]+=sp;second[2]+=sg
        return [HH,-TT*TT/3-pars['k']*EE*EE,TT,mass*phi-4*HH*TT,-HH*EE]+mode(v,ff,gg,pars['mu1'])+second+mode(vh,fh,gh,pars['mu2'])
    fixtures=[list(map(Q,[0,-1,Q(1,9),Q(-1,7),1,Q(2,9),Q(3,11),Q(-2,13),Q(1,8),Q(-1,10),Q(1,12),1,Q(1,5),Q(-1,6)])),
              list(map(Q,[0,Q(-2,3),Q(1,7),0,1,Q(-1,8),Q(2,9),Q(1,5),Q(-1,4),Q(1,11),Q(-1,13),1,Q(-1,5),Q(1,6)]))]
    counts={'coefficient_containments':0,'source_containments':0}
    for rate in (Q(21,200),Q(-3,5)):
        for fi,y in enumerate(fixtures):
            for forcing in (True,False):
                pars=dict(parameters(rate),forcing=forcing)
                exact=[[v] for v in y]
                for degree in range(DEGREE):
                    dy=rhs([Jet(v) for v in exact],pars)
                    for row,value in zip(exact,dy):row.append(value.a[degree]/(degree+1))
                for ei,engine in enumerate(engines):
                    ids=list(range(14)) if ei==0 else [i for i in range(14) if i!=4]
                    state=[engine.exact(y[i]) for i in ids]
                    pp={k:(v if isinstance(v,bool) else engine.exact(v)) for k,v in pars.items()}
                    actual=engine.coeff(state,DEGREE,pp)
                    label=f'{rate}_{fi}_{forcing}_{ei}'
                    gate('dimension_'+label,len(actual)==len(ids) and all(len(row)==DEGREE+1 for row in actual))
                    for j,i in enumerate(ids):
                        for degree in range(DEGREE+1):
                            gate(f'coeff_{label}_{i}_{degree}',contains(engine,actual[j][degree],exact[i][degree]))
                            counts['coefficient_containments']+=1
                    ss=engine.sources(state,pp)
                    ss=list(ss) if ei==0 else [ss[k] for k in ('Sp','Sg','Sc','c2')]
                    for j,val in enumerate(sources([Jet(v) for v in y],pars)):
                        gate(f'source_{label}_{j}',contains(engine,ss[j],val.a[0]));counts['source_containments']+=1
                    if rate==Q(-3,5):
                        oe=old[ei];oy=[oe.exact(y[i]) for i in ids]
                        op={k:(v if isinstance(v,bool) else oe.exact(v)) for k,v in pars.items()}
                        oc=oe.coeff(oy,DEGREE,op)
                        gate('forced_parent_reduction_'+label,all(contains(oe,oc[j][n],exact[i][n]) for j,i in enumerate(ids) for n in range(DEGREE+1)))
    # Direct Q5 expansion has xi1=0: normal e^(2 eta p)(T+eta g),
    # oscillator E²e^(-2 eta p)[eta(r²+3hr)chi+2eta²r²pchi].
    wall=load(root/'wall.py','growing_test_wall');engine=engines[0]
    for fi,y in enumerate(fixtures):
        pars=parameters(Q(21,200));rr,hh=pars['rate'],pars['h']
        W,HH,phi,TT,EE,v,ff,gg,*_=y
        d1=2-pars['mu1']*EE*EE;d2=2-pars['mu2']*EE*EE
        chi=ff/d1;tp=pars['m2']*phi-4*HH*TT
        o=EE*EE*(2*rr*rr-2*rr*(rr+3*hh))*v*chi
        j=2*v*gg+2*TT*v*v;c=-pars['c_factor']*(6*v*v+ff*ff);Gamma=21-1/d2
        for sigma in (1,-1):
            xi=sigma*rr*chi*chi/(4*(2*rr-hh))
            loadR=2*sigma*(TT*c-(tp-sigma*Gamma*TT/2)*xi-j+sigma*o/(2*d2))
            expected=dict(chi1=chi,xi2=xi,c2=c,o2=o,j2=j,Gamma2=Gamma,R2=loadR,d2=d2,Tp=tp,
                          qI=-rr*rr*EE*EE*chi*chi/2,divisor=sigma*EE*EE*2*rr*(2*rr-hh))
            pp={k:engine.exact(vv) for k,vv in pars.items()}
            state=[engine.exact(vv) for vv in y];ww=wall.reconstruct(state,pp,sigma)
            gate(f'wall_direct_values_{fi}_{sigma}',all(contains(engine,ww[k],v0) for k,v0 in expected.items()))
            yy=list(y);yy[10]=(Gamma*yy[9]+loadR)/(2*sigma)-2*TT*yy[8]
            out=wall.residuals([engine.exact(vv) for vv in yy],ww,pp,sigma)
            gate(f'wall_all_rows_{fi}_{sigma}',all(value.contains(0) for value in out.values()))
            changed=list(yy);changed[10]+=Q(1,7)
            bad=wall.residuals([engine.exact(vv) for vv in changed],ww,pp,sigma)
            gate(f'wall_wrong_slope_detected_{fi}_{sigma}',not bad['scalar_normal'].contains(0) and not bad['robin'].contains(0))
    gate('source_mutation_KG_sign',not (direct['K']+expected_source_K(t,mu1,p,f,e,m)).iszero())
    return {'pass':True,'all_gates':all(gates.values()),'classification':'GENERAL_RATE_QUADRATIC_SOURCE_AND_ENGINE_CONTROLS_PASS',
            'gate_count':len(gates),'gates':gates,'counts':counts,
            'exact_Q4_scaled_multipliers':[v.pack() for v in multipliers],
            'new_physical_integrations':0,
            'scope':'Exact general-rate S6 and scaled Q4 identities; rational degree-five two-engine recurrence, forced-parent reduction, direct wall values and Q5/Q6 elimination. No physical trajectory or full nonlinear solution.'}

def expected_source_K(t,mu1,p,f,e,m):
    """Deliberately reverse the pf contribution; a nonzero defect is required."""
    return -t.original_sources()['K'].a[2]+2*(4*m-6*mu1*e)*p*f

if __name__=='__main__':
    print(json.dumps(run(Path(__file__).resolve().parent),indent=2))

