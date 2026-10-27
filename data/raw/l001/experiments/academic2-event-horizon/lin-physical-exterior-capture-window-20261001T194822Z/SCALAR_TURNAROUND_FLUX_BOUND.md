# Scalar-turnaround flux bound

## Result

The proper-distance scalar equation yields an analytic necessary condition for
the turnaround required by the two Robin walls. For the declared parameters,
any positive-curvature shooting solution launched with

\[
 a=\Phi_a<0.0989750001
\]

cannot turn upward at any proper distance. The retained first-Israel-crossing
states bracketing the collapse separation have
\(a=0.0985760625\) and \(a=0.09871901956670638\), so both lie safely in this
no-turn region. The successful curved candidate has
\(a=0.09901086589880687\), above the threshold.

This does not by itself exclude every fixed-separation branch. It supplies a
sharp analytic discriminator for the validated D2A cover.

## Derivation

Let

\[
 J=e^{4A}S.
\]

The scalar equation gives

\[
 J_s=e^{4A}(S_s+4HS)=m^2e^{4A}\Phi.
\]

For \(k\ge0\),

\[
 H_s=-S^2/3-ke^{-2A}\le0,
\]

so \(H(s)\le H_0<0\), \(A(s)\le H_0s\), and
\(e^{4A(s)}\le e^{4H_0s}\). The scalar maximum principle gives
\(0<\Phi\le v_0\) on an admissible branch. Therefore

\[
 J(s)-S_0
 \le m^2v_0\int_0^s e^{4H_0u}\,du
 < \frac{m^2v_0}{-4H_0}.
\]

If

\[
 -S_0\ge\frac{m^2v_0}{-4H_0},
\]

then \(J(s)<0\), and hence \(S(s)<0\), for every finite \(s\). Such a
solution cannot satisfy an upper Robin condition that requires \(S_b>0\).

Using

\[
 S_0=\frac{\gamma}{2}(a-v_0),\qquad
 H_0=-\frac{\tau_a(a)}6,\qquad
 \tau_a(a)=\lambda_a+\frac{\gamma}{2}(a-v_0)^2,
\]

the no-turn criterion becomes

\[
 \gamma(v_0-a)\tau_a(a)\ge 3m^2v_0.
\]

The left side is strictly decreasing in \(a\) throughout the relevant
\(0<a<v_0\) interval, so there is one threshold.

## Exact rational threshold bracket

With the declared decimal inputs treated as exact rationals, define

\[
 P(a)=\gamma(v_0-a)\tau_a(a)-3m^2v_0.
\]

Exact rational evaluation gives

\[
 P(0.0989750001)
 =\frac{30509730282291799999}
 {5000000000000000000000000000}>0,
\]

and

\[
 P(0.0989750002)
 =-\frac{3686311084106862501}
 {625000000000000000000000000}<0.
\]

Thus the unique threshold lies in

\[
 (0.0989750001,\ 0.0989750002).
\]

For the two stored states bracketing the collapse separation, exact rational
values of \(P\) are approximately \(0.0478728\) and \(0.0307178\), well on
the no-turn side. For the retained curved candidate,
\(P\approx-0.00430390\), so the bound permits the turnaround that is present
in its profile.

## Consequence for D2A

A rigorous fixed-separation exclusion can now be cheaper than a full
two-residual branch cover:

1. validated-integrate to \(D_0\);
2. prove that every solution of the upper Israel condition at \(D_0\) has
   \(a<0.0989750001\);
3. invoke the analytic no-turn bound; and
4. use \(\Phi_b<v_1\) to show the upper scalar Robin condition requires
   \(S_b>0\), contradicting \(S<0\).

The existing finite scan strongly supports step 2 but does not prove it or
exclude a separate/tangential upper-Israel branch. Those are the precise
remaining interval tasks.
