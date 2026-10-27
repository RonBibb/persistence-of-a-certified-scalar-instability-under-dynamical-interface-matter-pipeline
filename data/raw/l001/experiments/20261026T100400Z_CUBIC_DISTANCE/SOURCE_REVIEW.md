# Independent prospective source review

Reviewer: `ab_mechanism_scope`. Read `CONTRACT.md`, `math_core.py`, `producer.py`, `storage.py`, `runner.py` and completed `audit.py`. **No blocking mathematical/source defect identified in the proposed distance construction.** This document is source review, not execution admission, a syntax-run receipt, or a terminal result. Main is responsible for the Linux AST gate before freeze.

## Physical coefficient and transport

For the frozen Eulerian chart, the cubic coefficient of `exp(b)` is `c3-2p3-2p1*c2+4p1*p2-(4/3)p1^3`. Expanding the moving integration endpoints gives `xi_b3-xi_a3 + integral(density) + [b1*xi2 + (b2+b1^2/2)*xi1 + b1prime*xi1^2/2]_a^b`. With `b1=-2p1` this is precisely the implemented endpoint expression, including the negative `p1prime*xi1^2` term. No factorial convention has been silently changed.

The generic transport derivative has all required terms: `-2u X2 -2p1 X2prime + w2prime X1 + w2 X1prime -uprime X1^2 -2u X1 X1prime`. The first-order derivative and second-order forced momentum expressions used to evaluate these quantities agree with the inherited equations. The producer's sparse-polynomial control differentiates the endpoint expression using the lower RHS; the auditor has a separately written formal product-rule control. These are intended execution gates, not identities claimed to have run during this review.

## Interval coverage and dependence

- Every parent whole-cell box is consumed, with a mandatory interval length below `D_lo` and optional signed contribution `density*[0,optional_length]` through `D_hi`. The exact totals must equal `D_lo` and `D_hi-D_lo`. This encloses the uncertain upper domain, including negative densities and cells beyond the mandatory prefix.
- Full A2 and A3 bindings are retained. The authoritative bulk integral multiplies one full A3 interval by the integrated homogeneous contribution. The direct whole-density calculation is a consistency comparator only. The endpoint and integrated transport forms likewise are not intersected to sharpen the answer.
- Affine interpolants are defined over the uncertain D, with full wall displacements and slopes. Their overenclosures lose correlations but retain each physical interpolant. Endpoint transport is the authoritative form; its integrated derivative is a cross-check.
- Dyadic denominator `2^80` exports explicitly contain their inputs. Exported contributions are used in the sums, not replaced by hidden tighter originals. The independent Fraction audit reconstructs densities, weights, sums and endpoint algebra and requires outward containment. Direct-W exponential evaluation remains an inherited producer obligation, explicitly outside that exact audit's independent coverage.
- The final cross-engine result is an outward hull, not an intersection. A zero-containing result is scientifically unresolved, not a failure to be repaired by selecting a different representation.

## Integrity and resources

Both producer and auditor stream bounded chunks, authenticate parent hashes and chain bindings, and preserve the accepted full-flow domain and inverse. The wrapper binds accepted terminals, sources and observed runtime, repeats checks after execution, preserves one-attempt failure evidence and retains the inherited one-core lease/aggregate policy. Atomic publication uses fsync and no-overwrite links. Production plus audit have the declared 1800-second budget; no new ODE, exact-resume promise or automatic successor is introduced.

## Minor prefreeze robustness note

Source review flagged a potential sub-`2^-80` sign/export edge: a sign decided before final outward export can become unresolved after export. **Resolved before freeze:** I reread the updated producer and auditor. The producer now classifies the exact endpoints of the exported final interval. The auditor checks that classification, retains outward containment of the un-intersected engine hull, permits widening to unresolved, and requires the same raw-hull sign whenever the export is nonzero. This neither creates a sign nor rescales an executed result. Main reports the Linux AST check passed for all five scripts; no additional computation was performed by this reviewer. No outstanding source-review blocker remains.

## Claim boundary

The calculation can establish a signed or unresolved **formal cubic proper-distance coefficient for the frozen lower-current direction**. It cannot by itself establish a finite-amplitude shortening, convergent nonlinear branch, evolution, tail bound or radius. The completed upper inverse was a prerequisite; its negative shooting coefficient does not preassign the distance sign.
