# Finite upper wall stiffness response

This prospective test keeps the certified central background and lower wall fixed while increasing the upper wall Hessian from 20 to 120. It seeks a finite, strictly positive mass displacement, not an extrapolation of the infinitesimal coefficient. A separate analytic argument identifies a branch for every finite nonnegative upper Hessian increment.

## Model and launch

Use the exact action, model dyadics, background launch interval A, event interval D, normalization psi(0)=1, 768 bit arithmetic, and unchanged two interval Taylor engines in `inputs/central_bindings.json`. The engines are byte copies of the previously qualified primary and independent producers. All stored interval and original producer validity premises remain inherited. No background or mode central value substitutes for an enclosure.

The deformation is tau_b(Phi) plus eta times (Phi−Phi_b*) squared divided by two, where Phi_b* is the actual upper background value. The first jet is unchanged, so the background is exactly preserved. The lower wall and its launch remain unchanged. In proper distance the residual is exactly R_eta=R_0+eta f_b/2. Neither the bulk equation nor the normalized lower launch depends on eta.

## Frozen finite test

The choice eta=100 is a sixfold upper Hessian, 20 to 120. Run both engines at exactly three masses: low −33/25000, high −131/100000, and finite_lower −164/125000. No bisection, replacement point, parameter tuning or retry is permitted. Each event row stores both R_0 and f at the whole certified event interval, with native state index 6 in the primary engine and 5 in the independent engine. Hulls cover every event cell without gaps.

For each engine separately require R_eta(low)>0 and R_eta(high)<0 uniformly for eta in [0,100]. Require also R_100(finite_lower)>0. The accepted original full mass strip and its profile positivity bounds apply unchanged because the initial value problem is unchanged. The accepted positive-overlap Green identity therefore gives exactly one real eigenvalue in this strip for each eta, including the original tracked root. Smoothness and the nonzero determinant derivative give its continuous differentiable dependence. The final root lies strictly between −0.001312 and −0.00131. The accepted initial upper bound is −4199/3200000, so the mass increase is strictly greater than 3/16000000=0.0000001875. This is a predeclared coarse finite displacement, not a precision target.

For the all-finite theorem, additionally record the strict low-mass signs R_0>0 and f_b>0. With the independently reviewed analytic upper endpoint sign at lambda=0, these provide a compact branch continuation domain for all finite eta>=0. That theorem is conditional on the proof and inherited background inputs, not established by signs alone.

## Classification and controls

`FINITE_RESPONSE_AND_GLOBAL_BRANCH` requires every finite and all-finite predicate in both engines plus terminal independent acceptance. `GLOBAL_BRANCH_ONLY` retains the all-finite witness if the predefined finite displacement predicates fail; it does not certify the sixfold displacement. `INCOMPLETE` records failure of the required witness or technical enclosure. An interval containing zero never counts as a sign. Preserve every failure and do not retune.

Controls include the inherited engine algebra controls, exact zero-touching rejection, denominator rejection, event-gap rejection, finite values, positive warp, and zero-containing constraint and first integral on every flow cell. These consistency checks do not replace the qualified Picard enclosure theorem. Source hashes and the runtime binary hashes are checked before launch. Production is at most six sequential flows, 90 seconds each and 300 seconds total, one worker and BLAS1. The absolute cutoff reserves 600 seconds before the hour deadline. The coordinator lease additionally applies. Expected runtime is about one minute from the preceding ten-flow run.

The independent terminal audit is sequential after production, at most 180 seconds, and reconstructs every event hull, affine residual interval, predicate and exact displacement using independent rational arithmetic; checks cell counts, coverage, source/runtime/gate hashes, execution and controls; and reviews the analytic proof. It need not rerun the validated engines. The two distinct engines provide independently formulated numerical enclosures, while their original producer-time validity remains inherited.

## Sources and scope

`SOURCE_BINDINGS.json` binds local source copies and inherited reports/proofs. The previous narrowed mass bracket identifies the same unique central branch; the stored strip covers all masses in this test. The regular positive norm and local response theorem come from the accepted finite stiffness proof, not a singular weighted scalar norm at the turning point. No claim about all eigenvalues, nonlinear stability, a stabilizing threshold, or generic novelty follows. The primary literature comparison is retained separately.
