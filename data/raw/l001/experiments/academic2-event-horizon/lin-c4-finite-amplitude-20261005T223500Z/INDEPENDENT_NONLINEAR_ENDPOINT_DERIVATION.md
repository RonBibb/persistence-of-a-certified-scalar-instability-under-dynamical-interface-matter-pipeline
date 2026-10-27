# Nonlinear endpoint discriminator and a root-equivalent map

Status: exact symbolic derivation PASS. No nonzero-amplitude D1 solve has been
performed. The scoped targets remain only epsilon = +/-5e-6, subject to a new
prospective freeze and interval certificate. No finite-amplitude existence is
claimed by this algebra alone.

## Answer to the curvature-cancellation question

Curvature **does survive** the nonlinear fourth-time scalar Robin condition,
even after the Hamiltonian, Israel, scalar Robin and exact second-time scalar
Robin conditions are imposed. The proper-coordinate normalized row contains
`-24 t q^2`; setting `t=c(Phi-vwall)` and `p=pwall` does not remove it.
Consequently the exact linear row reduction from the local C4 theorem must
not be extrapolated into nonlinear triangularity.

There is nevertheless a useful exact centered expression. Its explicit
metric-value feedback is quadratic about static D1. It can be used in a
root-equivalent nonlinear map without discarding any metric response.

## Coordinate and time-jet conventions

For this local derivation choose physical distance `l` as the spatial
coordinate on the initial reflection slice. Write

    p=A_l, t=Phi_l, u=Phi_ll, v=Phi_lll,
    w=Phi_llll, z=Phi_lllll,
    q=k exp(-2A), c=sigma gamma/2, m=m2,
    V=-6+m Phi^2/2, alpha^2=exp(2A).

The transformation is fixed in time using the initial L, so initial ell and
all its spatial derivatives vanish in these coordinates. Its second and
fourth TIME derivatives are not set to zero. The original lapse remains
`alpha=exp(A)/cosh(sqrt(k)t_time)`. In particular, the closed-chart terms in
the original time equations are retained.

The Hamiltonian gives

    p_l = q-2p^2-t^2/6-V/3.

All normal derivatives of this bulk identity may be taken. In contrast, the
endpoint-only Israel and Robin conditions are imposed only AFTER deriving
the local polynomial; they are not differentiated in the normal direction.

Define

    r=p^2-1-t^2/12+m Phi^2/12,
    S=u+4pt-m Phi, Delta=q-r.

The exact second time jets satisfy

    A2/alpha^2 = 2r-q,
    ell2/alpha^2 = 4 Delta,
    Phi2/alpha^2 = S,
    ell2+2 A2 = 2k.

Discarding ell2 in this derivation would incorrectly remove physical nonlinear
terms and change the preparation.

## Second-time scalar condition and full reduced fourth row

The normalized second-time row is

    R2/alpha^2 = v+(6p-c)u
        +(4p^2-m-t^2-2V/3-4cp)t-(2p-c)m Phi.

Let `v_required(p)` be the negative of the remaining terms, so exact R2 sets
`v=v_required(p)`. After this substitution, the exact fourth-time scalar row is

    R4/alpha^4 = z+(16p-c)w+P0(p,Phi,t,u,c,m)
                   +q(48tr-12cS)-24tq^2.                 (1)

Thus its highest proper fifth-jet coefficient is exactly one. The coefficient
of q squared is exactly `-24t`, and the coefficient of q is `48tr-12cS`.
These statements hold before imposing scalar Robin; afterward t is simply
replaced by `c(Phi-vwall)`.

Here is a complete, compact specification of the q-independent polynomial P0,
without omitted terms. Define the polynomial differential operator

    D0 = (-r-t^2/3) partial_p + t partial_Phi
            +(m Phi-4pt) partial_t,
    u_ref=m Phi-4pt,
    w_ref=D0^2 u_ref, z_ref=D0^3 u_ref,

and the explicit polynomial

    C1 = -(3 Phi^2 c m + 2 Phi^2 m p + 66 Phi m t
           +36 c^2 p -324 c p^2 +11 c t^2 -36c
           +24mp +1008p^3 -190pt^2 -24p)/3.

Then

    P0 = -z_ref-(16p-c)w_ref
           +(C1+12cr)S-(32/3)t S^2-24t r^2.              (2)

This finite polynomial definition is exact. Apply D0 treating p, Phi and t as
independent variables, with m and c constant; only afterward substitute wall
values. The machine-readable receipt also gives the fully expanded P0, its
coefficients grouped by powers of u, and explicit w_ref and z_ref polynomials.
These reference jets are algebraic functions of the CURRENT endpoint values;
they do not replace the certified background, curvature or wall by a fitted
static point.

Equivalently, (1) is the exact centered identity

    R4/alpha^4 = (z-z_ref)+(16p-c)(w-w_ref)
                  +C1 S-(32/3)t S^2
                  -12c S Delta-24t Delta^2.              (3)

On static D1, `S=Delta=0`. The derivative with respect to q is
`-12cS-48tDelta`, which vanishes there. This explains the zero metric-VALUE
coupling in the earlier linear Jacobian. It does not eliminate that coupling
at finite amplitude. In particular, replacing actual q by r would delete the
last two terms of (3) without justification.

## Off-Israel defects and exact root equivalence

The actual analytic preparation fixes the third proper scalar jet using the
target Israel slope `pstar=pwall=-sigma U(Phi)/6`, not an arbitrary actual
metric slope. Put

    J=p-pstar,
    v=v_required(pstar).

The second row then factors exactly as

    R2/alpha^2 = J [6u+{4(p+pstar)-4c}t-2m Phi].

Let R denote the FULL Hamiltonian-eliminated fourth polynomial before imposing
R2, with v an independent proper jet. The symbolic calculation proves the
polynomial identity

    R(pstar+J,q,Phi,t,u,v_required(pstar),w,z)
      -R(pstar,q,Phi,t,u,v_required(pstar),w,z)
        = J K(J,pstar,q,Phi,t,u,w,c,m).                  (4)

The full polynomial K is in the receipt. Its q dependence is only linear,
with coefficient

    partial_q K = 8[-4Jt+5m Phi+4ct-8pstar t-15u].

Equation (4) holds with the SAME actual `q=k exp(-2A)` on both sides. No q
substitution, no normal derivative of a wall identity, and no vanished-Israel
assumption was used to obtain its exact divisibility.

Return to the original coordinate s, where `P=A_s` and `p=P/L`. The first map
row is `I=P-L pstar`. The normalized original scalar row is `L^5 R`. Define
the transformed scalar row by evaluating the eliminated polynomial at
`p=pstar`, holding q and the prepared scalar jets fixed. Then

    F4_original-G4 = L^4 I K.                            (5)

The lower Israel condition is imposed in the launch, so its scalar row is
unchanged. For the upper wall, keeping I as the first equation makes the two
full three-variable systems exactly root-equivalent in both directions.
The transformation is a unit-triangular analytic row operation; at a root it
also preserves Jacobian nonsingularity. It does not require division by I or
J. Do not evaluate K numerically as a small difference divided by J; use the
polynomial if it is needed at all. The transformed map itself uses (1) or (3).

## Exact transformation of the fifth jet

Let `ell_j=partial_s^j log L` and `Phi_j=partial_s^j Phi`. Define

    P1=Phi_1,
    P_(n+1)=partial_s P_n-n ell_1 P_n,
    partial_l^n Phi=L^-n P_n.

In particular,

    P4 = Phi_4-6ell_1 Phi_3+(11ell_1^2-4ell_2)Phi_2
           +(-6ell_1^3+7ell_1 ell_2-ell_3)Phi_1,

    P5 = Phi_5-10ell_1 Phi_4+(35ell_1^2-10ell_2)Phi_3
           +(-50ell_1^3+45ell_1 ell_2-5ell_3)Phi_2
           +(24ell_1^4-46ell_1^2 ell_2+7ell_2^2
                         +11ell_1 ell_3-ell_4)Phi_1.

The original normalization is `R4/(alpha^4/L^5)`, namely `L^5` times the
proper normalized row. Since each H_i changes only its own fifth coordinate
endpoint jet by one while preserving jets through order four, the EXPLICIT
coefficient of b_i is exactly one after transforming back. Thus the transformed
row can be written `b_i+W_i(epsilon,q_i; exact background/mode data)`.

This is not a statement that its complete unknown-space Jacobian has diagonal
one: q_upper depends on the metric IVP, hence on A(0) and both b columns.
q_lower depends on A(0). That implicit response, including the factors
`-12cS-48tDelta`, must be propagated or enclosed in a finite-amplitude
Krawczyk/Newton proof.

## Corroboration and finite-certificate risks

The independently written differential-algebra derivation was compared with
the sealed predecessor's actual `time_jets.py` functions, using exact SymPy
scalar arithmetic in place of their numeric scalar adapter. Generic proper
jets satisfy the Hamiltonian and its derivatives; all variables remain
symbolic. Both fourth-Robin and fourth-Israel polynomials agree identically.
The latter also verifies `I4/alpha^4=-S(R2/alpha^2)` when scalar Robin holds.
No background or nonzero-amplitude trajectory was integrated.

All 12 exact checks pass under Linux SymPy 1.14.0. Source hashes are recorded
in `INDEPENDENT_NONLINEAR_ENDPOINT.json`; the independent derivation source is
`c9bc6d6780d77457516c3463b91243d6f581d071612a6d75bc1e59b3bc2e8ba2`.

For the finite certificate, retain the full certified background, mass/root,
event and mode uncertainties. The same implicit exact background and mode
must be used in every cancellation. Zero background or first-order residuals
may be removed analytically only using identities for the actual certified
static/eigenmode solution, not by declaring an arbitrary interval rectangle
point to satisfy a boundary or spectral condition. Endpoint fifth-jet
identities hold at the exact own/opposite walls. Interval AD must include q's
metric dependence and all off-Israel row transformations. These are source
and error-accounting obligations, not permission to tighten input domains or
to infer either requested finite-amplitude solution before certification.
