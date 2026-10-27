# Proof-obligation audit

## Purpose

This audit separates mathematical obligations from implementation and archive
controls. A hash match proves identity, not a theorem; a numerical enclosure
proves a theorem clause only when the enclosing algorithm and the clause are
connected explicitly.

## Theorem 1 — variable-separation existence and local uniqueness

| Obligation | Evidence | Status and boundary |
|---|---|---|
| The reduced IVP follows from the fixed action | Analytic reduction in `FORMAL_REDUCTION_LEMMA.md`; exact checks of the Einstein reductions, constraint propagation, conformal first integral, and wall identity | **Satisfied for the fixed convention.** This is not a derivation for other actions or signatures. |
| Both wall orientations and half-Robin factors agree with the source action | Line-by-line outward-to-inward normal audit; lower launch and upper residual comparison with the frozen code | **Satisfied.** `JUNCTION_CONVENTION_AUDIT.md` returns PASS. |
| The flow is regular over the represented interval | Validated Picard self-containment on every cell; positive global warp enclosure | **Satisfied on the certified domain.** No claim beyond the event interval. |
| The event used by the shooting function is transverse | `G_s` is strictly negative on the event enclosure | **Satisfied.** This licenses the local implicit-event map. |
| The total shooting derivative is correct and excludes zero | State sensitivity plus implicit-event formula; exact symbolic/algebra audit; sealed positive `q'` interval | **Satisfied on the frozen launch interval.** |
| A zero exists and is unique in the frozen interval | Strict interval-Newton self-map with derivative interval excluding zero | **Satisfied locally.** It is not global uniqueness in `0<=a<=v0`. |
| The root corresponds to a positive-curvature regular geometry | Strictly positive curvature, positive warp, finite positive conformal length, and first-integral/wall-identity enclosures | **Satisfied on the certified root/event box.** |
| The result is not tied to one interval-ODE producer | Independent fifth-order Taylor--Picard implementation at 8,192 and 16,384 steps; independent interval-Newton and geometry enclosures | **Satisfied.** The independent replay does not import the original producer or its enclosures. |
| The original and independent certificates concern the same root | Both implement the same reduced IVP, launch map, first-event residual, and frozen interval; each proves exactly one zero of that common shooting function in the interval | **Satisfied.** Root identity follows from uniqueness, not merely from overlapping numerical estimates. |

## Theorem 2 — fixed-separation positive-curvature exclusion

| Obligation | Evidence | Status and boundary |
|---|---|---|
| The fixed-distance residual is the same wall problem at exact `D0` | Same reduction, inputs, launch map, orientations, and residual definitions; only wall placement changes | **Satisfied.** |
| The entire declared launch interval is covered | 693 exact rational terminal boxes form a contiguous, gap-free, non-overlapping cover from exact zero to exact binary64 `v0` | **Satisfied for `0<=a<=v0`.** |
| Every positive-curvature possibility is discharged | Twenty boxes have strictly negative curvature; every other terminal box has at least one rigorously enclosing wall residual separated from zero | **Satisfied.** There are zero unresolved boxes. |
| The exclusion is separated from a near-zero numerical accident | On every non-negative-curvature route, the interval residual vector has certified infinity-norm distance greater than `77/10000` from zero; direct exact rederivation gives a minimum boxwise lower bound `0.0077281481292751026` | **Satisfied.** The simpler theorem floor is conservative, not a tolerance-level near miss. |
| The cover classification is reproducible from the stored enclosures | Post-run audit and consolidated verifier rederive counts, exact coverage, residual floor, and 86 checkpoint content addresses | **Satisfied at certificate level.** |
| The interval flow used inside the cover has an independent producer replay | No second full D2A ODE-cover implementation exists in this packet | **Not a theorem gate, but an audit limitation.** The proof relies on the frozen Arb producer, its validated-flow parent, exact guards, and inspectable source. An independent full cover would strengthen software assurance but is not needed to state what the current certificate proves. |

## Paired corollary

| Obligation | Evidence | Status and boundary |
|---|---|---|
| D1 and D2A concern the same fixed reduced family | Identical action, exact binary64 literals, wall orientations, lower launch family, and residual definitions | **Satisfied.** |
| The separation contrast is not rounded rhetoric | Exact rational subtraction and division by positive exact `D0`, recomputed by the authority verifier | **Satisfied.** Original D1 gives `D/D0` in `[1.9982189661663317,1.9983410805652175]`. |
| The pair excludes a missed positive-curvature root at `D0` | D2A covers the full declared launch interval rather than sampling it | **Satisfied within the declared range.** |
| The pair proves a dynamical transition between the separations | No time-dependent bridge is part of either theorem | **Not satisfied and not claimed.** |

## Integrity controls

- Twenty-one bound parent files rehash correctly.
- The reconciled verifier now passes 107 checks on both macOS and Linux.
- The exact reduction checker is dependency-free and passes on both platforms.
- The older consolidated evidence verifier passes on both platforms.
- No sealed parent was modified in this window.

These controls establish evidence identity and replayability. They do not
expand the mathematical domain of either theorem.

## Audit decision

**The paired theorem is internally supportable in manuscript form.** The
remaining proof-facing task is to present the interval algorithms and standard
interval-Newton implication clearly enough for an external reader. A second
independent D2A cover would be useful software assurance, but the present
absence of one should be disclosed rather than mischaracterized as a missing
mathematical clause.
