"""Exact centered Hamiltonian and certified-mode cancellation algebra only."""
import argparse
import hashlib
import json
from pathlib import Path
import sympy as S


def derive(endpoint_receipt):
    H,Phi,T,q,m,psi,f,g,theta,c=S.symbols('H Phi T q m2 psi f g theta c')
    eps,w,v,d,ds=S.symbols('epsilon w_metric v_metric d_scalar d_scalar_s')
    xi=eps*psi
    ps=-2*H*psi-T*f/3
    Hs=-T*T/3-q;Ts=m*Phi-4*H*T
    pss=-2*Hs*psi-2*H*ps-Ts*f/3-T*g/3
    Cbg=H*H-1-T*T/12+m*Phi*Phi/12-q
    delta=eps*f+d;deltas=eps*g+ds;j=eps*ps
    X=-6*xi-2*w;Y=-4*xi;Cpot=2-m*Phi*Phi/6
    def E1(x):return S.exp(x)-1
    def E2(x):return S.exp(x)-1-x
    full=(-2*j)*(H+j+v)+q*S.exp(X)+(Cpot-m*Phi*delta/3-m*delta*delta/6)*S.exp(Y)
    full+=-(T+deltas)**2/6-2*(H+j+v)**2
    nonlinear=(q*E2(X)+Cpot*E2(Y)-m*Phi*delta*E1(Y)/3
               -m*delta*delta*S.exp(Y)/6-deltas*deltas/6-4*j*j-6*j*v-2*v*v)
    centered=-4*H*v-2*q*w-(m*Phi*d+T*ds)/3+nonlinear
    metric_identity=S.simplify(S.expand(full-Hs-eps*pss-centered-(-2+8*xi)*Cbg))
    metric_checks={
        'full_centered_equation_exact_mod_background_constraint':metric_identity==0,
        'metric_value_Jacobian':S.simplify(S.diff(centered,w)+2*q*S.exp(X))==0,
        'metric_slope_Jacobian':S.simplify(S.diff(centered,v)+4*H+6*j+4*v)==0,
        'scalar_shape_Jacobian':S.simplify(S.diff(centered,d)+m*S.exp(Y)*(Phi+delta)/3)==0,
        'scalar_shape_gradient_Jacobian':S.simplify(S.diff(centered,ds)+(T+deltas)/3)==0,
    }
    dp_linear=-T*eps*f/3;dp_quad=-c*eps*eps*f*f/6;dp=dp_linear+dp_quad
    Rwall=H*E2(-2*xi)+dp_quad+E1(-2*xi)*dp
    raw_Israel=H+j+v-S.exp(-2*xi)*(H+dp)
    metric_checks['endpoint_Israel_centering']=S.simplify(S.expand(raw_Israel-v+Rwall))==0
    # Regular coupled mode equations, with theta=mu exp(-2W).
    gs=-4*H*g+(m-theta+2*T*T)*f+(12*H*T-4*m*Phi)*psi
    variables=[H,Phi,T,q,psi,f,g,theta]
    flow=[Hs,T,Ts,-2*H*q,ps,g,gs,-2*H*theta]
    def D(expr):return S.expand(sum(S.diff(expr,x)*dx for x,dx in zip(variables,flow)))
    constraint=T*g-Ts*f+(2*T*T-3*(theta+4*q))*psi
    mode_robin=g+2*T*psi-c*f
    mode_transport=S.factor(D(constraint)+4*H*constraint)
    energy_transport=S.factor(D(Cbg))
    r=H*H-1-T*T/12+m*Phi*Phi/12
    def atwall(expr):
        return S.factor(S.expand(expr).subs(g,c*f-2*T*psi).subs(q,r))
    Cwall=atwall(constraint)
    u0=Ts;v0=D(u0);w0=D(v0);z0=D(w0)
    f2=gs;f3=D(f2);f4=D(f3);f5=D(f4)
    psi2=D(ps);psi3=D(psi2);psi4=D(psi3)
    # Endpoint scalar first and third jets prescribed by the EXACT old C7 rule.
    p0,phi0,t0,u,v3,w4,z5=S.symbols('p Phi t u v w z')
    loc={'p':p0,'Phi':phi0,'t':t0,'u':u,'v':v3,'w':w4,'z':z5,'q':q,'m2':m,'c':c}
    receipt=json.loads(Path(endpoint_receipt).read_text())
    if receipt['status']!='PASS':raise RuntimeError('Endpoint algebra not passed')
    vreq=S.sympify(receipt['required_third_proper_jet'],locals=loc)
    R4=S.sympify(receipt['fourth_Robin_on_exact_second_Robin'],locals=loc)
    base={p0:H,phi0:Phi,t0:T,u:u0,w4:w0,z5:z0}
    dp1=-T*f/3
    du1=f2+4*psi*u0+2*ps*T
    dvreq=sum(S.diff(vreq,x)*dx for x,dx in
              [(p0,dp1),(phi0,f),(t0,c*f),(u,du1)])
    dvreq=dvreq.subs({p0:H,phi0:Phi,t0:T,u:u0},simultaneous=True)
    C7_first_linear=c*f-2*T*psi-g
    C7_third_constant=atwall(vreq.subs({p0:H,phi0:Phi,t0:T,u:u0},simultaneous=True)-v0)
    C7_third_linear=atwall(dvreq-6*psi*v0-6*ps*u0-2*psi2*T-f3)
    # C7's coefficients zero through epsilon degree one imply no changes to
    # ANY spatial jet at those degrees. Fifth controls are set to zero here
    # because these are the known forcing coefficients, not full b derivatives.
    dw1=f4+8*psi*w0+12*ps*v0+8*psi2*u0+2*psi3*T
    dz1=f5+10*psi*z0+20*ps*w0+20*psi2*v0+10*psi3*u0+2*psi4*T
    variations=[(p0,dp1),(phi0,f),(t0,c*f),(u,du1),(w4,dw1),(z5,dz1),(q,-2*q*psi)]
    R4_linear=atwall(sum(S.diff(R4,x)*dx for x,dx in variations).subs(base,simultaneous=True))
    R4_constant=atwall(R4.subs(base,simultaneous=True))
    linear_factor=S.factor(S.cancel(R4_linear/Cwall))
    checks={**metric_checks,
        'background_first_integral_transport':energy_transport==0,
        'regular_mode_constraint_transport':mode_transport==0,
        'C7_first_linear_equals_minus_mode_Robin':S.expand(C7_first_linear+mode_robin)==0,
        'C7_third_constant_zero':C7_third_constant==0,
        'C7_third_linear_proportional_to_mode_constraint':S.factor(C7_third_linear-S.Rational(2,3)*T*Cwall)==0,
        'fourth_forcing_constant_zero':R4_constant==0,
        'fourth_forcing_linear_proportional_to_mode_constraint':S.expand(R4_linear-linear_factor*Cwall)==0,
        'fourth_linear_factor_has_no_mode_unknown_denominator':not S.denom(linear_factor).has(psi,f,g,theta,H,Phi,T,q,c,m),
    }
    return {
        'status':'PASS' if all(checks.values()) else 'FAIL','sympy_version':S.__version__,
        'physical_integration_performed':False,
        'background_constraint':str(Cbg),'mode_constraint':str(constraint),
        'mode_Robin':str(mode_robin),'psi_s':str(ps),'psi_ss':str(S.factor(pss)),
        'notation':{'xi':'epsilon psi','j':'epsilon psi_s','delta':'epsilon f+d','delta_s':'epsilon g+d_s',
                    'X':'-6xi-2w','Y':'-4xi','q':'background k exp(-2W)'},
        'centered_metric_equation':'w_s=v; v_s=-4H v-2q w-(m2 Phi d+T d_s)/3+N',
        'nonlinear_N':'q E2(X)+(2-m2 Phi^2/6)E2(Y)-(m2/3)Phi delta E1(Y)-(m2/6)delta^2 exp(Y)-delta_s^2/6-4j^2-6jv-2v^2',
        'off_background_constraint_remainder':'(-2+8epsilon psi)*C_background',
        'metric_Jacobian_value':'-2q exp(X)','metric_Jacobian_slope':'-4H-6j-4v',
        'shape_Jacobian_forcing':'-[m2 exp(Y)(Phi+delta) H_i+(T+delta_s) H_i_s]/3',
        'delta_p_linear':str(dp_linear),'delta_p_quadratic':str(dp_quad),
        'endpoint_Rwall':'H E2(-2epsilon psi)+delta_p_quadratic+E1(-2epsilon psi)*delta_p',
        'original_Israel_residual':'v-Rwall',
        'C7_third_linear_after_mode_Robin':str(C7_third_linear),
        'C7_third_linear_factor':'(2/3)T times the regular mode constraint',
        'fourth_forcing_constant':str(R4_constant),
        'fourth_forcing_linear_factor_after_mode_Robin':str(linear_factor),
        'endpoint_algebra_receipt_sha256':hashlib.sha256(Path(endpoint_receipt).read_bytes()).hexdigest(),
        'checks':checks,
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--endpoint-receipt',required=True)
    result=derive(parser.parse_args().endpoint_receipt)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if result['status']!='PASS':raise SystemExit(1)
