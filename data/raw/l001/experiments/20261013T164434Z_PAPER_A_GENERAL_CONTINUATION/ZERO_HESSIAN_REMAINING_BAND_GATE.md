# The zero-Hessian corner controls the remaining tachyon count

Status: proposed analytic comparison and prospective numerical gate for independent review. No determinant or phase at μ=0 has been evaluated. This uses the accepted convex compact nonnegative-Hessian theorem.

The zero-Hessian corner means `κ_a=κ_b=0`, hence `L_a=L_b=0` with `L=f'+2Tψ`. It is not the ordinary scalar Neumann condition f'=0. Use shifted coordinates `c_i=1/(κ_i+1)`, so this corner is (1,1).

## Simplicity and response in the remaining band

For any regular root with `-4k<μ<=0`, λ=μ+4k is positive. The normalized launch remains valid because d<0 throughout the shifted square. The same endpoint nonvanishing argument applies: f_b=L_b=0 would force ψ_b=0 through the constraint since λ≠0, hence all mode data would vanish. Thus the nonzero K parameterization in the nonnegative theorem applies and gives

    G_μ=-Z/(4K a_b⁴)≠0,
    μ_ca=-9λ²/(d²Z)<0,
    μ_cb=-4a_b⁴K²/Z<0.                          (1)

These formulas hold for roots in the remaining band, including zero physical mass, and extend to every wall face. They do not require a negative λ. At λ=0 there is no root at all. The strictly negative auxiliary determinant on the compact wall square gives a common two-sided root-free neighborhood of λ=0 by continuity.

## Injection into the softest corner

Take any additional tachyon at a target wall pair, meaning `-4k<μ_target<0`. Continue it along the straight segment in c from that target to (1,1). Both c coordinates increase (the physical Hessians decrease). Equation (1) makes μ decrease, strictly unless the target is already the zero-Hessian corner. It remains below its strictly negative starting mass, so cannot escape through μ=0. The uniform auxiliary strip prevents escape through μ=-4k.

The branch is therefore trapped in a compact interval strictly inside (-4k,0). At any putative finite endpoint, the normalized regular IVP and continuity give a limiting root, and (1) makes that root simple. The implicit-function theorem extends it, including to the final zero-Hessian corner. Distinct target roots cannot merge along the common path because that would violate simplicity and local uniqueness. This supplies an injection from the target's additional-tachyon set into the zero-Hessian corner's additional-tachyon set.

Consequently,

    N_extra(target)<=N_extra(κ_a=κ_b=0).        (2)

In particular, **if** the zero-Hessian corner has no root in (-4k,0), **then** no member of the entire compactified nonnegative wall family has an additional tachyon there. Combined with the accepted unique μ<-4k mode, that would establish exactly one physical scalar tachyon everywhere in this declared family. The premise has not been evaluated here.

## Precise prospective phase diagnostic

At the zero-Hessian corner the upper condition is L_b=0, corresponding to lifted phase angles `π/2+jπ` for `θ=arg(L+i f)`. The accepted single-turn auxiliary phase lies in `(π,3π/2)`. Let θ_E be its continuously lifted endpoint phase at μ=0. The no-additional-tachyon criterion is

    θ_E<=3π/2.

Equality permits a massless root at μ=0 and does not count it as a tachyon. Strict inequality excludes that massless root too. A scalar sign of G(0)=L_b(0) alone cannot exclude an even number of additional crossings; the lift must be certified.

A prospective bounded test should freeze the zero-Hessian launch, upper L residual, exact background binding, phase lift from the accepted auxiliary branch, and the massless equality case. It should retain a rigorous count rather than infer it from a plot or principal-value angle. Only after independent formulation/preflight, resource lease and terminal audit may it be classified. No new numerical work is authorized by this note.

Relative to a baseline-20 band test, this corner has greater logical payoff: if the zero-Hessian band is empty, (2) covers every nonnegative wall pair. Conditioning and actual cost remain to be determined by preflight. Negative wall Hessians, other perturbation sectors and nonlinear conclusions remain outside the comparison.
