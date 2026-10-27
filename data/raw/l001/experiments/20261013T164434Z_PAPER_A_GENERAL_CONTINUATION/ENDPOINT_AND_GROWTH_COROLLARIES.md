# Orientation-independent endpoint test and linear de Sitter growth

Status: proposed corollaries to the independently reviewed seed-free theorem. They require separate independent review. No numerical calculation or background construction.

## Endpoint reversal and explicit sufficient stiffness thresholds

Suppose the exact finite canonical Einstein–scalar background and generic scalar-sector assumptions of the main theorem hold, with k>0 and

    T_a T_b<0.

Neither endpoint scalar derivative vanishes. Define the finite thresholds

    θ_a=2T'_a/T_a,       θ_b=-2T'_b/T_b.

For positive wall Hessians satisfying

    κ_a>max(0,θ_a),       κ_b>max(0,θ_b),          (1)

the main theorem applies, and at least one regular positive-norm mode has μ<-4k. Indeed (1) is exactly the orientation-independent pair of inequalities

    T_a(κ_a T_a/2-T'_a)>0,
    T_b(-κ_b T_b/2-T'_b)<0.

When T_a<0<T_b these are the original endpoint predicates. When T_a>0>T_b, reflect the field: `Phi_tilde=-Phi`, `V_tilde(x)=V(-x)`, and `tau_tilde_i(x)=tau_i(-x)`. This preserves the canonical action class, warp factor, k, physical mass, wall Hessians, and regular norm. It sends T and T' to their negatives, so the reflected problem satisfies the original predicates. A reflected mode has f_tilde=-f and the same ψ, hence maps back to a regular mode of the original problem. No physical change to the background is introduced by this relabeling of the scalar.

Choose any positive baseline Hessians strictly above these thresholds and apply the compact continuation theorem. Its DD corner has μ_DD<-4k. The DD conditions f_a=f_b=0 are independent of the chosen baseline Hessians. Therefore the endpoint reversal `T_a T_b<0` alone, together with the exact background/action/sector hypotheses, suffices for existence of a negative-shifted DD mode. No finite baseline value or numerical seed is required in this existence statement.

This sufficient endpoint test allows multiple or degenerate interior turns and does not count or locate them. For finite wall Hessians outside (1), this corollary gives no verdict. Threshold equality is not included; it can make a launch denominator or auxiliary endpoint sign degenerate.

## Physical linear growth in a de Sitter patch

Use an expanding spatially flat patch of the four-dimensional de Sitter metric,

    γ=-dt²+e^(2Ht) dx·dx,       H=√k>0.

The mode convention is `Box_γ Q=μ Q`. For a spatially homogeneous time dependence this gives

    Q_ddot+3H Q_dot+μQ=0.

Its growing solution is `Q=e^(σt)` with

    σ=(√(9k-4μ)-3√k)/2.

Every mass furnished by the theorem obeys μ<-4k, therefore σ>√k=H. A regular positive-norm perturbation consequently has an exponentially growing linear solution whose logarithmic growth rate exceeds the de Sitter expansion rate. This homogeneous time-dependent harmonic is in the retained generic sector: the exceptional nonconstant bending harmonics have μ=-4k, whereas this mass is strictly below that value; it is also not the constant harmonic.

On wall i, proper time is `τ_i=a_i t`, and the local Hubble and perturbation growth rates are

    H_i=H/a_i,       σ_i=σ/a_i,
    σ_i/H_i=σ/H>1.

Thus this dimensionless comparison does not depend on which wall's proper-time units are used. Since the tracked mass increases under either stiffness, σ decreases under stiffening; its DD limit still satisfies σ_DD>H. Under the uniform family gap `μ<-4k-δ`, the corresponding bound is

    σ/H > (√(25+4δ/k)-3)/2 >1.

This is a linear instability consequence for an explicitly separable perturbation. It does not determine its amplitude, duration of validity, nonlinear endpoint, backreaction, wall collision, or causal horizon structure. The spatially homogeneous solution is a mode solution in the flat patch; no claim of finite total spatial norm on noncompact R³ is needed or made.
