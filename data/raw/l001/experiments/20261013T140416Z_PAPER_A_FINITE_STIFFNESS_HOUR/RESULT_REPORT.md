# Finite stiffness response and the continuing mode branch

Three linked results are accepted: a certified finite upper wall response, a quantified upper Dirichlet saturation limit, and a smooth two-wall response surface extending to the double Dirichlet limit. Here mu is the physical scalar mass-squared eigenvalue in the model's units, and lambda=mu+4k is its curvature-shifted parameter. These are linear scalar modes of the fixed static background, not changes in black-hole mass or energy, dynamical relaxation, or a horizon result.

The frozen sixfold upper wall stiffness test passed both validated engines and [independent terminal audit](TERMINAL_REVIEW.json). The upper wall Hessian changes from 20 to 120 while the exact background and lower wall remain fixed. This is a finite mode displacement, not an extrapolation of the earlier local sensitivity. The action change is eta(Phi−Phi_b*)²/2 at the actual background wall value; merely changing the original gamma while holding its other potential parameters fixed would not be this background-preserving deformation.

The accepted initial mode satisfies −0.0013125<mu(0)<−0.0013121875. At the new Hessian, the predefined signs give −0.001312<mu(100)<−0.00131. Therefore

mu(100)−mu(0)>0.0000001875.

Exactly one real mode remains in the original certified mass strip throughout eta in [0,100]. The interval signs and the inherited positive-overlap uniqueness proof identify this as the same branch. The second audit strengthens strip persistence and uniqueness to every finite eta>=0. The eta100 bracket is intentionally coarse; the main new fact is nonoverlap and a finite response over the complete parameter interval.

## Continuation beyond the tested finite interval

The independently gated division-free proof, with its now-passing numerical lower endpoint witness, continues the original mode for every finite eta>=0. The branch increases strictly and approaches a branch-selected upper Dirichlet limit:

mu(0)<mu(eta)<mu_D<−4k<0, for eta>0.

At every finite eta, dmu/deta=a_b^4 f_b²/Z>0, where Z is the regular positive norm. The limiting profile satisfies f_b=0. The proof constructs an auxiliary solution at mu=−4k without dividing by the scalar derivative, and uses compactness and simple-root continuation. It neither integrates through a singular reduced equation nor substitutes a rounded background.

This is a constructive branch and saturation theorem. It does not identify the lowest eigenvalue, classify the other modes, or establish nonlinear stability. The exceptional auxiliary endpoint is not asserted to be a physical eigenmode.

## Quantified upper wall saturation

The distinct [Dirichlet limit test](DIRICHLET_DESIGN.md) passed its frozen criteria and [independent terminal audit](DIRICHLET_TERMINAL_REVIEW.json). It identifies the limit of this branch, not merely an unrelated Dirichlet root:

−0.00131175000 < mu_D < −0.00131171875.

The bracket has width 3.125e−8. Consequently the total available upper-wall-only gain is

4.375e−7 < mu_D−mu(0) < 7.8125e−7,

and the gain still available after the sixfold Hessian change obeys

0 < mu_D−mu(100) < 2.8125e−7.

The finite change therefore captures strictly more than 24 percent of this mode's total upper-wall-only mass-squared gain. This is a conservative certified lower bound, not an estimated fraction. The lower wall remains fixed throughout. The twelve midpoint flows took about 91 seconds and stopped at the predefined target; no replacement endpoints, retries or tuning were used.

## Independent control of both wall Hessians

The separately frozen [two-wall proof](TWO_WALL_PROPOSAL.md) passed [direct independent analytic review](TWO_WALL_REVIEW.json), without a new numerical integration. Add eta_i(Phi−Phi_i*)²/2 independently at both walls, with finite eta_i>=0. The same tracked mode defines a single smooth response surface, and its physical mass-squared increases strictly with either Hessian.

Reciprocal Hessians c_i=1/(20+eta_i) compactify the family to [0,1/20]². The proof shows that the lower normalized launch remains regular at c_a=0, the upper determinant remains regular at c_b=0, and every retained root stays simple with positive regular norm. A uniformly negative auxiliary determinant at lambda=0 traps the branch below that shifted-mass boundary. Parameter-dependent local uniqueness makes the continuation one consistent surface, including the edges and corner.

The surface has its strict maximum at the double Dirichlet corner. Calling that branch-selected value mu_DD, every finite nonzero pair of nonnegative stiffness increments obeys

mu(0,0) < mu(eta_a,eta_b) < mu_DD < −4k <0.

The initial point gives equality in the first comparison. The upper-only Dirichlet limit satisfies mu_D<mu_DD. The numerical bracket above applies only to mu_D, with lower Hessian20 fixed; no numerical value or quantitative gap for mu_DD was established. The endpoints c_i=0 are Dirichlet limits, not finite wall potentials. This result constructs and bounds the same mode's response under independent finite controls; it does not characterize unrelated spectral branches.

## Evidence and interpretation

The [frozen design](DESIGN.md), [branch proof](FINITE_BRANCH_PROOF.md), [pre-run gate](INDEPENDENT_GATE.json), and [exact output](output/RESULT.json) record the hypotheses and interval predicates. Production used six sequential flows with the original qualified primary and independent engines, no tuning or retry, and about 46 seconds of runtime. Stored interval and original producer validity remain inherited premises.

Stiffness-dependent masses, background-preserving Hessian variation and stiff-wall instability are known phenomena. The [primary literature comparison](LITERATURE_COMPARISON.md) places this result as a model-specific certified curved-background continuation with a regular scalar turning point, not a priority claim or new generic stabilization mechanism.

The [completion checklist](COMPLETION_CHECKLIST.md) maps the objectives to their gates, audits, source and runtime records. The next highest-value step is to consolidate these accepted results into a Paper A proposition and proof with explicit literature comparison. A separately authorized double-Dirichlet mass certificate could then quantify the joint maximum; full-spectrum counting and nonlinear dynamics remain separate higher-cost problems. No shared manuscript was edited and no automatic successor was launched.
