# Weighted analytic scalar and metric response

This proposed estimate quantifies Appendix C.2 on the fixed verified radial stadium of radius rho=1/20000. It assumes the accepted background and compatible source equations. It does not yet bound the nonlinear source maps or the charge-amplitude tail.

## Norms and input bounds

Let d(z)=1-dist(z,I)/rho, ||u||_q=sup d^q |u|, and

    U_n(u)=n²||u||_(2n)+n||uprime||_(2n+1)+||usecond||_(2n+2).

The independently audited real-axis scalar constant is 3932. For complex forcing and Robin data, split real and imaginary parts on the real interval and use the triangle inequality; the safe real-axis anchor constant is C_R=7864. The collar calculation must verify |a_n|<=5 and |V_n|<=6n² in both representations. The coefficients themselves are holomorphic there, with all reconstruction denominators nonzero.

## Scalar extension

Put p=2n, S=||F||_(p+2)+n max_i |g_i|, X=n²||f||_p and Y=n||fprime||_(p+1). At each complex point integrate the scalar ODE once and twice on the straight segment from its nearest real point. For p>0, the weighted single and double primitives cost rho/(p+1) and rho²/[p(p+1)] respectively; the linear initial term costs rho/(p+1). These follow by integrating (1-t/rho)^(-p-2). Thus

    X <= C_R(1+rho/2)S + (rho²/4)(5Y+6X+S),
    Y <= C_R S + (rho/2)(5Y+6X+S).

With alpha=rho²/4+rho/2, the sufficient gate 6alpha<1 gives

    X+Y <= [C_R(2+rho/2)+alpha]/(1-6alpha) S.

The equation then supplies ||fsecond||_(p+2)<=5Y+6X+S. Consequently

    U_n(f) <= {7[C_R(2+rho/2)+alpha]/(1-6alpha)+1} S.

To avoid assuming the weighted norms finite before proving the estimate, first take suprema on smaller closed stadia while retaining the original weight d. Each normal segment stays in that smaller domain. The constants are independent of its radius, so exhaustion yields the estimate on the open stadium. Analytic continuation of the linear ODE is single-valued on this stadium, with the solution fixed by its real initial data.

## Compatible metric extension

Write p_m for the metric coefficient to distinguish it from the weight index p. Define

    R_m=||Sc||_(2n+2)+U_n(f)+n||Sp||_(2n+1).

On the real interval only, the constraint gives

    p_m=(Sc-T fprime+Tprime f)/D_n,
    n²|p_m| <= A0 R_m,
    A0=max(1,T0+U0)/d0.

Here T0,U0 bound the real background |T| and |Tprime|, and D_n>=d0 n² on the real interval. The complex extension uses the compatible momentum equation, not the constraint as an analytic-index-gain shortcut:

    p_mprime=-2H p_m-Tf/3+Sp.

Use collar bounds Hbar,Tbar,Hprimebar,Tprimebar and the single-primitive gain rho/(2n). If rho Hbar<1, then

    n²||p_m||_(2n) <= B0 R_m,
    B0=[A0+rho(Tbar/6+1/2)]/(1-rho Hbar),
    n||p_mprime||_(2n+1) <= B1 R_m,
    B1=2Hbar B0+Tbar/3+1.

Differentiate the momentum equation. The source derivative is paid by the manuscript's Nagumo estimate and e<3:

    ||Spprime||_(2n+2)
        <= e(2n+2)/rho ||Sp||_(2n+1)
        <= (12/rho) n||Sp||_(2n+1).

Therefore

    ||p_msecond||_(2n+2) <= B2 R_m,
    B2=2Hprimebar B0+2Hbar B1+(Tprimebar+Tbar)/3+12/rho.

This gives U_n(p_m)<=(B0+B1+B2)R_m, and U_n(b)<=U_n(c)+2U_n(p_m) when b=c-2p_m. There is no division by the turning scalar gradient T. Compatibility is required: these are not solvability estimates for independently chosen incompatible Einstein residuals.

## Scope and next dependency

These constants are worst-case analytic estimates, not physical amplification measurements. A quantitative nonlinear majorant must still control the actual bulk, graph, wall, oscillator and current source maps, including analytic compositions in a reserved collar. No charge-amplitude interval, remainder bound, or finite-amplitude shortening claim follows from this estimate alone.
