# Central D1 validated negative mode — prospective contract

## Question and scope

Certify existence of at least one negative scalar-sector eigenvalue at the exact
central D1 static two-wall background already proved to exist. This is one bounded
successor to the sealed higher-precision numerical qualification, not a parameter
scan, causal experiment, stability theorem for the whole spectrum, or manuscript
change. No physical calculation under this contract occurs before its freeze.

## Exact inputs and equations

Bind the previous MP packet, the high-resolution D1 static certificate and its
independent static replay by SHA-256. Preserve all six model parameters as their
declared exact binary64 rationals, read from the previous BINDINGS.json.

The exact root a* is enclosed by the high-resolution certificate's exact Newton
image A=[456607025194779413/4611686018427387904,
114151756532473697/1152921504606846976]. Its exact first upper-wall event lies in
D=[1.99749755859375,1.99761962890625], interpreted as exact rationals. We do not
substitute the numerical midpoint for the true root or event.

The prospective mass interval is the exact decimal interval
M=[-0.00132,-0.00131]. It is selected from the already sealed numerical mode,
not a pilot of this calculation. Unlike the old numerical bracket it must lie
entirely below the exceptional sector mu+4k=0. Require K>0, B0 excludes zero,
and sup(M+4K)<0 before either engine runs.

Background: W'=H, H'=-T^2/3-k exp(-2W), Phi'=T,
T'=m2 Phi-4HT. At s=0, W=0, Phi=a, T=gamma(a-v0)/2,
H=-(lambda_a+gamma(a-v0)^2/2)/6,
k=H^2-1-T^2/12+m2 a^2/12.

Regular mode: psi'=-2H psi-T f/3, f'=g,
g'=-4Hg+(m2-mu exp(-2W)+2T^2)f+(12HT-4m2 Phi)psi.
Set psi(0)=1, B0=gamma T0/2-(m2 a-4H0T0),
f0=3(mu+4k)/B0 and g0=gamma f0/2-2T0.
The lower Robin condition and constraint C0=0 hold identically.
C=Tg-(m2 Phi-4HT)f+[2T^2-3(mu+4k)exp(-2W)]psi obeys C'=-4HC.
No expression divides by T; a scalar-gradient turn is regular.
Upper determinant F=g+2T psi+gamma f/2 at the actual D*.

## Validated integrations

Outward-rounded Arb at 768 bits; one Linux process, one numerical thread.
Primary state W,H,Phi,T,E,psi,f,g with E'= -HE and E0=1, polynomial
Taylor recurrence. Independent state W,H,Phi,T,psi,f,g with an independently
written exp(-2W) recurrence, no import of the primary implementation.

Both use a Picard cell box strictly containing its image, at most 32 iterations,
box inflation width/8+2^-640, Taylor coefficients through order 4 at the left
enclosure and an order-5 remainder evaluated over the whole validated cell.
Primary h=2/8192; independent h=2/16384. Integrate through the first cell whose
right edge reaches D_max; no adaptive change of these choices is permitted.
For every cell intersecting D, evaluate the validated Taylor range over its full
time intersection with D; hull ALL such determinant ranges. Endpoint samples or
a grid-node hull alone cannot certify the free event time.
Require finite enclosures, positive warp, and constraint/first-integral diagnostic
intervals containing zero at every cell. Those containments are consistency
checks, not replacements for analytic propagation.

Task ordering: primary lower mu, primary upper mu, independent lower mu,
independent upper mu. Retain both endpoint implementations even if one has an
unresolved sign. An enclosure failure terminates that task without widening or
retuning its settings. Mathematical certification requires strict opposite signs
from BOTH engines and compatible (overlapping) same-endpoint determinant bounds.

For the same fixed exact a*,D*, F is continuous in mu: coefficients are smooth on
the already certified compact background and the mode IVP is linear with regular
lower normalization. Uniform endpoint enclosures therefore imply a zero for that
same background, not different backgrounds at different endpoints. Mu<0 and the
nonexceptional sector are certified on the whole interval. No uniqueness or
lowest-eigenvalue claim is made.

## Conditional separation qualification

Only after both endpoint certificates pass, run primary then independent with
mu as the full interval M. This is a uniform family enclosure, not another root
search. Require psi_min>0 in all Picard cells up to D_max. Record global finite
W,psi,f bounds. Then Z=2 integral exp(2W)(f^2+6psi^2)ds obeys
Z >= 12 D_min exp(2 W_min) psi_min^2 > 0, and
deltaD=-2 integral psi ds is enclosed by
[-2 D_max psi_max,-2 D_min psi_min] < 0.
An arbitrary overall mode sign remains free: nonzero response does not select
physical contraction versus expansion. Interpretation inherits the previously
audited action, gauge and two-wall boundary model; this is not a new derivation
of that physical model or a nonlinear fate prediction.

If the full strip cannot certify positivity, retain the endpoint result as
NEGATIVE_SCALAR_EIGENVALUE_CERTIFIED_RADION_OVERLAP_UNRESOLVED. Do not report a
radion/separation certificate from endpoint profiles alone. Both strip engines
must pass for NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1.
If endpoint signs do not certify: VALIDATED_MODE_UNRESOLVED, not absence of a mode.
Unexpected execution/integrity errors: TECHNICAL_INCOMPLETE, never scientific PASS.
All classifications remain producer-provisional until independent post-run audit.

## Recovery and bounded preflight

Before physical evaluation, run only algebraic identities and an exact analytic
vacuum flow. Test Taylor coefficients, outward containment, native Arb
midpoint/radius binary mantissa/exponent serialization, and a fresh-process next
step from a real analytic checkpoint. The first synthetic trial demonstrated that
Arb's public constructor can round some 30-bit radius mantissas up by one unit.
Before saving, enlarge each radius outward to a constructor-stable native binary
tuple, verify unchanged midpoint and nonshrinking radius, and replace the live
continuation state with that SAME canonicalized state. Require fixed-point
stability within three constructor applications; otherwise fail. The post-canonical
binary tuple must reproduce BOTH midpoint and radius exactly on load. This is
exact resumption of the declared checkpointed algorithm, not a claim of lossless
serialization of every possible raw Arb radius. Rational or decimal reconstruction
is not accepted. Preserve the first failed synthetic trial.
Reject changed guard fingerprints and ignore uncommitted temporary files.

Every 256 accepted cells and task completion, atomically publish an immutable
checkpoint and separately update a latest pointer and read-only progress record.
Store full interval state, parameters, exact rational cell index/time, task order,
event cover, extrema, prior task results, source/input/runtime guard and elapsed
time. Resume verifies the guard and checkpoint digest and never restarts a
terminal or failed task. Synthetic tests validate the recovery path before freeze.

Authenticate sources, parents and runtime before launch and before publication.
Preserve all parent directories unchanged; no Python cache writes. No broad test
framework, mutation campaign or unrelated unit suite is required. After terminal
evidence and independent review, seal the result and whole-file manifest.
