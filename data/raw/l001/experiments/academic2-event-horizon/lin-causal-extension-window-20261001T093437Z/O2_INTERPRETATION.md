# O2 interpretation — an affine terminal-time memory, not an epoch-1 attractor

## Outcome

O2 is technically complete and independently verified.

- Scientific classification:
  `VALID-NO-EPOCH1-TERMINAL-LOCALIZATION-FUTURE-EXTENSION-REQUIRED`
- Localized common steps: 0 of 17; 16 were required.
- All nine null traces passed their domain, null-defect, caustic,
  crossover, and polar-ordering gates.
- Every unparameterized curve comparison passed its projection and coverage
  gates.
- Independent verification rederived the classification in 272 checks with
  zero failures.

This is a valid adverse result for the finite epoch-1 localization question,
not a technical failure and not evidence against the existence of an event
horizon.

## Numerical separation is not the explanation

The frozen control envelope was

`E = 0.009303915007599332` native cells,

below the preregistered budget `0.05/3 = 0.016666666666666666`.  Its source is
almost entirely angular label transfer:

| Control against the N=165, 257-label coordinate primary | Maximum distance (native cells) |
|---|---:|
| 129 angular labels | 9.303915e-3 |
| N=173 terminal surface | 4.183674e-8 |
| N=157 terminal surface | 3.823388e-8 |
| strict integration tolerance | 1.677926e-12 |
| Hamiltonian formulation | 1.569206e-13 |

The four-terminal diameter is 35.34–35.55 times the full control envelope.
After adding the frozen `2E` allowance, the localization target is missed by a
factor 6.95–6.99 at every common time.  The nonlocalization therefore cannot
reasonably be assigned to surface resolution, integration tolerance, or null
formulation within this experiment.

## What the four null sheets do

Across H-steps 512 through 1536:

- the all-terminal diameter changes only from 0.328794 to 0.330726 native
  cells;
- tracing farther backward reduces that diameter by only 0.584%;
- dropping the earliest terminal reduces the diameter to
  0.663609–0.663611 of the full value, close to the two-thirds expected when a
  three-gap interval is shortened to two equal gaps;
- pairwise distances fit terminal-gap count with descriptive
  `R^2 = 0.99992266–0.99992270` and maximum relative deviation below 0.291%;
- the three adjacent late-step gaps are 0.110995, 0.110109, and 0.109237
  native cells.

Thus the family does not show collapse toward a terminal-independent null
sheet.  It behaves like an almost evenly spaced one-parameter family labeled
by terminal time.

## Where that pattern enters

The N=165 O1 terminal profiles themselves show the same structure.  For each
successive 16H terminal gap, every collocation entry of the radial profile
increases.  The three unweighted collocation-vector RMS increments are

`9.956508e-4`, `9.893281e-4`, and `9.831027e-4`.

Successive increment vectors have cosine similarities

`0.9999996453` and `0.9999996485`.

The best-fit amplitude ratios are `0.9936493` and `0.9937071`, with residual
fractions below 8.43e-4.  These are representation-space diagnostics, not
geometric norms, but they show that the tracked MOTS is moving outward along
an almost fixed deformation shape while the increment amplitude declines only
about 0.63% per terminal gap.

The most economical reading is therefore:

> The moving terminal MOTS injects an almost affine terminal-time offset, and
> the epoch-1 backward null flow transports that offset nearly unchanged.

This is stronger and more specific than saying merely that terminal dependence
persists.  It identifies a coherent mechanism within the represented
spacetime: continued quasi-steady motion of the terminal seed rather than an
unstable or noisy null integration.

## Scientific boundary

The result says that the present late MOTSs are not yet suitable terminal
surrogates for a terminal-independent event-horizon reconstruction on this
archive.  It does not say that no event horizon exists.

The calculation remains conditional on the inherited P407 spacetime.  The
physical wall is not future null infinity, escape and capture witnesses have
not been defined, and the branch-01 wall-acceleration compatibility issue is
unresolved for the late archive.  The sibling near-formation result must not
be numerically transferred to these late states without an ancestry and
applicability check.

