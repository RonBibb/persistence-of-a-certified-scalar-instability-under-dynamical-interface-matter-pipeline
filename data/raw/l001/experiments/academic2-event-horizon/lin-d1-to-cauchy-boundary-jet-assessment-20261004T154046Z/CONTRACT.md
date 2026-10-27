# Prospective D1-to-Cauchy boundary-jet join assessment

## Scope

This is a read-only comparison.  It does not modify D1, P16, P17, the
mixed-source successor, any manuscript, or any evolution record.  It does not
solve constraints or evolve data.  It asks whether the certified D1 static
solution can be used as boundary data for the present Lin initial-data family,
and it separates a coordinate/gauge/reference mismatch from missing Cauchy
data and from a genuine physical-data incompatibility.

The assessment is allowed to return a non-join.  No connection is claimed
unless the full declared wall and source jet is compatible.

## Bound authorities

- Independent D1 interval replay result, SHA-256
  `41077a7977079705dbd49379f2f9ecb3fe9c007c518b02277aba6aa4b8df7d16`.
- Consolidated D1/D2A theorem, SHA-256
  `705e6b01e60504ec3d960fbd081313ef7c61116b60f2a4d54574eb64f2f74bbc`.
- P16 manifest, SHA-256
  `0dfbd5faa0cedcb099056a87b0a91a8ee9c0ce62e2e33fc48af3915d66955b6d`.
- P17 manifest, SHA-256
  `aa6ea811d3be9417d519815a53e82965204cca2e1be26d9d31971b79d3e24107`.
- Sealed mixed-source successor manifest, SHA-256
  `9194366085fbcacaed28b89afa384f42f42f25e0a7eece574b6dc495af3bf424`.

All parents are read only.  The finest independent D1 root-box endpoint
enclosures, rather than midpoint values, drive every D1 interval below.

## Frozen Cauchy chart

Use the static-patch chart of the positive-curvature four-dimensional base,

    gamma_k = -f(r) dt^2 + dr^2/f(r) + r^2 dOmega_2^2,
    f(r)=1-k r^2.

This chart has zero shift and a time-symmetric spatial slice.  It is regular on
the declared radial domain only if `f(10)>0`, which is a technical gate.  It is
chosen because P16 has zero first metric and scalar velocities.  The flat
de-Sitter slicing remains a separately recorded alternative: it has the same
flat radial topology but nonzero extrinsic curvature and therefore cannot be
identified with P16's zero-velocity preparation.

Let `y` be the D1 conformal coordinate, `dy/ds=exp(-A)`, with total conformal
length `L`.  Map it to the code coordinate `x in [1,e]` by

    y = c (x-1),  c=L/(e-1),

where `e` is the code's binary64 endpoint.  Write `w=exp(A)`, `U=Phi_s`, and
retain D1's `H=A_s`.  At radius `r=10`, the nine regular SO(3) Cauchy fields
in the production order

    (g_x0, g_xr/r, g_00, g_perp,
     (g_rr-g_perp)/r^2, g_0r/r, g_xx, Phi, chi)

are

    q = (0,0,-w^2 f,w^2,w^2 k/f,0,w^2 c^2,Phi,0).

Their first time derivatives vanish.  The ADM variables in the sign convention
`K_ij=-(2 alpha)^-1 partial_t h_ij` are

    alpha=w sqrt(f), beta^i=0, K_ij=0,
    Pi_Phi=Pi_chi=0.

The required spatial jets are generated from

    partial_x = c w partial_s,

and include `q`, `q_x`, `q_r`, and `q_xr` at both walls.  The wall laws must
reduce to the D1 junction conditions with `sqrt(g_xx)=cw`; this is checked as
an interval identity rather than assumed.

## Geometric source and natural reference

Use the same regular source formulas as P16/P17.  On this chart,

    H_0 = 0,
    H_x = (1/2) partial_x log[g_xx/(N B g_perp^2)] = -3 c w H,
    H_r/r = 4 k/f,

where `N=-g_00` and `B=g_rr`.  The natural D1 reference is the geometric
source itself, with the target anchored to that same source.  Therefore

    partial_t H_0 = partial_x partial_t H_0 = 0,
    partial_r H_x = partial_x partial_r H_x = 0.

The exact outer-face radial moment is then zero: `Y=(1/2) partial_r log W=0`
at both walls and `integral partial_r H_x dx=0`.  This checks whether D1
supplies a moment-consistent reference.  It does not silently replace P16's
authenticated projected reference.

## Comparisons and gates

1. Rehash all bound authorities before evaluation.
2. Require `f(10)>0`, positive lapse and spatial metric intervals.
3. Require both D1 wall metric/scalar junction residual intervals to contain
   zero under the frozen coordinate map.
4. Publish interval enclosures for all declared D1 wall variables and jets.
5. Compare the D1 intervals directly with P16's saved `q`, `q_x`, `q_r`, and
   `q_xr` values and with its zero velocities.  A point datum passes only if it
   lies in the D1 interval enlarged by the unchanged `1e-8` absolute gate.
6. Compare the D1 natural temporal trace slope and mixed normal-source
   derivative with P17 and the sealed mixed-source correction values.  These
   comparisons are chart/reference dependent and may not be promoted to a
   physical incompatibility by themselves.
7. Check the D1 natural radial source moment symbolically and by interval
   substitution.  State explicitly whether the mixed-source successor's
   dependent `A s^2(1-s)^2 psi(r)` correction is needed for D1 or only for its
   retained projected reference.

## Classification rule

- **(a) Coordinate/gauge/reference translation:** a discrepancy confined to
  source targets, source traces, coordinate components, or another chart,
  while the same physical D1 data remain internally compatible.
- **(b) Missing freely specifiable Cauchy data:** the physical background and
  wall jets agree, but an otherwise free lapse, shift, extrinsic-curvature,
  source, or outer-reference datum is absent.
- **(c) Genuine incompatibility with the present dynamic preparation:** the
  frozen D1 physical fields, wall placement, matter content, or extrinsic
  geometry fail the present P16 physical data after the chart is fixed.

More than one category may apply to different layers.  Category (a) cannot
erase a category-(c) physical mismatch.  Category (b) is not assigned merely
because a different initial-data family could be constructed.

The only admissible positive join classification requires the full physical
and source jet to pass.  Otherwise the report must specify the smallest new
data family and constraints required, without launching it.

