"""Independent narrow qualification. Linux only; no physical trajectory run.

Fraction radial jets evaluate the already-qualified direct S6 polynomials,
not either candidate source evaluator. Main must review/freeze this checker.
"""
import sys
sys.dont_write_bytecode=True
import importlib.util
from math import factorial
from fractions import Fraction as Q
from pathlib import Path
N=5
class J:
    def __init__(self,v=0):
        self.a=tuple((list(v)+[Q(0)]*(N+1))[:N+1]) if isinstance(v,(list,tuple)) else (Q(v),)+(Q(0),)*N
    @staticmethod
    def cast(v):return v if isinstance(v,J) else J(v)
    def __add__(self,v):return J([a+b for a,b in zip(self.a,J.cast(v).a)])
    __radd__=__add__
    def __neg__(self):return J([-a for a in self.a])
    def __sub__(self,v):return self+-J.cast(v)
    def __rsub__(self,v):return J.cast(v)+-self
    def __mul__(self,v):
        b=J.cast(v).a
        return J([sum((self.a[i]*b[n-i] for i in range(n+1)),Q(0)) for n in range(N+1)])
    __rmul__=__mul__
    def __truediv__(self,v):return J([a/Q(v) for a in self.a])
    def __pow__(self,n):
        r=J(1)
        for _ in range(n):r=r*self
        return r
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def evaluate(poly,values):
    total=J(0)
    for powers,c in poly.t.items():
        term=J(c)
        for v,n in zip(values,powers):
            if n:term=term*v**n
        total=total+term
    return total
def run(root):
    assert sys.platform=='linux','LINUX_ONLY'
    from flint import ctx,fmpq
    ctx.prec=768
    root=Path(root)
    parent=root.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION'
    t15=load(parent/'T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py','control_t15')
    t15.initialize()
    direct={k:v.a[2] for k,v in t15.original_sources().items()}
    compatibility,polys=t15.compatibility(direct)
    engines=[load(root/'primary.py','control_primary'),load(root/'independent.py','control_independent')]
    oldroot=parent/'T20_AB_SECOND_HARMONIC_HOMOGENEOUS_INVERSE/engine'
    oldengines=[load(oldroot/'primary_interval.py','control_old_primary'),load(oldroot/'independent_interval.py','control_old_independent')]
    gates={};counts={'coefficient_containments':0,'source_containments':0}
    def gate(n,v):
        gates[n]=bool(v)
        assert v,n
    def contains(engine,ball,q):
        lo,hi=engine.bounds(ball);return Q(str(lo))<=q<=Q(str(hi))
    bg=6*t15.H*t15.H-t15.T*t15.T/2-6+t15.m*t15.Phi*t15.Phi/2-6*t15.h*t15.h*t15.e
    first=t15.T*t15.g-t15.Tp*t15.f+(2*t15.T*t15.T-3*(t15.mu1+4*t15.h*t15.h)*t15.e)*t15.p
    _,remainder=t15.divide(compatibility,[first,bg])
    gate('exact_source_compatibility_modulo_constraints',remainder.iszero())
    def src(y,p):
        if not p.get('forcing',True):return [J(0)]*4
        W,H,phi,T,E,v,f,g,*_=y
        vals=(g,H,T,phi,E*E,v,f,J(p['m2']),J(p['h']))
        return [evaluate(polys[k],vals) for k in ('Sp2','Sg2','Sc2','c2')]
    def rhs(y,p):
        W,H,phi,T,E,v,f,g,vp,fp,gp,vh,fh,gh=y
        sp,sg,sc,c2=src(y,p);m=p['m2'];k=p['k']
        def mode(a,b,c,mu):return [-2*H*a-T*b/3,c,-4*H*c+(m-mu*E*E+2*T*T)*b+(12*H*T-4*m*phi)*a]
        z=mode(vp,fp,gp,p['mu2']);z[0]+=sp;z[2]+=sg
        return [H,-T*T/3-k*E*E,T,m*phi-4*H*T,-H*E]+mode(v,f,g,p['mu1'])+z+mode(vh,fh,gh,p['mu2'])
    def exact_coeff(y,p):
        rows=[[Q(v)] for v in y]
        for n in range(N):
            r=rhs([J(x) for x in rows],p)
            for row,j in zip(rows,r):row.append(j.a[n]/(n+1))
        return rows
    fixtures=[list(map(Q,[0,-1,Q(1,9),Q(-1,7),1,Q(2,9),Q(3,11),Q(-2,13),Q(1,8),Q(-1,10),Q(1,12),1,Q(1,5),Q(-1,6)])),
              list(map(Q,[0,Q(-2,3),Q(1,7),0,1,Q(-1,8),Q(2,9),Q(1,5),Q(-1,4),Q(1,11),Q(-1,13),1,Q(-1,5),Q(1,6)]))]
    pars={'m2':Q(2,5),'h':Q(1,10),'k':Q(1,100),'mu1':Q(-18,100),'mu2':Q(-108,100)}
    for fi,y in enumerate(fixtures):
        for forcing in (True,False):
            p=dict(pars,forcing=forcing);expected=exact_coeff(y,p)
            for ei,e in enumerate(engines):
                ids=list(range(14)) if ei==0 else [i for i in range(14) if i!=4]
                yy=[e.exact(y[i]) for i in ids];pp={k:(v if isinstance(v,bool) else e.exact(v)) for k,v in p.items()}
                actual=e.coeff(yy,N,pp)
                gate(f'dimension_{fi}_{forcing}_{ei}',len(actual)==len(ids) and all(len(row)==N+1 for row in actual))
                for j,i in enumerate(ids):
                    for n in range(N+1):
                        gate(f'coefficient_{fi}_{forcing}_{ei}_{i}_{n}',contains(e,actual[j][n],expected[i][n]));counts['coefficient_containments']+=1
                ss=e.sources(yy,pp);ss=list(ss) if ei==0 else [ss[k] for k in ('Sp','Sg','Sc','c2')]
                for j,val in enumerate(src([J(v) for v in y],p)):
                    gate(f'source_{fi}_{forcing}_{ei}_{j}',contains(e,ss[j],val.a[0]));counts['source_containments']+=1
                # RHS is separately checked against the derivative coefficient.
                rr=e.rhs(yy,pp)
                gate(f'rhs_{fi}_{forcing}_{ei}',all(contains(e,rr[j],expected[i][1]) for j,i in enumerate(ids)))
                if not forcing:
                    old=oldengines[ei]
                    for offset,mu in ((5,p['mu1']),(8,p['mu2']),(11,p['mu2'])):
                        subset=(list(range(5)) if ei==0 else list(range(4)))+list(range(offset,offset+3))
                        convert=old.exact if ei==0 else old.exact_ball
                        oy=[convert(y[i]) for i in subset]
                        op={k:convert(v) for k,v in {'m2':p['m2'],'k':p['k'],'mu':mu}.items()}
                        oc=old.coeff(oy,N,op) if ei==0 else old.taylor_coefficients(oy,N,op)
                        gate(f'parent_source_off_{fi}_{ei}_{offset}',all(contains(old,oc[j][n],expected[i][n]) for j,i in enumerate(subset) for n in range(N+1)))
    # Manufactured polynomial solution of the augmented equations: flat zero
    # background/mass, f1=1+2s, g1=2, p1=0. Loaded p2=-s/3-s²/3.
    # This checks forced integration, not a physical constrained AB fixture.
    y=[Q(0)]*14;y[4]=Q(1);y[6]=Q(1);y[7]=Q(2)
    p={k:Q(0) for k in ('m2','h','k','mu1','mu2')};p['forcing']=True
    expected=exact_coeff(y,p)
    gate('manufactured_exact_nonzero_source',expected[8]==[Q(0),Q(-1,3),Q(-1,3),Q(0),Q(0),Q(0)])
    for ei,e in enumerate(engines):
        ids=list(range(14)) if ei==0 else [i for i in range(14) if i!=4]
        yy=[e.exact(y[i]) for i in ids];pp={k:(v if isinstance(v,bool) else e.exact(v)) for k,v in p.items()}
        end,cell=e.step(yy,fmpq(1,1024),pp)
        gate(f'manufactured_full_cell_{ei}',cell['picard_iterations']>0 and len(cell['box'])==len(ids))
        for j,i in enumerate(ids):
            value=sum(expected[i][n]*Q(1,1024)**n for n in range(N+1))
            gate(f'manufactured_endpoint_{ei}_{i}',contains(e,end[j],value))
    # Constrained nonzero-forcing fixture: H=-1, W=-s, E=exp(s),
    # p1=exp(2s), p2P=-4/13*(exp(4s)-exp(2s)), p2H=exp(2s).
    # All scalar fields vanish, FI=0, all constraints=0 and Q6 loads=0.
    # Its degenerate graph sector is not a physical AB wall fixture.
    y=[Q(0)]*14;y[1]=Q(-1);y[4]=y[5]=y[11]=Q(1)
    p={k:Q(0) for k in ('m2','h','k','mu1','mu2')};p['forcing']=True
    expected=exact_coeff(y,p)
    for n in range(N+1):
        gate(f'constrained_exact_p1_{n}',expected[5][n]==Q(2**n,factorial(n)))
        gate(f'constrained_exact_loaded_{n}',expected[8][n]==-Q(4,13)*Q(4**n-2**n,factorial(n)))
    def expbounds(x):
        terms=[x**n/factorial(n) for n in range(41)]
        lo=sum(terms,Q(0));upper=lo+x**41/factorial(41)/(1-x/42)
        return lo,upper
    h=Q(1,1024);eh=expbounds(h);e2=expbounds(2*h);e4=expbounds(4*h)
    endpoint=[(Q(0),Q(0))]*14
    endpoint[0]=(-h,-h);endpoint[1]=(Q(-1),Q(-1));endpoint[4]=eh;endpoint[5]=endpoint[11]=e2
    endpoint[8]=(-Q(4,13)*(e4[1]-e2[0]),-Q(4,13)*(e4[0]-e2[1]))
    for ei,e in enumerate(engines):
        ids=list(range(14)) if ei==0 else [i for i in range(14) if i!=4]
        yy=[e.exact(y[i]) for i in ids];pp={k:(v if isinstance(v,bool) else e.exact(v)) for k,v in p.items()}
        end,cell=e.step(yy,fmpq(1,1024),pp)
        for j,i in enumerate(ids):
            lo,hi=endpoint[i];gate(f'constrained_endpoint_{ei}_{i}',contains(e,end[j],lo) and contains(e,end[j],hi))
        gate(f'constrained_whole_cell_{ei}',all(v.contains(0) for v in e.constraints(cell['box'],pp).values()) and e.first_integral(cell['box'],pp).contains(0))
        canon=e.physical(end);_,H,phi,T,E,v,f,g,vp,fp,gp,vh,fh,gh=canon
        for sigma in (1,-1):
            gate(f'constrained_Q6_{ei}_{sigma}',(2*sigma*(gp+2*T*vp)-(e.exact(21)-e.exact(Q(1,2)))*fp).contains(0))
    # Targeted polynomial mutations must change the independent direct oracle
    # at the nonzero fixture; this tests sensitivity, not production rescoring.
    yy=[J(v) for v in fixtures[0]];W,H,phi,T,E,v,f,g,*_=yy
    vals=(g,H,T,phi,E*E,v,f,J(pars['m2']),J(pars['h']))
    mutations={'qK_sign':2*evaluate(direct['K'],vals),
               'c2prime_sign':-2*T*(-J(Q(3,13))*(12*v*(-2*H*v-T*f/3)+2*f*g)),
               'Sc_omitted_time_stress':18*pars['k']*E*E*f*f}
    baseline=src([J(v) for v in fixtures[0]],pars)
    for name,d in mutations.items():
        gate('mutation_'+name,d.a[0]!=0)
        source_index=2 if name=='Sc_omitted_time_stress' else 1
        for ei,e in enumerate(engines):
            ids=list(range(14)) if ei==0 else [i for i in range(14) if i!=4]
            state=[e.exact(fixtures[0][i]) for i in ids];pp={k:e.exact(v) for k,v in pars.items()}
            ss=e.sources(state,pp);ss=list(ss) if ei==0 else [ss[k] for k in ('Sp','Sg','Sc','c2')]
            gate(f'mutant_excluded_{name}_{ei}',not contains(e,ss[source_index],baseline[source_index].a[0]+d.a[0]))
    # Exact transport sign fixture: X=1+s,b=2+3s, integral (Xb)'=8.
    gate('transport_product_rule',Q(3)+Q(2)+Q(6,2)==Q(2)*Q(5)-Q(1)*Q(2))
    gate('transport_wrong_sign_detected',-(Q(3)+Q(2)+Q(6,2))!=Q(8))
    return {'classification':'INDEPENDENT_AUGMENTED_RECURRENCE_CONTROLS_PASS','all_gates':all(gates.values()),'gate_count':len(gates),'counts':counts,'gates':gates,'new_physical_integrations':0,
            'scope':'Two fixed rational recurrence fixtures including T=0; degree-five exact direct-S6 polynomial oracle; source-off and nonphysical manufactured forced step. Not a proof at every state or a physical AB trajectory.'}
if __name__=='__main__':
    import json
    print(json.dumps(run(Path(__file__).resolve().parent),indent=2))
