# Proof and certificate narrative

## 1. The mathematical question

Fix the five-dimensional Einstein--scalar action, wall potentials, binary64
parameter values, orientation, and maximally symmetric warped ansatz stated in
`THEOREM.md`. After the lower-wall junction conditions and the Einstein first
integral are imposed, the remaining static boundary-value problem is a
one-parameter shooting problem in the lower-wall scalar value

\[
a=\Phi(0).
\]

For each admissible `a`, the reduced initial-value problem determines a local
trajectory. The upper-wall Israel residual is `G(s,a)`. When its first zero is
transverse, it defines an event location `D(a)`. The remaining scalar-wall
condition is then the scalar function

\[
q(a)=h(D(a),a).
\]

The consolidation establishes two complementary statements about this same
declared reduced problem:

1. a unique zero of `q` exists in one small shooting interval when the wall
   separation is allowed to be selected by the first upper-Israel event; and
2. no positive-curvature solution exists at the original fixed separation
   `D0` for any declared launch value `0 <= a <= v0`.

The proof is computer assisted. It does not infer either statement from a
floating-point root finder alone.

## 2. Clause-to-certificate map

| theorem clause | mathematical certificate | controlling artifact |
|---|---|---|
| fixed action and parameterization | source-pinned model and prospective BVP derivation | `source-snapshot/brane-horizon-phase-structure/MODEL_V1.md`; `capture-to-model-2026-09-12/static-background-successor/PROSPECTIVE_BVP_DESIGN.md` |
| validated reduced flow | interval ODE prerequisite with manifest-bound terminal | `lin-d1-validated-flow-prerequisite-20261001T212157Z/` |
| validated first-event construction | event prerequisite with manifest-bound terminal | `lin-d1-validated-event-prerequisite-20261001T212800Z/` |
| D1 existence and local uniqueness | strict interval-Newton self-map with derivative excluding zero | `lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json` |
| D1 formula and inclusion audit | independent symbolic differentiation and exact rational inclusion arithmetic | `lin-d1-independent-audit-20261002T014828Z/RESULT.json`; `INCLUSION_CERTIFICATES.json` |
| D2A fixed-distance exclusion | exact contiguous interval cover of the complete declared launch interval | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json` |
| D2A independent reconstruction | classifications, coverage, checkpoints, and residual floor reproduced | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/POSTRUN_AUDIT.json` |
| packet-level recheck | hashes, manifests, inclusions, cover, counts, residual floor, and checkpoint addresses rederived | `verify_evidence.py` |

All paths in the table are relative to the research root, under
`branches/02-event-horizon/` unless otherwise shown.

## 3. Why D1 proves a root

The D1 producer propagates interval enclosures for the state and its
sensitivity with respect to `a`. Transversality is certified by

\[
G_s<0
\]

throughout the relevant event enclosure. The implicit-function formula is
therefore valid and supplies `D'(a)`. Combining it with the state sensitivity
gives the total derivative `q'(a)`.

At 32,768 validated steps and 768-bit Arb precision, the narrow interval has
the interval-Newton image

\[
[0.09901086573766466,\ 0.09901086594043548].
\]

Its exact rational endpoints are recorded in the theorem and the D1 result.
The image is strictly inside the frozen narrow interval. The standard
interval-Newton theorem therefore gives existence and uniqueness of a zero
inside that interval. The derivative interval

\[
q'(a)\subset[124130.66976980511,124218.80928782765]
\]

excludes zero. The higher-resolution image is also strictly nested inside the
16,384-step image; nesting is corroborative refinement evidence, while the
strict self-map is the proof-bearing condition.

The independent D1 audit rederived every sensitivity and implicit-event
formula symbolically and checked the inclusion arithmetic using exact
rationals. It did not independently replay the interval ODE integration. That
distinction is retained as a publication limitation.

The certified event-position enclosure is

\[
D\in[1.99749755859375,1.99761962890625].
\]

## 4. Why D2A excludes the fixed-distance solution

D2A does not sample isolated launch values. It starts from the exact interval
representing the complete declared domain `0 <= a <= v0` and constructs an
adaptive interval cover. The post-run audit rederived an exact, gap-free,
non-overlapping cover from zero through the exact binary64 value of `v0`.

Each terminal box is discharged by one of four mathematically sufficient
routes:

- negative launch curvature, incompatible with the declared
  positive-curvature branch;
- both upper-wall residual intervals exclude zero;
- the upper-Israel residual interval excludes zero; or
- the upper-scalar residual interval excludes zero.

There are 693 terminal boxes and no unresolved boxes. The reproduced counts
are 20, 670, one, and two respectively. On every box reaching the upper wall,
the independently reconstructed lower bound satisfies

\[
\max(|G(D_0,a)|,|h(D_0,a)|)>0.0077.
\]

Consequently no admissible launch can make both fixed-distance wall residuals
zero at the declared `D0`. This is an exclusion theorem for the fixed reduced
static family, not a statement about all five-dimensional configurations.

## 5. What the paired result adds

D1 alone says that the fixed action admits a positive-curvature reduced static
solution after the separation is allowed to adjust. D2A alone says that the
original separation has no positive-curvature solution within the complete
declared launch interval. Together they show that the nearly factor-of-two
separation mismatch is structural within this fixed reduced family: it is not
explained by a missed scalar launch or ordinary root-finder tolerance.

The pair does **not** supply a dynamical mechanism moving one separation to the
other. In particular, it does not prove radion evolution, stability,
same-development selection, collapse formation, an event horizon, or a baby
universe.

## 6. Reproducible certificate check

From the research root, run:

```bash
python3 -B branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py
```

The verifier is read-only. A valid run ends with `"status": "PASS"`. It
independently recomputes the bound file hashes, source-manifest contents,
terminal-to-manifest bindings, exact D1 interval inclusions, D2A coverage and
classification counts, the conservative residual floor, and all D2A
checkpoint content addresses.

