# Two regular scalar tachyons at the concave example soft corner

The admitted fixed-box test proves that the existing exact concave example has exactly one regular scalar eigenvalue in -4k<mu<0 at zero wall Hessians. Combined with its inherited one eigenvalue below -4k and exclusion of the auxiliary threshold, its total regular scalar tachyon count is exactly two at this corner. There is no massless regular scalar mode at the corner. This is a conditional analytical result in the inherited action and regular-mode framework, pending the independent terminal audit of this proof.

For every other nonnegative wall-Hessian pair, including Dirichlet limits, the established injection bounds the total negative-mass-squared count between one and two. It does not decide which count holds at each pair, nor exclude massless modes away from the soft corner. This example has different bulk and wall data from the original central background, whose complete count remains one.

## Exact background and normalization

All input bounds are those frozen in PLAN.md and independently admitted. Let a_-=a(-1/100)>0 and let s=r+1/100 run from 0 to D=1/50. For this proof retain the unnormalized a(r), k=3 and physical mass parameter mu. Write lambda=mu+12. The perturbations are psi, f, g=f', and L=g+2T psi.

The existing exact construction supplies throughout the interval

    9/10 <= a <= 11/10,             -21/10 <= H <= -19/10,
    |Phi| <= 1/100,                 |T| <= 1/50,
    205499/250000 <= T' <= 294501/250000,
    -1 <= V'' <= -2497/2500.

It also supplies the exact Hamiltonian constraint, constructed background junctions, one simple scalar turn and the signs T_a<0<T_b. These are inherited analytical facts, not a new numerical background solve.

Lower-wall normalization is a_new=a/a_- with k_new=3/a_-^2. The four-metric changes by the positive constant factor a_-^2, so mu_new=mu/a_-^2 and lambda_new=lambda/a_-^2. Thus k_new/a_new^2=k/a^2 and mu_new/a_new^2=mu/a^2. The regular equations, profile signs and counts are unchanged. The band (-12,0) in the unnormalized convention is precisely (-4k_new,0) in the lower-normalized convention. No mass value is inferred by setting a_-=1 in an unnormalized expression.

## Regular flow and constrained launch

Substitution of g=L-2T psi in the retained regular system gives, at physical mu=0,

    psi' = -2H psi - T f/3,
    f'   = L - 2T psi,
    L'   = -4H L + (V'' + 4T^2/3) f - 2T' psi.       (1)

For clarity, the last equation follows by differentiating L=g+2T psi. The terms proportional to psi sum to

    8HT + 12HT - 4V' + 2(V'-4HT) - 4HT
      = 8HT - 2V' = -2T',

and the f coefficient is V''+2T^2-2T^2/3=V''+4T^2/3. No division by T occurs, so (1) remains regular through the scalar turn.

The general constrained relation is

    T L - T' f = 3lambda psi/a^2.

At physical mu=0, lambda=12. The zero-Hessian lower condition L_a=0 with psi_a=1 therefore fixes

    psi_a=1,   f_a=-36/(a_-^2 T'_a),   L_a=0.          (2)

The initial constraint is exactly zero. Its inherited propagation C'=-4HC preserves it. The factor a_-^2 in (2) is essential: P31 in the normalized convention has a_new,a=1, whereas this proof uses the original unnormalized warp. Zero Hessian imposes L=0, not g=0; here g_a=-2T_a.

The lower constrained wall data span one nontrivial solution at mu=0 because lambda=12 is nonzero and T'_a>0. Therefore showing this solution fails L_b=0 excludes a massless mode at the corner.

## Initial profile bound

The frozen background bounds give

    16645419/25000000 <= a_-^2 T'_a <= 35634621/25000000.

The strict integer inequalities

    55 * 16645419 = 915498045 > 900000000,
    25 * 35634621 = 890865525 < 900000000

imply

    -55 < -900000000/16645419 <= f_a
        <= -900000000/35634621 < -25.                 (3)

Thus the admitted initial bound [-55,-25] holds, with strictly positive distances of at least one and two to the proposed f-box faces -56 and -23. The initial psi=1 is at distance 1/2 from each psi face. L starts on its lower face; that face requires a strict inward vector field rather than a positive initial distance.

## Executed fixed-box inequalities

Use exactly the admitted box

    1/2 <= psi <= 3/2,    -56 <= f <= -23,    0 <= L <= 3.   (4)

Define B=V''+4T^2/3. Since 0<=4T^2/3<=1/1875,

    -1 <= B <= -2497/2500+1/1875 = -7487/7500 < 0.    (5)

On (4), the strict lower-L barrier follows from H<0 and L>=0:

    L' >= (7487/7500)*23 - 2*(294501/250000)*(3/2)
        = 14569591/750000 > 0.                       (6)

This inequality holds throughout the box, including its lower face. It makes L positive immediately after entry and prevents a later crossing through L=0 while the other bounds hold.

For the other faces, the exact derivative bounds are

    |psi'| <= 2*(21/10)*(3/2)+(1/50)*56/3
            = 1001/150,
    |f'|   <= 3+2*(1/50)*(3/2) = 153/50,
    L'     <= 4*(21/10)*3 + 56 + 2*(294501/250000)*(3/2)
            = 21183503/250000.                       (7)

The final line is a valid upper bound even though the last actual term in (1) is negative. Using its absolute value only weakens the bound. No small cancellation or floating-point sign decision enters (5)-(7).

Multiplying (7) by the entire interval length D=1/50 yields the face tests:

| Quantity | Full-interval displacement bound | Required distance | Exact positive slack |
|---|---:|---:|---:|
| psi | 1001/7500 | 1/2 | 2749/7500 |
| f toward lower face | 153/2500 | 1 | 2347/2500 |
| f toward upper face | 153/2500 | 2 | 4847/2500 |
| L toward upper face | 21183503/12500000 | 3 | 16316497/12500000 |

All four frozen tests pass strictly. There was no change to the profile box, time interval, launch interval, background enclosure or arithmetic precision.

## Full-path enclosure rather than an endpoint sign test

Equation (1) is a linear system with continuous bounded coefficients on the existing exact compact background. Its nontrivial constrained solution exists uniquely over the whole interval. At the entry, psi and f are strictly inside their box faces; (6) points strictly into L>0. Suppose a first exit from (4) occurred at s_*<=D. Up to s_* the derivative bounds apply. Integration of (7) contradicts every psi/f face or upper-L exit by the strictly positive slacks above. A lower-L exit contradicts (6). Hence no first exit occurs.

It follows throughout 0<s<=D that

    1/2 < psi < 3/2,     -56 < f < -23,     0 < L < 3.

More explicitly, integrating (6) and (7) gives

    14569591/37500000 <= L_b <= 21183503/12500000.      (8)

In particular L_b is bounded strictly away from zero. The vector z(s)=L(s)+i f(s) never vanishes; its entire positive-s path lies in the open fourth quadrant. This is a full-path result, not an inference of winding from a final determinant sign.

## Lifted phase and exact count

The inherited F.12 corner attachment fixes the lower phase for lambda>0 at 3pi/2. Starting from z_a=i f_a with f_a<0, the just-proved fourth-quadrant path therefore has the continuous lift

    theta(s)=3pi/2+arctan(L(s)/(-f(s))),   0<s<=D,

with arctan taking its positive value in (0,pi/2). Thus

    3pi/2 < theta_E=theta_b(mu=0) < 2pi.              (9)

The absence of an extra winding follows from the whole path in that quadrant; it is not an independently reset principal endpoint argument.

For this one-turn background, the inherited auxiliary endpoint at mu=-12 lies strictly between pi and 3pi/2. The inherited spectral derivative P7 is strictly positive at the upper endpoint for -12<mu<=0. Upper zero-Hessian roots are exactly L_b=0, namely lifted thresholds pi/2+j*pi. Precisely one such threshold lies strictly between the auxiliary endpoint and (9): 3pi/2. The next is 5pi/2, above (9). Continuity, strict spectral monotonicity and simplicity therefore give exactly one root in -12<mu<0, with no root at mu=0. The auxiliary mu=-12 is excluded by the inherited endpoint sign theorem.

The accepted restricted count is exactly one below -12. Adding the disjoint sectors proves two negative regular scalar masses at the zero-Hessian corner. Rescaling by a_-^2 gives the identical statement with threshold -4k_new. The Green identity and positive regular kinetic form supply the inherited reality and simplicity premises; this calculation does not replace those action/domain arguments.

## What follows for other walls and what remains open

The same background has one mode below -4k_new for every nonnegative Hessian pair, including Dirichlet limits. F.11 injects each remaining-band root at another pair into the soft corner. Since the soft corner has exactly one such root, every other pair has at most one. Hence

    1 <= total regular scalar tachyon count <= 2

throughout that family. Which pairs lose the additional mode through mu=0 is not determined. A massless crossing at another pair is allowed by this result. No equality of all-wall counts or all-wall massless exclusion is claimed.

This gives a concrete reason not to identify the number of scalar turns with the complete physical tachyon count: it controls the below-threshold sector, while this already specified concave example carries an additional mode in the remaining band. The positive background coefficient Q is not a stability condition. The present calculation does not isolate bulk concavity alone as the cause across models, because the compared backgrounds and wall data differ.

No mass location, growth timescale, tensor/vector stability, nonlinear evolution, horizon, child universe or halo consequence is established. No numerical integration, executable scientific worker, precision change or resource lease was used. This proof is the executed result of the one admitted analytical test; the remaining required gate is independent terminal review.
