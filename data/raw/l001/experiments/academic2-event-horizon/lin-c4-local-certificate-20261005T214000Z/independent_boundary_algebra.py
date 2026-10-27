"""Exact symbolic boundary linearization only; no physical integration or data fit."""
import json
import sympy as S


def main():
    H, P, T, q, a2, h, v, m, c, b = S.symbols("H Phi T q alpha2 h h_s m2 c b")
    eta = S.symbols("eta0:7")
    variables = [H, P, T, q, a2, h, v, *eta[:-1]]
    flow = [-T*T/3-q, T, m*P-4*H*T, -2*H*q, 2*H*a2,
            v, -4*H*v-2*q*h-(m*P*eta[0]+T*eta[1])/3, *eta[1:]]

    def derivative(expression):
        return S.expand(sum(S.diff(expression, x)*dx for x, dx in zip(variables, flow)))

    # Linear second time derivatives after the Hamiltonian variation; radial
    # variation is initially zero for the three shooting/jet columns.
    U = a2*(4*H*v+4*q*h+(m*P*eta[0]-T*eta[1])/3)
    V = -2*U
    F = a2*(eta[2]+4*H*eta[1]+4*T*v-m*eta[0])
    Hs = -T*T/3-q
    # Exact linearization of the original time-jet equations at closed D1.
    F4 = a2*(derivative(derivative(F))+4*H*derivative(F)-m*F
              +6*T*derivative(U)+4*m*P*U)-6*a2*q*F
    V4 = 12*a2*q*U+a2*(4*derivative(derivative(U))+16*H*derivative(U)
              +2*T*derivative(F)+4*U*(4*Hs+4*H*H+T*T)+S.Rational(2,3)*m*P*F)
    U4 = a2*(derivative(derivative(U))+10*H*derivative(U)
              +4*U*(Hs+4*H*H)+S.Rational(2,3)*m*P*F)
    endpoint = {x: 0 for x in eta[:5]}
    endpoint[eta[5]] = b
    R2 = S.factor((derivative(F)-T*V-c*F).subs(endpoint)/a2)
    R4 = S.factor((derivative(F4)-T*V4-c*F4).subs(endpoint)/(a2*a2))
    I4 = S.factor((derivative(U4)-H*V4+T*F4/3).subs(endpoint)/(a2*a2))
    constraint_q = H*H-1-T*T/12+m*P*P/12
    reduced = S.factor(R4.subs(q, constraint_q))
    reduced_israel = S.factor(I4.subs(q, constraint_q))
    coefficients = {"h": S.factor(S.diff(reduced, h)),
                    "h_s": S.factor(S.diff(reduced, v)),
                    "fifth_jet": S.factor(S.diff(reduced, b))}
    B = 4*H*T-m*P+c*T
    expected_R4 = b+8*q*B*v
    d, c0, c1, beta = S.symbols("d c0 c1 beta", nonzero=True)
    jacobian = S.Matrix([[d,c0,c1],[0,1,0],
                         [beta*d,beta*c0,1+beta*c1]])
    inverse = S.Matrix([[(1+beta*c1)/d,-c0/d,-c1/d],
                        [0,1,0],[-beta,0,1]])
    s, D = S.symbols("s D", positive=True)
    shapes = [s**5*(D-s)**6/(120*D**6),
              s**6*(s-D)**5/(120*D**6)]
    shape_checks = []
    for i, shape in enumerate(shapes):
        for side, position in enumerate([0,D]):
            for order in range(6):
                target = 1 if side == i and order == 5 else 0
                shape_checks.append(S.simplify(S.diff(shape,s,order).subs(s,position)-target) == 0)
    mu, k, time = S.symbols("mu k time")
    Q = 1-mu*time**2/2+mu*(mu+6*k)*time**4/24
    mode_time_identity = S.expand(S.diff(Q,time,2)+3*k*time*S.diff(Q,time)+mu*Q)
    checks = {
        "fourth_Robin_exact_reduction": S.expand(R4-expected_R4) == 0,
        "second_Robin_exact_reduction": S.expand(R2+4*B*v) == 0,
        "linear_Israel_fourth_identity": I4 == 0,
        "coupled_determinant_equals_old_derivative": S.factor(jacobian.det()-d) == 0,
        "full_inverse_identity": (jacobian*inverse-S.eye(3)).applyfunc(S.simplify) == S.zeros(3),
        "all_exact_Hermite_endpoint_jets": all(shape_checks),
        "closed_mode_second_and_fourth_time_factors": all(
            S.expand(mode_time_identity).coeff(time,n) == 0 for n in [0,2]),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "sympy_version": S.__version__,
        "physical_integration_performed": False,
        "variables": "q=k exp(-2W); alpha2=exp(2W); c=sigma gamma/2; h=delta A; h_s=delta A_s",
        "second_Robin_normalized_by_alpha2": str(R2),
        "fourth_Robin_normalized_by_alpha4_before_first_integral": str(R4),
        "fourth_Robin_exact_reduced_formula": str(expected_R4),
        "fourth_Robin_normalized_by_alpha4_on_first_integral": str(reduced),
        "fourth_Israel_normalized_by_alpha4_before_first_integral": str(I4),
        "fourth_Israel_normalized_by_alpha4_on_first_integral": str(reduced_israel),
        "coefficients": {name: str(value) for name, value in coefficients.items()},
        "no_metric_value_coupling": coefficients["h"] == 0,
        "unit_fifth_jet_coefficient": coefficients["fifth_jet"] == 1,
        "linear_Israel_fourth_identity": reduced_israel == 0,
        "coupled_Jacobian": str(jacobian),
        "coupled_Jacobian_inverse": str(inverse),
        "determinant": str(S.factor(jacobian.det())),
        "Hermite_shapes": [str(shape) for shape in shapes],
        "closed_mode_fourth_time_factor": str(mu*(mu+6*k)),
        "checks": checks,
        "residual_after_linear_collection": str(S.simplify(reduced-sum(
            coefficients[name]*var for name, var in (("h",h),("h_s",v),("fifth_jet",b))))),
    }
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
