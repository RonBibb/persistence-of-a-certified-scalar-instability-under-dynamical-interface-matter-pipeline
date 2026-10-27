"""Exact nonlinear proper-coordinate endpoint algebra; no physical integration.

Derives the original closed-chart time jets before imposing any endpoint-only
relations. Scalar Robin or Israel conditions are never normally differentiated.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
import sympy as S


def derive(original_code):
    p,phi,t,u,v,w,z,q,a,m,c = S.symbols('p Phi t u v w z q alpha2 m2 c')
    potential=-6+m*phi*phi/2
    ps=q-2*p*p-t*t/6-potential/3
    variables=[p,phi,t,u,v,w,q,a]
    flow=[ps,t,u,v,w,z,-2*p*q,2*p*a]
    def D(f):return S.expand(sum(S.diff(f,x)*dx for x,dx in zip(variables,flow)))
    SA=ps+4*p*p-2*q+S.Rational(2,3)*potential
    SL=4*ps+4*p*p+t*t+S.Rational(2,3)*potential
    SF=u+4*p*t-m*phi
    A2=a*SA;L2=a*SL;F2=a*SF;k=a*q
    DSA=D(D(A2))+8*p*D(A2)-p*D(L2)-2*L2*(ps+4*p*p)+4*q*A2+S.Rational(2,3)*m*phi*F2
    DSL=4*D(D(A2))+8*p*D(A2)-4*p*D(L2)+2*t*D(F2)-2*L2*(4*ps+4*p*p+t*t)+S.Rational(2,3)*m*phi*F2
    DSF=D(D(F2))+(4*D(A2)-D(L2))*t+4*p*D(F2)-2*L2*(u+4*p*t)-m*F2
    A4=S.expand(-2*L2*A2-4*k*A2-2*A2*A2+a*DSA)
    L4=S.expand(-2*A2*L2-4*k*L2-2*L2*L2+a*DSL)
    F4=S.expand(-2*A2*F2-2*L2*F2-4*k*F2+a*DSF)
    R2=S.factor((D(F2)-L2*t-c*F2)/a)
    R4=S.factor((D(F4)-L4*t-6*L2*D(F2)+3*L2*L2*t-c*F4)/(a*a))
    v_required=S.solve(R2,v)[0]
    reduced=S.factor(R4.subs(v,v_required))
    qcoeff=S.factor(S.diff(R4,q))
    qcoeff_on_R2=S.factor(S.diff(reduced,q))
    r=p*p-1-t*t/12+m*phi*phi/12
    scalar_acceleration=u+4*p*t-m*phi
    P0=S.factor(reduced.subs(q,0)-z-(16*p-c)*w)
    Svar,Delta=S.symbols('S Delta')
    def Dstatic(f):
        return S.expand(S.diff(f,p)*(-r-t*t/3)+S.diff(f,phi)*t+
                        S.diff(f,t)*(m*phi-4*p*t))
    static_u=m*phi-4*p*t
    static_v=Dstatic(static_u);static_w=Dstatic(static_v);static_z=Dstatic(static_w)
    centered=S.expand(reduced.subs({u:Svar-4*p*t+m*phi,q:r+Delta},simultaneous=True))
    centered_C1=S.factor(centered.coeff(Svar,1).subs(Delta,0))
    centered_formula=(z-static_z)+(16*p-c)*(w-static_w)+centered_C1*Svar-S.Rational(32,3)*t*Svar*Svar-12*c*Svar*Delta-24*t*Delta*Delta
    pstar,j=S.symbols('pstar J')
    prepared=S.expand(R4.subs(v,v_required.subs(p,pstar)).subs(p,pstar+j))
    target=S.expand(reduced.subs(p,pstar))
    off_factor=S.factor((prepared-target)/j)
    wall_v=S.symbols('vwall')
    robin_reduced=S.factor(reduced.subs(t,c*(phi-wall_v)))
    # Fourth Israel identity at R0=0, without imposing R2: I4=-Phi2 R2.
    I4=S.factor((D(A4)-L4*p-6*L2*D(A2)+3*L2*L2*p
                 +t*F4/3+c*F2*F2)/(a*a))
    israel_identity=S.factor(I4+SF*R2)
    # Coordinate conversion d_l=exp(-ell)d_s. These Pn satisfy Phi_l^n=P_n/L^n.
    phis=S.symbols('phi_s1:7');ells=S.symbols('ell_s1:6')
    def Ds(f):
        return S.expand(sum(S.diff(f,x)*y for x,y in zip(phis[:-1],phis[1:]))+
                        sum(S.diff(f,x)*y for x,y in zip(ells[:-1],ells[1:])))
    Pn=[None,phis[0]]
    for n in range(1,5):Pn.append(S.expand(Ds(Pn[-1])-n*ells[0]*Pn[-1]))
    # Independent corroboration by executing the frozen predecessor's ORIGINAL
    # Taylor-jet functions with exact SymPy scalar arithmetic. No metric or
    # scalar IVP is integrated, no nonzero D1 amplitude is evaluated, and no
    # frozen source is edited. Only the numeric scalar adapter is replaced.
    class ExactScalar:
        @staticmethod
        def mpf(x):return S.Rational(x)
        exp=staticmethod(S.exp)
    original_code=Path(original_code).resolve()
    sys.path.insert(0,str(original_code))
    spec=importlib.util.spec_from_file_location('original_time_jets',original_code/'time_jets.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    sys.path.pop(0)
    if Path(original.core.__file__).resolve()!=original_code/'core.py':
        raise RuntimeError('Unexpected original core module')
    original.mp=ExactScalar;original.core.mp=ExactScalar
    Ader=[S.Integer(0),p]
    for n in range(2,6):Ader.append(D(Ader[-1]))
    fields=[[Ader[n]/S.factorial(n) for n in range(6)],
            [S.Integer(0)]*6,[x/S.factorial(n) for n,x in enumerate([phi,t,u,v,w,z])]]
    old2,old4=original.time_jets(fields,q,m)
    oldA2,oldL2,oldF2=old2;oldA4,oldL4,oldF4=old4
    original_R4=oldF4[1]-oldL4[0]*t-6*oldL2[0]*oldF2[1]+3*oldL2[0]*oldL2[0]*t-c*oldF4[0]
    original_I4=oldA4[1]-oldL4[0]*p-6*oldL2[0]*oldA2[1]+3*oldL2[0]*oldL2[0]*p+t*oldF4[0]/3+c*oldF2[0]*oldF2[0]
    checks={
        'radial_second_identity':S.expand(L2+2*A2-2*k)==0,
        'highest_proper_fifth_jet_coefficient_is_one':S.diff(R4,z)==1,
        'q_dependence_degree_exactly_two':S.diff(R4,q,3)==0 and S.diff(R4,q,2)==-48*t,
        'q_survives_exact_second_Robin':S.diff(reduced,q,2)==-48*t,
        'q_survives_scalar_Robin':S.diff(robin_reduced,q,2)==-48*c*(phi-wall_v),
        'second_Robin_reduced_q_part':S.expand(reduced-(z+(16*p-c)*w+P0+q*(48*t*r-12*c*scalar_acceleration)-24*t*q*q))==0,
        'centered_quadratic_q_feedback_identity':S.expand(centered-centered_formula)==0,
        'off_Israel_factorization_exact':S.expand(prepared-target-j*off_factor)==0,
        'fourth_Israel_exact_identity':israel_identity==0,
        'coordinate_fifth_jet_coefficient_is_one':S.diff(Pn[5],phis[4])==1,
        'original_frozen_time_jet_Robin_polynomial_identity':S.expand(original_R4-R4)==0,
        'original_frozen_time_jet_Israel_polynomial_identity':S.expand(original_I4-I4)==0,
    }
    return {
        'status':'PASS' if all(checks.values()) else 'FAIL',
        'sympy_version':S.__version__,'physical_integration_performed':False,
        'notation':'p=A_l, t=Phi_l, u=Phi_ll, v=Phi_lll, w=Phi_llll, z=Phi_lllll, q=k exp(-2A), c=sigma gamma/2',
        'hamiltonian_p_l':str(ps),
        'second_Robin_over_alpha2':str(R2),
        'required_third_proper_jet':str(S.factor(v_required)),
        'fourth_Robin_over_alpha4_full':str(R4),
        'q_coefficient_full':str(qcoeff),
        'fourth_Robin_on_exact_second_Robin':str(reduced),
        'coefficient_w_on_second_Robin':str(S.factor(S.diff(reduced,w))),
        'q_independent_lower_jet_polynomial_P0':str(P0),
        'P0_grouped_by_u':{str(n):str(S.factor(S.expand(P0).coeff(u,n))) for n in range(3)},
        'static_r':str(r),
        'scalar_acceleration_S':str(scalar_acceleration),
        'centered_C1':str(centered_C1),
        'static_fourth_jet':str(S.factor(static_w)),
        'static_fifth_jet':str(S.factor(static_z)),
        'centered_formula':'(z-z_static)+(16*p-c)*(w-w_static)+C1*S-(32/3)*t*S^2-12*c*S*Delta-24*t*Delta^2; Delta=q-r',
        'off_Israel_factor':str(off_factor),
        'off_Israel_q_coefficient':str(S.factor(S.diff(off_factor,q))),
        'fourth_Israel_identity_remainder':str(israel_identity),
        'proper_jet_coordinate_numerators':{str(n):str(Pn[n]) for n in range(1,6)},
        'original_sources':{name:hashlib.sha256((original_code/name).read_bytes()).hexdigest()
                            for name in ('core.py','time_jets.py')},
        'checks':checks,
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--original-code',required=True)
    result=derive(parser.parse_args().original_code)
    print(json.dumps(result,indent=2))
    if result['status']!='PASS':raise SystemExit(1)
