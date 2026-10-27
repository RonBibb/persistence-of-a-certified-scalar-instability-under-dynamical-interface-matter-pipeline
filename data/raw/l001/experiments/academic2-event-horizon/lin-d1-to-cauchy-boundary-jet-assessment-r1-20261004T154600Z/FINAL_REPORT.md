# D1 is a viable new Cauchy background, not a boundary repair of P16

## Result

The certified D1 static solution has a clean, time-symmetric embedding in the
Lin evolution variables on the declared radial domain.  In a de Sitter
static-patch chart, `R=10` is safely inside the coordinate horizon,
the lapse and spatial metric are positive, both wall junction intervals contain
zero, and the geometric generalized-harmonic source supplies an **exactly
moment-consistent outer reference**.

It nevertheless does **not** join directly to P16.  Once the chart is fixed,
D1 and P16 are different physical Cauchy datasets: their separation, wall
metric, scalar, and nonzero spatial jets disagree.  The classification is

> `NO_DIRECT_D1_TO_P16_JOIN__NEW_D1_CAUCHY_FAMILY_REQUIRED`.

This is not a negative result about D1.  It is a constructive distinction:
D1 can seed a new background-embedding test, but it cannot be used as one more
repair coefficient for the present P16 data.

## Frozen translation

Use the D1 static-patch base

    gamma_k = -(1-k r^2) dt^2 + dr^2/(1-k r^2) + r^2 dOmega_2^2

and map the certified D1 conformal coordinate of length `L` to the production
compact coordinate `x in [1,e]`.  With `c=L/(e-1)`, `w=exp(A)`, and
`f=1-k r^2`, the production fields are

    q = (0, 0, -w^2 f, w^2, w^2 k/f, 0, w^2 c^2, Phi, 0).

The lapse is `alpha=w sqrt(f)`, the shift vanishes, and in the convention
`K_ij=-(2 alpha)^-1 partial_t h_ij`, all components of `K_ij` vanish.
Both scalar momenta vanish.  The complete interval records for `q`, `q_x`,
`q_r`, and `q_xr` at both walls are in `output/RESULT.json`.

This chart is the closest physical comparison with P16 because both are
time-symmetric.  A flat-slicing de Sitter chart would share P16's flat radial
topology but has

    K_ab = -sqrt(k) exp(-A) h_ab,

so it cannot be identified with P16's zero-velocity preparation.  A global
de Sitter time-symmetric slice instead changes the radial topology.  The chart
choice is therefore substantive input to any future evolution, not a hidden
coordinate convenience.

## Certified wall data

At the outer radius, the static-patch factor is enclosed by

    f(10) in [0.9673158624, 0.9673158699],

so the whole declared radial interval lies inside the static patch.  Selected
wall intervals are:

| Quantity | Lower wall | Upper wall |
|---|---:|---:|
| `g_00` | `[-0.9673158691,-0.9673158632]` | `[-0.01766355135,-0.01765376380]` |
| `g_perp` | `[1,1]` | `[0.01825025773,0.01826037585]` |
| `(g_rr-g_perp)/r^2` | `[3.378847789e-4,3.378848427e-4]` | `[6.166484134e-6,6.169904388e-6]` |
| `g_xx` | `[13.78305934,13.79184556]` | `[0.2515443409,0.2518442837]` |
| `Phi` | `[0.09901086490,0.09901086690]` | `[0.08830813702,0.08833598175]` |
| lapse | `[0.9835221722,0.9835221752]` | `[0.1328674696,0.1329042940]` |

The D1 proper separation is

    D in [1.997497558594,1.997619628906],

whereas the P16-line metadata separation is

    D0 = 0.9996389747145851.

Their difference is enclosed by
`[0.997858583879,0.997980654192]`, strictly away from zero.

Both wall metric and scalar junction checks contain zero under the frozen map.
The upper enclosures are wider because the replay encloses the whole D1 root
box and first-event cell; no midpoint was substituted.

## Direct comparison with P16

P16's complete declared wall comparison contains 72 point-versus-interval
checks: four jet blocks at two walls, with nine fields per block.  Exactly
32 pass.  Those are the four fields that are identically zero in both
constructions—`g_x0`, `g_xr/r`, `g_0r/r`, and `chi`—in every block.

All 40 comparisons involving the five nonzero physical channels fail the
unchanged absolute `1e-8` gate:

- `g_00`;
- `g_perp`;
- `(g_rr-g_perp)/r^2`;
- `g_xx`;
- `Phi`.

They fail in `q`, `q_x`, `q_r`, and `q_xr` at both walls.  For example, the
lower P16 values are approximately

    g_00=-1.484309346,
    g_perp=1.484309346,
    g_xx=1.484309346,
    Phi=0.09901808720,

while D1 gives the lower intervals displayed above.  This is not a small
higher-jet discrepancy.  It is a different background geometry.

The original initial-data branch also has nonzero collapse matter away from
the corner, while D1 sets `chi=0`, and the exact upper bare-tension literal
differs by about `6.38e-13`.  The parameter difference is not the cause of the
large component mismatch, but it independently prevents an exact same-input
claim without a parameter enclosure.

## What happens to the source obstruction

For the D1 static-patch metric, the geometric source is

    H_0 = 0,
    H_x = -3 c w A_s,
    H_r/r = 4k/f.

Its temporal trace slope and mixed normal-radial source derivative vanish:

    partial_t H_0 = 0,
    partial_x partial_t H_0 = 0,
    partial_r H_x = 0,
    partial_x partial_r H_x = 0.

The P16/P17 lineage instead has nonzero temporal source data.  At the lower
and upper corners respectively,

| Quantity | Lower | Upper |
|---|---:|---:|
| P17 geometric `partial_t H_0` | `-1.49336e-3` | `-4.67405e-4` |
| P17 geometric `partial_x partial_t H_0` | `+0.371117` | `-0.117667` |
| projected-reference `partial_x partial_t H_0` | `+0.415728` | `-0.130118` |
| sealed temporal correction `d` | `-0.0446107` | `+0.0124516` |
| sealed mixed normal-source correction `e` | `+1.95011e-6` | `-2.13269e-7` |

These differences are real, but they are source/gauge/reference differences,
not invariant evidence that D1 violates the physical equations.

More importantly, D1 resolves the global moment structurally.  For its natural
reference, chosen from the same geometric field,

    W = g_xx/(N B g_perp^2) = c^2 w^-6,
    Y = (1/2) partial_r log W = 0,
    integral partial_r H_x dx = 0.

Hence the exact radial-source moment defect is zero.  D1 does **not** need the
mixed-source successor's proposed dependent
`A s^2(1-s)^2 psi(r)` adjustment.  That adjustment belongs to the retained
P16 projected-reference interpolation, whose sealed defect is
`-5.32246e-7`; it is not a missing term in the D1 geometry.

This is the positive part of the result: the remaining P16 moment defect is
confirmed to be reference-extension specific, not a universal obstruction
from the action or wall system.

## Mismatch classification

The answer is layered rather than a single label.

1. **Category (a), coordinate/gauge/reference translation, applies to the
   source traces.**  D1's natural source is internally compatible and
   moment-consistent.  P16/P17 use a different projected reference and fixed
   anchors.
2. **Category (b), missing freely specifiable Cauchy data, is not the primary
   explanation.**  A D1-specific outer reference must be supplied, but no
   free source or lapse datum can convert P16's fixed physical metric and
   scalar into D1.
3. **Category (c), genuine incompatibility with the present dynamic
   preparation, applies to the direct join.**  Separation and all five
   nonzero physical wall channels differ after the closest common chart is
   fixed.

Thus the correct next object is a **new D1 Cauchy background family**, not a
further repair of P16.

## Claim boundary

This assessment supplies a complete analytic/interval boundary-data map and a
precise contract for a future embedding.  It does not solve the production
constraints, assemble a global numerical field, or execute an evolution.
It establishes neither selection of D1 by the collapse lineage nor a radion
transition, event horizon, or parent-child spacetime connection.

The frozen evaluator first stopped on an exponent-form decimal parser issue.
That failure is preserved.  R1 changed only the exact decimal parser and
produced the result above with all parent hashes intact.

