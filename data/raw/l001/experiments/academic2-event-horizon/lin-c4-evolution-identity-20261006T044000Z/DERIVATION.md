# Identity of the exact prepared D1 family

## Which objects may be identified

An exact physical Cauchy family, its finite polynomial approximation, conformal
grid samples and finite-resolution numerical time histories are distinct.
This packet identifies the first through its defining equations and quantifies
the approximation of the second/third where validated bounds are available.
It does not turn a numerical trajectory into a continuum spacetime theorem.

The common action is the canonical five-dimensional Einstein-scalar theory,
R_ab=Phi_a Phi_b+(2/3)V g_ab, Box Phi=m2 Phi, with
V=-6+m2 Phi^2/2 and the two pure-quadratic action-derived walls. The exact six
rational action literals are compared in BINDINGS.json; gamma=20. The original
wall normalization and curvature k remain fixed, not refitted. The independent
spatial-evolution reader checks these same Ricci/scalar equations rather than
using a phenomenological response model.

## Background and normalized mode

Hold the same exact central static background a*, D*, k* fixed. The historical
static certificate selects the unique root in its specified central box.
The numerical preparation solves that same background boundary problem; its
saved a,D are approximations, not new exact model parameters. The neighborhood
certificate quantifies a separate family of backgrounds and is not a license
to replace the central one by an arbitrary nearby member.

The two source implementations have identical regular differential equations
for W,H,Phi,T,E=exp(-W),psi,f,g=f_s, the same launch constraint and psi(0)=1.
At the upper wall F(mu)=g+2T psi+gamma f/2. Inherited signs give existence on
[-33/25000,-131/100000]. For the same fixed background and event, the new
variational equations propagate u=psi_mu,v=f_mu,w=g_mu and test F_mu<0 uniformly.
If this passes it supplies uniqueness in this bracket; launch normalization
then selects one exact physical mode. It says nothing about other spectral
bands. The numerical polynomial comparison carries the full certified source
uncertainties rather than treating the saved approximate seed as exact.

## Nonlinear completion, including backreaction

Both exact targets define ell=-2 epsilon psi and
Phi_epsilon=Phi+epsilon f+C7+b0 H0+b1 H1. C7 is the unique degree-seven Hermite
polynomial preserving endpoint scalar values and second coordinate derivatives
while imposing the same nonlinear first/third derivative targets. The two
degree-eleven shapes are s^5(D-s)^6/(120D^6) and s^6(s-D)^5/(120D^6).
Both have vanishing endpoint jets through fourth order and unit own-wall fifth
jet. Equality follows from their Hermite constraints, not a polynomial fit.

In both constructions the full metric satisfies

    A_ss=ell_s A_s+k exp(2ell-2A)+2 exp(2ell)
         -m2 exp(2ell) Phi_epsilon^2/6-Phi_epsilon,s^2/6-2A_s^2.

The correction coordinates are exactly (a,b0,b1), with A(0)=epsilon+a.
The certified centered variables w=A-W-epsilon psi and v=w_s are an exact
change of variables in this equation. The already independently derived
centered equation and root-equivalent endpoint reduction retain every nonlinear
curvature and scalar term. The three defining rows are upper Israel and the
two scalar fourth-time wall rows; all three correction responses remain coupled.
The connected certificate supplies uniqueness in the common correction box for
every exact epsilon in [-1/200000,1/200000]. A numerical coefficient vector in
that box is not automatically the root: this packet uses the validated root
image to give its distance, not overlap as proof.

## Why the conformal lapse is not a different physical completion

See INDEPENDENT_IDENTITY_NOTES.md and its 15 independently implemented symbolic
checks. With q=q_s=q_ss=0 at a wall and B=A+q, the exact scalar-row identity is

    R4_conformal=R4_material+4 eta R2_material
        +exp(2A)[5 Phi_ll+(16 A_l-c)Phi_l-4m2 Phi] D2,

where c=sigma gamma/2, eta=ell_TT-A_TT+k and D2 is the conformal second-time
temporal-minus-angular Israel defect. The prescribed third lapse jet sets D2=0
with positive coefficient exp(2A-3ell). The fifth lapse jet sets the analogous
fourth-time Israel difference to zero with positive coefficient exp(4A-5ell).
It does not enter the scalar fourth-time row. On the same constrained C2 data,
the scalar C4 zero sets therefore agree. The complete lapse Hermite convention
is retained; no physical scalar jet or correction variable is adjusted.

This is an explicit finite-jet/gauge bridge, not an assumption that changing
the lapse cannot affect wall compatibility. It also does not prove all-order
boundary compatibility or existence of a global coordinate chart.

## Initial coordinate, normals, clocks and observables

Put x(s,epsilon)=integral_0^s exp(ell-B) ds. Finite real fields give x_s>0, so
this is a smooth increasing initial spatial diffeomorphism onto [0,X(epsilon)].
Then exp(2B)dx^2=exp(2ell)ds^2; the angular radius exp(A)/sqrt(k), scalar,
K_ij=0, Pi=0 and zero additional collapse field are unchanged. The outward
normal is -sigma exp(-ell)partial_s=-sigma exp(-B)partial_x, with sigma=+1
below and -1 above. Proper separation is invariant; coordinate length X varies.

At each wall q=0, so the initial material and conformal lapse agree. Their
subsequent coordinate times need not agree. The physical clock is obtained
from the actual lapse: d tau=exp(B)dt, sigma_clock=tau/exp(W_wall). The initial
normalized rate is exp(A_wall-W_wall), not necessarily 1 at nonzero epsilon.
The fixed-x mode includes the spatial relabeling, and a fixed normalized-grid
coordinate adds the change in X. The native tangent (psi,-2psi,f) must not be
compared directly to fixed-grid array differences without that pullback.

For the second-order construction, U=U0+epsilon U1+epsilon^2 U2, where U2 is
half the second derivative. Its pullback z=x X0/X(epsilon) and r=X0/X(epsilon)
are differentiated along this same exact family. Its inverse proper-clock
term gives Q2=Phi2(sigma)-Phi2(0)-I1(sigma)Phi1_t(sigma). This is a coefficient
identity; a finite history is not literally its quadratic truncation.

## What the validated comparison does and does not bound

For each accepted spatial enclosure cell [s_i,s_i+h] and D* in [Dlo,Dhi],
the native polynomial representing the same normalized u is evaluated on

    s_native in [s_i D_native/Dhi, (s_i+h)D_native/Dlo] intersect [0,D_native].

Every overlapping native polynomial segment is included. Differences from
the whole validated cell enclosure therefore bound the fields at each common
u, including uncertain endpoint location. Source/mode uncertainty, exact
polynomial decimal storage, root-coefficient uncertainty and numerical shape
differences are retained. Interval dependency and cell widths can make these
bounds much coarser than observed discretization changes; that must be visible.

The signed root-image intervals enclose the exact (a,b0,b1), and the unchanged
spatial Hamiltonian flow encloses their complete material fields. A separate
80/100-decimal replay checks the six already-evolved conformal grids and gives
positive whole-cell bounds for the represented coordinate polynomial derivative.
This replay shares the inherited gauge/map constructor but independently
evaluates saved field polynomials; it is not advertised as a second independent
continuum solver. Material-field bounds do not automatically bound the exact
completed lapse, inverse coordinate map, or later evolution errors. Those
limits remain explicit wherever no validated map bound has been supplied.

Existing amplitude strings are treated as exact stored decimals and compared
to the exact targets. A tiny nonzero storage offset is an approximation term,
not a new exact target or an enlargement of the certified interval. The larger
signed 1e-5 cohort is excluded. No time integration is performed here.
