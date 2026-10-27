# R2: sourced physical homogeneous map, finite adjoint and width equations

This is the actual declared homogeneous untwisted scalar sector with a fixed tangential coordinate normalization. The physical width q and Pq are independent retained canonical variables. It is not an auxiliary zero-frequency limit, a general twisted/marked-boundary sector or a nonlinear Fourier-average construction. Time derivatives and source variations are at fixed rho in [0,1]. The prescribed clock kappa_bg(t,rho) is independent of variable q.

## 1. Exact metric constraints, true density and canonical mean

Use gamma=exp(2lambda)diag(q^2,1), barA^{rho rho}=A/q^2, barA^{xx}=-A, Pi per rho and barp=Pi/q. Define

    Q=2A^2+G^AB Pi_A Pi_B/(2q^2),
    F=-2lambda_rhorho/q^2-G_AB X_rho^A X_rho^B/(2q^2)
                          -exp(-2lambda)Q+exp(2lambda)(kappa^2/2-B),
    M=A_rho-exp(2lambda)kappa_rho/2-Pi_A X_rho^A/(2q),
    H=-qF, H_rho=-2qM,
    Pq=2 integral_0^1 A d rho.

The mean condition is physical canonical data, not an arbitrary boundary value for A. The exact post-clock one-form is Pq delta q+integral v delta kappa+Pi delta X+sum p_i delta psi_i, with v=q exp(2lambda), the oriented corner one-form, and endpoint generator -Fclock(tf)+Fclock(ti), Fclock=integral kappa v. The raw pre-clock q coefficient differs by -integral kappa exp(2lambda); it is not used here.

Put h=delta q/q, w=delta lambda, a=delta A, u=delta X, p=delta barp=delta Pi/q-h barp and d=delta kappa. The section fixes d=0, but its known profile-source terms are displayed below.

## 2. Complete direct smooth-source table

Let Lrho=-q^-2 partial_rho^2+exp(-2lambda)Q+exp(2lambda)(kappa^2/2-B), dA=4exp(-2lambda)A and Drho=exp(2lambda)kappa_rho. Then

    delta F=2Lrho w-dA a+Fdata,
    Fdata=-G_AB X_rho^A u_rho^B/q^2
              -exp(-2lambda)G^AB Pi_A delta Pi_B/q^2
              +exp(2lambda)(kappa d-B_A u^A)
              +h[4lambda_rhorho/q^2+G_AB X_rho^A X_rho^B/q^2
                              +exp(-2lambda)G^AB Pi_A Pi_B/q^2],
    delta M=a_rho-Drho w-Sdata,
    Sdata=exp(2lambda)d_rho/2
                         +[(delta Pi_A/q-h barp_A)X_rho^A
                                             +barp_A u_rho^A]/2,
    2 integral a=delta Pq.                                  (MS)

For physical data set the full delta F,delta M to zero. All direct reference-width, true-density and clock sources have been kept. There is no inverse scalar gradient.

At a wall use epsilon_i=-1,+1, b_wall=exp(lambda), nu_out=epsilon exp(-lambda)q^-1 partial_rho, k_out=epsilon exp(-lambda)lambda_rho/q, and R1's delta P,delta Z. The first Israel row is

    Bbar w=epsilon h lambda_rho/q+exp(lambda)delta P/2
                   +exp(-lambda)delta Z/4-exp(lambda)K_ee delta eta,
    Bbar=epsilon q^-1 partial_rho+exp(lambda)pwall/2,
    K_ee=kappa/2-exp(-2lambda)A.                              (ME)

The pressure/third-Israel source is

    Bbar delta alpha=alpha[exp(lambda)delta P/2
              -exp(-lambda)delta Z/4+exp(lambda)rho_wall w/2
              -exp(lambda)pwall h/2
              -exp(lambda)(U delta eta+K_nunu delta eta)],
    K_nunu=kappa/2+exp(-2lambda)A.                            (MP)

Here U delta eta means its derivative along the background wall rest velocity. This follows from delta nu=-(w+h)nu and the actual boosted acceleration law. Tangency supplies delta beta^nu=alpha delta eta; thus delta beta^rho_i=epsilon_i alpha_i exp(-lambda_i)delta eta_i/q. These sources are kept before restricting NEW cuts to eta=0. The inward scalar law is G n_in.X=Fwall; with the OUTWARD normal above it is G n_out.X=-Fwall. That sign is never interchanged.

The homogeneous tangential momentum has its own range condition: b_rho=f_x with endpoint b_i=t_i is solvable iff integral f_x=t_b-t_a. Actual LINEAR homogeneous scalar/boost loads vanish, so b=0. The adjoint's constant tangential shift is the coordinate translation, fixed by an origin convention. It is not a physical width degree of freedom. General quadratic mean currents or marked-boundary twist data are outside this declared linear sector.

## 3. Full physical mean inverse and its finite adjoint row

Treat the metric output as TWO bulk rows, two energy endpoints and the actual canonical mean:

    Cy0(w,a)=(2Lrho w-dA a, a_rho-Drho w,
                         Bbar w_a,Bbar w_b,2 integral a).

For arbitrary smooth loads the mean specifies a_mean, and

    a=a_mean+q_bg^-1 partial_rho zeta,
    zeta(0)=zeta(1)=0.

There is exactly ONE factor q_bg^-1; equivalently a=a_mean+partial_r zeta at fixed background time. This converts the map to C5's zero operator with the explicit supplied mean source, proving its inverse on H2 x H1 -> L2^2 direct-sum endpoint^2 direct-sum R. No auxiliary limiting mean is substituted.

Pair its outputs in fixed d rho measure with bulk(l,v), energy endpoints(mu_i) and mean(z). Its bulk adjoint is

    2Lrho l-Drho v,
    -dA l-v_rho+2z.

The Green endpoint table is

    epsilon_i[-2l_i/q^2+mu_i/q] w_rho,i
                +[2epsilon_i l_rho,i/q^2+mu_i beta_i]w_i
                +epsilon_i v_i a_i,
    beta_i=exp(lambda_i)pwall_i/2.

Thus mu_i=2l_i/q and v_i=0, with remaining w trace (2/q)Bbar l. In the canonical ACTION physical l=q alpha and v=2q beta^rho; hence mu_i=2alpha_i. These trace factors match exactly +2alpha b_wall I_E. The finite z is NOT zero or an extra lapse boundary condition. It is the width-velocity multiplier, as the next section shows.

## 4. Exact width action and both global equations

A transparent way to keep the mean variation is to introduce A and Pq independently and add a time-dependent multiplier tau(t) for 2integral A-Pq. The exact gauge-coordinate action is

    Sg=integral dt[Pi Xdot+sum_i p_i psidot_i+Pq qdot
                       -Hnew+tau(2integral A-Pq)]
                      +S_corner-Fclock(tf)+Fclock(ti),

with kappa=kappa_bg(t,rho). This augmentation is an exact representation of the same canonical mean, not a new physical constraint. Varying Pq gives tau=qdot. Varying A then gives the LOCAL TF-preservation equation

    tau=q[2alpha exp(-2lambda)A+partial_rho beta^rho]. (Wlocal)

Its spatial mean is

    qdot/q=2integral alpha exp(-2lambda)A d rho
                                  +beta^rho_b-beta^rho_a.

At the NEW orthogonal wall cuts those two beta^rho traces vanish. The finite constant in the mean adjoint is therefore precisely the retained global canonical velocity; setting it to zero would freeze physical width. Linearizing gives

    hdot=integral[C delta alpha+2alpha exp(-2lambda)(a-2A w)]d rho
                         +delta beta^rho_b-delta beta^rho_a,
    C=2exp(-2lambda)A.                                      (WV)

The local linearized shear equation is delta beta^rho_rho+C delta alpha-hdot=-2alpha exp(-2lambda)(a-2A w); differentiating removes the finite constant. Together with the varied PMC equation and (MP), this is exactly C9's homogeneous adjoint inverse with actual sources. Recover the constant by (WV), not by an extra condition on the gauge inverse. The PMC source uses R1's exact fixed-rho (LS), now with

    (delta Lrho)alpha=(2h/q^2)alpha_rhorho+alpha delta Vbar,
    delta Vbar=exp(-2lambda)[4A a+G^-1 barp.p-2Qw]
                       +exp(2lambda)[2(kappa^2/2-B)w-B_Au+ kappa d].

All background shift/time-shape terms remain in the exact PMC equation before differentiation.

For completeness the exact orthogonal POST-clock Hamiltonian after spatial curvature/GHY cancellation is

    Hnew=integral d rho {
       -2alpha_rho lambda_rho/q+alpha G X_rho^2/(2q)
       +2alpha q exp(-2lambda)A^2
       +alpha exp(-2lambda)G^-1 Pi^2/(2q)
       -alpha q exp(2lambda)(kappa^2/2-B)
       +beta^rho[-2q A_rho+q exp(2lambda)kappa_rho+Pi_A X_rho^A]
       -q exp(2lambda)kappadot }
       +sum_i alpha_i[exp(lambda_i)P_i+exp(-lambda_i)Z_i/2].

Its q Euler row, with tau=qdot and the mean constraint retained, is

    Pqdot=-integral d rho {
       2alpha_rho lambda_rho/q^2-alpha G X_rho^2/(2q^2)
       +2alpha exp(-2lambda)A^2
       -alpha exp(-2lambda)G^-1 Pi^2/(2q^2)
       -alpha exp(2lambda)(kappa^2/2-B)
       +beta^rho[-2A_rho+exp(2lambda)kappa_rho]
       -exp(2lambda)kappadot }.                              (WP)

This is -partial_q Hnew at fixed lambda,A,TRUE Pi,X,wall pairs,alpha,beta and the prescribed fixed-rho curvature profile. The full linear WP source is its ordinary coefficient variation; every coefficient and held variable is specified, including the clock term. It is NOT a partial derivative before clock exchange at fixed v=q exp(2lambda): that derivative adds lambda_q|v=-1/(2q) times the lambda Euler row and changes the raw momentum. The complete rows agree on stationarity, but their pieces cannot be mixed. The wall Hamiltonian has no direct q dependence at fixed tangential normalization and fixed lambda; indirect response enters through the full variation/constraints.

## 5. What R2 supplies to reconstruction

R2 closes the distinct physical mean source/adjoint map, pressure and normal-shift sources, the translation compatibility, the finite width multiplier and BOTH explicit global width equations. On a stationary reduced action, arbitrary q and Pq tests are exactly the missing finite mean equations; C9's remaining gauge range treats width as output, not an omitted fixed gauge coordinate. R3 must still use the complete moving-interface/corner/cap action to remove residuals in all fixed gauge/angle slots. Neither this table nor a canonical one-form alone is that proof. No arbitrary-data evolution, IR map, finite total background charges or kinetic/no-ghost conclusion is drawn.
