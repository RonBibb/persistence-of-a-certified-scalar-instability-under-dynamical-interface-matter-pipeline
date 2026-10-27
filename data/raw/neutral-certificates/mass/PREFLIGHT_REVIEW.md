# Independent preflight review

Review disposition: PASS for the declared bounded calculation, subject to the
runner's mandatory passing analytic/recovery controls on the final source bytes
and subsequent source/input/runtime freeze. This note does not certify an
eigenvalue or any newly evaluated physical result. No physical solve was run by
the reviewer before freeze.

## Mathematical sufficiency

The inspected contract, primary polynomial flow, independent exponential flow,
and runner implement the argument in `INDEPENDENT_PROOF_AUDIT.md`. The exact
certified static root and event remain the same fixed background as mu varies.
Both formulations preserve the regular constraint analytically, avoid division
by the scalar gradient, and impose the same lower launch and upper determinant.
The extra primary variable obeys E'=-HE, E(0)=1, so E=exp(-W) exactly.

Strict Picard self-containment bounds the full cell trajectory. The left-state
Taylor coefficients through degree four and fifth coefficient over that Picard
box give an outward fifth-order remainder. Event evaluation covers every time
in every cell intersection with the full rational event interval, rather than
only evaluating grid nodes. The runner retains both endpoint implementations,
requires strict opposite signs and compatible same-endpoint bounds, and admits
the full-mu-strip tasks only after both endpoint certificates pass.

The initial curvature, nonsingular normalization and nonexceptional-sector
gates are appropriate. Uniform positive psi is reserved for the separate
separation certificate. That certificate now checks both a strictly positive
computed Z lower bound and a strictly negative upper endpoint of the recorded
outward deltaD bound. Failure of the strip does not erase an endpoint existence
certificate or silently become a separation certificate. No uniqueness,
lowest-mode, parameter-box, evolution or horizon claim is admitted.

## Arithmetic and recovery corrections before freeze

The first synthetic controls exposed two binding-specific behaviors, without
evaluating the physical model. Generic Arb exponentiation could return a
nonfinite value for a tiny zero-straddling squared ball; runtime quadratic
terms therefore use explicit products. The independent source contains no
runtime Arb square powers; its remaining powers are exact integer constants
or symbolic expressions. The primary launch's remaining quadratic expression
is also to be expressed as an explicit product before the final controls.

Raw native midpoint/radius tuples are not universally lossless: the public Arb
constructor can round a 30-bit radius upward. The revised serializer explicitly
checks unchanged midpoint and nonshrinking radius, iterates to a constructor-
stable outward representation within a fixed bound, and rejects otherwise.
Checkpointing restores this canonicalized full state into the live state
dictionary, including parameters, extrema and event bounds. Subsequent steps
read that restored state. Thus the small declared checkpoint widening occurs
in the uninterrupted algorithm as well as the resumed algorithm. Loading
requires exact tuple reproduction; the fresh-process continuation control
starts from the post-canonical checkpoint. No universal raw-tuple exactness
claim remains. Earlier failed synthetic trials are to be retained as provenance.

The runner authenticates source, scientific configuration, parents and runtime;
checkpoint guards and digests bind the restored state. Atomic immutable task
publication has a guarded recovery path if publication precedes the following
checkpoint. Terminal/failed packets cannot restart. An interrupted in-flight
cell is not published as resumable state; KeyboardInterrupt leaves the last
durable checkpoint recoverable rather than creating a terminal failure.

## Admission and remaining review

Final analytic containment, algebraic identities, post-canonical serialization,
fresh-process continuation and guard/temporary-file controls must pass against
the exact frozen source and pinned Linux runtime. The freeze routine rejects a
stale control receipt. The independent source reviewed here has SHA-256
`260150e6371209bc3eac1834e7be2c97b4d7e582338cd567c82843a4f44efbeb`.

After execution, actual determinant signs, full event coverage, strip extrema
and positive-norm/separation bounds must be checked independently together with
source/input/result integrity. A process completion flag alone is not evidence
of a mathematical certificate. Within this scope no further scientific or
operational blocker was identified.
