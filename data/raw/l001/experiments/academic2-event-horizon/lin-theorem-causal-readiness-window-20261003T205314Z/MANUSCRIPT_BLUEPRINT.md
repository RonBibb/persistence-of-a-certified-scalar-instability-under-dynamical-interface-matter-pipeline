# Theorem-paper blueprint

## Scientific identity

**Question.** For one fixed five-dimensional Einstein--scalar model with two
quadratic wall potentials, are the wall junction conditions compatible with a
positive-curvature static geometry at the originally prescribed separation?

**Answer.** A positive-curvature solution exists and is locally unique on the
certified shooting interval when the second wall is placed at its first
transverse Israel event, selecting a proper separation near 1.9975. For the
same action, wall parameters, orientations, and launch family, an exhaustive
interval cover excludes every positive-curvature solution at the prescribed
separation near 0.999639 throughout the declared launch interval.

**Contribution.** The paired result establishes a model-specific static
compatibility failure: the desired curved branch is not absent, but it is
incompatible with the prescribed separation in the certified reduced family.
It is not a claim of a new scalar stabilization mechanism.

## Working title

**Computer-assisted existence and fixed-separation exclusion in a
five-dimensional Einstein--scalar two-wall boundary-value problem**

Short alternative:

**A certified separation mismatch in a five-dimensional Einstein--scalar
two-wall model**

## Abstract draft

We prove a paired computer-assisted result for a fixed five-dimensional
Einstein--scalar model on a two-wall interval. Reduction of the warped
maximally symmetric field equations and doubled-cover junction conditions
gives a one-parameter first-event shooting problem. Validated interval
integration and a strict interval-Newton inclusion establish a locally unique
positive-curvature solution whose proper separation lies near 1.9975. A second,
producer-independent Taylor--Picard implementation reproduces the root and
encloses the curvature, warp factor, conformal length, first integral, and wall
identities. For the same action, wall parameters, orientations, and launch
family, an exact adaptive interval cover of the full declared launch interval
excludes every positive-curvature solution at the prescribed separation
0.9996389747145851: all 693 terminal boxes are resolved, and the upper-wall
residual vector satisfies `max(|G|,|h|)>0.0077` wherever positive curvature is
admissible. The separation mismatch is therefore a certified property of
this reduced static family rather than a missed shooting root. The result does
not establish stability, dynamical selection, collapse, or a causal horizon.

## Main-text architecture

### 1. Introduction: the compatibility question

Open with the physical tension, not the verification history. Bulk scalars can
select inter-wall spacing; curved wall solutions, phase-space wall curves,
numerical shooting, multiplicity, and even instability-driven restructuring
are known in related two-brane models. The concrete question here is narrower:
whether one source-pinned action and set of wall potentials simultaneously
support the desired positive four-curvature and the prescribed proper
separation, with a proof rather than an unconstrained root search.

The opening pages should establish three points:

1. scalar-selected spacing and curved scalar branes are established ideas;
2. a numerical near-root at one wall placement does not answer compatibility
   at another prescribed placement;
3. the contribution is a paired, machine-checkable existence/exclusion result
   for one fixed reduced model.

State the main theorem before discussing protocols, hashes, or implementation
details. End the introduction with the static-family boundary.

### 2. Fixed model and two reductions

Give the action, warped maximally symmetric ansatz, potentials, units, and the
six exact binary64 input literals. Derive the proper-distance IVP, first
integral, lower launch map, upper residuals, and both boundary placements:

- variable separation: first transverse `G=0` event followed by `q(a)=0`;
- fixed separation: simultaneous residual `R_D0(a)=(G,h)=0`.

This section should be analytic. The normal-orientation table can appear in a
short appendix, with only the final junction conditions in the body.

### 3. Paired theorem

State Theorem 1, Theorem 2, and the separation-mismatch corollary together.
Readers should see the numerical intervals, exact launch domains, cover count,
and residual floor before seeing implementation detail.

### 4. Variable-separation existence and uniqueness

Explain the validated flow, transverse first-event map, total derivative, and
interval-Newton self-map. Report the original narrow root/event certificate.
Anchor the interval-Newton implication and validated Taylor-flow method to the
standard references collected in `METHODS_CITATION_CHAIN.md`, while making
clear that the local certificates—not the citations—establish the hypotheses
for this model.
Then explain why an independent implementation was needed and report only its
load-bearing geometric enclosures:

- independent root image;
- positive curvature;
- negative `G_s`;
- positive `q'`;
- positive global warp and finite conformal length;
- first-integral and wall-identity containment.

The point of the replay is producer independence, not a second physical
solution.

### 5. Fixed-separation exclusion

Describe the exact adaptive cover and four discharge rules. Report the 693-box
classification once, preferably as one table or horizontal cover plot. Explain
why zero unresolved boxes and the uniform 0.0077 residual floor turn a failed
search into an exclusion theorem over the declared positive-curvature class.

### 6. Interpretation and comparison

The scientific inference is that the fixed inputs overconstrain the desired
positive-curvature static branch at `D0`; allowing the upper-wall position to
be selected yields a certified solution at roughly twice that separation.
This can be compared with prior work in which scalar and wall parameters select
distance and curvature together. It must not be described as a force causing
the walls to move, because no dynamics is solved.

Present the novelty as the exact paired certificate. Prior curved branches,
local uniqueness expectations, scalar stabilization, and computer-assisted
Einstein existence proofs are context, not claims of novelty.

### 7. Limitations and conclusion

State once, directly, that the theorem is restricted to the reduced static
ansatz, fixed binary64 literals, frozen local root interval, exact `D0`, and
`0<=a<=v0`. Stability, alternative potentials, other launch domains,
non-maximally symmetric solutions, Cauchy evolution, collapse, marginal
surfaces, event horizons, and baby universes remain outside the theorem.

Close with the positive contribution: the result converts an apparent failure
of the original fixed-distance construction into a precise theorem about where
the compatible curved branch exists and where it cannot exist.

## Main article evidence

The body needs only two principal tables and, at most, two figures.

### Table 1: fixed model and theorem intervals

Include the six fixed literals, root interval, event-separation intervals,
curvature, `G_s`, `q'`, exact `D0`, launch domain, cover count, and residual
floor. Do not include hashes in this table.

### Table 2: independent replay geometry

Include original versus independent producer, method, step level, Newton image,
event interval, warp enclosure, conformal separation, and identity-containment
status. This table answers the implementation-dependence concern.

### Figure 1: paired boundary-placement geometry

The ready figure `figures/certified_separation_mismatch.pdf` shows the global
`D0`--D1 gap and a zoomed comparison of the independent and original D1
enclosures. Its provenance is in `FIGURE_PROVENANCE.json`. A separate schematic
may show the same lower launch family reaching either:

- the first transverse upper-Israel event at variable `D(a)`; or
- the prescribed slice `D0`, where both residuals are demanded.

It must be labeled as a schematic, not as a spacetime evolution.

### Figure 2: exact D2A cover classification

The ready figure `figures/d2a_exact_cover.pdf` plots the launch interval as
contiguous terminal boxes colored by discharge rule, resolves the three narrow
single-residual boxes in a zoomed panel, and shows the certified residual
distance from zero. The residual panel uses horizontal boxwise interval lower
bounds rather than sampled midpoint values. Its source and hashes are bound in
`FIGURE_PROVENANCE.json`.

## Supplement and archive placement

The supplement should contain the full reduction details, sensitivity system,
interval-Newton theorem used, event-isolation criteria, adaptive-cover
algorithm, exact rational endpoint tables, junction audit, environment matrix,
and failure/incompleteness definitions.

The methods bibliography and the precise role of each general theorem are
mapped in `METHODS_CITATION_CHAIN.md`.

The archive should contain the exact sources, machine-readable results,
manifests, all checkpoint addresses, verifiers, replay commands, and the
optional 150.9 MB D2A checkpoint pack. Protocol chronology, mutable status
files, and cache artifacts should not appear in the article.

## Editorial failure modes to prevent

- Do not lead with the number of tests or audits.
- Do not describe the theorem as evidence for a dynamical transition.
- Do not call local uniqueness of a curved branch novel.
- Do not imply the parameter set is generic; explain its source provenance.
- Do not hide the 0.9996 versus 1.9975 contrast under implementation detail.
- Do not let the event-horizon research line enter the title, abstract, or
  theorem.
- Do not claim an absolute literature first; use bounded “to our knowledge”
  language after a conventional citation review.

## Submission-readiness gate

The paper becomes submission-ready only when the article is written and
compiled from the actual upload package, the compact proof archive has been
clean-replayed from its staged relative paths on both macOS and Linux, all
references have been bibliographically verified, and the author has authorized
an external archive or submission. None of those external actions occurs in
this window.
