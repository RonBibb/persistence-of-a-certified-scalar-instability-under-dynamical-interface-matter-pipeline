# Updated manuscript-readiness decision

## Verdict

**GO TO A NARROW MANUSCRIPT DRAFT; NOT YET SUBMISSION-READY.**

The mathematical core is now strong enough to organize as a paper.  The two
proof-authority gaps that previously made the old consolidation conditional
have been closed by a sealed producer-independent replay, complete geometric
enclosures, an explicit reduction lemma, an exact dependency-free algebra
check, and a line-by-line junction convention audit.

This decision applies only to a computer-assisted theorem paper about the
reduced static boundary-value problem.  It is not a decision to merge the result
into the collapse, MOTS, event-horizon, or baby-universe line.

## Central result

For the fixed binary64 parameter literals

`m^2=0.41`, `gamma=20`, `v0=0.1`,
`v1=0.09048374180359596`,
`lambda_a=5.999990376773895`, and
`lambda_b=-6.052844277744164`,

the reduced Einstein--scalar two-wall system has a locally unique
positive-curvature shooting solution when the upper wall is placed at the first
transverse Israel event.  The original 32,768-step certificate locates the
proper separation in

\[
 D\in[1.99749755859375,1.99761962890625].
\]

An independent Taylor--Picard/interval-Newton implementation reproduces the
root and encloses the wider first-event interval

\[
 D\in[1.9974365234375,1.9976806640625]
\]

with strictly positive curvature

\[
 k\in[0.000326841301145298,0.0003268413757636101].
\]

For the same action, parameters, orientations, and launch family, the D2A exact
cover excludes every positive-curvature solution satisfying both upper-wall
conditions at

\[
 D_0=0.9996389747145851
\]

throughout the declared `0 <= a <= 0.1` domain.  Its 693 terminal boxes leave
zero unresolved cases; on every box not excluded by negative curvature,
`max(|G|,|h|)>0.0077`.

The paired statement—not either ingredient in isolation—is the paper's central
contribution: the fixed-separation mismatch is a certified property of this
reduced model rather than a missed numerical root.

## Closure of the old critical gaps

| Old requirement | Current state | Authority |
|---|---|---|
| Producer-independent D1 interval-ODE replay | **closed** | sealed classification `INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS` |
| Curvature, length, warp, first-integral, and wall enclosures | **closed** | independent result SHA `41077a79...d16`; exact authority table |
| Formal action-to-IVP/first-event/fixed-distance reduction | **closed for draft** | `FORMAL_REDUCTION_LEMMA.md` |
| Algebra and coordinate identities | **closed** | dependency-free exact checker, five passes |
| Junction signs and factors | **closed for the fixed convention** | `JUNCTION_CONVENTION_AUDIT.md`, `PASS` |
| Human-auditable proof interval table | **closed** | `THEOREM_AUTHORITY_TABLE.md` and exact JSON |
| Focused primary-source citation chain | **materially advanced** | `NOVELTY_CITATION_CHAIN.md`; priority remains bounded |
| Standard validated-numerics method citations | **closed for draft** | `METHODS_CITATION_CHAIN.md`; model-specific hypotheses remain locally certified |
| Scientific motivation and provenance of the exact parameter point | **closed for draft** | `PARAMETER_PROVENANCE_AND_MOTIVATION.md`; source ancestry is explicitly separated from dynamical ancestry |
| Clean cross-platform certificate replay | **closed for existing sealed records** | dependency-free checks pass on macOS and Linux; see `CROSS_PLATFORM_VERIFICATION.md` |
| Clean public source archive and stable identifier | **open** | must be built from the minimal proof sources |
| Full article and clean compile/render audit | **open** | no manuscript package produced in this window |

## Defensible novelty

The literature already contains bulk-scalar stabilization, scalar-selected
brane distance, curved de Sitter/anti-de Sitter scalar branes, and
computer-assisted Einstein existence proofs.  None is a novelty claim here.

The focused search did not locate the exact paired theorem for one fixed
two-wall model: validated local existence/uniqueness after variable separation
selection together with exhaustive positive-curvature exclusion at a separately
prescribed separation over the complete declared launch interval.  The article
should therefore say **“to our knowledge”** and present the pairing as a
model-specific result, not claim a new stabilization principle or universal
nonexistence.

## Required before submission

1. Write the article in theorem-proof form using the formal reduction and
   authority table; do not structure it as a protocol history.
2. Build a minimal clean archive containing exact input literals, the original
   D1 producer certificate, the independent D1 replay, D2A cover, verifiers,
   environment specifications, commands, and machine-readable results.
3. Replay the eventual packaged archive in a clean environment and retain the
   transcript.  The current unbundled checks already pass on macOS and Linux;
   the remaining requirement is to verify the actual publication package.
4. Finish a conventional forward/backward **physics novelty** citation check through citation
   databases and the bibliographies of the closest papers before asserting
   even bounded novelty in submission prose.
5. Integrate the prepared source-pinned motivation into the article without
   implying that the collapse selects the static solution.
6. Compile from the actual upload package and inspect every page, equation,
   table, reference, cross-reference, and data-availability statement.

## Recommended argument structure

1. Ask whether the source-pinned wall model admits the required curved static
   background at its prescribed separation.
2. Define the fixed action and derive the two reduced problems.
3. State the paired theorem immediately.
4. Present D1 existence/uniqueness and independent replay.
5. Present D2A exhaustive exclusion and uniform residual floor.
6. Explain the separation mismatch and exactly what the certificates exclude.
7. Compare with established scalar-brane and rigorous-numerics literature.
8. End with the static-family boundary: stability and dynamical selection are
   open.

Full hashes, checkpoint inventories, failed precursor runs, and operational
details belong in the supplement/archive, not the article's main argument.

## Suggested title

**Computer-assisted existence and fixed-separation exclusion in a
five-dimensional Einstein--scalar two-wall boundary-value problem**

## Updated abstract seed

We prove a paired computer-assisted result for a fixed five-dimensional
Einstein--scalar model on a two-wall interval.  A reduction of the warped
maximally symmetric field equations and junction conditions gives a
one-parameter first-event shooting problem.  Validated interval integration
and a strict interval-Newton inclusion establish a locally unique
positive-curvature solution whose proper separation is near `1.9975`; an
independent Taylor--Picard implementation reproduces the root and encloses the
curvature, warp, first integral, and wall identities.  For the same action,
wall parameters, orientation, and launch family, an exact adaptive interval
cover of `0 <= a <= 0.1` excludes every positive-curvature solution at the
prescribed separation `D0=0.9996389747145851`: all 693 terminal boxes are
resolved, and `max(|G|,|h|)>0.0077` wherever positive curvature remains
admissible.  Thus the
separation mismatch is intrinsic to this reduced static family rather than a
missed shooting root.  The theorem does not establish stability, dynamical
selection, collapse, or an event horizon.

## Viability

The line is **viable as a specialist mathematical-relativity/validated-numerics
paper**. Its independence from the unresolved dynamical line is a strength: the
theorem remains true even if no compatible causal evolution is ever
constructed.

The chief remaining risk is significance and framing rather than internal
certificate correctness. Felder--Frolov--Kofman and Martin et al. already give
the phase-space wall-curve picture, numerical shooting for specified brane
potentials, possible multiplicity/nonexistence of warped configurations, and
dynamical restructuring. A referee may therefore regard a single
parameter-point certificate as too narrow unless the paper makes the
source-pinned compatibility question and the exhaustive fixed-separation
exclusion scientifically clear. Burying the pair under protocol detail or
implying unsupported dynamics would make that risk worse.
