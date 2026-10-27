"""Exact symbolic affine identity controls. Linux runner owns authentication."""
import importlib.util,sys
from pathlib import Path
from fractions import Fraction as Q
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def prepare(root):
    global ring,source,wall,oracle
    assert sys.platform=='linux'
    root=Path(root)
    ring=load('affine_independent_polynomial_ring',root.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
    source=load('affine_source_controls',root/'sources_affine.py');wall=load('affine_wall_controls',root/'wall_affine.py')
    oracle=load('affine_rational_jet_utility',root.parent/'20261026_GROWING_MODE_CUBIC_FLOW/controls.py')
    oracle.prepare(root.parent/'20261026_GROWING_MODE_CUBIC_FLOW')
def run(root,engines=None,initial=None):
    assert sys.platform=='linux'
    if 'ring' not in globals():prepare(root)
    names=('H','T','Phi','E','a','f','g','P','F','G','Ph','Fh','Gh','r','h','m','C','J','A','Tp','u','gp','c','x','chi','chi2','chih','c3','c3h')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    v={k:ring.variable(i) for i,k in enumerate(names)};globals_unused=None
    H,T,Phi,E,a,f,g,P,F,G,Ph,Fh,Gh,r,h,m,C,J,A,Tp,u,gp,c,x,chi,chi2,chih,c3,c3h=[v[k] for k in names]
    p=dict(m2=m,k=h*h,rate=r,h=h,mu1=-r*(r+3*h),mu2=-2*r*(2*r+3*h),c_factor=C,c3_factor=J)
    z=[ring.P(0),H,Phi,T,E,a,f,g,P,F,G,Ph,Fh,Gh];s0,s1=source.channels(z,p)
    full=source.base.cubic(H,T,Phi,E*E,a,f,g,P+A*Ph,F+A*Fh,G+A*Gh,p)
    gates={}
    def eq(n,q):gates[n]=q.iszero();assert gates[n],n
    for key in ('c3','Sp3','Sc3','Sg3'):eq('all_variable_source_affinity_'+key,full[key]-s0[key]-A*s1[key])
    w=dict(E=E,rate=r,h=h,H=H,T=T,Tp=Tp,p1=a,u1=u,f1=f,g1=g,g1prime=gp,p2=P,f2=F,g2=G,c2=c,xi2=x,chi1=chi,chi2=chi2,c3=c3)
    tangent=dict(p2=Ph,f2=Fh,g2=Gh,chi2=chih,c3=c3h)
    for sigma in (-1,1):
        b,d=wall.polynomial_channels(w,tangent,sigma)
        shifted=dict(w,**{k:w[k]+A*tangent[k] for k in tangent});whole=wall.base.closed(shifted,sigma)
        for key in ('qI3','o3','j3','c3_numerator'):eq(f'wall_affinity_{sigma}_{key}',whole[key]-b[key]-A*d[key])
        dg=b['graph_divisor'];dn=b['d3']
        # Multiplying the Robin load by dg*dn clears fixed graph/oscillator
        # denominators without dividing symbolic polynomials.
        def scaled(s,cubic):
            xnum=-s['qI3']
            return 2*sigma*(T*cubic*dg*dn-Tp*xnum*dn-s['j3']*dg*dn)+(21*dn-1)*T*xnum+s['o3']*dg
        eq(f'full_eliminated_robin_affinity_{sigma}',scaled(whole,c3+A*c3h)-scaled(b,c3)-A*scaled(d,c3h))
        eq(f'graph_divisor_unchanged_{sigma}',whole['graph_divisor']-dg)
        eq(f'oscillator_divisor_unchanged_{sigma}',whole['d3']-dn)
    counts={'radial_coefficients':0}
    if engines is not None:
        Jet=oracle.J;record=oracle._cache[2]
        h=Q(1,10);r=Q(21,200)
        pars=dict(m2=Q(2,5),k=h*h,h=h,rate=r,mu1=-r*(r+3*h),mu2=-2*r*(2*r+3*h),mu3=-3*r*(3*r+3*h),c_factor=r/(2*(2*r-h)),c3_factor=4*r/(3*(3*r-h)),radial_v2=12*h*h-3*r*r-18*h*r,radial_f2=r*r/2)
        def exact_sources(y):
            W,H,Phi,T,E,a,f,g,P,F,G,Ph,Fh,Gh=y[:14]
            values=dict(G=G,g=g,H=H,T=T,Phi=Phi,e=E*E,p=a,f=f,P=P,F=F,m=Jet(pars['m2']),C=Jet(pars['c_factor']),J=Jet(pars['c3_factor']),r=Jet(r),h=Jet(h))
            ordered=[values[k] for k in record['variables']];direction={'P':Ph,'F':Fh,'G':Gh}
            zero={};deriv={}
            for key in ('c3','Sp3','Sc3','Sg3'):
                zero[key]=oracle.eval_record(record['sources'][key],ordered);v=Jet(0)
                for term in record['sources'][key]:
                    for field,tangent in direction.items():
                        j=record['variables'].index(field);degree=term['powers'][j]
                        if degree:
                            powers=list(term['powers']);powers[j]-=1
                            v+=tangent*oracle.eval_record([dict(coefficient=str(Q(term['coefficient'])*degree),powers=powers)],ordered)
                deriv[key]=v
            return zero,deriv
        def rhs(y):
            W,H,Phi,T,E,a,f,g=y[:8];m=pars['m2'];u=-2*H*a-T*f/3
            c=-pars['c_factor']*(6*a*a+f*f);cp=-pars['c_factor']*(12*a*u+2*f*g);sp=H*c-a*u-f*g/6
            gp=-4*H*g+(m-pars['mu1']*E*E+2*T*T)*f+(12*H*T-4*m*Phi)*a
            qk=2*E*E*r*(r+3*h)*a*f+6*u*g+4*a*(gp+4*H*g+6*T*u)+8*m*Phi*a*a
            sg=T*cp+2*m*Phi*c-6*T*sp-qk;s0,s1=exact_sources(y)
            def mode(j,mu,sp=0,sg=0):
                a,f,g=y[j:j+3]
                return [-2*H*a-T*f/3+sp,g,-4*H*g+(m-mu*E*E+2*T*T)*f+(12*H*T-4*m*Phi)*a+sg]
            return [H,-T*T/3-pars['k']*E*E,T,m*Phi-4*H*T,-H*E]+mode(5,pars['mu1'])+mode(8,pars['mu2'],sp,sg)+mode(11,pars['mu2'])+mode(14,pars['mu3'],s0['Sp3'],s0['Sg3'])+mode(17,pars['mu3'],s1['Sp3'],s1['Sg3'])+mode(20,pars['mu3'])
        for fi,T0 in enumerate((Q(-1,7),Q(0))):
            y=[Q(0),Q(-1),Q(1,9),T0,Q(1)]+[Q((-1)**j,j+3) for j in range(18)]
            coeff=[[v] for v in y]
            for n in range(5):
                dy=rhs([Jet(v) for v in coeff])
                for row,v in zip(coeff,dy):row.append(v.a[n]/(n+1))
            for name,m in engines.items():
                ids=list(range(23)) if name=='primary' else [i for i in range(23) if i!=4]
                yy=[m.exact(y[i]) for i in ids];pp={k:m.exact(v) for k,v in pars.items()}
                got=m.coeff(yy,5,pp)
                assert len(got)==len(ids)
                for j,i in enumerate(ids):
                    assert len(got[j])==6
                    for n in range(6):
                        lo,hi=map(lambda x:Q(str(x)),m.bounds(got[j][n]));label=f'exact_radial_{fi}_{name}_{i}_{n}'
                        gates[label]=lo<=coeff[i][n]<=hi;assert gates[label],label;counts['radial_coefficients']+=1
    return {'pass':True,'gate_count':len(gates),'gates':gates,'counts':counts,'classification':'EXACT_GENERAL_RATE_CUBIC_AFFINITY_PASS','scope':'All-variable polynomial identities for analytic source derivatives, wall graph/scalar/oscillator loads and denominator-cleared full Robin elimination. Independent exact qualified-polynomial derivative oracle for degree-five augmented radial recurrence when engines supplied. No interval differencing, ODE integration or finite-amplitude result.'}
