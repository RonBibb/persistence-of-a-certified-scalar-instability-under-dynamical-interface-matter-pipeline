# O4-R1 interpretation — late P407 bulk-wall incompatibility is present

## Outcome

O4-R1 completed all three authenticated endpoints under the actual P407-R2
`qualified-batched` contract.  The active mode was
`legacy_wall_axis_outer`, `batched_open_bulk=true`, and all four optional wall
forcings were `None`.

The late P407 archive is **not cleared as a physically compatible parent for
event-horizon reconstruction**.  At the well-conditioned upper wall, the
implemented raw coordinate acceleration-level wall rows are satisfied to
about `1e-12`, while the same reconstructed acceleration leaves material
physical Einstein and scalar-wave residuals.  This coordinate-row statement
must not be confused with complete normalized geometric compatibility: the
largest displayed upper-wall `wall_normalized2` normal row remains
`1.44e-6` to `1.73e-6` across the three samples.

| H-step | time | upper j35 `E_ll/T_ll` | upper j36 `E_ll/T_ll` | upper j35 chi residual | upper j36 chi residual |
|---:|---:|---:|---:|---:|---:|
| 512 | 0.008 | -5.425816e-3 | -5.274744e-3 | +1.079249e-1 | +1.045557e-1 |
| 1152 | 0.018 | +6.264119e-3 | +6.115986e-3 | -9.058603e-2 | -8.806917e-2 |
| 1792 | 0.028 | +3.722853e-3 | +3.663655e-3 | -2.134156e-1 | -2.071963e-1 |

At j35 the corresponding absolute `(E_ll,T_ll)` pairs are
`(-0.180669,33.298049)`, `(0.208312,33.254725)`, and
`(0.123250,33.106456)`.  The result is not an artifact of division by a small
upper-wall stress normalization.

The lower-wall normalized ratios are not used for the scientific reading
because `T_ll` is poorly conditioned there, consistent with the earlier
branch-01 caution.  Absolute arrays remain in the result.

## What the time sequence says

The upper-wall Einstein projection changes sign between H-steps 512 and 1152
and its magnitude is non-monotone.  The scalar residual also changes sign and
its final magnitude is about twice its H-step-512 value.  Three points do not
define a time law, but they rule out treating the near-formation mismatch as a
fixed numerical percentage and provide no evidence that compatibility is
settling toward zero over this archive.

This is stronger than the ancestry audit.  Shared ancestry merely made the
question applicable; O4 measures the incompatibility directly on the active
late states.

## Why the result is not a wall-solver failure alone

The active wall closure drives its own raw coordinate acceleration-level rows
to approximately `1e-12` or smaller at these samples.  The physical bulk
Einstein/scalar evaluation nevertheless remains nonzero.  Therefore the
measured issue is the simultaneous bulk-wall compatibility identified by
branch 01: satisfying the implemented coordinate wall algebra does not make
the endpoint acceleration a solution of the physical bulk equations at the
wall.

The raw-bulk acceleration comparator is not an admissible correction.  O4
evaluates it pointwise and does not re-evaluate the complete raw-line wall
derivative system, so this experiment does not directly certify a full wall
violation for that counterfactual.  It also does not uniformly improve the
pointwise physical Einstein projection: at H-step 1792, upper j35 changes from
saved `E_ll/T_ll=+0.00372285` to raw `-0.0112807`.  O4 does not replace any
endpoint with that comparator.

## Portability controls

Away from the compact-direction endpoints, the saved acceleration satisfies
the reduced nine-equation packing at maxima `1.78e-14`, `1.07e-14` and
`1.42e-14` for H-steps 512, 1152 and 1792.  The saved-minus-raw acceleration
maxima on the sampled interior are `1.83e-13`, `1.17e-13` and `1.49e-13`.
Thus the interior equation packing and jet reconstruction are portable at the
sampled points; the material discrepancy is localized to the physical-wall
compatibility question rather than a general interior implementation drift.

The incompatibility is present at all three sampled late states.  Three
samples do not establish continuous persistence, a decay law, or a continuum
obstruction.

## Consequence for the causal line

O1 and O2 remain exact statements about the represented numerical geometry:
the stable-band MOTS surfaces reproduce, and their backward null sheets retain
a coherent terminal-time offset.  O4 changes what may be inferred physically
from that geometry.

Another long extension of the same P407 lineage would sharpen the causal
properties of a representation that has not passed simultaneous bulk-wall
compatibility.  It should not be the next priority.  The next physical task is
the branch-01 common initial/boundary compatibility construction, followed by
a short admitted evolution companion.  Only if that companion preserves the
MOTS lineage should the causal localization experiment be repeated.

No event-horizon, no-event-horizon, continuum, or geometric-disappearance
claim follows from O4.  The finite-resolution MOTS/dynamical-horizon geometry
is not erased by this result; its interpretation as part of a valid Einstein
development remains conditional on repairing or otherwise resolving the
compatibility problem.
