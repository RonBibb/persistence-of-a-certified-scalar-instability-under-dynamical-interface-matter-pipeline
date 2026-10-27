# Static half of the Lin integration test

Round: 20261008T121619Z_PRIORITY_THREE_TESTS. Owner: row 1.

## Frozen question and scope

Derive the action-consistent material-to-conformal initial-data map, test it on
the existing admitted C6 representations, and determine which parts of the
static/C4 theorem and its quantitative bounds actually transfer. A shared
action or small numerical difference is not a theorem-membership test.

The central exact action has the six literals in the connected C4 binding.
The fixed-background C4 family is epsilon in [-1/200000,+1/200000], with
ell=-2 epsilon psi, Phi=Phi_star+epsilon f+C7+b0 H5_L+b1 H5_R,
and correction unknowns (a,b0,b1). P01 is a separate static tension-neighborhood
theorem, not a theorem for an arbitrary physically corrected initial family.

The existing C6 input is one positive epsilon=1/200000 saved representation,
with a physically changed scalar in two H7 directions and a re-solved metric.
Its 80/100-digit records share a saved source; their agreement cannot bound
the source's continuum error. No root, mode, metric or time evolution is solved
in this test. No parameter or inherited gate is adjusted.

## Tests, fixed before new calculations

1. Exact-rational action equality, amplitude labels/storage offsets, fixed
   background provenance and certificate-domain inventory.
2. Independently derive and symbolically check x_s=exp(ell-B), B=A+q, metric
   pullback, oriented normals, wall clocks and areal-radius definitions.
3. Using only saved polynomials and q, construct the coordinate integral and
   invert it at 65 equally spaced normalized-conformal labels, at each saved
   precision/resolution. Compare a Taylor-integral implementation with direct
   16-point-per-cell Gauss quadrature. Gate: absolute/relative coordinate,
   inverse-metric and paired-observable disagreements <=1e-20. No evolution
   grid or PDE boundary discretization is admitted by these diagnostic nodes.
4. Enclose the saved polynomial representation's exp(ell-B) and exp(ell)
   cellwise using outward Arb arithmetic, obtaining positive-Jacobian and
   coordinate/proper-length integral enclosures. These certify represented
   polynomials, not the exact continuum C6 datum. Require numerical integrals
   inside these enclosures and a strictly positive Jacobian lower bound.
5. Evaluate original spatial Israel/scalar rows from saved analytic derivatives,
   q=0 and q_s=0 at walls, with 1e-20 representation gates. Reuse, by binding,
   the existing independent C2/C4/C6 readbacks; do not call their launchers.
6. Exact polynomial-ansatz membership: the old C4 correction has degree <=11.
   Test the degree-12..15 quotient of the new correction using exact saved
   decimals, and independently reconstruct the H5/H7 change. A nonzero
   degree-15 coefficient excludes absorption into (a,b0,b1) at the same saved
   source and fixed epsilon. This is not a continuum nonexistence theorem.
   Check Hermite endpoint jets and a scalar-at-common-proper-distance witness.
7. Propagate admitted E01 material-field bounds to C4-only radius, lower-wall
   clock and proper-distance bounds, using a conservative enclosing static
   k,D range from P01. State the conditional bound for lapse/inverse-map
   propagation and mark any missing exact q/high-jet enclosure explicitly.
   These C4 bounds must not be relabeled as C6 error bars.

## Decision

Joint labels are restricted to the shared contract. On this side:

- ADMITTED requires actual coverage of the physical C6 correction directions,
  complete required continuum bounds, consistent action/coordinates/gauge,
  and passing independent partner membership/corner checks.
- EXCLUDED requires a demonstrated obstruction in the explicitly stated
  common continuum domain, not merely missing proof or a loose enclosure.
- Otherwise STATIC_INITIAL_BRIDGE_INCOMPLETE, accompanied by the positive
  map checks and any narrower fixed-representation ansatz exclusion.

The likely distinction is a valid initial coordinate map versus an unextended
physical-family theorem. This is a hypothesis from existing records, not the
test result. An operational failure is technical incompleteness.

## Execution and preservation

Only the assigned new row-1 directory may receive sources, status, checkpoints,
results and audits. The shared directory receives the hash-bound exchanged
packet and readable report after local checks. Every migrated/legacy input is
read-only; all imports avoid original runtime/launcher modules.

Use Linux CPU 4 (CPU 5 remains available but unused), one process/thread,
4 GiB address-space ceiling. Conservative common cutoff: 2026-10-08T13:16:19Z,
one hour after round authorization, with no reset. Completed precision levels
are atomic recovery checkpoints; no long numerical solver is required.
Each launch is guarded by input/source hashes and the absolute deadline.

Use one proportionate preflight (analytic identities plus input/domain checks),
one producer, and a separately written exact-arithmetic/integrity audit. The
partner supplies independent scientific membership/corner review. No subagent,
evolution, rescue, manuscript/Git/automation change or automatic successor.
