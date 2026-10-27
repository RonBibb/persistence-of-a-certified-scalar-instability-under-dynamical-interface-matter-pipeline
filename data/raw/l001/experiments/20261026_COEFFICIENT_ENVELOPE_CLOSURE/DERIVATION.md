# Coefficient envelope closure

The compatible coefficient recursion admits a positive analytic majorant radius if the inherited source estimates and response bounds hold. This calculation assembles the boundary loads and checks that radius using exact rational arithmetic. It does not reconstruct the physical solution or certify a distance remainder.

## Common norm and sources

Use the working collar rho = 1/40000 and A = 160001. Promote every geometric source envelope to y²/(1−Ay)^11 and every current source envelope to z C_N/(1−Ay)^11, where y = Y below order n and C_N = |N_a|² + |N_b|². The promotion is coefficientwise, since each inherited denominator has no larger scale or power. Preserve separate geometric and current constants. All source norms retain their inherited outer order weights; no assertion zY′ ≤ Y is used.

The two authenticated implementations cover the same selected parameter domain. Maxima across their assembled constants give a common envelope, not a new background or action.

## Boundary reduction

Write Ct for the tracefree response constant, Sp for the weighted mixed source, Sc and F for the scalar reduction sources, Xi for the graph response, J for the weighted scalar normal load and O for the weighted oscillator load. Let T and Tp bound the background scalar derivative and its derivative. The real endpoint coefficient satisfies 0 < Gamma = 21−1/d ≤ 21.

Manuscript Q6 and Q7 give, in each channel,

    Rload = 4 T Ct + 2 (Tp + 21 T/2) Xi + 2 J + O/dO
    gload = Ainv Rload/2 + 4 T Ainv Sc/dD

Here dD and dO are the authenticated positive lower bounds for D/n² and the oscillator divisor/n². Both factors 4 include the two endpoint traces. These estimates bound n times the summed endpoint loads and therefore also bound the maximum used by the scalar inverse.

## Responses on the working collar

Recompute the inherited complex response proof at rho = 1/40000 rather than relabeling its earlier constants. With alpha = rho/2 + rho²/4,

    S = ceil(7 [7864 (2+rho/2)+alpha]/(1−6 alpha) + 1).

For the metric response use the inherited real extrema and complex background bounds:

    U0 = m P0 + 4 H0 T0
    d0 = 42 kmin e0²
    A0 = max(1, T0+U0)/d0
    Hp = T²/3 + kup E²
    Tp = m P + 4 H T
    B0 = [A0 + rho (T/6+1/2)]/(1−rho H)
    B1 = 2 H B0 + T/3 + 1
    B2 = 2 Hp B0 + 2 H B1 + (Tp+T)/3 + 12/rho
    C = ceil(B0+B1+B2).

The response theorem applies to compatible analytic Einstein sources. It is not an inverse theorem for arbitrary unrelated loads.

## Complete coefficient estimate

For each channel set

    Uf = S (F+gload)
    Up = C (Sc+Uf+Sp)
    Ub = Ct+2 Up
    Qosc = (2 Uf+T Xi+O)/dO
    K = Uf+3 Up+Ct+Xi+Qosc.

The oscillator formula follows from chi_i = (f_i+T_i xi_i−o_i)/d_i. The factor 2 counts the two endpoint values of f. Favorable powers of n are discarded only for n ≥ 1. Taking maxima gives KG and KC and the triangular inequality

    Y_n ≤ [z^n] (KG Y_<n² + KC z C_N)/(1−A Y_<n)^11.

## Positive radius

Normalize w = z C_N. Require KG > 0 and KC > 0, and choose

    s = min(1/(16 KG), 1/(88 A), 1/1000000)
    r = s/(16 KC).

For the map Phi(M,w) = (KG M²+KC w)/(1−AM)^11, check exactly

    N = KG s²+KC r
    N/(1−As)^11 < s
    2 KG s/(1−As)^11 + 11 A N/(1−As)^12 < 1/2.

These give a uniform complex contraction on |M| ≤ s for |w| ≤ r. The fixed point is analytic in w and has nonnegative coefficients. Triangular coefficient induction dominates Y by this fixed point. For C_N > 0, the corresponding coefficient-series radius in z is r/C_N; C_N = 0 is the neutral branch. This is a deliberately conservative sufficient radius, not a measured limit of the branch.

Physical field reconstruction requires additional inner-collar summation and composition checks. The earlier outer-collar Y(16z) argument must not be reused without reconciling its different norm. A distance-tail certificate remains prospective.
