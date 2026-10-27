# A growing perturbation with finite spatial norm

Status: proposed analytic physical corollary for independent review. This strengthens the homogeneous-mode example by constructing real smooth wave packets with finite spatial norm at every finite time. It remains a linear perturbation statement.

Let μ<-4k be any eigenvalue supplied by the regular theorem. Write `H=√k` and

    ν=√(9/4-μ/k)>5/2,
    σ=(ν-3/2)H>H.

On the spatially flat de Sitter patch, the Fourier amplitude of `Box_γ Q=μQ` obeys

    q_p''+3Hq_p'+(|p|²e^(-2Ht)+μ)q_p=0.        (1)

Set `z=(|p|/H)e^(-Ht)` and `q_p=e^(-3Ht/2)y(z)`. Direct substitution gives

    z²y''+zy'+(z²-ν²)y=0.

Choose the real Bessel solution

    q_p(t)=e^(-3Ht/2)Y_ν((|p|/H)e^(-Ht)).      (2)

Let A(p) be a nonzero real even C∞ function with compact support in an annulus `0<p_min<=|p|<=p_max<∞`. Define Q(t,x) by the inverse Fourier transform of `A(p)q_p(t)`. Equation (1) is satisfied mode by mode, and the compact smooth Fourier support justifies differentiating under the transform. At every finite time, `A(p)q_p(t)` is smooth and compactly supported, so Q(t,·) is a real Schwartz function. In particular it has finite comoving L² norm, finite spatial-derivative L² norms, and finite proper spatial L² norm because the latter differs by the finite factor e^(3Ht) at each fixed time.

For every real ν>0, the leading small-argument expansion is

    Y_ν(z) ~ -[Γ(ν)/π](2/z)^ν    as z→0+.

It holds for integer as well as noninteger positive ν; any logarithmic subleading terms at integer order do not change this leading limit. Since p stays in a compact annulus, the expansion is uniform over the support of A. Therefore

    e^(-σt) A(p)q_p(t)
       → B(p):=-[Γ(ν)/π](2H/|p|)^ν A(p)

uniformly and in Fourier L² as t→∞. Plancherel gives

    e^(-σt) Q(t,·) → Q_∞(·)=FourierInverse[B]
       in comoving L²,

where Q_∞ is nonzero because A is nonzero and the multiplier never vanishes on its support. Compact support also gives Fourier L¹ convergence and thus uniform spatial convergence of the rescaled packet. The comoving L² amplitude consequently grows asymptotically like `e^(σt)||Q_∞||₂`, with σ>H.

Multiplying this Q by the theorem's nontrivial regular radial profile supplies an admissible linear scalar–metric perturbation. Its radial kinetic norm is positive. A finite packet removes reliance on an infinite-volume homogeneous Fourier mode; it does not imply a finite conserved positive total perturbation energy, since the mode is tachyonic and de Sitter time evolution is not a static energy problem.

The asymptotic statement is about the mathematical linearized equation. A perturbation of nonzero initial amplitude eventually leaves the linear regime; no nonlinear continuation or causal fate is inferred. Wall proper-time growth-to-expansion ratios remain σ/H as in ENDPOINT_AND_GROWTH_COROLLARIES.md.
