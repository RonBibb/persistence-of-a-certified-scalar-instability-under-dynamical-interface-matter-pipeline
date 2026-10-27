# The two wall instability transition is one decreasing convex curve

The fixed analytical test gives a complete implicit classification of the nonnegative two-wall Hessian family for the existing concave background. A finite decreasing convex curve separates the region with two negative regular scalar modes from the region with one. On the curve there is one negative mode and one massless mode. Both Dirichlet faces lie in the one-mode region with no massless mode. The statement is conditional on the authenticated exact background and regular scalar spectral framework; its new proof is given below for independent terminal audit.

This is an analytical transfer criterion with rational enclosures, not a numerical spectrum or a parameter scan. The persistent below-threshold instability is never removed. The original central model and its distinct complete-one-mode result are unchanged.

## An equivalent two-component problem at physical zero mass

Keep the original unnormalized warp, k=3, D=1/50 and physical mu=0, so lambda=12. The regular constraint gives

    psi = a^2(T L - T' f)/36.

Substituting into the admitted regular flow gives

    f' = A f + E L,       L' = C f + D_c L,           (1)
    A = a^2 T T'/18,      E = 1-a^2 T^2/18,
    C = V''+4T^2/3+a^2(T')^2/18,
    D_c = -4H-A.

This substitution is equivalent, not merely necessary. For any solution of (1), define psi by the displayed constraint. The background identity is

    T'' = -4H T' + (V''+4T^2/3+12/a^2)T.

Differentiating the reconstructed psi, using the unreduced expressions f'=L-2T psi and L'=-4HL+(V''+4T^2/3)f-2T'psi, yields

    psi' = (a^2/36)[-2H(TL-T'f)-12Tf/a^2]
         = -2H psi - T f/3.

The other retained equations follow by g=L-2Tpsi. No division by T is used; division by the nonzero constant 3lambda=36 is valid through the scalar turn. The two-dimensional solution space therefore describes precisely the constrained physical-zero-mass sector. Lower-warp normalization scales mu and k by the same positive factor and changes none of these coefficient ratios or wall Hessians.

## Exact coefficient bounds

The inherited T' upper bound is strictly below 6/5. With the unchanged a,T,H,V'' rectangle,

    |A| <= (121/100)(1/50)(6/5)/18 = 121/75000 < 1/500,
    1-121/4500000 <= E <= 1,
    -1 <= C <= -7487/7500+121/1250 = -6761/7500 < -9/10,
    38/5-1/500 <= D_c <= 42/5+1/500.

Thus all predeclared targets hold:

    |A|<=1/500, 99/100<=E<=1, -1<=C<=-9/10, 7<=D_c<=9.  (2)

The lower C bound uses V''>=-1 and the two nonnegative squared terms. No sampled coefficient or cancellation-sensitive floating calculation enters (2).

## First fundamental column

Start (f,L)=(1,0) and retain the admitted box

    9/10<=f<=11/10,   -1/10<=L<=0.

On this box,

    -2 <= L'=Cf+D_c L <= -81/100 < 0,
    |f'| <= (1/500)(11/10)+1/10 = 511/5000.

The L=0 entry face points strictly inward. Full-interval f displacement is at most 511/250000, less than 1/10 by 24489/250000. Full-interval downward L displacement is at most 1/25, less than 1/10 by 3/50. Hence first exit through either f face or L=-1/10 is impossible; L=0 cannot be recrossed upward. Linear ODE existence on the compact exact background supplies the full interval.

For this first column at the upper wall,

    249489/250000 <= m11 <= 250511/250000,
    -1/25 <= m21 <= -81/5000.                        (3)

In particular m11>0 and m21<0, with a full-path proof.

## Second fundamental column

Start (f,L)=(0,1) and retain the second admitted box

    0<=f<=1/10,   1<=L<=13/10.

Throughout it,

    4949/5000 <= f' <= 6501/5000,
    69/10 <= L' <= 59/5.

For the last upper bound it is enough to use |Cf|+D_c L<=1/10+117/10=59/5. Both lower entry faces have strict inward derivatives. The full-interval upper f displacement 6501/250000 is less than 1/10 by 18499/250000. The upper L displacement 59/250 is less than 3/10 by 8/125. The first-exit argument therefore closes without changing the box.

The second column obeys

    4949/250000 <= m12 <= 6501/250000,
    569/500 <= m22 <= 309/250.                       (4)

Thus both entries are strictly positive. Equations (3)-(4) are exact enclosures of the fundamental matrix M, not values inferred from a numerical approximation.

## Determinant and the entire massless locus

Let M map (f_a,L_a) to (f_b,L_b). The trace of (1) is A+D_c=-4H. Since the fundamental matrix is initially the identity, Liouville's identity gives

    det M = exp(-4 integral_a^b H ds) = (a_a/a_b)^4 > 0.  (5)

This is an exact identity, not the rounded difference of two approximate products.

Set x=kappa_a>=0 and y=kappa_b>=0. For finite x, normalize f_a=1 and impose L_a=x/2. Constraint reconstruction gives psi_a=a_a^2(T_a x/2-T'_a)/36, so these data are nontrivial and exactly satisfy the lower wall. Every nontrivial lower-admissible solution at mu=0 is a multiple: f_a=0 would force L_a=psi_a=0. The upper condition L_b+y f_b/2=0 is therefore equivalent to

    S(x,y)=2m21+x m22+y m11+(xy/2)m12 = 0.          (6)

For x=y=0, this normalized solution is just a nonzero scalar multiple of the predecessor's psi_a=1 solution; hence -2m21/m11 agrees exactly with the T1 upper threshold. No normalization changes the zero set.

The constant term is negative and the three other coefficients are positive. Define

    x_*=-2m21/m22,       y_*=-2m21/m11.

Both are finite and positive. The full zero set in the nonnegative quadrant is exactly

    y=y_c(x)=-(2m21+x m22)/(m11+x m12/2),  0<=x<=x_*.

There is no nonnegative solution for x>x_*. The denominator is positive everywhere. Differentiation with (5) gives

    y_c'(x) = -det M/(m11+x m12/2)^2 < 0,
    y_c''(x) = det M*m12/(m11+x m12/2)^3 > 0.        (7)

Thus the transition is a single smooth strictly decreasing convex arc between the two axes. Its coefficients are exact uniquely defined transfer entries, with the rational bounds (3)-(4). This specifies the locus implicitly without claiming numerically resolved coordinates.

## Complete count on both sides

Fix a finite target (x,y) other than the origin and travel along the same-background ray t(x,y), 0<=t<=1. Its zero-mass residual is

    S(tx,ty)=2m21+t(xm22+ym11)+t^2 xy m12/2.

It starts negative and is strictly increasing in t. There is no crossing if S(x,y)<0, one endpoint crossing if it equals zero, and one interior crossing if it is positive. At any crossing the inherited norm/response identity gives

    dmu/dt = x*a_a^4*f_a^2/Z + y*a_b^4*f_b^2/Z > 0.

The mode is simple and crosses upward through zero mass. The inherited soft-corner remaining-band count is one. Simple-root continuation and the uniform auxiliary exclusion prevent changes except at mu=0; roots cannot collide or disappear inside the bounded remaining band. Thus the complete regular scalar count, including the persistent one below -4k, is

| Condition | Negative regular scalar modes | Massless regular scalar modes |
|---|---:|---:|
| S(x,y)<0 | 2 | 0 |
| S(x,y)=0 | 1 | 1 |
| S(x,y)>0 | 1 | 0 |

This is not a count inferred from determinant sign alone: the sign is attached to the known soft-corner count by the unique transverse crossing and continuation argument. At the curve the massless mode is not included in the negative count.

## Dirichlet faces

At upper Dirichlet with finite x, the zero-mass boundary condition is f_b=m11+x m12/2=0, which is impossible by (3)-(4). At lower Dirichlet choose (f_a,L_a)=(0,1); the finite upper condition becomes m22+y m12/2=0, also impossible. At double Dirichlet it is m12=0, again impossible. Thus no Dirichlet face has a massless mode.

Nearby sufficiently large finite stiffnesses have S>0 and just one negative mode. A hypothetical negative remaining-band root on a Dirichlet face would continue to neighboring finite-wall data, contradicting that count. The inherited auxiliary strip excludes an exception at mu=-4k. Hence both complete Dirichlet faces have exactly the persistent below-threshold tachyon and no additional negative or massless regular mode.

## Certified regions and axis intercepts

For s=x+y<=1/50, use xy<=s^2/4 and the larger of the m11,m22 upper bounds, 309/250. Equations (3)-(4) imply

    S <= -81/2500+(309/250)(1/50)+(6501/5000000000)
      = -38393499/5000000000 < 0.

Thus the full frozen triangular witness region x+y<=1/50 has two negative modes and no massless mode. For s>=1/10, both m11,m22 exceed 9/10 and xy>=0, so

    S >= -2/25+(9/10)(1/10) = 1/100 > 0.

The full frozen region x+y>=1/10 therefore has exactly one negative mode and no massless mode. Both tests pass without moving their thresholds. In the intervening strip the exact implicit S criterion applies; the broad witness bounds alone do not determine individual pairs there.

The same enclosures yield the finite positive intercept bounds

    27/1030 <= x_* <= 40/569,
    8100/250511 <= y_* <= 20000/249489.                (8)

The lower-wall intercept is strictly smaller than the upper-wall intercept, because m22>=569/500 exceeds m11<=250511/250000. More quantitatively,

    249489/309000 <= x_*/y_* = m11/m22 <= 250511/284500 < 1.

This is a specific asymmetry of the same background, not a universal statement about which wall is more effective. The exact diagonal crossing can also be written without a root scan as the unique positive root of

    (m12/2) kappa^2+(m11+m22) kappa+2m21=0,

or kappa_*=-4m21/[m11+m22+sqrt((m11+m22)^2-4m12*m21)]. These are algebraic consequences of the single admitted map, not additional parameter tests.

## Scientific meaning and limits

The extra remaining-band instability is boundary-controllable: finite nonnegative wall stiffening can remove it through one massless transition. It is not protected by the scalar-turn index. The other negative mode is protected within this wall family and survives every stiffness and both Dirichlet limits; there is no completely stable member of this family in the regular scalar sector.

Both frozen columns, coefficient bounds and witness regions passed. The result covers the entire admitted two-wall family implicitly and supplies explicit conservative regions and intercept bounds. Actual masses, rates of growth, high-precision numerical curve coordinates, nonlinear saturation and other perturbation sectors were not measured. No inference is transferred to a charged action, an event horizon, a child universe or the original central-background count. No numerical worker, CPU lease, precision change or external action occurred.
