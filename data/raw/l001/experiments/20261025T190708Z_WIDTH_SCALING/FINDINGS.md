# Width scaling and the geometry of the persistent mode

The fixed concave one-turn example now has a quantitative explanation for its small scalar participation. Narrowing the mathematical double-Dirichlet interval makes the spectral gap quadratic in width, the scalar kinetic share quartic, and the separation-coherence deficit eighth order. These conclusions combine exact local coefficients, interval calculations at three widths, and uniform certificates over the full positive-width interval.

This is the L001 fixed example with V(Phi)=Phi-Phi²/2+Phi⁴, k=3 and central data (a,H,Phi,T)=(1,-2,0,0). It is not a new calculation of the older horizon residual, nor a result for Paper A's different original central background.

## What has been established

Let D be the full interval width, d=D/2 and lambda=mu+12. The boundary condition is f=0 at both mathematical cuts. Existing wall potentials are not being moved while held fixed.

For every 0<D<=.02, the accepted uniform interval calculation establishes

(2/15) D² < -lambda < (1/5) D².

Fresh positive warp, negative H, positive scalar acceleration and opposite endpoint scalar-slope signs support the inherited one-turn branch-count argument on each restriction. The zero-width system is only a desingularized analytic limit, not a physical eigenmode.

The exact local spectral expansion is

-lambda = D²/6 - 5D⁴/36 + 383D⁶/960 + O(D⁸).

The coefficient derivation is independent of numerical fitting. A held-out D=.015 root supports the sixth-order coefficient within its predeclared window. This is not a uniform finite-width bound on the O(D⁸) remainder.

| Full width D | Certified spectral gap, rounded for display |
| --- | --- |
| .02 | [6.6644469328e-5, 6.6644470259e-5] |
| .01 | [1.6665277957e-5, 1.6665278539e-5] |
| .015 | [3.7492973292e-5, 3.7492973294e-5] |

Exact rational interval endpoints in each RESULT.json remain authoritative.

## Why a small scalar share does not mean an absent scalar

Write s for the scalar fraction of the mode's kinetic norm. T9 establishes a strictly positive scalar profile in the interior of every admitted positive-width restriction and a uniform coefficient enclosure:

.01212205 <= s/D⁴ <= .03927050.

The analytic limit is s/D⁴ -> 1/45. More precisely, the exact local calculation gives

s/D⁴ = 1/45 - (3/140) D² + O(D⁴).

At the two endpoint widths, the measured scalar-share ratio is [15.9953859,15.9953880], close to the leading prediction 16. The scalar remains coupled and nonzero; its small share follows a quantified scaling law.

These are kinetic-norm fractions. They are not energy fractions. The metric contribution belongs to the scalar perturbation sector and is not a separate tensor polarization.

## Why the separation response is nearly coherent

Let K be the squared canonically normalized proper-separation response. The exact local result is

K/D = 1/3 + (11/36) D² + O(D⁴).

The full-width/half-width K ratio is approximately 2.0005501707, close to the leading factor two.

For w=a² psi and the positive weight dm=a^-2 dx, define eta=(E[w])²/E[w²]. The field equation gives w_x=-d⁴ a² tau F/3. It follows that w varies only at fourth order and its weighted variance begins at eighth order. The accepted uniform bound is

0 < 1-eta <= .009616262 D⁸,

with exact local limit (1-eta)/D⁸ -> 1/75600. The strict lower inequality is analytic; no positive numerical lower bound has been invented. Near-unity coherence is therefore explained, not treated as exact saturation.

## What accounts for the finite-width change

With J=integral from -1 to 1 of a^-2 dx, an exact identity gives

K/D - 1/3 = (J-2)/6 - Js/6 - J(1-s)(1-eta)/6.

The terms are the warp-weight gain, scalar kinetic penalty and coherence penalty. Their leading orders are D², D⁴ and D⁸, respectively. At the three measured widths the scalar penalty is only about 2.42e-6 to 9.69e-6 of the warp gain; the coherence penalty is smaller still.

This is an exact accounting decomposition, not three independent causal interventions. T14 independently certifies the dominance throughout 0<D<=.02: the combined penalties are less than 2.903126e-5 of the warp gain, or 0.002903126%. It also establishes the conservative uniform envelope

.22265971 D² <= K/D - 1/3 <= .42948487 D².

The positive increase in normalized separation response is therefore dominated by the warp-weight term throughout this mathematical family, not merely at the three sampled widths.

## Test inventory

Each test directory contains its contract, source bindings, execution record, result and independent reviews.

| Test | Purpose | Accepted conclusion |
| --- | --- | --- |
| T1 | Fresh half-width DD restriction | Root and predeclared leading-gap windows supported |
| T2 | Higher-order interval method qualification | Signed-step Taylor enclosure method qualified on declared controls |
| T3 | Precise full-width root | Fourth-order correction resolved |
| T4 | Precise half-width root | Independent half-width correction resolved |
| T5 | Exact two-width comparison | Gap ratio near four and correction ratio near sixteen |
| T6 | Continuous width-family interval calculation | Uniform quadratic gap envelope over 0<D<=.02 |
| T7 | Exact sixth-order spectral derivation | Coefficient 383/960, without fitting |
| T8 | Held-out third width | Sixth-order coefficient prediction supported |
| T9 | Uniform profile and participation | Nonzero scalar interior and uniform D⁴ share bounds |
| T10 | Actual mode norms at three widths | Leading scalar and separation scaling supported |
| T11 | Exact norm corrections | Coefficients -3/140 and 11/36 |
| T12 | Uniform coherence mechanism | Strictly positive deficit bounded by D⁸ |
| T13 | Separation-response accounting | Warp gain dominates measured finite-width corrections |
| T14 | Uniform warp dominance | Entire width family has positive, warp-dominated response increase |

## Next substantive test

The next mathematical gap is a uniform higher-order spectral remainder certificate. A proposed successor would write lambda=-2d²/3+20d⁴/9+beta d⁶, factor d⁴ from the scaled characteristic residual, and enclose the resulting characteristic uniformly in d, including its analytic limit at zero. A parameter-Taylor method must certify the cancellation and remainder; dividing a broad interval residual by a small power is not sufficient.

A reasonable prospective target is to enclose the effective D⁶ coefficient between 383/1200 and 383/800 throughout 0<D<=.02. That target has not been proved by the present samples. The new parameter-dependent enclosure method requires its own qualification and independent admission before execution.

The current results do not establish nonlinear evolution, a physical moving-wall process, a horizon or child universe. No manuscript, shared inventory or parent packet was edited.
