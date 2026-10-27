# Convex backgrounds: one negative-shifted mode for every positive Hessian pair

Status: proposed strengthening for independent review. It retains the exact finite canonical-action/background/sector hypotheses and endpoint reversal. It extends the prior stiffness range to every positive wall Hessian, including softening below the inherited value 20, while preserving the exact background through the declared wall-potential change.

Assume V''>=0 on the traversed scalar range and T_a<0<T_b. The accepted convex-range lemma gives a unique scalar turn s*, with `T'(s*)>0`, T<0 to its left and T>0 to its right. Differentiating the background scalar equation gives

    T''+4HT'=C(s)T,
    C(s)=V''+4k/a²+4T²/3>0.

Equivalently,

    (a⁴T')'=a⁴ C T.

To the left of s* the right side is negative. Therefore a⁴T' decreases towards its strictly positive value at s*, and is strictly positive at every earlier point, including the lower endpoint. To the right it increases from that same positive value and is again strictly positive through the upper endpoint. Consequently

    T'(s)>0 for every s∈[0,b].                   (1)

For every positive pair κ_a,κ_b, (1) implies

    B_a=κ_a T_a/2-T'_a<0,
    β_b=-κ_b T_b/2-T'_b<0.

One may choose that pair itself as the positive baseline in the general theorem. The exact turning index is then one, and the compact response reaches either or both Dirichlet limits. Since the pair was arbitrary, there is exactly one regular eigenvalue with μ<-4k for every κ_a>0,κ_b>0. Its positive norm and reality follow as before. Local response derivatives `∂μ/∂κ_i=a_i⁴f_i²/Z>0` hold throughout this positive quadrant, and uniqueness makes the local continuations agree wherever baseline rectangles overlap.

The DD eigenvalue is likewise unique in μ<-4k, so the ceiling reached from any positive baseline is the same eigenvalue of the fixed-background DD problem. In particular, softening or stiffening the central model's wall Hessians within the positive quadrant never removes its unique negative-shifted mode. The action deformation can now have negative η_i=κ_i-20 when 0<κ_i<20; its value and first derivative still vanish on the exact background, so the background is preserved exactly.

This corollary does not include κ_i=0 or negative Hessians, does not count the remaining physical-tachyon band, and does not construct an exact background. It does not assert one uniform positive spectral gap over the noncompact reciprocal-stiffness quadrant; uniform estimates continue to require a compact family with the stated margins. Field reflection gives the equivalent reversed endpoint orientation.
