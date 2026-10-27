"""Exact independent wall-jet gauge bridge; no physical solve or producer import.

Initial proper-distance coordinate is used solely to simplify differential
algebra. Lapse jets of orders 3,4,5 remain independent before endpoint reduction.
Run under the coordinated symbolic runtime; JSON is printed, not saved here.
"""
import hashlib
import json
from pathlib import Path
import time
import sympy as S


def run():
    started = time.monotonic()
    p, phi, t, t1, t2, t3, t4, E, Q, m, c = S.symbols(
        'p phi t t1 t2 t3 t4 E Q m2 c', real=True)
    q = S.symbols('q0:6', real=True)
    V = -6 + m*phi*phi/2
    p1 = Q+2-m*phi*phi/6-t*t/6-2*p*p
    pairs = [(p,p1),(phi,t),(t,t1),(t1,t2),(t2,t3),(t3,t4),
             (E,2*p*E),(Q,-2*p*Q)] + list(zip(q[:-1],q[1:]))

    def d(f):
        return S.expand(sum(S.diff(f,a)*b for a,b in pairs))

    def zero(f):
        return S.expand(f) == 0

    wall = {q[0]:0,q[1]:0,q[2]:0}
    at = lambda f:S.expand(f.subs(wall))
    k = E*Q

    # Material alpha=e^A/cosh(sqrt(k)T), from the original time equations.
    TA = p1+4*p*p
    TL = 4*p1+4*p*p+t*t
    TF = t1+4*p*t
    a2 = E*(TA-2*Q+2*V/3)
    l2 = E*(TL+2*V/3)
    f2 = E*(TF-m*phi)
    da, dl, df = d(a2),d(l2),d(f2)
    a4 = -2*l2*a2-4*k*a2-2*a2*a2 + E*(
        d(da)+8*p*da-p*dl-2*l2*TA+4*Q*a2+2*m*phi*f2/3)
    l4 = -2*a2*l2-4*k*l2-2*l2*l2 + E*(
        4*d(da)+8*p*da-4*p*dl+2*t*df-2*l2*TL+2*m*phi*f2/3)
    f4 = -2*a2*f2-2*l2*f2-4*k*f2 + E*(
        d(df)+(4*da-dl)*t+4*p*df-2*l2*TF-m*f2)
    R2 = df-l2*t-c*f2
    R4 = d(f4)-l4*t-6*l2*df+3*l2*l2*t-c*f4

    # Independently differentiated conformal wave equations, in material space.
    EB = E*S.exp(2*q[0])
    K = k*S.exp(2*q[0])
    ac2 = EB*(p1+(4*p+q[1])*p-2*Q+2*V/3)
    bc2 = EB*(p1+q[2]+(p+q[1])**2-3*p*p+3*Q-V/3+t*t/2)
    fc2 = EB*(t1+(4*p+q[1])*t-m*phi)
    dac, dbc, dfc = d(ac2),d(bc2),d(fc2)
    dEV = EB*(2*V*bc2+m*phi*fc2)
    ac4 = EB*(d(dac)+(4*p+q[1])*dac)-4*K*(bc2-ac2)+2*dEV/3-6*ac2*ac2
    bc4 = EB*(d(dbc)+(p+q[1])*dbc-6*p*dac)+6*K*(bc2-ac2)-dEV/3+EB*t*dfc+6*ac2*ac2-fc2*fc2
    fc4 = EB*(d(dfc)+(4*p+q[1])*dfc+3*dac*t)-m*EB*(2*bc2*phi+fc2)-6*ac2*fc2
    D2 = at(d(bc2-ac2)-bc2*q[1])
    D4 = at(d(bc4-ac4)-bc4*q[1]-6*bc2*d(bc2-ac2)+3*bc2*bc2*q[1])
    RC2 = at(d(fc2)-bc2*t-c*fc2)
    RC4 = at(d(fc4)-bc4*t-6*bc2*dfc+3*bc2*bc2*t-c*fc4)
    eta = l2-a2+k
    factor = 5*t1+(16*p-c)*t-4*m*phi
    checks = {
        'curvature_k_constant':zero(d(k)),
        'conformal_A2_material_A2':zero(at(ac2)-a2),
        'conformal_B2_material_ell2':zero(at(bc2)-l2),
        'conformal_Phi2_material_Phi2':zero(at(fc2)-f2),
        'scalar_second_row_equal':zero(RC2-R2),
        'temporal_spatial_second_difference':zero(D2-(d(l2-a2)+E*q[3])),
        'third_lapse_jet_coefficient':zero(S.diff(D2,q[3])-E),
        'third_lapse_jet_affine':zero(S.diff(D2,q[3],2)),
        'scalar_fourth_value_pullback':zero(at(fc4)-f4-4*eta*f2-E*D2*t),
        'scalar_fourth_row_bridge':zero(RC4-R4-4*eta*R2-E*factor*D2),
        'scalar_fourth_independent_q4':zero(S.diff(RC4,q[4])),
        'scalar_fourth_independent_q5':zero(S.diff(RC4,q[5])),
        'fifth_lapse_jet_coefficient':zero(S.diff(D4,q[5])-E*E),
        'fifth_lapse_jet_affine':zero(S.diff(D4,q[5],2)),
    }
    # The exact original-root equivalence follows after the sequential gauge
    # choice D2=0 and existing material second scalar compatibility R2=0.
    q3star = -d(l2-a2)/E
    checks['bridge_after_third_lapse_choice'] = zero(
        (RC4-R4-4*eta*R2).subs(q[3],q3star))
    return {'status':'PASS' if all(checks.values()) else 'FAIL',
            'checks':checks,'sympy':S.__version__,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'physical_integration_performed':False,
            'assumptions':['Initial proper-distance coordinate',
                           'Hamiltonian constraint and its spatial derivatives',
                           'Time reflection and the stated material/conformal time PDEs',
                           'q=q_l=q_ll=0 at the wall; higher lapse jets not preconstrained'],
            'seconds':time.monotonic()-started}


if __name__ == '__main__':
    result=run()
    print(json.dumps(result,sort_keys=True,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
