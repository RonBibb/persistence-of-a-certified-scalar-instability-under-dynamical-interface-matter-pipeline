# Final report — standalone Lin static theorem publication track

## Success and how the bar moved

The D1/D2A line is ready to advance as a standalone narrow theorem manuscript.
The central result is stronger than the October 3 draft framing: the curved
solution is not merely locally unique near one shooting value. A later exact
cover establishes that it is the **only positive-curvature simultaneous-wall
solution on the complete declared first-event launch interval**, and a separate
two-variable Jacobian certificate shows that the corresponding `(a,D)` zero is
isolated. D2A independently excludes the original prescribed separation.

The resulting paper-level inference is:

> For the fixed reduced Einstein--scalar two-wall model, there is exactly one
> positive-curvature first-event solution on the declared launch interval. It
> is an isolated configuration near `D=1.9975`; no admissible
> positive-curvature solution exists at the prescribed
> `D0=0.9996389747145851`.

This converts the earlier “candidate at a different separation” into a paired
global-uniqueness, isolation, and fixed-separation-exclusion theorem within the
declared reduced family.

## Decisive numbers

- D1 launch box: `[0.09901086489880687, 0.09901086689880687]`.
- Original proper-separation enclosure:
  `[1.99749755859375, 1.99761962890625]`.
- Independent curvature enclosure:
  `[0.000326841301145298, 0.0003268413757636101]`.
- Global first-event cover: 726 terminal boxes, consisting of one root box,
  19 negative-curvature exclusions, and 706 scalar-residual exclusions; zero
  unresolved boxes.
- Full residual Jacobian determinant:
  `[2221.879246216278, 2224.53955879436]` in the primary producer and
  `[2220.8647309726075, 2225.5545418744878]` independently. Both are strictly
  positive.
- Fixed separation: `D0=0.9996389747145851`.
- D2A: 693 exact terminal boxes, zero unresolved, and
  `max(|G|,|h|)>0.0077` on every positive-curvature route.
- Read-only authority verification: 23/23 checks pass on macOS and Linux.

The later generalized-harmonic support is also technically positive but is not
part of the theorem. The raw background acceleration falls to
`1.6732223747e-6` at `513 x 241`, with last observed order `4.682`, and the
roundoff-corrected short scalar response passes through `t=0.001`.

## Issues and boundaries

1. The theorem fixes one exact parameter point, one reduced static ansatz, the
   declared launch interval, positive curvature, and the first-event branch.
2. The D2A cover has one proof-bearing interval producer. Its exact stored
   cover is independently audited, but a second full implementation has not
   regenerated it.
3. No parameter-neighborhood theorem exists.
4. The GH scalar perturbation is not a constraint-solved perturbation family,
   spans one amplitude and one short interval, and is not a stability test.
5. The literature already contains scalar stabilization, curved scalar
   branes, phase-space shooting, multiple or absent static solutions,
   instability-driven transitions, and computer-assisted Einstein existence.
   The candidate novelty is the exact paired certificate and compatibility
   conclusion for this fixed model.
6. No P16, collapse, MOTS, event-horizon, radion-transition, or child-universe
   inference follows.

## Publication viability

The result is viable as a specialist mathematical-relativity or
validated-numerics paper. Its strongest title-level concept is an **isolated
selected separation** rather than a new stabilization mechanism.

Existing manuscript material is substantial: 2,603 words of introduction,
theorem/proof, and discussion/conclusion; 981 words of formal reduction; two
publication figures; and an exact theorem table. The main scientific revision
is small and favorable: replace local uniqueness with the complete-launch
global theorem, add the isolated-root corollary, and keep the GH evidence out
of the headline.

The article is not submission-ready. It still needs integrated methods prose,
the full bibliography, LaTeX production, supplement and archive assembly,
clean replay of the actual staged package, page-level render inspection, and a
conventional citation-database review. No external archive or submission was
created or altered.

## Exact next step

The next mandatory step is publication engineering, not another physics run:

1. assemble the compact relative-path proof archive;
2. replay that exact staged package on macOS and Linux;
3. revise the existing article draft around `UPGRADED_THEOREM.md` and
   `MANUSCRIPT_CLAIM_PACKAGE.md`; and
4. obtain a manuscript-level independent review focused on the junction
   convention, global-cover completeness, isolation inference, and novelty
   wording.

Only after the paper core is stable should one choose a scientific extension.
A parameter-neighborhood enclosure is the shortest route to broader
significance. A gauge-invariant scalar/radion spectral calculation is the
correct route to stability, but it requires a new derivation and cannot be
inferred from the bounded GH response.

## Artifacts

- `UPGRADED_THEOREM.md` — strongest current theorem and exact boundary.
- `MANUSCRIPT_CLAIM_PACKAGE.md` — title, abstract, paper argument, tables, and
  evidence placement.
- `NOVELTY_REFRESH.md` — bounded primary-literature comparison.
- `PUBLICATION_READINESS.md` — precise readiness, reused material, blockers,
  and smallest remaining calculation.
- `BINDINGS.json` and `verify_upgrade.py` — immutable parent bindings and the
  read-only 23-check verifier.
- `RESULT.json` — machine-readable terminal conclusion.
