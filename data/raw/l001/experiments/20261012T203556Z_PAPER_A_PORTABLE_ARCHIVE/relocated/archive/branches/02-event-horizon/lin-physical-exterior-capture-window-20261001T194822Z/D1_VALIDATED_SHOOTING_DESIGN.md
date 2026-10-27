# D1 validated-shooting design

## Purpose

Promote the retained positive-curvature warp/scalar background from a
qualified binary64 BVP candidate to a rigorous existence result, or return an
explicitly inconclusive validated-numerics outcome. This is the first gate in
the warped-Kottler route. It is independent of P407 and does not evolve the
collapse data.

The efficient formulation is **not** an interval Newton solve on the 5,372
node collocation vector. The previously derived proper-distance shooting
reduction leaves one scalar shooting parameter and is the natural target for
validated ODE integration plus a one-dimensional interval Newton step.

## Exact problem

Use proper distance \(s\) and

\[
 y=(A,H,\Phi,S,Z),\qquad A=\log\psi,\quad H=A_s,\quad S=\Phi_s,
\]

with

\[
 \begin{aligned}
 A_s&=H,\\
 H_s&=-S^2/3-k e^{-2A},\\
 \Phi_s&=S,\\
 S_s&=m^2\Phi-4HS,\\
 Z_s&=e^{-A}.
 \end{aligned}
\]

All action and wall parameters are the exact dyadic values represented by the
bound binary64 inputs. The only shooting variable is
\(a=\Phi(0)\). Define

\[
 H_0(a)=-\frac{\lambda_a+\gamma(a-v_0)^2/2}{6},\qquad
 S_0(a)=\frac{\gamma(a-v_0)}2,
\]

\[
 k(a)=H_0(a)^2-1-\frac{S_0(a)^2}{12}+\frac{m^2a^2}{12},
\]

and launch from \(A_0=Z_0=0,\ \Phi_0=a\). These formulas impose the lower
Israel, lower scalar and Einstein-constraint conditions exactly.

The upper Israel event and remaining scalar residual are

\[
 G(s,a)=H(s,a)-\frac{\lambda_b+\gamma(\Phi(s,a)-v_1)^2/2}{6},
\]

\[
 h(a)=S(D(a),a)+\frac{\gamma}{2}
       [\Phi(D(a),a)-v_1],\qquad G(D(a),a)=0.
\]

An existence certificate must enclose a zero of \(h\), not merely reproduce
the floating-point candidate.

## Bound numerical seed, not proof data

The authenticated search supplies the starting interval

\[
 a\in[0.09901076956670637,\ 0.09901087894170638].
\]

At its endpoints the recorded scalar residuals are respectively
\(-1.1983400975\times10^{-2}\) and \(+1.6191749961\times10^{-3}\). The retained
root is near \(0.09901086589880687\), with \(D\simeq1.99756727919\),
\(L\simeq6.38029536952\), and \(k\simeq3.26841338454225\times10^{-4}\).
The nominal derivative of the upper-Israel event along the flow at the root is
about \(-1.79\times10^{-2}\), so the crossing appears strongly transverse.
Across the nearest retained admitted level-0 samples, scalar-residual secant
slopes are positive and lie between approximately \(1.2386\times10^5\) and
\(1.2437\times10^5\); the original sign bracket gives
\(1.243664\times10^5\). This is favorable evidence for a derivative bounded
away from zero, but it is not a derivative enclosure.
These numbers choose the validation box; none is an interval conclusion.

## Certificate sequence

1. **Bind the exact problem.** Record the dyadic rational form of every fixed
   input, the shooting interval, precision, ODE Taylor order, subdivision
   limits, runtime libraries, and all source hashes before execution.
2. **Validated flow tube.** Integrate \(y\) and its \(a\)-variational equation
   with outward-rounded interval arithmetic. Use a high-order Taylor model or
   an equivalent validated ODE method. The existing Arb runtime can provide
   arithmetic, but the old cap-enclosure code is not a validated ODE solver and
   cannot be relabelled as one.
3. **Guard enclosure.** On the entire tube prove \(\psi=e^A>0\),
   \(0<\Phi\le v_0\), finite \(Z\), and enclosure of the conserved constraint
   containing zero with a separately bounded defect.
4. **First-crossing authority.** Prove \(G\) has one transverse zero and no
   earlier zero on the validated interval. The load-bearing derivative is
   \[
   G_s=-S^2/3-k e^{-2A}
       -\frac{\gamma}{6}(\Phi-v_1)S.
   \]
   A sign enclosure for \(G_s\), together with signed pre-event and event
   boxes, must replace the floating solver's first-detected-event language.
5. **Event-time sensitivity.** Integrate the variational equation and use the
   interval implicit-function formula
   \(D'(a)=-G_a/G_s\). Propagate this into an enclosure of \(h'(a)\).
6. **Interval Newton.** Apply a one-dimensional interval Newton or Krawczyk
   map to a narrowed \(a\)-box. A strict self-map proves a unique root in that
   box. If it does not self-map, subdivide prospectively; do not widen gates
   or replace the proof with a floating residual.
7. **Derived quantities.** Enclose \(a,k,D,L=Z(D)\), the endpoint fields,
   \(\min\psi\), both wall identities, and the first integral on the whole
   interval.
8. **Independent replay.** Reconstruct the certificate from exact rational
   inputs in a separate checker. The checker must verify every interval
   inclusion and the no-earlier-crossing cover without calling the producer's
   acceptance function.

## Outcomes

- RIGOROUS-CURVED-BACKGROUND-EXISTS: a strict interval-Newton inclusion,
  complete validated flow cover, unique first upper-wall crossing, and all
  wall/positivity identities pass.
- VALIDATED-SEARCH-INCONCLUSIVE: interval wrapping, unresolved event order,
  or failure of the Newton self-map. This is not nonexistence.
- BOUND-BOX-EXCLUDES-A-SOLUTION: only if interval arithmetic proves that the
  specified box contains no admissible root. It says nothing outside that
  box.

Even the first outcome supplies only D1. It does not repair the factor-of-two
brane-separation mismatch or establish that the collapse evolves toward this
exterior; those are the separate D2 lineage questions.

## Feasibility ruling

This is a small validated problem: five ODE state variables, five
sensitivities, one shooting interval and a proper-distance span of about two.
It should be materially cheaper and easier to audit than intervalizing the
full collocation vector. The non-rigorous data show a wide residual sign
change and a non-negligible event transversality margin, both favorable for an
interval proof. Feasibility is therefore **promising but untested** until a
validated-flow pilot reports actual enclosure widths.
