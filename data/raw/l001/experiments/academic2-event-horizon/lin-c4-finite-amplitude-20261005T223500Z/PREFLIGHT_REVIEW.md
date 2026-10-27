# Independent bounded preflight review

Status: **PASS FOR THE FROZEN BOUNDED DISCRIMINATOR**, conditional on unchanged
sources/inputs, successful packet-local authentication and controls, the stated
physical interval gates, and independent postrun verification. This is not a
finite-amplitude existence result. No physical D1 integration was performed by
this review, and no production result was inspected before this decision.

## Scope and inspected evidence

I read the complete staged CONTRACT, centered derivation, algebra, source flow,
preparation, nonlinear flow, validated driver, arithmetic/record primitives and
runner. I compared the unchanged C7 construction and C4 normalization against
the sealed Cauchy predecessor's core.py, time_jets.py and higher_run.py. The
sealed local-family and accepted central spectral certificates remain the
source premises; the new experiment does not replace their exact source by the
saved numerical examples.

The target is exactly epsilon=+1/200000 and -1/200000, separately, with the
six inherited action literals and full root, mode-mass and event intervals:

    a_bg: [456607025194779413/4611686018427387904,
           114151756532473697/1152921504606846976]
    D:    [32727/16384,32729/16384]
    mu:   [-33/25000,-131/100000].

The three unknowns are (a,b0,b1), A(0)=epsilon+a. The fixed rational Newton
centers come only from the declared saved examples; they are not source
profiles or exact solutions. The fixed half-widths are (1e-5,0.1,0.1) and
preconditioner diag(-24/23,1,1). No amplitude continuum, larger amplitude,
evolution or successor is admitted by this review.

## Mathematical correspondence

1. The independent nonlinear endpoint derivation gives a fifth-proper-jet
   coefficient of one and retains the curvature dependence. After the exact
   second Robin row, the q terms are not zero: in centered form they are
   -12c S(q-r)-24t(q-r)^2. Substitution p=pwall in the fourth row is legitimate
   only because the original row minus the reduced row is the retained Israel
   row times an analytic factor. Lower Israel is imposed in the launch; upper
   Israel remains the first equation. The row transformation is invertible,
   preserving zeros and their local uniqueness. The original time-PDE Taylor
   implementation corroborates both the scalar polynomial and the fourth
   Israel identity. No nonlinear triangularity is assumed.

2. Fourteen independent exact SymPy identities verify the centered Hamiltonian,
   its value/slope/shape derivatives, the endpoint Rwall formula, background
   constraint transport, mode constraint transport, and the required mode
   cancellations. The main nonlinear RHS is precisely the same centered
   equation with regrouped potential terms. Its three variation columns have
   the correct interior forcing, including both b-column metric responses.
   The first-row Jacobian uses the propagated v columns; each scalar row uses
   its direct unit b coefficient plus the full q(A) chain rule. No finite
   difference determinant or sampled derivative enters the proof.

3. The scalar preparation is the unchanged degree-seven, endpoint-value and
   second-coordinate-jet preserving Hermite lift. Its first and third targets
   match the predecessor. The exact degree-eleven shapes preserve coordinate
   jets zero through four and have own fifth jet +1. The material/proper fourth
   and fifth transformations and L^5 normalization match the independent
   endpoint derivation. Direct symbolic extraction of the staged long static
   fourth/fifth-jet and C1 polynomial literals also gives three exact matches
   to the independent expressions.

4. Removing epsilon coefficients zero and one is justified for the actual
   certified source, not for every point of an interval rectangle. The C7
   first coefficient is minus the mode Robin residual; after that Robin row,
   its third coefficient is (2/3)T times the regular mode constraint. The
   scalar fourth-row linear coefficient is likewise a polynomial times that
   constraint, with no T division. The constant terms vanish on the static
   source. This proves the two allowed deletions in expansions about zero.
   No deletion is made in the eighth-coefficient remainder at its interval
   center. Quadratic terms and q feedback remain.

## Enclosure and source-error accounting

The source flow is the regular background/mode ODE with the same lower launch,
full a_bg and mu intervals, and no scalar-turn division. Fresh source
enclosures, not old dense approximations, supply all endpoint jets and the
global C7 coefficients. Intersections with proved wall identities retain the
same exact physical source. The accepted spectral premise supplies a mode
satisfying the upper Robin row; the code does not assert that every arbitrary
parameter tuple in its enclosing rectangle is an eigenmode.

The interval epsilon algebra uses ordinary Taylor coefficients, so coefficient
eight is the eighth derivative divided by 8!. Evaluating that coefficient at
epsilon's entire zero-to-target segment with first derivative one, retaining
all shifted-center terms, gives the real Lagrange remainder for each fixed
source. The same treatment propagates through the global Hermite operator and
the scalar W rows. Degree-14 E2 with its fifteenth-order absolute remainder
encloses exp(x)-1-x for the explicitly checked |x|<=1/10. Its Taylor derivative
recurrence uses exp(x)-1 and is consistent with that enclosure.

The common endpoint enclosures and each nonlinear carrier can be decorrelated
for interval evaluation because all include the same exact source. This may
widen results but is not an omitted source error. The box and center flows
retain the full scalar forcing and Hamiltonian backreaction. Strict Picard
inclusion establishes cell existence; the order-four polynomial with the
fifth coefficient evaluated on the enclosing cell bounds the full event-time
range, not merely endpoint hulls. Complete exact D coverage is checked before
acceptance. Positivity/finite-interval failures stop the calculation.

For each fixed admitted physical source, the computed image is the ordinary
fixed-point image for x -> x-CG(x). Containment inside 0.9 of every declared
radius and the weighted infinity-norm bound <=1/2 suffice for existence and
uniqueness within that box. Source uncertainty is included uniformly; it is
not an additional fitted unknown or a replacement source. Both signs must
pass independently for the two-sample claim.

## Recovery and controls

One prefreeze implementation defect was found and repaired: a parameter-dict
alias could survive outward checkpoint canonicalization. The final production
step entry now always reads state['p'], exactly as resumed execution does.
The new manufactured fixture requires a genuinely widening parameter radius,
replacement of the parameter dictionary, and matching fresh-process versus
uninterrupted next-step digests. No equation, scientific domain, gate or
numerical limit changed in this correction.

I inspected analytic-control-04/RESULT.json: all 15 narrow controls pass on the
source bytes below, including exact Hermite inversion, E2 consistency,
manufactured vacuum, native recovery, changed-guard refusal, partial-file
isolation and both fresh-process controls. Its SHA-256 is
`de94273b247e427086f4f890f9dbfac60324f9188706f2a64418c90260cdde64`.
The runner authenticates sources, reviews, runtime, exact inputs and all three
sealed parent manifests; signed workers additionally authenticate the common
source result against its terminal hash. Checkpoints use the same outward,
constructor-stable native state for live continuation and resumption.
Shared Arb, Taylor/Picard, arithmetic and recovery primitives are disclosed;
this review is mathematical/code independence, not a disjoint interval library.

No remaining scientific or implementation blocker was identified for this
bounded attempt. A failure of its fixed enclosures or inclusion gates must
remain unresolved, not become a nonexistence claim or an automatic retuning.

## Exact reviewed source bytes

```text
990c23a8e064f3446ebd1089da43719a142bc77a9c9d24ad10485b9002858500 CONTRACT.md
cd76af8917f142c782c6de70fee3f40829f0e36a162b2f8daecf0286f5e43c26 CENTERED_IVP_DERIVATION.md
2b6d373839620cd9abdd0d88b88aee8d4bd3f780f30ce75b96a494ab246b180d algebra.py
d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603 series.py
081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e records.py
0a48f058b282197b9b4e6d5a99e36af578bcb9e6d036d9848d5513adc009c7d3 validated.py
a9faa6490ae30842180c39ef1e61cc555488ee26f2afe94319d0d215d2e296a5 source_flow.py
70f6cfa03976114b440c8bb8c53ee624aadb83bec896bc6f68ea7af6dec21ac9 preparation.py
f303d46f2d6f5fd4639294df9d6db777689e2ea3f4f144e38e2321ec5c31bf2c nonlinear.py
92b06c0aa373c2e06ad1951e748d5cb2b7c12356d0cf05bf6178573cd4da415c runner.py
```

Independent exact algebra and derivations, directly bound in REVIEWS:

```text
c9bc6d6780d77457516c3463b91243d6f581d071612a6d75bc1e59b3bc2e8ba2 independent_nonlinear_endpoint.py
93511b04a5b504ecfc4a844c381455568948a34d3d32a95f4f0e5c2f6edadf97 INDEPENDENT_NONLINEAR_ENDPOINT.json
35da94ef96e089cdc0b8e46dfd9d3f81ebfc8919c3db2f91ef841aa38bbca214 INDEPENDENT_NONLINEAR_ENDPOINT_DERIVATION.md
75a2e8958c7f3569574196660abec8a06c2b321aff6b0ed94edb6367064ccf88 independent_centered_ivp.py
f482c8942380c5b9dc1a1762298639155b43645d47266c3c0730186dc9ff1bc3 INDEPENDENT_CENTERED_IVP.json
83c8174dafec6206cca04a1ce3e5dc151fd75c51c465aa2f2c911cb069bfbff1 INDEPENDENT_CENTERED_IVP_DERIVATION.md
```
