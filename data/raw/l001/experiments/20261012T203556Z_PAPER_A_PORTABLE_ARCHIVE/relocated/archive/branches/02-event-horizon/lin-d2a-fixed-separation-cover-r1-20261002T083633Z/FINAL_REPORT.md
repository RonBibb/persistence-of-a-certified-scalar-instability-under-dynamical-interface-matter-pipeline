# Corrected D2A fixed-separation cover: final report

## 1. Success and movement of the bar

The corrected validated cover completed and excludes a positive-curvature
static solution at the original source-bound proper separation

`D0 = 0.9996389747145851`

throughout the complete declared launch range `0 <= a <= v0`.

The exact contiguous cover contains 693 terminal boxes:

- 20 boxes have rigorously negative launch curvature and lie outside the
  positive-curvature route;
- 670 possible-positive-curvature boxes have both upper-wall residuals
  rigorously separated from zero;
- one box is excluded by the upper-Israel residual alone; and
- two boxes are excluded by the upper-scalar residual alone.

There are no gaps, overlaps, or unresolved boxes. On every box not already
excluded by negative curvature, the validated enclosure gives the uniform
disjunction

`max(|G_D|, |h_D|) > 0.0077`.

Thus the two upper-wall equations cannot vanish simultaneously anywhere in
the admitted positive-curvature launch range. The terminal classification is

`FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE`.

This materially moves the bridge question. D1 rigorously establishes a root
of the reduced curved-background shooting problem near proper distance
`1.9975`, while D2A now rigorously excludes the same reduced static route at
the collapse lineage's original distance near `0.99964`. The factor-of-two
separation difference is not a small tolerance or locator error within this
fixed-parameter static family.

## 2. Issues and controls

The predecessor D2A run was technically incomplete because it ignored the
direct upper-scalar residual fallback below the analytic no-turn threshold.
The corrected producer changes only that classification logic: every box is
now excluded whenever either wall residual rigorously excludes zero, while the
analytic no-turn theorem remains an additional certificate.

Preflight passed all six classification routes, exact Arb containment and
strict-nesting controls, negative-curvature and target-width routing, the
nominal cover count, a real below-threshold box with a non-admissible scalar
path, and exact checkpoint rational round-trip. That real box was immediately
excluded by both residuals, directly exercising the repaired path.

Production used 1,024 validated proper-distance steps per integrated box,
512-bit Arb arithmetic, and 673 integrated boxes. Runtime was 162.36 seconds.
It published 86 content-addressed exact-resumption checkpoints. The post-run
audit reproduced every classification from exact rational bounds, verified
the contiguous cover and all checkpoint addresses, and found no live worker.

## 3. Next justified step

Do not search for another fixed-separation static root by relaxing gates or
freeing a physical parameter; that would answer a different question. The
remaining same-development possibility is dynamical: a radion/separation
transition from the collapse data toward the D1-enclosed static geometry.

D2B must not begin until a complete joint initial-data set is globally
admitted with compatible wall, corner, Hamiltonian, momentum, and scalar
constraints. The immediate next task is therefore the globally admitted
initial-data prerequisite and a go/no-go design for D2B, not an evolution
run. If that prerequisite cannot be met, the causal-exterior construction
remains a conditional model control rather than a development of the collapse
lineage.

## 4. Viability

The reduced static mathematics is now strong: D1 gives rigorous root
authority at the longer separation, and D2A supplies a rigorous exclusion at
the original separation. The physical bridge is narrower, not established.
The direct static identification is closed for the declared model; only a
properly constrained dynamical separation transition or a genuinely changed
physical model remains.

This is a scientifically useful answer even though it is an exclusion. It
does not establish a collapse event horizon, does not promote the conditional
Kottler causal control, and does not show that the collapse evolution selects
the D1 geometry.
