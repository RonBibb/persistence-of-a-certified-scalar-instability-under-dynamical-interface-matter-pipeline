# Exact local C4 family: bounded certificate result

The producer has passed all contracted gates. Independent acceptance is recorded
separately in the final root `RESULT.json` and `POSTRUN_REVIEW.md`; this report
is authoritative only together with those records and the sealed manifest.

## What gap this calculation closes

The predecessor's rigorous one-variable local argument covered the first
constraint preparation. Its final higher-order preparation added two scalar
fifth-jet corrections and solved a coupled three-variable problem, but that
final family had only numerical C4 qualification. The earlier one-variable
argument could not simply be carried over.

This packet retains the exact same central D1 background, physical scalar
mode, Hermite preparation, lapse convention and boundary conditions. It proves
that the final three-variable boundary map is locally invertible, including
both scalar corrections' effects on the metric throughout the interval. The
certified physical mode is the tangent of the resulting exact nonlinear
constraint family, with the retained wall compatibility through fourth time
order. No static parameter sweep or spacetime evolution was performed.

Producer classification:
`LOCAL_C4_D1_NATIVE_FAMILY_CERTIFIED_WITH_EXPLICIT_CONSERVATIVE_RADIUS`.

Evidence class: analytic local existence with an interval-certified coupled
Jacobian and exact rational complex-domain comparison bounds. This is a local
constraint-family theorem, not a claim inferred from a finite mesh trend or
finite-difference derivative.

## Exact retained preparation

For one fixed certified physical mode `(psi,f)` on the exact central background,

    ell = -2 epsilon psi,
    Phi = Phi_star + epsilon f + C7(epsilon,s) + b0 H0(s) + b1 H1(s),
    H0 = s^5 (D-s)^6/(120 D^6),
    H1 = s^6 (s-D)^5/(120 D^6).

The degree-seven Hermite correction C7 is precisely the predecessor's analytic
preparation. Each added shape has its own fifth endpoint derivative equal to
one and preserves all derivatives through fourth order at both endpoints.
The nonlinear Hamiltonian IVP determines the metric from A(0), with the lower
Israel derivative imposed. The unknowns are `(A(0),b0,b1)`; the equations are
the upper Israel mismatch and the two normalized fourth-time scalar Robin
rows. The complete inherited scalar-root interval and wall-event interval,
not fitted point estimates, remain controlling.

The fixed mass interval is `(-33/25000,-131/100000)`. The exact six action
literals, initial scalar interval and full event interval are recorded in
`BINDINGS.json`. The event interval is
`[32727/16384,32729/16384]`.

## Coupled argument and measurements

If `h=delta A` and `eta=delta Phi`, the complete metric response is

    h_ss + 4H h_s + 2q h = -(m2 Phi eta + T eta_s)/3,
    q = k exp(-2W).

The independent divergence form evolves `Q=exp(4W)h_s`. Neither formulation
discards the shape-induced metric response. At the upper wall, write
`d=u_s(D)`, `cj=wj_s(D)` and `beta=8q B_upper`. Exact algebra gives

    J = [ d       c0       c1        ]
        [ 0       1        0         ]
        [ beta*d  beta*c0  1+beta*c1 ].

Subtracting beta times the first row from the third proves `det J=d`.
The numerical certificate nevertheless encloses the complete matrix and its
inverse. A separate dual-number evaluation of the original time equations
checks the endpoint reductions. Thus the analytic simplification is not a
substitute for propagating the full coupled system.

| Certificate | Direct form | Divergence form |
| --- | ---: | ---: |
| Validated cells | 8,183 | 16,365 |
| Full determinant enclosure, displayed approximately | [-0.9588769541, -0.9584013416] | [-0.9588769696, -0.9584013366] |
| Maximum Picard iterations | 3 of 32 | 3 of 32 |
| Elapsed calculation time | 9.01 s | 18.56 s |
| Full wall-event coverage | Pass | Pass |
| Original/reduced endpoint identities | Pass | Pass |
| Background, model and inverse premises | Pass | Pass |

Exact rational interval endpoints, not these rounded display values, are the
certificate in `output/RESULT.json`. Both implementations enclose both event
subintervals, split at `4091/2048`. Corresponding full-matrix entries overlap,
and each analytic determinant agrees with its inherited one-variable derivative
enclosure. The full determinant is strictly negative in both calculations.
The producer completed in 27.679 seconds using one process, one arithmetic
thread, 768-bit Arb arithmetic and a 4 GiB address-space limit.

## Existence statement and radius

There is a unique local analytic choice of the three correction parameters
near the zero-amplitude background. In the shifted chart `a=A(0)-epsilon`,
the exact physical-mode tangent gives

    a = O(epsilon^2), b0 = O(epsilon^2), b1 = O(epsilon^2).

The higher corrections do not change the first-order physical mode or its
nonzero separation variation. Lower-order scalar compatibility follows from
the retained preparation and the solved Israel conditions. The mixed Einstein
identity relates the fourth Israel condition to scalar Robin and second-time
compatibility, so no extra free parameter is silently required.

The explicit real amplitude interval certified by the conservative argument is

    |epsilon| <= 2^-9216.

The proof uses a complex parameter polydisc of radius `2^-4096`, the declared
boundary-map bound `2^512`, inverse-norm bound `2^64`, and exact rational
majorants. The fixed contraction factor is at most `2^-441`, and the self-map
remainder divided by the unknown-ball radius is at most `2^-443`. Every
runtime premise of that argument passed over the full validated interval.
The stronger measured majorant ceilings were not used to tune the proposed
radius after seeing results.

This extremely small radius is an explicit existence witness, not a useful
finite-amplitude error guarantee. It includes none of the predecessor's
`+/-1e-5` or `+/-5e-6` examples. Those remain numerical examples, not members
certified by this radius. The word C4 here denotes the retained finite-order
wall compatibility; it is not all-order compatibility or a hyperbolic
spacetime-existence theorem.

## Technical failure retained, not erased

The original frozen attempt at
`../lin-c4-local-certificate-20261005T214000Z` failed before accepting its first
cell. Its Picard box builder inflated already-contained components, including
the affine coordinate s'=1; this amplified the high-degree forcing while the
initially zero correction columns caught up. It is sealed as
`TECHNICAL_INCOMPLETE_ENCLOSURE_CONSTRUCTION`, with no physical conclusion.

R1 preserves a currently contained component and rechecks every component
against the full updated box on each iteration. It changes no step, precision,
iteration ceiling, inflation amount, input interval, equation or scientific
gate. An exact polynomial-forcing control exercises this failure mode. All 15
synthetic controls passed before the R1 freeze, including native checkpoint
roundtrip, fresh-process next-step equality and changed-guard rejection.

The original failure and binding are authenticated inputs to R1. No frozen
source, previous result, manuscript, research inventory or other chat's packet
was modified. Both numerical formulations share Arb, shape/series arithmetic
and the Taylor/Picard driver. Their agreement is independent formulation
corroboration, not verification by disjoint arithmetic implementations.

## Where this leaves the line

The final corrected initial-data family is no longer supported only by the
finite C4 examples: the local nonlinear constraint/compatibility bridge to
the certified physical mode is supplied. This is a positive mathematical
advance on a specific admission gap.

It does not solve the separate hyperbolic formulation or well-posed boundary
problem, demonstrate a spacetime development, justify any finite-amplitude
evolution, determine nonlinear fate, or demonstrate a horizon or child universe.
The static physical mode and this local family remain distinct from a dynamical
outcome. None of the prior causal admission blockers is silently waived.

The next justified task, if separately authorized, is to reconcile this exact
family and its finite-order boundary compatibility with an actually well-posed
evolution formulation and its constraint propagation. A practical certified
amplitude range is also still open. Neither task is launched by this packet.

## Artifact map

- `BINDINGS.json`, `FREEZE_RECORD.json`: guard, exact inputs, source/reviewer/runtime hashes.
- `CONTRACT.md`: unchanged scientific question and disclosed R1 construction repair.
- `INDEPENDENT_C4_DERIVATION.md`, `INDEPENDENT_BOUNDARY_ALGEBRA.json`: exact coupled argument.
- `ANALYTIC_RADIUS.md`, `majorants.py`: complex-domain and contraction proof.
- `preflight/RESULT.json`, `PREFLIGHT_REVIEW.md`: source-bound launch qualification.
- `output/RESULT.json`, `output/TERMINAL.json`, `output/checkpoints/`: numerical certificate and recovery.
- `INDEPENDENT_AUDIT.json`, `POSTRUN_REVIEW.md`: independent final disposition.
- Root `RESULT.json`, `MANIFEST.json`: authoritative acceptance and immutable artifact inventory.

R1 guard: `233defdff9efcaef4e2c0b427af22776b85c94c233894a7da16e3a9936cf2cdc`.
No numerical worker or successor remains running for this packet after its
producer terminal. Other research lines must be checked separately.
