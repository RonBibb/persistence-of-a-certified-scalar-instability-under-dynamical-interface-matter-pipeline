# Parameter provenance and scientific motivation

## Why this exact parameter set is worth certifying

The six binary64 literals were not chosen after the static calculation to
create a positive result. They are inherited from the already defined
Einstein--AdS--scalar wall model and its source-bound selector:

```text
m^2       = 0.41
gamma     = 20
v0        = 0.1
v1        = 0.09048374180359596
lambda_a  = 5.999990376773895
lambda_b  = -6.052844277744164
```

The parent model uses `ell=kappa_5=1`, `Lambda_5=-6`, quadratic stabilizer
wall potentials, and a separate collapse scalar. In the static theorem the
collapse scalar is set to zero, so the question concerns the vacuum
Einstein--stabilizer sector of that same declared action.

The scientific reason to certify this point is therefore concrete rather than
generic. The original source supplied a momentarily stationary constrained
selector on a proper interval of

```text
D0 = 0.9996389747145851.
```

That selector was never a solution of every equation of the later static
maximally symmetric ansatz. The theorem asks the well-posed antecedent question:
with the wall action held fixed, does a complete positive-curvature static
solution exist, and is it compatible with the original proper separation?

The paired answer is informative:

- allowing the upper-wall position to be selected produces a locally unique
  positive-curvature solution near `D=1.9975`;
- retaining the original `D0` yields no positive-curvature simultaneous wall
  root anywhere in the complete declared `0<=a<=v0` launch interval;
- the exact separation ratio is certified between 1.998218966 and 1.998341081
  using the narrower original D1 enclosure.

Thus the theorem converts a source-specific modeling question into a precise
compatibility statement. It shows that the fixed wall data and the originally
prescribed separation do not jointly realize the certified curved static
branch within the reduced family.

## Exact provenance of the literals

- `m^2=0.41`, `gamma=20`, and `v0=0.1` are fixed model inputs inherited from
  the source action and stabilizer construction.
- `v1=0.09048374180359596` is the exact P394 binary64 literal. It is not
  recomputed when the separation changes, because doing so would change the
  upper-wall potential while claiming to solve the same model.
- `lambda_b=-6.052844277744164` is independently frozen in the P394 source
  record and agrees with the source-bound N65 reconstruction.
- `lambda_a=5.999990376773895` is reconstructed from the unchanged source
  constructor's explicit `6-U_a` rule at the same bound N65 solution. No
  separate archived lower-tension literal was located. This asymmetric
  provenance must remain explicit.
- `D0=0.9996389747145851` is the source-bound selector's proper separation,
  not its coordinate width and not a newly tuned theorem input.

All decimals are interpreted as their exact binary64 dyadic values in the
certificates. The theorem is about those fixed values; it is not a robustness
claim over a parameter neighborhood.

## What the motivation does not imply

Source ancestry is not dynamical ancestry. The certified static branch has a
different proper separation and a positive-curvature four-dimensional base.
In a flat-slicing de Sitter chart its Cauchy slice also has nonzero extrinsic
curvature. It cannot be inserted into the old interval by coordinate relabeling
while preserving the physical geometry and junction problem.

Accordingly, the parameter provenance does **not** establish that the collapse
development selects the D1 branch, that a radion evolves from `D0` to D1, or
that the static solution is stable. Those questions require a compatible
Cauchy embedding and a separately admitted evolution.

## Recommended article language

> We certify a source-pinned parameter point rather than a generic parameter
> family. The literals are inherited from the pre-existing wall model and its
> constrained selector; they are held fixed throughout both certified boundary
> placements. This makes the paired theorem a test of static compatibility for
> that declared model. It does not imply that the associated dynamical system
> evolves between the two separations.

This paragraph should appear near the model definition. The provenance details
and hashes belong in the supplement or archive.
