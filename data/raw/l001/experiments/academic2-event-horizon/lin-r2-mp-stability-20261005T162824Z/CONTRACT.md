# Multiprecision background repair and bounded stability qualification

## Prerequisite and question

The previous combined packet lin-r2-stability-qualification-20261005T152128Z
must be sealed and authenticated before this source is frozen. Its background
gate remains failed at 2.4163588398835808e-8 against 1e-8; its scientific test
remains UNRESOLVED. The R2 continuous static certificate is already audited.

Does genuinely higher-precision background integration AND storage resolve
the failed independently differentiated metric check while preserving the same
central branch and growing mode? Only if central qualification succeeds may
the eight original neighboring-parameter cases be evaluated. No new points,
models, action terms, physical boundary conditions or mass brackets are allowed.

## Frozen physics and order

All six action parameters retain their exact binary64 rational meanings in the
predecessor. v1 and lambda_b use the nine exact rational parameter pairs and
ordering in its SPECTRUM_R1_BINDINGS.json: center, four axial points, four corners.
The exact R2 root bracket is used. Proper-coordinate equations, wall orientations,
normalizations, scalar-turn treatment and mode equations are the predecessor's.
The existing growing mode is NOT assumed to imply stability or causal admission.

## Prospective precision and resolution controls

Background: direct MP Taylor integration of (W,H,Phi,T,E,z), E=exp(-W), with
W_s=H, H_s=-T^2/3-k E^2, Phi_s=T, T_s=m2 Phi-4HT, E_s=-HE, z_s=E.
Taylor coefficients use the polynomial convolution recurrence, not a SciPy
interpolant. Each control independently shoots a and its first upper-wall
event from the frozen bracket; no old rounded root, k or D is promoted as exact.

| Control | MP decimal digits | Taylor degree | Maximum proper step | Shooting residual target |
| --- | --- | --- | --- | --- |
| coarse | 50 | 24 | 2/64 | 1e-30 |
| fine | 70 | 30 | 2/128 | 1e-45 |

Both use at most 80 bracketed secant/bisection iterations without bracket
expansion; the upper event must precede s=2. Save 2001 MP nodes D*j/2000 and all
background fields plus a,k,D,L as decimal strings with dps+8 digits. Samples
are parsed directly into Linux 113-bit arithmetic for saved-field verification.
The background auxiliary identity E exp(W)=1 must be <=1e-20.

Mode: retain the existing regular proper-coordinate DOP853 implementation,
rtol 2e-11/2e-13, atol rtol*1e-3, step D/64 or D/128 and mass root settings.
Its binary64 coefficient conversion occurs only at the mode solver interface;
the authoritative background fields retain MP digits. Mass bracket remains
[-0.0015,-0.0011]. This is not a claim of an MP eigenvalue or spectral enclosure.

## Unchanged scientific admission gates

Independently differentiate the saved fields with nine-point local polynomials
on both 1001 and 2001 nodes INCLUDING endpoints. Background equations, direct
W_ss, scalar equation, first integral and all walls: normalized maximum <=1e-8.
Mode momentum, Einstein constraint, direct scalar KG and Robin walls: <=1e-6.
The scalar-turn finite relation: <=1e-6. Positive norm and normalized separation
response above 1e-6. Require each physical mass < -1e-8; pair difference <=1e-7,
|mu|>100 times that difference, and |mu+4k|>100 times its own pair difference.
Central a,D,k remain in the D1 enclosures. Central archived mass agreement <=1e-7,
separations relative <=1e-7 and full central background profiles scaled <=1e-7.
Independent norm and displacement integrals must agree within relative 1e-7.

Two coordinate formulations must also agree before the neighbors start.
The independent reviewer imports no primary background equations or solver.
It audits the saved MP background via separate barycentric derivative rows and
replays the regular mode in conformal coordinates from 1001 and 2001 background
samples, with the same fixed mass bracket; mode mass agreement <=1e-7 and full
scaled profile agreement <=1e-6. At central fine it independently integrates
the conformal background with MP RK4 at 50 digits and 4/8 substeps per saved
z interval. Same MP initial a,k and independent conformal equations; physical
fields and both walls must agree/close at normalized 1e-8. This is independent
IVP/formulation verification, not independent root finding. Its 4/8-step
controls are fixed before results.

## Controls, execution and recovery

Before science: inherited analytic vacuum/Robin and symbolic constraint controls;
direct MP Taylor vacuum solution error <=1e-20; MP serialization round trip;
independent derivative polynomial control; and a fresh-process exact Taylor-step
resume test from an actual analytic-control checkpoint. Reject altered source,
inputs, runtime, precision, case order or gates. Test that partial writes are
not valid completed checkpoints and that terminal artifacts cannot restart.

Linux only, one process and one numerical-library thread, after shared-resource
inspection. Case limit 600 seconds, unchanged. Source, contract, runtime,
preflight and parent inputs are frozen before any physical case is evaluated.
Save an immutable MP background, binary64 mode NPZ and receipt after each case;
atomically commit their hashes in CHECKPOINT.json. Preserve pending/completed
order, guard and runtime. Interrupted in-flight cases may replay only from the
last authenticated completed boundary under identical frozen code. No completed
case reruns. Progress is separate and informational. An incomplete publication
fails closed for review; it is never silently adopted or overwritten.

After the central pair, run the independent audit BEFORE admitting neighbors.
Stop on any decisive scientific failure or technical blocker. A terminal,
failed or stale-binding packet cannot restart. Preserve a failed result, even
if a precision or engineering successor would be obvious. All new work is in
this fresh packet; previous artifacts and manuscript files remain unchanged.

## Outcomes and evidence boundary

Central failure: seal the discriminator; no wider scan. Central success and
later point failure: seal completed cases and state what was not run. All nine
qualify: finite-resolution persistence at nine prescribed points, NOT uniform
spectral instability over a continuous box. R2 remains a rigorous reduced
static theorem; the new spectral result remains numerical. No exact-background
eigenvalue enclosure, nonlinear evolution, event horizon, healthy-background
assumption, or D1-P16 merger follows.
