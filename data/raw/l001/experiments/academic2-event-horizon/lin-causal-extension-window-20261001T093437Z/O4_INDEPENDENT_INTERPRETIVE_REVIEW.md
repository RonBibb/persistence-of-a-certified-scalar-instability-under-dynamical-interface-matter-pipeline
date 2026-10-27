# Independent interpretive review of O4-R1

The reviewer inspected the O4 result and source mapping without re-running the
numerical diagnostic.  The central conclusion is supported with the following
qualifications now incorporated into `O4_INTERPRETATION.md`.

1. Say the mismatch is present at all three sampled late states.  Do not infer
   continuous persistence, a decay law or a continuum obstruction from three
   samples.
2. The upper-wall stress normalization is well conditioned (`T_ll` is about
   33), so the displayed `E_ll/T_ll` values are not small-denominator effects.
3. The result means the current P407 lineage is not yet qualified as a physical
   Einstein-scalar parent for event-horizon reconstruction.  It does not mean
   no event horizon exists and does not erase or reverse the represented
   MOTS/dynamical-horizon geometry.
4. O4's raw-bulk comparator is pointwise.  It does not execute a complete
   raw-line wall derivative evaluation and therefore cannot be described as a
   direct full-wall-violation measurement.
5. At H-step 1792, upper j35, the raw pointwise physical ratio is
   `E_ll/T_ll=-0.0112807`, worse in magnitude than the saved `+0.00372285`.
   This reinforces that the counterfactual is not a correction, while not
   supplying the missing complete wall test.
6. The raw coordinate wall-row closure near `1e-12` must be distinguished from
   the normalized geometric row, whose displayed upper-wall magnitude remains
   about `1.44e-6` to `1.73e-6`.

The review is interpretive.  The authoritative numerical payload remains
`o4r1-output/O4_RESULT.json`.
