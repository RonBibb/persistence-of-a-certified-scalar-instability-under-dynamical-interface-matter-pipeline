# Uniform scalar/radion instability in the certified static neighborhood

## Result and meaning

The frozen experiment's six validated interval integrations all passed, and
the independent post-run audit passed. The accepted result extends the
previous central negative-mode certificate to **every parameter pair in the
complete, previously certified static neighborhood**, including its boundary.

For each such pair, its own exact static background has at least one scalar mode
with

    -0.00132 < mu < -0.00131,

a positive kinetic norm, and a nonzero perturbation of the physical wall
separation. This is not just evidence from nine sampled parameter points.
It is a uniform, interval-validated existence statement on the continuous box.

The useful physical conclusion is robustness: the central scalar/radion
instability is not eliminated by the small upper-wall parameter variations
already covered by the static existence certificate. The static branch exists
throughout this box, but no member is linearly stable against all perturbations
in the declared scalar sector.

It does **not** identify the nonlinear endpoint, choose expansion rather than
contraction, establish causal evolution, or connect this static branch to the
separate horizon/residual/P16 line. The overall sign of a linear eigenmode is
arbitrary.

## Frozen scope and logic

The physical model is the inherited canonical bulk scalar with pure quadratic
two-wall potentials and fixed stiffness gamma=20. Only v1 and lambda_b vary in
the exact box specified in CONTRACT.md and BINDINGS.json, approximately plus or
minus 1e-4 about 0.09048374180359596 and -6.052844277744164 respectively.

The full original R2 static root tube has width 4e-8. Its upper wall satisfies

    D in [8177/4096, 8187/4096].

Neither interval was replaced by a central value or a narrower fitted interval.
Both numerical kernels are byte-identical to the accepted central R1 kernels.
The varied parameters are carried explicitly as intervals in the checkpoints.
For these fixed-stiffness quadratic walls, their effect on the mode problem is
through the selected background and wall location, not an additional varying
Robin coefficient.

At each fixed parameter pair p, the same exact a*(p), D*(p) are held fixed while
mu varies. Both implementations enclose strictly positive lower-endpoint and
strictly negative upper-endpoint determinants over the entire enclosing root
and event rectangle. Continuity then gives at least one root for each p.
The quantifier is **for every p, there exists a mu_p**; no claim is made that all
backgrounds share one eigenvalue, that it is unique or lowest, or that a smooth
global eigenbranch has been selected.

## Measured certificate

Rounded determinant intervals below are only a readable display; the exact
rational bounds in output/RESULT.json are authoritative.

| Check | Primary | Independent |
| --- | ---: | ---: |
| F at mu=-0.00132 | [28.2460, 29.8374] | [28.2467, 29.8372] |
| F at mu=-0.00131 | [-9.17012, -7.51235] | [-9.16788, -7.51510] |
| Full-strip minimum psi | >0.9998410 | >0.9997742 |
| Certified lower bound on kinetic norm Z | >0.4360838 | >0.4360389 |
| Full D-interval cell intersections per task | 11 | 21 |
| Accepted cells per task | 8,187 | 16,374 |

Both full-strip calculations also enclose deltaD strictly away from zero.
A conservatively rounded enclosure covering both is

    -219.549 < deltaD < -3.991,

at normalization psi(0)=1. These broad bounds certify nonzero overlap, not a
precise physical amplitude. The inherited identities are

    Z = 2 integral_0^D exp(2W) (f^2 + 6 psi^2) ds,
    deltaD = -2 integral_0^D psi ds.

Positive curvature, nonexceptional mu+4K<0, nonzero launch denominator,
constraint enclosure, positive warp, and finite field enclosures passed.
The event enclosures cover complete cell intersections, not only sample nodes.

## Execution and independent acceptance

- Linux production: 2026-10-05 18:34:45 to 18:35:34 UTC.
- Integration time: 49.1071 seconds, one process and one numerical thread.
- Arithmetic: 768-bit outward Arb; fifth-order Taylor/Picard inclusion.
- Validated cells: 73,683 across six tasks.
- Atomic checkpoint schedule: every 256 accepted cells and each task boundary.
- Source/input/runtime/config binding:
  `2c83c19c3db530b475b59cbffcde1d22db86e90a72cbeb4070b76fdc3aaf07cf`.

The accepted publication is the root RESULT.json together with
INDEPENDENT_AUDIT.json, POSTRUN_REVIEW.md and MANIFEST.json. The producer's
output/RESULT.json is explicitly provisional until those artifacts accept it.
The Linux read-only audit completed at 18:39:19 UTC and independently rederived
the exact domain inclusion, determinant signs and overlap, full event coverage,
and kinetic/separation bounds without rerunning the physical IVP. It verified
all 288 checkpoint parameter domains and digests, 11,808 native interval
roundtrips, 699 hash/file links, 694 unique files unchanged, all 42 runtime
libraries, and all 326 files in the sealed central predecessor manifest.

## Issues, failed checks, and remaining gap

No scientific gate failed in this experiment. No parameter subdivision,
mass-bracket change, root-tube shrinkage, or acceptance-gate relaxation was used.
A pre-freeze path correction selected the actual static parent's terminal
filename; final-source synthetic controls were rerun afterward. The original
central serialization failure remains preserved in its own predecessor packet.

This certificate inherits the stated action, scalar perturbation reduction and
boundary conditions. It is not an independently derived new physical action,
a full-spectrum theorem, or a stability statement about other sectors.
Uniform linear instability does not supply constraint-satisfying dynamical
initial data or demonstrate a nonlinear trajectory.

## Next steps and viability

The authorized bounded question is answered and independently accepted;
no additional calculation is required to decide it. This strengthens the
static-plus-linear line: the existence/instability contrast now holds across a
continuous two-parameter neighborhood rather than only at its central point.

Potential later questions are a quantitative growth-rate enclosure or a
separately admitted nonlinear/causal experiment with valid initial data. They
require a new bounded design and authority. Nothing here admits a causal run,
changes a manuscript, or launches an automatic successor.

The numerical worker has exited. No successor calculation has been launched.
