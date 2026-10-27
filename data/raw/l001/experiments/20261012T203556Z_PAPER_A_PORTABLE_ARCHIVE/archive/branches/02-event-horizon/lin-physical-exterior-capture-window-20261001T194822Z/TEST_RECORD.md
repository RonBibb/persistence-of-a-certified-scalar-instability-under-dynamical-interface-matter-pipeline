# Test record

Runtime: macOS 15.8 arm64, Python 3.14.4, SymPy 1.14.0 and mpmath 1.3.0.
No floating-point PDE evolution or precision-sensitive production result was
run on the Mac; the numerical root display uses 80-decimal mpmath arithmetic,
while the load-bearing curvature and frame checks are symbolic.

## Executed controls

### Pure geometry and authority tests

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
python3 -m unittest -v test_kottler_barrier.py
```

Outcome: **19 passed, 0 failed**.  The authority test exhausts all 8,192
Boolean combinations of the thirteen declared gates and confirms that only the
all-true exact case returns `ONE-CENTRAL-END-RELATIVE-BRACKET-QUALIFIED`.
The category counts are preserved in `AUTHORITY_ENUMERATION.json`.

### Independent symbolic/high-precision control

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 \
python3 -B symbolic_kottler_control.py
```

Outcome:

- all 25 five-dimensional warped-Kottler Ricci-component identities and eight
  independent Eddington-Finkelstein frame/expansion identities vanish exactly
  in SymPy;
- the retained positive-curvature parameter is sub-Nariai;
- the chosen cap is future trapped;
- the chosen barrier lies strictly between the two horizons and has positive
  outward expansion;
- the full normalized remainder is zero; and
- the exact outgoing visible curve reaches the barrier in finite advanced
  time.

Every field emitted by a fresh `symbolic_kottler_control.py` reexecution
matches the corresponding stored field. The stored `CONTROL_RESULT.json` has
one additional `unit_tests` metadata object, added after the generator run;
there is no scientific-value mismatch.

The same sources were then replayed read-only on `linux.vm` with Python 3.12.3,
SymPy 1.14.0 and mpmath 1.3.0 after checking load and active processes.  All 19
tests pass there, and every generator-emitted control field matches the stored
Mac record. The same extra `unit_tests` metadata qualification applies. The
replay used one deterministic thread and did not
interfere with the two pre-existing one-core tracking jobs.

All twelve local predecessor bindings in `SOURCE_BINDINGS.json` were recomputed
from their current bytes and match exactly.

### Fixed-separation diagnostic probe

The source-bound selector separation \(D_0=0.9996389747145851\) was used in a
new floating diagnostic. A 601-point launch scan over
\(a\in[0.0924,0.09999]\) was run at two DOP853 tolerance/step levels. On the
sampled admissible paths, each level found one sign-change root of the upper
Israel residual:

\[
 a=0.09862479074023135.
\]

At the finer Mac level its upper scalar residual is
\(-0.801435770035221\), with \(S_b=-0.2385173566\). The root is
\(3.5021\times10^{-4}\) below the exact no-turn threshold and has positive
no-turn polynomial margin \(0.0420254\). A Linux replay with older independent
SciPy/NumPy versions agrees in \(a\) to \(2\times10^{-17}\) and in the scalar
residual to approximately \(3.1\times10^{-14}\).

This is a sizing result, not root completeness: finite sampling cannot exclude
a tangent root, a missed invalid-to-valid pocket, or a separate branch.
`FIXED_SEPARATION_PROBE_RESULT.json` records that boundary explicitly.

## Not executed

- no P407 extension;
- no collapse evolution;
- no MOTS solve;
- no production null tracing;
- no BVP refinement or interval enclosure; and
- no alteration of a sealed predecessor.

## Classification boundary

The tests certify the algebra and causal decision logic of a conditional exact
model family.  They do not certify existence of the curved warp/scalar
antecedent, its nonlinear stability, a transition from the collapse data, or
an event horizon in the collapse lineage.
