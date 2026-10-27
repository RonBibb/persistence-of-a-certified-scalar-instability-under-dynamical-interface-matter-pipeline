"""Independent cubic source/augmented recurrence qualification, Linux only.

Certified exact polynomial records are the cubic oracle. Degree-five rational
radial jets are independent of the candidate Arb recurrences. No numerical
evolution or source work occurs at import; prepare() only loads dependencies.
"""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json
from fractions import Fraction as Q
from pathlib import Path
ORDER=5
_cache=None

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def prepare(root):
    global _cache
    assert sys.platform=='linux','LINUX_ONLY'
    if _cache is not None:return
    root=Path(root);base=root.parent;bp=base/'20261026_GROWING_MODE_CUBIC_BULK'
    assert sha(bp/'RESULT.json')=='d7b513c1796e081896f442d8cec9a2bb13c771db9e6ae3939cf13634a47df6eb'
    assert sha(bp/'bulk.py')=='b3af563119b75a4e4da00815ad9da684b6fe0796fb3e2528541a57db32c4aad8'
    binding=json.loads((bp/'BINDING.json').read_text())
    # Authenticate imported sparse ring, common helper, and cubic series before
    # the symbolic module imports them. Bind the entire existing input map.
    for path,digest in binding['files'].items():assert sha(path)==digest,'BULK_INPUT:'+path
    terminal=json.loads((bp/'TERMINAL.json').read_text())
    assert terminal['pass'] and terminal['result_sha256']==sha(bp/'RESULT.json') and terminal['binding_sha256']==sha(bp/'BINDING.json')
    b=load('flow_control_qualified_bulk',bp/'bulk.py')
    source=load('flow_control_candidate_sources',root/'sources.py')
    record=json.loads((bp/'RESULT.json').read_text());assert record['pass']
    _cache=(b,source,record)

class J:
    def __init__(self,v=0):
        self.a=tuple((list(v)+[Q(0)]*(ORDER+1))[:ORDER+1]) if isinstance(v,(tuple,list)) else (Q(v),)+(Q(0),)*ORDER
    @staticmethod
    def cast(x):return x if isinstance(x,J) else J(x)
    def __add__(self,x):return J([a+b for a,b in zip(self.a,self.cast(x).a)])
    __radd__=__add__
    def __neg__(self):return J([-a for a in self.a])
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        b=self.cast(x).a
        return J([sum((self.a[i]*b[n-i] for i in range(n+1)),Q(0)) for n in range(ORDER+1)])
    __rmul__=__mul__
    def __truediv__(self,x):return J([a/Q(x) for a in self.a])
    def __pow__(self,n):
        value=J(1)
        for _ in range(n):value=value*self
        return value

def eval_record(poly,values):
    result=J(0)
    for term in poly:
        v=J(Q(term['coefficient']))
        for value,power in zip(values,term['powers']):
            if power:v=v*value**power
        result=result+v
    return result

def run(root,engines,initial=None):
    assert sys.platform=='linux','LINUX_ONLY'
    prepare(root);b,source,record=_cache;b.setup()
    gates={};counts={'source_coefficients':0,'radial_coefficients':0}
    def gate(label,ok):gates[label]=bool(ok);assert ok,label
    def contains(m,ball,q):
        lo,hi=m.bounds(ball);return Q(str(lo))<=q<=Q(str(hi))
    params=dict(m2=b.m,k=b.h*b.h,rate=b.r,h=b.h,mu1=b.mu1,mu2=b.mu2,c_factor=b.C,c3_factor=b.J)
    candidate=source.cubic(b.H,b.T,b.Phi,b.e,b.p,b.f,b.g,b.P,b.F,b.G,params)
    gate('qualified_variable_order',list(b.ring.NAMES)==record['variables'])
    for key in ('c3','Sp3','Sc3','Sg3'):
        stored=b.ring.P({tuple(v['powers']):Q(v['coefficient']) for v in record['sources'][key]})
        gate('exact_symbolic_candidate_'+key,(candidate[key]-stored).iszero())
    def parameters(A2,rate=Q(21,200)):
        h=Q(1,10)
        return dict(m2=Q(2,5),k=h*h,h=h,rate=rate,mu1=-rate*(rate+3*h),
                    mu2=-2*rate*(2*rate+3*h),mu3=-3*rate*(3*rate+3*h),
                    c_factor=rate/(2*(2*rate-h)),c3_factor=4*rate/(3*(3*rate-h)),
                    radial_v2=12*h*h-3*rate*rate-18*h*rate,radial_f2=rate*rate/2,A2=A2)
    def third(y,p):
        W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=y[:14]
        P=ap+p['A2']*ah;F=fp+p['A2']*fh;G=gp+p['A2']*gh
        vals=dict(G=G,g=g,H=H,T=T,Phi=Phi,e=E*E,p=a,f=f,P=P,F=F,
                  m=J(p['m2']),C=J(p['c_factor']),J=J(p['c3_factor']),r=J(p['rate']),h=J(p['h']))
        ordered=[vals[k] for k in record['variables']]
        return {key:eval_record(record['sources'][key],ordered) for key in ('c3','Sp3','Sc3','Sg3')}
    def second(y,p):
        W,H,Phi,T,E,a,f,g=y[:8];r=p['rate'];h=p['h'];mass=p['m2']
        u=-2*H*a-T*f/3;cp=-p['c_factor']*(12*a*u+2*f*g);c=-p['c_factor']*(6*a*a+f*f)
        sp=H*c-a*u-f*g/6
        # Unreduced direct S6 scalar source, rather than candidate's compact
        # (4m-6mu1 E²)pf form. The first-mode ODE supplies f''.
        fpp=-4*H*g+(mass-p['mu1']*E*E+2*T*T)*f+(12*H*T-4*mass*Phi)*a
        qk=2*E*E*r*(r+3*h)*a*f+6*u*g+4*a*(fpp+4*H*g+6*T*u)+8*mass*Phi*a*a
        sg=T*cp+2*mass*Phi*c-6*T*sp-qk
        return sp,sg
    def rhs(y,p):
        W,H,Phi,T,E=y[:5];mass=p['m2'];sp2,sg2=second(y,p);s=third(y,p)
        def mode(j,mu,sp=0,sg=0):
            a,f,g=y[j:j+3]
            return [-2*H*a-T*f/3+sp,g,-4*H*g+(mass-mu*E*E+2*T*T)*f+(12*H*T-4*mass*Phi)*a+sg]
        return [H,-T*T/3-p['k']*E*E,T,mass*Phi-4*H*T,-H*E]+mode(5,p['mu1'])+mode(8,p['mu2'],sp2,sg2)+mode(11,p['mu2'])+mode(14,p['mu3'],s['Sp3'],s['Sg3'])+mode(17,p['mu3'])
    fixtures=[list(map(Q,[0,-1,Q(1,9),Q(-1,7),1,Q(2,9),Q(3,11),Q(-2,13),Q(1,8),Q(-1,10),Q(1,12),1,Q(1,5),Q(-1,6),Q(1,19),Q(-1,17),Q(1,23),1,Q(2,17),Q(-1,29)])),
              list(map(Q,[0,Q(-2,3),Q(1,7),0,1,Q(-1,8),Q(2,9),Q(1,5),Q(-1,4),Q(1,11),Q(-1,13),1,Q(-1,5),Q(1,6),Q(-1,17),Q(1,23),Q(-1,19),1,Q(-2,17),Q(1,29)]))]
    for fi,y in enumerate(fixtures):
        for amp in (Q(0),Q(-2,7)):
            p=parameters(amp);coeff=[[v] for v in y]
            for n in range(ORDER):
                deriv=rhs([J(row) for row in coeff],p)
                for row,value in zip(coeff,deriv):row.append(value.a[n]/(n+1))
            expected=third([J(row) for row in coeff],p)
            # Separate local scalar/jet implementation must match qualified
            # polynomial records at every radial coefficient of this fixture.
            z=[J(row) for row in coeff];W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=z[:14]
            actual=source.cubic(H,T,Phi,E*E,a,f,g,ap+amp*ah,fp+amp*fh,gp+amp*gh,p)
            for key in expected:
                for n in range(ORDER+1):
                    gate(f'exact_jet_source_{fi}_{amp}_{key}_{n}',actual[key].a[n]==expected[key].a[n]);counts['source_coefficients']+=1
            for name,m in engines.items():
                ids=list(range(20)) if name=='primary' else [i for i in range(20) if i!=4]
                yy=[m.exact(y[i]) for i in ids];pp={k:m.exact(v) for k,v in p.items()}
                result=m.coeff(yy,ORDER,pp)
                gate(f'dimension_{fi}_{amp}_{name}',len(result)==len(ids) and all(len(row)==ORDER+1 for row in result))
                for j,i in enumerate(ids):
                    for n in range(ORDER+1):
                        gate(f'radial_{fi}_{amp}_{name}_{i}_{n}',contains(m,result[j][n],coeff[i][n]));counts['radial_coefficients']+=1
                derivative=m.rhs(yy,pp)
                gate(f'point_rhs_{fi}_{amp}_{name}',all(contains(m,derivative[j],coeff[i][1]) for j,i in enumerate(ids)))
                physical=m.physical(yy)
                gate(f'canonical_state_{fi}_{amp}_{name}',len(physical)==20 and all(contains(m,value,y[i]) for i,value in enumerate(physical)))
                # Removing cubic forcing changes the derivative for this
                # nonzero fixture; dropping the cubic load is detectable.
                s0=third([J(v) for v in y],p)
                shift=0 if name=='primary' else -1
                gate(f'omitted_Sp3_detected_{fi}_{amp}_{name}',not contains(m,derivative[14+shift],coeff[14][1]-s0['Sp3'].a[0]))
                gate(f'omitted_Sg3_detected_{fi}_{amp}_{name}',not contains(m,derivative[16+shift],coeff[16][1]-s0['Sg3'].a[0]))
    return {'pass':True,'all_gates':all(gates.values()),'classification':'INDEPENDENT_GENERAL_RATE_CUBIC_AUGMENTED_CONTROLS_PASS',
            'gate_count':len(gates),'gates':gates,'counts':counts,
            'qualified_bulk_result_sha256':'d7b513c1796e081896f442d8cec9a2bb13c771db9e6ae3939cf13634a47df6eb',
            'physical_initial_callback_used':False,'new_physical_integrations':0,
            'scope':'Exact all-variable cubic source equality to qualified polynomial records, degree-five rational radial-jet oracle on two fixtures and two A2 values, including T=0, tested against both augmented engines. No physical trajectory or fresh Picard-tube proof.'}

if __name__=='__main__':
    raise SystemExit('Use the authenticated owning runner: prepare(root), then run(root, engines).')
