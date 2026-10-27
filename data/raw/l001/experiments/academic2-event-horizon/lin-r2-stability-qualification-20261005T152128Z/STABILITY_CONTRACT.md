# Proper-distance scalar/radion qualification on the certified R2 neighborhood

## Purpose and authority

This is one bounded numerical qualification/sensitivity experiment. It follows
the successful R2 continuous static theorem and the completed central-branch
audit in this packet. It reconstructs the background directly from the D1
launch equations, avoiding the archived conformal background interpolant as a
coefficient source, and independently solves its physical growing mode.
The old source and results remain read-only. Manuscript and P16 work are held.

The nine points are the Cartesian product of lower endpoint, exact midpoint,
and upper endpoint of each R2 parameter interval (v1, lambda_b). Run the center
first, then the four axial points, then the four corners. No point is moved or
added after outcomes. The six action parameters use D1's exact-binary64
interpretation; v1 and lambda_b alone take these declared values.

## Background and physical fluctuation equations

Use proper distance s with lower warp exp(W(0))=1, H=W_s, T=Phi_s.

    W_s=H; H_s=-T^2/3-k exp(-2W); Phi_s=T;
    T_s=m2 Phi-4HT; z_s=exp(-W).

At launch a=Phi(0), H0=-(lambda_a+gamma(a-v0)^2/2)/6,
T0=gamma(a-v0)/2, k=H0^2-1-T0^2/12+m2 a^2/12.
Find the first downward upper Israel event H-tau_b(Phi)/6=0 before s=2,
then zero its scalar mismatch T+gamma(Phi-v1)/2 using the fixed R2 a-tube.

With Box_gamma q=mu q, integrate the regular proper-coordinate equations

    psi_s=-2H psi-T f/3; f_s=g;
    g_s=-4H g+(m2-mu exp(-2W)+2T^2)f+(12HT-4m2 Phi)psi.

The remaining Einstein constraint is

    C=T g-(m2 Phi-4HT)f+[2T^2-3(mu+4k)exp(-2W)]psi=0.

Its exact propagation is C_s=-4HC. Wall conditions are
g+2T psi=sigma gamma f/2, sigma_lower=+1, sigma_upper=-1.
For lower psi=1, use f=3(mu+4k)/B0,
B0=gamma T0/2-(m2 Phi0-4H0 T0), g=gamma f/2-2T0.
Require |B0|>1e-12. No division by T occurs, including through its turn.

Find a root only in the predeclared physical-mass bracket
[-0.0015,-0.0011], with no expansion. Z=2 integral exp(2W)(f^2+6psi^2) ds
and deltaD=-2 integral psi ds. The growth rate is
s_growth/H_dS=sqrt(9/4-mu/k)-3/2. Report mu and lambda=mu+4k separately.

## Numerical controls and fixed gates

Each point has two fresh background-plus-mode solutions using DOP853:
rtol=2e-11, maximum background step 2/64; and rtol=2e-13, step 2/128.
Atol=rtol*1e-3. Mode max step is its interval/64 or /128. Scalar shooting
uses xtol=5e-17, rtol=1e-14; mass shooting xtol=5e-16, rtol=2e-14.
Both use at most 80 iterations. Saved samples: 2001 uniform proper nodes.

Before science: symbolic propagation identity, exact vacuum de Sitter mode
(mu=-4k) and flat massless mode, and analytic finite-Robin scalar control;
analytic residual gate 1e-10, vacuum numerical profile gate 1e-8, and local
polynomial differentiation control 1e-20 using Linux extended precision.

For every accepted case:

- Positive curvature, root inside the frozen R2 root tube, admitted first
  upper-wall event, and both full background walls within normalized 1e-8.
- Independently differentiate saved background fields (including endpoints):
  normalized ODE and first-integral maxima <=1e-8. This verifier never uses
  the primary ODE RHS as an equation derivative.
- Independently differentiate saved psi/f on 1001 and 2001 nodes with 9-point
  local polynomials. Momentum, Einstein constraint, scalar KG and both Robin
  walls must have normalized residual <=1e-6 at every saved test node.
- Preserve the scalar turn. Its finite relation
  m2 Phi_star f_star+3(mu+4k)exp(-2W_star)psi_star=0 must meet 1e-6.
- Paired masses agree within 1e-7; |mu|>1e-8 and |mu|>100 times their
  paired numerical mass discrepancy. Physical instability requires mu<0,
  Z>0 and |deltaD/sqrt(Z)|>1e-6.
- |mu+4k| must exceed 100 times its paired discrepancy, or flag exceptional
  mass-sector separation unresolved. This is separate from the mu<0 test.

Central branch qualification additionally requires root/D/k membership in the
central D1 enclosures, |new mu-old mu|<=1e-7, proper and conformal separations
within 1e-7 relative, and a full-field comparison within scaled 1e-7 between
(W, exp(W)H, Phi, exp(W)T) and archived (W,A,Phi,S) at z(s).
The legacy interpolant is used only for this comparison. New invariant
overlap and norm are verified independently by Simpson integration.

Use the existing verified Fornberg differentiation helper but independently
implement the proper-coordinate equations. Lift binary64 constants exactly
into extended precision, rather than reinterpret their decimal spellings.

## Interpretation

All nine passes establish resolved numerical persistence at those nine points,
plus a direct numerical central-background link. They do not establish uniform
spectral instability across the continuous parameter box. No finite sign
search establishes full stability or a lowest eigenvalue. Root, residual,
normalization or bracket failures mean unresolved qualification at that point;
all outcomes remain in the record. No gate is changed after results.

R2 remains a rigorous static certificate. This new spectrum remains numerical:
there is no interval perturbation-operator enclosure or rigorous eigenvalue
bound for the exact background, and no nonlinear, causal or initial-data claim.

## Execution and recovery

Linux only, one process, one BLAS/OpenMP thread. Authenticate source, contract,
runtime and inputs before science and on resume. Publish an immutable receipt
and NPZ after each case; completed cases are reused only if all hashes match.
Atomically checkpoint the exact pending/completed case queue after each case;
status is informational and read-only for monitors. A lost in-flight IVP is
replayed deterministically from the prior case boundary, never silently
interpolated or promoted. Each case has a 600-second cap; no known long
integration is launched. A terminal packet is never restarted.
