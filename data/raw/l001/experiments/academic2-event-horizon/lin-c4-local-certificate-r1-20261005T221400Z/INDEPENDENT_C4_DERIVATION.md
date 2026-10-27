# Independent derivation: the final three-variable C4 preparation

Status: exact analytic reduction and symbolic corroboration PASS. This is not a
new physical integration, a quantitative amplitude certificate, or an evolution
existence theorem. The proposed finite interval corroboration remains to be
frozen, executed, and audited.

## Scope and controlling preparation

This review concerns the final preparation in
`d1-native-cauchy-20261005T201829Z`, not just its earlier one-variable shooting
family. It uses the stated Einstein-scalar action, quadratic wall potentials,
closed de Sitter time-reflection slice, and lapse continuation
`alpha=exp(A)/cosh(sqrt(k)t)`. Sources inspected directly were
`LOCAL_EXISTENCE_ARGUMENT.md`, `DERIVATION.md`, `HIGHER_TIME_DERIVATION.md`,
`code/core.py`, `code/time_jets.py`, `code/higher_run.py`, `BINDINGS.json`, and
`results/REGULARITY_CERTIFICATE.json`. The latter's SHA-256 is
`8c1e003e718d201e8a632704d9ce2472bdc6d0ebcbebc5b6ea4b7008a3532714`.

Fix the same exact central background and any one physical mode supplied by the
certified negative-mass interval. No unique or lowest eigenvalue is assumed.
The exact background values remain in the inherited rational root and event
intervals; a fitted midpoint does not replace them. All derivatives below are
coordinate derivatives in the base proper coordinate `s`, where `L=1`.

Write `H=W_s`, `T=Phi_s`, `q=k exp(-2W)`,
`c_i=sigma_i gamma/2`, and

    B_i = c_i T - T_s = (4H+c_i)T-m2 Phi.

The unknowns are `x=(A(0),b0,b1)`. The prescribed scalar is background plus
`epsilon f`, the old degree-seven endpoint correction, and `b0 H0+b1 H1`.
The two exact fifth-coordinate-jet shapes are

    H0(s) = s^5 (D-s)^6 / (120 D^6),
    H1(s) = s^6 (s-D)^5 / (120 D^6).

Each has zero endpoint derivatives of orders zero through four. Its fifth
derivative is one at its own wall and zero at the other wall. These statements
hold at the actual endpoint `s=D`; they are not identities for two unrelated
interval arguments `s` and `D`.

## Full Hamiltonian response, including both shape columns

At epsilon zero, let `h=delta A`, `eta=delta Phi`, and `delta ell=0`. Linearizing
the Hamiltonian metric IVP gives

    h_ss + 4H h_s + 2q h = -(m2 Phi eta + T eta_s)/3.

For the first column `eta=0`, `(h,h_s)(0)=(1,0)`; call this solution `u`.
For shape column `j`, `eta=Hj`, `(h,h_s)(0)=(0,0)`; call it `wj`.
In particular, the interior scalar correction backreacts on the upper-wall
metric slope. It is incorrect to set either `wj_s(D)` to zero without proof.

The flux representation is obtained directly, without a fitted derivative:

    Q = exp(4W) h_s,
    h_s = exp(-4W) Q,
    Q_s = -2k exp(2W) h
          - exp(4W)(m2 Phi eta+T eta_s)/3.

This provides an economical second equation representation for the same three
columns. Sharing an interval arithmetic library or Taylor/Picard driver must
still be disclosed; it is not fully independent software verification.

## Exact endpoint reduction and coupled Jacobian

Let `R2` and `R4` be the second- and fourth-time scalar Robin defects obtained
from the original time equations. Let `I4` be the fourth-time Israel defect.
At a base wall, for a column with `eta` endpoint jets zero through order four,
the exact linear identities are

    delta R2 / alpha^2 = -4 B_i h_s,
    delta R4 / alpha^4 = eta_sssss + 8q B_i h_s,
    delta I4 / alpha^4 = 0.

The normalized fourth row in this experiment is `R4/(alpha^4/L^5)`; because
the base row itself vanishes and base `L=1`, its differential is precisely the
second expression above. Differentiating the normalization adds no term.
There is no uncancelled `h` value term. The identities follow from the actual
closed-chart time equations, including their time-dependent lapse terms.

Set

    d = u_s(D), c0 = w0_s(D), c1 = w1_s(D), beta = 8 q(D) B_1(D).

In row order upper Israel, lower normalized fourth Robin, upper normalized
fourth Robin, the complete Jacobian is

    J = [ d       c0       c1       ]
        [ 0       1        0        ]
        [ beta*d  beta*c0  1+beta*c1 ].

The lower scalar row uses the exact launch identity `h_s(0)=0`. Subtracting
`beta` times the first row from the third yields `(0,0,1)`, so

    det J = d,

    J^-1 = [ (1+beta*c1)/d  -c0/d  -c1/d ]
           [ 0              1      0     ]
           [ -beta          0      1     ].

Thus there is an exact analytic block reduction to the inherited shooting
derivative, while retaining every shape-induced metric response. The earlier
rigorous intervals for `d` were approximately
`[-0.9588769433,-0.9584013525]` and
`[-0.9588769588,-0.9584013475]`; the exact rational JSON endpoints control.
They exclude zero. This is sufficient for qualitative invertibility, once
the inherited certificate's source/input identity is authenticated. A new
full-column direct/flux enclosure remains useful corroboration and gives a
quantitative bound for the inverse; a finite-difference determinant is neither
necessary nor an acceptable substitute.

The separate source `independent_boundary_algebra.py` implements exact
differential algebra for these identities, the Hermite endpoint jets, the
coupled determinant and inverse. It imports no producer modules. Linux SymPy
1.14.0 returned PASS, recorded in `INDEPENDENT_BOUNDARY_ALGEBRA.json`.
Source SHA-256:
`a4670fc0b0a557aba810c7f60648879570b2f6c36b62653ba12df98364a0473f`.
The direct fourth-Robin reduction already holds before substituting the
background first integral into the displayed result. The derivation does use
the background field equations and the linearized Hamiltonian.

## Nonlinear lower-order and Israel compatibility

The old degree-seven preparation fixes scalar Robin exactly. Its third-jet
prescription uses the Israel target slope `pstar=-sigma U/6`, while the actual
metric slope is `p=A_s/L`. On a Hamiltonian solution, subtraction of the
second-Robin formula at these two slopes gives the exact identity

    R2/alpha^2 = (p-pstar)
        [6 t_l + {4(p+pstar)-4c_i} t - 2m2 Phi],

where `t=Phi_s/L`. Consequently upper Israel plus the prescribed lower launch
implies both second-time scalar conditions. Adding `H0,H1` changes none of
the endpoint jets needed for this identity. Its linearization at the
background is the `-4 B_i h_s` expression above.

There is also an exact nonlinear fourth-Israel identity; an observed small
fourth-Israel residual need not be elevated to an extra adjustable equation.
With

    Jwall = L^-1 A_s + sigma U/6,
    Rwall = L^-1 Phi_s - sigma U'/2,

the mixed Einstein equation in the declared lapse is

    -3(A_ts-ell_t A_s) = Phi_t Phi_s,
    (Jwall)_t = -Phi_t Rwall/3.

At a time-reflection slice this yields

    (Jwall)_tt = -Phi2 Rwall/3,
    (Jwall)_tttt = -Phi4 Rwall/3 - Phi2 (Rwall)_tt.

Hence exact scalar Robin and second-time scalar Robin imply fourth-time
Israel. To apply this to formal time jets one uses the mixed constraint and
its formal propagation from the Hamiltonian, momentum constraint and original
evolution equations, not an independent assumption that numerical residuals
are zero. No solution of the nonlinear time-evolution IBVP is claimed here.
Odd time derivatives vanish by the chosen reflection symmetry.

## Analytic family and the physical-mode tangent

The regular background and mode ODEs divide by neither `T` nor a turning-point
quantity. On the compact exact interval their fields are analytic. With this
background and mode fixed, the old correction and the two explicit shapes
are analytic in `(epsilon,b0,b1)`; `D` is bounded away from zero. The metric
IVP is analytic in these parameters and its initial value for a sufficiently
small neighborhood where the solution remains finite. Exponentials defining
`L`, `alpha`, and row normalization have no zeros. These facts make the full
three-row boundary map analytic, and the nonzero determinant above invokes
the analytic implicit-function theorem for the final C4 preparation.

For clarity about the first-order tangent, the homogeneous closed de Sitter
time factor satisfies

    Q_tt + 3 sqrt(k) tanh(sqrt(k)t) Q_t + mu Q = 0,
    Q(0)=1, Q_t(0)=0,
    Q_tt(0)=-mu, Q_tttt(0)=mu(mu+6k).

The factor is `mu(mu+6k)`, not `mu(mu+3k)`. The physical linear lift is
`(delta A,delta ell,delta Phi)=(psi,-2psi,f)Q`. Its scalar wall defect at
every time is

    Q [f_s+2T psi-c_i f] = 0.

Its fourth-time defect is the same vanishing bracket times `mu(mu+6k)`.
This also supplies the third-jet argument ensuring that the old correction
has zero first epsilon derivative. The full boundary map therefore has the
candidate tangent `(A(0)'(0),b0'(0),b1'(0))=(psi(0),0,0)=(1,0,0)`.
Invertibility makes that tangent unique. Both fifth-jet controls begin at
order epsilon squared, and the family's first-order proper-separation change
is still `-2 integral psi ds`, the certified nonzero physical overlap.

This establishes a local analytic Cauchy-data family with the original
constraints, walls and their time compatibility through order four. It does
not assert all-order boundary compatibility, a hyperbolic existence interval,
nonlinear instability evolution, horizon formation, or any global endpoint.

## Prospective quantitative corroboration and explicit radius

The bounded numerical corroboration should enclose the background and all
three first-variation columns over the complete inherited root/event
intervals, with direct and flux equations, outward arithmetic, validated
cell remainders and complete event-time coverage. Independent endpoint dual
Taylor evaluation of the original time equations should overlap the reduced
rows, retaining `c0,c1`. All reported inverse bounds must be outward bounds
on the whole interval matrices. No finite-difference determinant is a proof.

The proposed radius route is mathematically adequate if its stated majorants
are actually established. In the shifted chart `a=A(0)-epsilon`, the full
map has `F(0,0)=0` and `F_epsilon(0,0)=0`. For the proposed complex polydisc
radius `r0=2^-4096`, a proved bound `sup ||F||_infinity <= M=2^512` and a proved
`||J^-1||_infinity <= 2^64` leave substantial slack at
`delta=2^-9216`: the proposed contraction bound is `2^-441`, and the stated
quadratic self-map remainder divided by delta is `2^-443`.

The essential, still prospective premises are the complete complex-polydisc
profile and spatial-jet bounds, the metric nonescape/Gronwall comparison,
and the full normalized three-row map bound. Bounds on real sampled solutions
alone do not prove them. The preparation majorant must include old Hermite
coefficients, `H0,H1`, endpoint lapse factors and all spatial derivatives
needed through fifth order. A value-plus-deviation majorant keeps small
parameter powers explicit. The row-map Cauchy estimate must specify its
norm, dimension, convergence margin and shifted coordinates. Exact rational
arithmetic can check the final inequalities without integrating an outcome.

If these majorants are proved and the finite gates pass, an explicit tiny
radius is a genuine conservative witness. It does not certify the much
larger amplitudes sampled in the predecessor. If any premise is unresolved,
the justified conclusion is the qualitative local theorem above, with an
unspecified radius, not a relaxed or inferred quantitative certificate.
