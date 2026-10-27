# From cubic shortening to a controlled amplitude range

The accepted complete cubic coefficient is negative, but a usable amplitude range requires a bound on all omitted orders. Appendix C supplies an existential analytic majorant, not its numerical constants. The next justified task is to quantify that majorant and the proper-distance observable. This note derives sufficient acceptance inequalities; it does not certify a numerical radius or launch a numerical experiment.

## Bound sources and accepted inputs

- Governing manuscript: `papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md`, Appendix C, especially S3, S5, Q8–Q10 and C2.
- Accepted coefficient report: sibling `20261026T100400Z_CUBIC_DISTANCE/FINAL_REPORT.md` and its bound RESULT and audit. The report supplies d1 approximately -72.9214, d2 in [-4490.546,-4490.267], d3 in [-402306,-401703]. Use exact bound records, not these displays, in any numerical certificate.
- Fixed direction: (Na²,Nb²)=(1,0), z=delta² exp(-6ht), unchanged action, background and clock, no-factorial coefficients.

## Explicit sufficient majorant gate

Write the manuscript majorant as

    Y = F(z,Y) = K [C z + Y² + C z Y] / (1-KY)^M,
    C = |Na|² + |Nb|² = 1.

K and integer M must be certified for the actual source maps and inverse estimate. They cannot be fitted to three observed coefficients. Choose trial bounds r>0 and b>0 satisfying

    K b < 1,
    K [C r + b² + C r b] <= b (1-Kb)^M,
    L = K (2b+C r)/(1-Kb)^M
        + M K² [b²+C r(1+b)]/(1-Kb)^(M+1) < 1.

For |z|<=r and |Y|<=b, the first two inequalities give a self-map of the complex disk; the last bounds its derivative in Y and makes it a contraction. Uniform iteration from zero gives an analytic solution inside |z|<r, bounded by b. All coefficients are nonnegative, since the defining germs and iteration have nonnegative coefficients.

The self-map condition can equivalently be tested as

    r <= [b(1-Kb)^M - K b²] / [K C (1+b)],

with a strictly positive numerator. This rearrangement is only for C>0; the chosen direction satisfies it. These gates are sufficient, not an optimal convergence radius.

For 0<=z<r, positivity yields the weighted field-majorant tail bound

    sum_(n>=4) Y_n z^n <= b (z/r)^4.

Indeed (z/r)^n <= (z/r)^4 for n>=4 and sum Y_n r^n<=b. This is a tail in the manuscript's coefficient norm, not yet a proper-distance error. If recovering fields on an inner complex collar with d>=d_min, retain the d^(-2n) weight loss explicitly; the corresponding unweighted amplitude disk shrinks by d_min². On the real interval d=1.

## Convert field control to the measured distance

In the fixed flattened interval, write the exact distance as

    D(z) = integral_a^b J(z,r) exp(beta(z,r)) dr,
    J = 1 + [xi_b(z)-xi_a(z)]/(b-a),

where beta denotes the full radial metric exponent pulled back consistently into this chart. It is not the majorant bound b. Background compositions and both moving endpoints must be included in the quantitative norm map.

A certified uniform complex-disk bound |D(z)-D0|<=B_D for |z|<=r_D implies, by Cauchy coefficient estimates,

    |R4(z)| <= B_D (z/r_D)^4 / (1-z/r_D),  0<=z<r_D.

One conservative way to obtain B_D is to certify |J-1|<=j and |beta|<=v on that disk and real reference interval, in the original proper-radial background chart:

    B_D <= (b-a) [ j exp(v) + exp(v)-1 ].

Here b-a denotes the background interval length, not the majorant trial bound. This estimate follows from J exp(beta)-1=(J-1)exp(beta)+(exp(beta)-1). Use separate notation for interval endpoints in implementation. The majorant-to-j,v conversion must be proved with the actual norm definitions; do not equate Y with the observable error.

Once this bound exists, the full distance is strictly shorter than D0 whenever

    d1_upper z + d2_upper z² + d3_upper z³ + |R4(z)| < 0.

This tests the observable, not only relative size of adjacent polynomial terms. It says shortening at fixed time in this charge direction; it does not say accelerating contraction in time.

## Missing quantitative inputs

1. A certified complex collar for the same background, with explicit coefficient bounds and nonzero lapse/Jacobian/denominator margins. Real-axis flow cells alone do not certify complex-collar bounds.
2. A uniform inverse constant in S5: finitely many low-order scalar Robin problems plus a quantified all-higher-order estimate. Nonzero matching determinants at orders one through three do not bound the inverse at every order.
3. Numerical analytic-source constants, including moving-normal, wall acceleration, oscillator, current and composition terms; an explicit K and M dominating Q8–Q10.
4. The norm conversion to graph displacement and pulled-back radial exponent, yielding j,v and B_D on a common radius.

These are distinct from a fourth-order coefficient. A fourth-order calculation could help diagnose coefficient growth, but cannot replace any of these inputs.

## Smallest next research task

First inventory quantitative ingredients for items 1 and 2 in the accepted background and spectral certificates. Derive an explicit uniform inverse estimate with a stated order cutoff, or identify the precise missing bound. Do not start a full finite-amplitude solver or a fourth-order flow merely to produce another sign.

If the constants can be assembled, freeze a one-direction amplitude certificate with the above inequalities, exact/outward arithmetic, independent reconstruction of the inequalities and observable map, and a reported certified interval. Failure to close an inequality is an unresolved certificate, not evidence of physical divergence.

If no useful quantitative constants are available, the alternative is a separately designed a posteriori validation around the cubic approximation. That requires a compatible full-equation inverse and nonlinear Lipschitz bounds; a small equation residual alone is not a distance-error bound.

## Status

Analytic scoping only. No numerical radius, finite-amplitude solution, new coefficient, or independently reviewed theorem is claimed here. No scientific process was launched, and no sealed parent or manuscript was modified. The equations above are a proposed sufficient certification route pending independent review and quantified inputs.
