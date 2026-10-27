# Compact nonnegative-Hessian theorem, including zero-Hessian walls

Status: proposed analytic strengthening for independent review. This preserves the accepted positive-Hessian theorem and extends its convex-background class to κ_a,κ_b>=0, including either zero Hessian and either Dirichlet limit. All exact canonical action/background/sector hypotheses remain in force. The coordinate constant1 below uses the same fixed nondimensional units as the action; it is a compactification convention, not a physical additional stiffness.

## Compact wall coordinates and regular launch

The accepted convex-range and weighted-derivative arguments give one scalar turn and `T'>0` everywhere, with `T_a<0<T_b`. Define shifted reciprocal coordinates

    c_i=1/(κ_i+1),       0<=c_i<=1.

Here c_i=1 means a finite wall Hessian κ_i=0, and c_i=0 means the Dirichlet limit κ_i→∞. Define

    d(c_a)=(1-c_a)T_a/2-c_a T'_a<0,
    ψ_a=1,
    f_a=3λ c_a/d(c_a),
    g_a=3λ(1-c_a)/(2d(c_a))-2T_a,
    G=c_b L_b+(1-c_b)f_b/2,       L=g+2Tψ.       (1)

The lower d is an affine combination of the strictly negative values T_a/2 and -T'_a, hence bounded away from zero on [0,1]. At c_a>0, (1) gives `L_a=κ_a f_a/2` and the regular constraint, including κ_a=0 at c_a=1. At c_a=0 it gives scalar Dirichlet data. The upper G imposes the finite upper Robin relation when c_b>0, including L_b=0 at c_b=1, and scalar Dirichlet when c_b=0.

Every nontrivial retained solution permits ψ_a=1 normalization: at finite κ_a, `B_a=κ_a T_a/2-T'_a<0`, while at lower Dirichlet `T_a≠0` makes the constraint fix g_a in terms of ψ_a. Vanishing ψ_a would force the entire launch to vanish. The regular determinant is analytic in μ and both c coordinates around the compact square.

## Uniform signs without a positive stiffness lower bound

At λ=0 the same auxiliary solution gives

    f_b=-T_b v_b<0,       L_b=-T'_b v_b<0.

Therefore G<0 on the entire square, including both zero-Hessian faces and the DD corner. Its strict margin is uniform by compactness.

At λ=-q² use the positive-denominator scalar reduction from the general theorem,

    f''=P_q f'+Q_q f,
    Q_q=q²/a²+V''+4k/a²+2T²+E T'/D,
    D=2T²+3q²/a²>0,
    E=12HT-4V'.

With `A=max a` and `Q0=||V''+4k/a²+2T²||∞+(A²/3)||ET'||∞`, choose

    q²>=1,       q²>A²Q0.

Then Q_q>0 uniformly. The launch (1) has f_a>=0 and g_a>0 for every c_a∈[0,1], including both endpoints. The cone f>=0,g>=0 is forward invariant: at f=0 its derivative is g>=0, and at g=0 with f>0 its derivative is Q_qf>0. Regular uniqueness excludes reaching (f,g)=(0,0), and the data enter f>0 immediately if f_a=0. Hence f_b>0 and g_b>0.

Since both T_b and T'_b are positive,

    L_b=(3q²g_b/a_b²+2T_bT'_b f_b)/D_b>0.

Consequently G>0 uniformly for every c pair, including c_b=1. The argument holds for every larger q, so all shifted-negative roots have a common finite lower mass barrier. Opposite endpoint signs give at least one root on every face and corner, with a uniform root-free strip next to λ=0.

## Face simplicity and exact count

At a root with λ<0, the vector (f_b,L_b) is nonzero by the regular constraint and IVP uniqueness. The upper wall equation implies that there is a unique nonzero real K with

    (f_b,L_b)=K(2c_b,-(1-c_b)).                  (2)

This parameterization stays regular at c_b=0 and c_b=1; explicitly one may use

    K=[2c_b f_b-(1-c_b)L_b]/[4c_b²+(1-c_b)²].

The lower Green flux vanishes for equal c_a, including both endpoint walls. Comparing the root profile to a nearby mass profile gives

    J_b=2K a_b⁴ G,
    G_μ=-Z/(4K a_b⁴)≠0.                        (3)

Thus every shifted-negative root is simple, including zero-Hessian faces. The determinant is analytic and all these roots are trapped strictly between two common barriers, so its finite root count is locally constant throughout the compact square. On the positive-Hessian interior, the accepted convex turning index is exactly one. Connectedness therefore gives exactly one shifted-negative root everywhere on the square. No root can emerge or disappear at a zero-Hessian edge without violating the barriers or simplicity.

## Global response, DD ceiling and uniform gap

At 0<c_i<1 the wall response and `dκ_i/dc_i=-1/c_i²` give

    μ_ca=-9λ²/(d(c_a)²Z)<0,
    μ_cb=-4a_b⁴K²/Z<0.                          (4)

Analytic local simplicity extends these formulas continuously to every face, including c_i=1; all right-hand sides remain strictly negative. The unique mode therefore defines one analytic response surface across the compact square. Its mass strictly increases with each finite nonnegative physical Hessian, and its maximum is the unique DD mass. Uniform auxiliary exclusion gives

    μ(κ_a,κ_b)<=μ_DD<-4k-δ<0                   (5)

for some δ>0 across the entire compactified nonnegative family. Equality in the first inequality occurs only at the DD corner. This uniform family is now compact because zero Hessians have been included using the regular shifted coordinates. It is not the earlier noncompact unshifted coordinate argument.

The symbolic gap can be made explicit by the same Gronwall construction as EXPLICIT_GAP_COROLLARY.md, with `c_a*=c_b*=1`, `d_*=min(|T_a|/2,T'_a)`, and

    m0=(2b/A²)min(T'_b,T_b/2)>0,
    R0=2|T_b|+1/2+1.

The launch bounds Y0,Y1 there remain valid because the new factor (1-c_a) is at most1. Its matrix bounds are unchanged, and the residual row is now `(2c_bT_b,(1-c_b)/2,c_b)`, bounded by this R0. Consequently the same `δ_exp=min(q0²/2,m0/(2M1))` supplies a positive explicit uniform gap. These are symbolic bounds, not a newly evaluated numerical margin.

For the inherited central quadratic background this proves exactly one shifted-negative, strictly lowest regular scalar mode for every nonnegative wall-Hessian pair, including zero Hessians and Dirichlet limits, on the exact same background. Its local growth exponent remains above H throughout. Negative Hessians, additional perturbation sectors, remaining-band tachyon counts, operator completeness and nonlinear fate remain outside this theorem.
