# Corrections before numerical admission

The first prospective source review identified three implementation deficiencies before any scientific execution. They were corrected without changing the model, step counts, precision, tube rates or acceptance thresholds.

- Original producer checked runtime versions and before/after hash equality but did not enforce the predeclared hashes. The corrected producer also compares to the exact Python and Arb hashes recorded during read-only preflight.
- Original wrapper alone imposed the 600-second timeout. The corrected child installs its own 590-second wall alarm, so inherited resource locks cannot accompany an indefinitely surviving child after wrapper loss.
- Original background and M comparisons used outward Arb container intervals. Such containers can exceed an exact rational box slightly. Corrected checks compare outward dyadic endpoints as exact fmpq numbers against the stated rational limits.

The original, unadmitted producer SHA-256 was `3b8f5ff177e2029f585651003732ef9169438a0bbbdd87073daf2a690abd76ce`; original plan SHA-256 was `f0467db07b9867c66d2d4c3f0d0789bb33c714fcab61e1339a9a2642b00c8cbc`. The lease wrapper is unchanged. These are source-review findings, not failed numerical experiments or scientific adverse outcomes. The first reviewer disposition and corrected admission remain separate records.
