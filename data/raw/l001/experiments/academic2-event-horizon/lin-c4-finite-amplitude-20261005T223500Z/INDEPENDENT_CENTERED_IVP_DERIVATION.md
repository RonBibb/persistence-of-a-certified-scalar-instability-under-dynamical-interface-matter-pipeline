# Independent centered Hamiltonian and mode-cancellation audit

This is symbolic preflight evidence, not a nonzero-amplitude calculation or an
existence result. `independent_centered_ivp.py` ran in Linux SymPy 1.14.0; all
14 exact identities in `INDEPENDENT_CENTERED_IVP.json` pass. The nonlinear
endpoint polynomial used here is the separately derived, original-time-PDE
corroborated polynomial in `INDEPENDENT_NONLINEAR_ENDPOINT.json`.

## Centered equation and its three columns

Write q=k exp(-2W), m=m2, theta=mu exp(-2W), xi=epsilon psi,
j=epsilon psi_s, delta=epsilon f+d, delta_s=epsilon g+d_s, with
d=C7+b0 H0+b1 H1. Set X=-6xi-2w, Y=-4xi, E1(x)=exp(x)-1 and
E2(x)=exp(x)-1-x. Direct subtraction of the static and first-variation
Hamiltonian equations gives

    w_s = v,
    v_s = -4H v - 2q w - (m Phi d + T d_s)/3 + N,
    N = q E2(X) + (2-m Phi^2/6) E2(Y)
        - (m/3) Phi delta E1(Y) - (m/6) delta^2 exp(Y)
        - delta_s^2/6 - 4j^2 - 6jv - 2v^2.

The unreduced Hamiltonian minus this expression is exactly
(-2+8epsilon psi) Cbg, where
Cbg=H^2-1-T^2/12+m Phi^2/12-q. Its derivative is zero under the source
equations. This is a legitimate cancellation for the same exact certified
background; an arbitrary independent point of its enclosing rectangle need
not satisfy it.

For a parameter column (h,z)=partial_x(w,v), with eta=0 for a and eta=H_i
for b_i, direct differentiation gives

    h_s = z,
    z_s = (-4H-6j-4v) z - 2q exp(X) h
          - [m exp(Y)(Phi+delta) eta + (T+delta_s) eta_s]/3.

Initial columns are (1,0),(0,0),(0,0). Both b columns therefore retain the
metric response caused by their entire interior shapes; their endpoint fifth
jet is not a reason to drop that response.

## Exact wall centering

At a physical wall let c=sigma gamma/2, df=epsilon f,
dp_linear=-T df/3 and dp_quad=-c df^2/6. Scalar endpoint values are unchanged
by either Hermite correction. The exact wall slope is exp(-2xi)(H+dp),
dp=dp_linear+dp_quad. Using psi_s=-2H psi-Tf/3,

    Rwall = H E2(-2xi) + dp_quad + E1(-2xi) dp,
    original Israel mismatch = v - Rwall.

Thus w(0)=a, v(0)=Rwall_lower and the first upper row is
v(D)-Rwall_upper. Rwall is independent of a,b0,b1. This confirms the staged
launch and first-row Jacobian.

## Why precisely two epsilon coefficients may be removed

The regular mode constraint and wall Robin row are

    C = T g - (m Phi-4HT) f + [2T^2-3(theta+4q)] psi,
    R = g + 2T psi - c f.

The regular ODE gives C_s=-4HC without division by T. At epsilon=0 the first
and third C7 corrections vanish. Their linear coefficients are respectively
-R and, after R=0 and Cbg=0, (2/3)T C. Since the degree-seven Hermite operator
is linear, C7 and every spatial derivative of C7 have exactly zero epsilon
coefficients of degrees zero and one for the admitted physical mode.

The reduced normalized scalar fourth-row forcing at b=0 also has zero constant
term. After R=0 and Cbg=0 its linear term is C times the polynomial

    (2/9)[108H^2 T + 18H Phi m - 54HTc - 8Phi^2 Tm
           + 6Phi c m - 30T^3 - 12Tm + 3T theta + 96T].

This has no singular denominator or scalar-turn exception. The subsequent
q-r feedback is quadratic because S=0 and q-r=0 at the static source. Hence
the constant/linear W coefficients may be removed, but only in the Taylor
expansion about epsilon=0 and only for the certified physical mode. They may
not be removed in the shifted interval-center eighth-derivative calculation.
No identity licenses deletion of quadratic terms, q dependence, source
uncertainty, or the metric response of either b column.

## Implementation comparison and scope

The staged nonlinear RHS is the same equation with the potential terms
regrouped; its coefficients ell_s-4A_s and -2q exp(X) match the independent
columns. The wall formula uses dp_quad=-sigma gamma df^2/12, equal to the
expression above. The interval source supplies enclosures of the same exact
solution, and intersecting those enclosures with proved wall identities keeps
that solution. It does not turn every rectangle point into an eigenmode.

The full nonlinear endpoint audit already shows that the q terms survive and
that reduced and original fourth rows differ by the unchanged Israel row times
an analytic factor. Retaining the Israel row therefore preserves the roots;
the present calculation does not assume nonlinear triangularity. A finite
amplitude claim still requires all frozen interval IVP, image and contraction
gates. No hyperbolic-evolution or connected-amplitude-interval conclusion is
being asserted.

Source SHA-256: `75a2e8958c7f3569574196660abec8a06c2b321aff6b0ed94edb6367064ccf88`.
Receipt SHA-256: `f482c8942380c5b9dc1a1762298639155b43645d47266c3c0730186dc9ff1bc3`.
Endpoint receipt SHA-256: `93511b04a5b504ecfc4a844c381455568948a34d3d32a95f4f0e5c2f6edadf97`.
