# Extra eigenvalue near the wall transition

Measure the unique regular scalar eigenvalue in the remaining band at the concave background, keeping V=Phi-Phi²/2+Phi⁴, central (a,H,Phi,T)=(1,-2,0,0), k=3 and r in [-.01,.01]. Physical mu is in the original unnormalized metric, lambda=mu+12. No new physical action or wall potential values/slopes. Hessians alone label the perturbation boundary conditions.

## Frozen numerical test

Use independent integer outward dyadic intervals at 256 fractional bits from the accepted T7 implementation. All integer powers use explicit multiplication. Strict whole-step Euler tube inclusion encloses the exact IVP; n=4096 then 8192 steps center to lower, 2n lower to upper. Background tube rectangle and Hamiltonian checks are retained. Background rates are (3,5,.1,2); reduced f,L rates (1,5), full psi,f,L audit rates (1,1,5). No rate changes after execution.

For lambda>0 eliminate only the nonsingular constraint: K=a²/(3lambda), U=T′, psi=K(TL-Uf). Reduced coefficients are A=2KTU, E=1-2KT², C=V″-mu/a²+4T²/3+2KU², D=-4H-A. Launch f=1,L=kappa_a/2; upper characteristic is L+kappa_b f/2. This normalization differs from the previous psi=1 phase normalization by a sign, not an eigenvalue change. Inherited full-path phase/count theorem establishes at most one remaining-band root; certified opposite signs establish existence without inferring an index from sign alone.

Search endpoints are [-1/5,-1/1000] at equal Hessians kappa_a=kappa_b=9/500=.018. This lies strictly below the certified equal-wall critical interval, and the same inherited injection theorem bounds the remaining-band count by one. Start this test only after T1R2 receives terminal acceptance. Compare its bracket with T1R2 by exact rational interval subtraction and |mu| ratio, without growth-time conversion. Bisection at each level updates only on strict interval signs. Stop at width <=.001; an ambiguous midpoint triggers two quarter-point evaluations, shrinking only if strict signs permit. Maximum 24 iterations and three ambiguous iterations; failure to reach width is TECHNICAL_INCOMPLETE, not mode absence. Never evaluate lambda=0. Coarse and fine brackets must overlap and fine width not exceed coarse width. All tested masses remain in (-12,0).

## Independent equation audit and controls

At fine bracket endpoints independently propagate the full regular system psi′=-2Hpsi-Tf/3, f′=L-2Tpsi, L′=-4HL+(V″-mu/a²+4T²/3)f-2Upsi with constrained launch, at n=16384. Require opposite endpoint signs, overlap of reduced and full residual enclosures at each endpoint, and constraint enclosure containing zero at every endpoint. This is a different equation representation, not a different physical model. The independent reviewer checks the implementation and both brackets before acceptance.

Controls: exact arithmetic corner inclusion and zero divisor rejection; signed constant step and undersized tube rejection; exact central reduced coefficients; reduced and full reconstructed derivative identities on rational points; at mu=0 reconstruct the earlier transfer coefficient residual and require overlap with accepted T4 n=2048. Preserve all failures, source hashes and runtime identity. Pin Linux Python3.12.3 digest from T7. One core including controller and child, thread counts one, 1GiB address-space cap, 590s child/600s wrapper limit, existing global/line/CPU leases and HOLD, no queue or retry. Per-test packet lock and refusal of output overwrite. This finite test has no >1h computation or resume claim.

## Acceptance and interpretation

Accept only after all tube, sign, width, binding, representation, control and independent review gates pass. Record the eigenvalue bracket, not a central floating point as a certified value. The other below-minus-twelve mode persists. No growth-time inference or arbitrary-data dynamical completeness is part of this test.

Before any T2 admission or execution, the resolution was increased fourfold in response to the preserved T1 coarse-level accuracy failure. This is a pre-execution design decision; T2 has no prior result to rescore. The zero-mass anchor uses the configured final level.

Before admission, the search-control ordering correction from T1R2 was applied: successful width after strict quarter-sign updates is recognized before applying the auxiliary ambiguity counter. T2 depends on accepted T1R2, not failed T1R1. No numerical criterion is relaxed.
