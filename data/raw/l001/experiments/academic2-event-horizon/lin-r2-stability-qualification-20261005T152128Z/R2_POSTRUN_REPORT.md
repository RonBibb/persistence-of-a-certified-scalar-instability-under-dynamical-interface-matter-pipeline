# Continuous static neighborhood certificate: formal post-run report

R2 completed at 2026-10-05 12:24:39 UTC. The declared reduced static
Einstein–scalar two-wall problem has one admissible first-event shooting root
throughout the entire frozen two-parameter neighborhood. The separately
prescribed proper separation D0 remains excluded throughout that neighborhood.

The parameter intervals are v1 in approximately
[0.09038374180359596, 0.09058374180359596] and lambda_b in
[-6.052944277744164, -6.052744277744164]. The exact rational endpoints in the
R2 result are authoritative. The whole parameter cell passed without parameter
subdivision; admitted exact parameter volume equals the declared volume.

Both independently implemented interval producers give strict parametric
interval-Newton inclusion. The limiting inclusion margin is 8.429676259e-9.
The launch-domain certificate contains 715 contiguous boxes: 19 negative-
curvature exclusions, 695 dual first-event scalar-residual exclusions, and
one certified root container. Its limiting signed exclusion distance is
1.003226759e-4. The fixed-D0 certificate contains 693 boxes: 20 inherited
negative-curvature exclusions and 673 integrated wall-residual exclusions;
its limiting residual-vector bound is 7.711024911e-3. No box is unresolved.

## Completed verification

The original frozen post-run auditor was executed on Linux against byte-for-
byte copies of RESULT and TERMINAL in this new packet. Its six checks pass;
the original R2 packet was not modified. A separate source and rational-
arithmetic audit passes 41 checks, including exact full-volume admission,
both strict Newton inclusions, derivative signs, signed event exclusions,
positive fixed-D0 bounds, gap-free covers and checkpoint/result agreement.

Artifacts in this packet:

- `audit/r2_frozen/POSTRUN_AUDIT.json`: original frozen auditor result.
- `audit/R2_POSTRUN_AUDIT.json`: independent rational and artifact checks.
- `r2_postrun.py`: source for the separate verification.
- `AUDIT_FREEZE.json`: audit source/binding record.

Controlling predecessor:
`../lin-static-parameter-neighborhood-r2-20261005T120100Z/output/RESULT.json`,
SHA-256 `3d6353e7277e273fdf35101ef3b9126802de04ac0c1dbf7931d06209e90e8b21`.

## Preserved incomplete attempts

The initial neighborhood attempt could not close its excessively wide root
container. R1 corrected that container prospectively and passed the root gate,
but stopped when non-finite event-record conversion escaped the subdivision
logic. R2 preserved the saved state and treated that condition conservatively
as a box requiring subdivision, retaining the original depth ceiling. Both
incomplete predecessor records remain unchanged. The successful campaign was
not rerun for this report.

## Consequence

The static result is robust under the declared finite changes of two wall
parameters. This is a rigorous certificate for the declared reduced static
problem. A spectral calculation is separately required to determine whether
perturbations grow. No dynamical, global initial-data, event-horizon or P16
identification is supplied by this certificate.
