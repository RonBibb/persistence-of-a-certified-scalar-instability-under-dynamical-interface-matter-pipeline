# Fixed curved-candidate scalar–geometry stability test

Frozen before scientific spectrum evaluation, 2026-09-29. The inherited candidate and the six model parameters in EXECUTION_REQUEST.md remain fixed. No parameter rescue, donor experiment or other research line is included.

## Action and physical problem

The doubled-cover action is the canonical 5D Einstein–scalar action, with gravitational coefficient 1/2, Lambda5=-6, bulk potential m_bulk^2 Phi^2/2, m_bulk^2=.41, and single wall actions tau_i=lambda_i+gamma(Phi-v_i)^2/2. kappa5=ell=1. The fundamental interval has inward signs sigma_a=+1 and sigma_b=-1. Its background is a^2(z)[gamma_k+dz^2], Ric(gamma_k)=3k gamma_k. The action provenance is source-snapshot/brane-horizon-phase-structure/MODEL_V1.md; the candidate is independently static, unlike the historical momentarily stationary selector.

Use scalar longitudinal perturbations delta g_zz=2a^2 N q, delta g_munu=2a^2 psi q gamma_munu and delta Phi=f q, with Box_gamma q=mu q. Generic scalar harmonics obey N=-2psi. Define A=a'/a, S=Phi', Vp=a^2 m_bulk^2 Phi, B=Vp-4AS and lambda=mu+4k. An undivided, regular bulk system is

    psi' = -2A psi - S f/3,
    f' = p,
    p' = -3A p + (a^2 m_bulk^2-mu+2S^2) f
         + (12AS-4Vp) psi.

The remaining Einstein constraint is

    C = S p - B f + (2S^2-3mu-12k) psi = 0.

It propagates as C'=-2AC using the background equations. No division by S occurs. At S=0 this enforces -S' f-3lambda psi=0. The scalar field equation used as the third ODE follows directly from variation of the canonical action; it is also an independent residual for the two-field spectral system.

At each coordinate-fixed wall the physical finite-stiffness condition is

    p+2S psi = sigma a gamma f/2.

The perturbed Israel trace follows from the momentum constraint and background junctions. Traceless Israel fixes longitudinal brane bending to zero for generic harmonics without brane matter anisotropic stress. Coordinate-fixed endpoints do not fix the physical separation: delta D/q=-2 integral a psi dz. Exceptional de Sitter harmonics with vanishing traceless Hessian are discussed separately; a mode with generic harmonics and nonzero delta D is sufficient for instability.

The regular doubled-cover kinetic coefficient is Z=2 integral a^3(f^2+6psi^2) dz. For a nonzero smooth physical mode Z>0. Wall potentials have no tangential derivative terms. This tests a positive-kinetic scalar tachyon, not a ghost inferred from a singular discretized mass matrix. Other gravitational sectors and the independent collapse scalar are not claimed tested.

Physical growth on an expanding flat de Sitter chart obeys qddot+3H qdot+(p_com^2 exp(-2Ht)+mu)q=0, H=sqrt(k). A resolved mu<0 gives late growth exponent s/H=sqrt(9/4-mu/k)-3/2. Numerical lambda<0 is not the required criterion: subtract 4k to obtain mu. On a brane proper time rescales both H and s by 1/a_wall.

## Numerical methods frozen before evaluation

1. Primary regular two-field generalized Chebyshev pencil, Lobatto N=33,49,65,97 on the unchanged conformal interval. Momentum is imposed at all nodes; the undivided Einstein constraint is imposed in the interior; scalar Robin replaces constraint rows at the two walls. Singular-pencil infinite eigenvalues are algebraic and not physical. Retain all finite eigenvalues, not just a favored root. Report real candidates in mu in [-1,1] and compare their lowest stable branch across grids. Very large or complex nonconvergent roots are unresolved discretization branches, not physical instabilities.
2. Independent continuum-style shooting of the regular three-field ODE with its lower Einstein constraint and finite Robin. With psi(a)=1, f(a)=3(mu+4k)/(c_a S_a-B_a), p(a)=c_a f(a)-2S_a, c_a=a_a gamma/2. Verify that the denominator is nonzero before using this normalization. Solve the upper scalar Robin determinant around each low converged spectral candidate. DOP853 tolerances rtol=2e-9,2e-11,2e-13, corresponding atol=rtol*1e-3. A finite initial bracket half-width max(1e-5,0.05*abs(mu)) may widen at most three times by factor two; no unlimited scan.
3. Evaluate off-grid momentum, Einstein, scalar-KG and both wall residuals using spectral polynomial derivatives on 1001 points. Independently compute the shooting constraint on 2001 points. Retain eigenfunctions and physical separation/kinetic integrals, including scalar-turn matching values.
4. Repeat finest shooting on the immediately preceding fine background (already bound by the inherited fine-collocation contract) to measure background representation sensitivity. Recompute the background and selected mode with arbitrary-precision shooting if binary64 comparisons do not settle the sign. Otherwise perform a 40/60-digit fixed-step RK4 integration comparison on the same retained background polynomial, with step refinement; this checks arithmetic and shooting formulation, not a higher-precision continuum background.

Controls run before science: (i) de Sitter pure-gravity radion, psi=a^-2, f=0, mu=-4k, with analytic AdS warp and a positive norm/nonzero delta D, using the candidate k and L; (ii) flat pure-gravity limit k=0 at the same L, the massless separation mode; (iii) independent flat scalar finite-Robin interval with control gamma=2, L=2 and m_bulk^2=.41, whose lowest wave number satisfies q tan(qL/2)=gamma/2, testing derivative orientation and the scalar boundary signs. These control parameters do not alter the scientific background. Verify the exact constraint-propagation identity symbolically.

## Decisions and fixed gates

- Controls: analytic equation/constraint/wall normalized residual <=1e-10; numerical pure-gravity integration relative profile error <=1e-8; flat scalar Robin eigenvalue error <=1e-8. Failed controls stop science until an explicitly recorded implementation correction passes; criteria stay fixed.
- Physical eigenmode: real to relative/absolute imaginary threshold 1e-8 max(1,abs(mu)); last two spectral masses and finest two shooting masses agree within 1e-7 max(1,abs(mu)); independent methods within the same bound; normalized bulk/constraint/wall residuals <=1e-6. Do not accept a mode solely because the pencil residual is small.
- Sign resolution: abs(mu)>100 times the maximum measured spectral, shooting-tolerance, background and arithmetic mass sensitivity, and abs(mu)>1e-8. These are finite numerical sensitivity requirements, not rigorous error enclosures.
- A positive-kinetic accepted negative-mass mode with nonzero separation response establishes a physical linear instability and ends this candidate's test. Retain additional computed roots descriptively; no retuning or subsequent evolution follows.
- A stability pass requires excluding negative physical modes, including exceptional modes and finite-wall modes; a limited positive search alone is insufficient. If no accepted negative mode is found and completeness is not justified, classify unresolved rather than stable.
- Technical failure or failure to derive the physical operator is inconclusive.

## Resources, preservation and records

All new files stay in this successor; old inputs are read-only and hash-bound. Linux shared output is /media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-curved-stability-2026-09-29. Use the existing codex-precision-noble-py312 runtime, one BLAS/OpenMP thread per process and at most four independent workers. Per spectral/shooting case limit 300 seconds, precision case 900 seconds, successor storage cap 100 MB. Individual jobs are designed below one hour; results are atomically saved per case. Any extension exceeding one hour needs exact-resumption checkpoints and source/input compatibility checks before launch. No deletion, installation or unrelated process changes.

STATUS.json distinguishes formulation, controls, numerical launch and interpretation. Source and specification hashes are bound in CONTRACT.json before controls or science launch. Formulation/implementation amendments, if required by a failed control, are recorded explicitly rather than silently altering the frozen design.

Primary comparison: Frolov and Kofman, Physical Review D 69, 044021 (2004), arXiv:hep-th/0309002, equations (8) and (14); their divided formula is not used at the scalar turn. The undivided equations and action kinetic sign are independently derived for this action in the accompanying analysis notes.
