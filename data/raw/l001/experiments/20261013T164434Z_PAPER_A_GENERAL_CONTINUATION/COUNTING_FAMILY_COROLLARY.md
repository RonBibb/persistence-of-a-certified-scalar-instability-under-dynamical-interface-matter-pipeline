# Restricted spectral count and compact-family robustness

Status: proposed corollary to GENERAL_THEOREM_PROPOSAL.md, requiring independent review. No new numerical calculation. This concerns real regular modes with shifted mass λ<0 only; it does not count modes with λ>=0 or give completeness of a self-adjoint operator realization.

## Finite odd count on one background

Fix the hypotheses and determinant G of the main theorem. Choose q0 satisfying its strict cone inequalities (6). Those same inequalities hold for every q>=q0. The cone proof therefore gives

    G(-4k-q²,c_a,c_b)>0 for all q>=q0 and all wall pairs.

Thus there are no negative-shifted roots at or below `-4k-q0²`. The uniform auxiliary exclusion gives δ>0 such that there are no roots in `[-4k-δ,-4k]`. All λ<0 roots are consequently confined to a common compact mass interval, strictly separated from both barriers. On that interval, G is analytic in μ, is not identically zero (the endpoint signs already forbid this), and every root is simple by the regular Green identity. There are finitely many such roots. The determinant starts positive and ends negative, and each simple real root reverses its sign; hence their number N is odd and at least one.

As the reciprocal wall pair varies on its connected compact rectangle, N is locally constant. To verify this without assuming spectral completeness, cover the finitely many simple roots at a fixed wall pair by disjoint small intervals on which the mass derivative has one nonzero sign. The implicit-function theorem retains exactly one root in each interval for nearby wall pairs. On the compact complement, the determinant has positive distance from zero; continuity excludes additional roots there. The fixed uniform barriers exclude roots escaping the mass interval. Therefore N is constant on the rectangle.

Ordering the roots `μ_1<...<μ_N` supplies global labels. Simplicity forbids collisions. Every label has the main theorem's analytic local response, strictly negative derivatives in both reciprocal wall coordinates, and a compact continuation to its own DD corner. This strengthens the existence statement to an odd, constant, but uncomputed count of negative-shifted branches. It does not assert N=1, that any given previously certified mode is the lowest mode, or that these are the only modes of the full system.

## Uniform background-family statement

Let θ range over a compact connected parameter set. Suppose the main theorem's exact action/background/sector hypotheses hold for each θ. Assume the intervals have continuous lengths `b_θ>0`; after identifying `s=b_θ x`, `0<=x<=1`, all background and mode-equation coefficients and the proper-distance derivatives entering the main theorem depend continuously on θ, uniformly in x. Require a common positive lower bound for a, and continuity of k and positive baseline Hessians κ_i0. Require the endpoint inequalities (H) strictly at every θ. Compactness then makes their margins uniform; in particular k has a positive lower bound. For smooth conclusions in θ, additionally require a smooth finite-dimensional family of the coefficients and endpoints.

Use `ξ_i=κ_i0(θ)c_i∈[0,1]` to identify all wall rectangles, and use λ as the mass coordinate. Finite coefficient suprema in the cone proof admit one q0 for the entire compact family. The zero-shift auxiliary determinant is strictly negative on the compact product of θ and the wall square, so continuity gives a common δ>0 with no roots for `-δ<=λ<=0`. Thus every family's negative-shifted root is confined to

    -q0² < λ < -δ.

The same local finite-root argument works with continuous θ because the determinant and its μ derivative depend continuously on all parameters. Its finite odd count N is constant on the connected product. Ordered labels give globally continuous eigenvalues and normalized profiles, smooth in θ when the family is smooth and analytic in each fixed-background wall rectangle. The physical masses obey the uniform inequality

    μ_j(θ,c_a,c_b)<-4k(θ)-δ<0.

This is a robustness result conditional on a supplied family of exact backgrounds with the stated margins. It does not construct that family, assert that arbitrary potential changes preserve the background, or turn approximate numerical backgrounds into exact ones. No compactness assumption is silently extended to a noncompact or singular limit.

## Scientific use

The endpoint predicates and coefficient bounds now suffice to establish a protected negative-shifted sector without first solving an eigenvalue shooting problem. A certified family of backgrounds could use this theorem to establish persistence and an odd sector count across that family; locating or quantifying its individual masses remains a separate task. Interior T zeros need not be simple, unique, or separately located for any of these statements.
