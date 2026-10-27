# Independent mathematical audit of the central spectral discriminator

This is a prospective proof audit, not a result certificate. No new physical
calculation was evaluated for this note. The proposed interval calculation is
sufficient under the following explicit conditions.

## Fixed background and intermediate-value argument

Let a_star and D_star denote the same exact static D1 solution certified by
the authenticated existence/uniqueness results. Their retained rational
enclosures A and D are input sets; neither a_star nor D_star varies with the
spectral parameter. The six action parameters retain their exact binary64
rational meanings. Replacing either enclosure by a floating midpoint would
not establish the intended theorem.

Use the prospectively chosen exact rational mass interval
J=[-0.00132,-0.00131]. Let K enclose the launch curvature for A. Verify K>0,
J<0, and J+4K<0. The last condition excludes the exceptional scalar-harmonic
sector without discarding its separately physical vacuum radion example.

The regular proper-coordinate mode IVP starts with psi(0)=1 and
f(0)=3(mu+4k)/B0, g(0)=gamma*f(0)/2-2*T0, where
B0=gamma*T0/2-(m2*Phi0-4*H0*T0). Require 0 not in B0(A). On the compact
certified background interval, its coefficient matrix is continuous and
bounded, affine in mu. Linear ODE existence and continuous parameter dependence
therefore make the real upper-wall determinant

    F(mu)=g(D_star)+2*T(D_star)*psi(D_star)+gamma*f(D_star)/2

continuous throughout J. Outward enclosures F(mu_lo)>0 and F(mu_hi)<0, or
the reverse, holding for all allowed A and D, imply by the intermediate-value
theorem an exact zero for this fixed background at some mu_star in J.
There is no eigenvalue-uniqueness or lowest-mode inference.

Each event-time enclosure must include every time in D intersecting its
validated integration cell. Interval Taylor evaluation with a Picard-contained
remainder is sufficient. A hull of sampled endpoint values alone is not.

## Constraint, walls and physical interpretation

The initial vector satisfies both the lower Robin condition and the remaining
Einstein constraint C=0 exactly. The regular equations give C_s=-4HC, hence
C remains exactly zero. They retain the scalar equation through T=0, without
division by T or a new matching condition. The upper determinant supplies the
remaining scalar wall condition; the trace Israel variation follows from the
momentum equation and the exact background wall junction. In the generic
nonconstant scalar sector, the traceless equation fixes N=-2psi and the
Einstein identities complete the remaining tangential equation.

The physical premises are the declared Einstein–canonical-scalar action,
kappa5=1, its doubled bulk/appropriate Gibbons–Hawking normalization, pure
potential walls of the fixed finite stiffness, and no localized kinetic or
induced Einstein terms. The inspected independent formulation and kinetic
derivations give

    Z=2*integral_0^D exp(2W)*(f^2+6*psi^2) ds,
    deltaD=-2*integral_0^D psi ds.

The nonexceptional longitudinal variables are gauge invariant. Thus psi(0)=1
ensures a nonzero physical profile, and finite continuous fields on the finite
positive-warp interval give finite Z>0. A negative mu_star is a positive-norm
linear scalar instability; it is not a ghost claim or a nonlinear endpoint.

If the full J-strip enclosure additionally yields global psi_min>0, it
certifies a physical separation component. With global W_min,W_max and
absolute profile bounds, explicit sufficient bounds are

    Z >= 12*D_min*exp(2W_min)*psi_min^2 > 0,
    Z <= 2*D_max*exp(2W_max)*(f_abs_max^2+6*psi_abs_max^2),
    -2*D_max*psi_max <= deltaD <= -2*D_min*psi_min < 0.

Failure to close this strip enclosure must be recorded separately from a
successful endpoint eigenvalue-existence certificate. It cannot silently be
reported as a certified separation overlap. No omitted physical action or norm
premise was identified within the declared model above.

## Independent implementation and inspected provenance

The primary E=exp(-W) polynomial flow and the independent exp(-2W) flow use
different right-hand-side representations. The independent engine contains its
own exponential/convolution recurrence, Picard inclusion, and fifth-order
Taylor remainder. Its proof method is drawn from the inspected sealed
`lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay.py`; no
predecessor integration function is imported. The original sensitivity-Newton
source, its R1 wrapper, 32768-step confirmation wrapper, D1 rational result,
and the archived independent fluctuation/kinetic derivations were also read.
The new module supplies separate symbolic launch/propagation identities and
exact synthetic Taylor controls. Final source, input, runtime and recovery
authentication remain prerequisites to numerical proof admission.

The intended new theorem concerns one central static background and this
scalar sector. It gives no continuous parameter-box theorem, complete spectrum,
nonlinear evolution, global initial data, event horizon or P16 identification.
