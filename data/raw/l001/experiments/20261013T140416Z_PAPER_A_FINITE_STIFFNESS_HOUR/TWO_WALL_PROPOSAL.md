# Compact two wall stiffness response surface

This is a prospective analytic extension for independent review, not an accepted result. It requires no new background or spectral integration. Its purpose is to construct the response of the same mode under both wall Hessians, including the joint Dirichlet limit, rather than infer a finite response from local derivatives.

## Parameters and inherited assumptions

Keep the exact certified background, action and normalization a(0)=psi(0)=1. Independently add eta_i(Phi−Phi_i*)²/2 to each wall action, eta_i>=0. The background first jets are unchanged. Write gamma=20 and c_i=1/(gamma+eta_i). Finite nonnegative Hessian increments correspond to 0<c_i<=1/gamma. Include c_i=0 only as the regular Dirichlet boundary limit, not a finite wall potential.

The inherited exact background satisfies k>0, T_a<0, T_b>0, B_a0=gamma T_a/2−T'_a<0 and beta_b0=−gamma T_b/2−T'_b<0. Here T=Phi_s and T'=m²Phi−4HT. Exact T_a<0 follows from the bound lower launch interval A<v0 and T_a=gamma(A−v0)/2; the other signs are in the accepted background/response records. All original flow and action validity premises remain inherited.

Define d(c_a)=T_a/2−T'_a c_a. Its endpoint values are d(0)=T_a/2<0 and d(1/gamma)=B_a0/gamma<0. As an affine function, d is strictly negative throughout the compact interval. The regular normalized lower launch is

f_a=3lambda c_a/d(c_a),  g_a=3lambda/[2d(c_a)]−2T_a,  psi_a=1,

where lambda=mu+4k and g=f_s. At c_a>0 these are the original constraint and lower Robin condition with Hessian gamma+eta_a. At c_a=0, f_a=0 and the constraint fixes g_a=3lambda/T_a−2T_a. Thus the launch is analytic through the lower Dirichlet face; there is no normalization pole. A nontrivial lower Dirichlet solution cannot have psi_a=0: the constraint with T_a!=0 then also forces g_a=0, making all regular mode data zero. In the Robin case d!=0 gives the same conclusion. The normalization remains legitimate on every face and corner.

Let the regular solution of this launch define L_b=g_b+2T_b psi_b and the upper scaled residual

G(mu,c_a,c_b)=c_b L_b+f_b/2.

For c_b>0 this is the upper Robin residual divided by its Hessian, and at c_b=0 it is upper Dirichlet. It is real analytic in all parameters on a neighborhood of every point in the compact reciprocal-Hessian square and bounded mass interval, since the bulk IVP has regular coefficients and d is bounded away from zero.

## Uniform auxiliary boundary sign

At lambda=0 the launch reduces to f_a=0,g_a=−2T_a,psi_a=1 for every c_a, including zero. The accepted division-free auxiliary construction in FINITE_BRANCH_PROOF.md therefore gives the same solution for every lower Hessian: psi_b>0, f_b<0 and original upper residual R_0<0. Consequently

G(−4k,c_a,c_b)=c_b R_0+(1−gamma c_b)f_b/2<0

for every (c_a,c_b) in [0,1/gamma]². This is a convex combination of the negative endpoint values R_0/gamma and f_b/2. Compactness and continuity give some uniform delta>0 with no zero of G in mu in [−4k−delta,−4k], throughout this square. No numerical value of delta is asserted.

## Simplicity on Robin and Dirichlet faces

At a root with lambda<0, L_b cannot vanish. If c_b>0, G=0 would then give f_b=0; the constraint gives psi_b=0 and hence g_b=0, contradicting the nonzero normalized solution. If c_b=0, f_b=0 and the constraint gives T_b L_b=3lambda psi_b/a_b². Vanishing L_b again forces psi_b=g_b=0. In both cases L_b is nonzero.

For two masses with fixed c_a, the lower Green flux vanishes, also at c_a=0 because both lower f values vanish. At the upper boundary and at a root, the proper/conformal conversion of the accepted regular Green concomitant is

J_b=a_b^4(f_* L_mu−L_* f_mu)=−2a_b^4 L_* G(mu,c_a,c_b),

using f_*=−2c_b L_*. The integrated identity gives dJ_b/dmu=−Z/2 at the root. Therefore

G_mu=Z/[4a_b^4 L_b] != 0,

where Z=2 integral a²(f²+6psi²)ds>0. This formula is valid on the Dirichlet face and at the double Dirichlet corner as well as in the Robin interior. It uses no division by the interior scalar derivative and makes no assumption about a singular weighted norm.

In the interior, the accepted wall response identities imply

mu_ca=−9lambda²/[d(c_a)²Z]<0,
mu_cb=−4a_b^4 L_b²/Z<0.

The first follows from dmu/deta_a=f_a²/Z and deta_a/dc_a=−1/c_a²; the second from dmu/deta_b=a_b^4 f_b²/Z and f_b=−2c_b L_b. The same expressions extend by continuity and the implicit function theorem to both Dirichlet faces. Their right hand sides stay strictly negative because lambda<0, d!=0, L_b!=0 and Z>0.

## Construction and global consistency

Start at the accepted simple mode at c_a=c_b=1/gamma. For each target point in the closed square, follow the straight segment from this base point. Both c coordinates are nonincreasing along the segment; the local response formulas make mu nondecreasing, and strictly increasing unless the target is the base point. The mass stays above its initial value and below the uniform auxiliary zero-free strip.

Any putative finite failure of continuation has a subsequence with convergent mass and parameters in this compact region. The initial mass boundary is not a failure boundary: local existence holds at the base point, and strict radial monotonicity places every later point above the mass at any earlier positive segment time. The upper boundary is excluded uniformly by the auxiliary sign. The analytic residual gives a limiting root, and the regular positive norm formula makes that root simple, including boundary faces. The limiting normalized profile still has psi_a=1, so its regular norm is strictly positive. The implicit function theorem therefore extends the branch. This constructs the root along every radial segment, including its endpoint.

Continuous and smooth dependence on the target follows from local uniqueness and the parameter-dependent implicit function theorem along each compact radial segment: a finite chain of overlapping simple-root neighborhoods covers the segment, and their unique branches agree on overlaps. Nearby radial segments therefore select the same local root near their common endpoint. This defines a single smooth function mu(c_a,c_b) on the closed square, locally extending across its edges. There is no path-dependent reassignment of roots; local uniqueness identifies any continuation from this surface with the same surface. This does not assert that no other spectral branch exists.

Since both partial derivatives are strictly negative, the maximum occurs at the double Dirichlet corner c_a=c_b=0. Denote that branch-selected mass by mu_DD. Then

mu_base < mu(c_a,c_b) < mu_DD < −4k <0

for every finite nonnegative pair with at least one positive increment. At zero increments the first inequality is equality. Along the upper-only edge, its previously accepted upper Dirichlet limit is strictly below mu_DD. The double Dirichlet profile is nontrivial and regular with f_a=f_b=0. The uniform gap is qualitative, and no numerical value of mu_DD is supplied.

## Review boundary

The proposed result is a constructive compact response surface and a well-defined joint stiff-wall limit for the tracked mode. It is not a full-spectrum ordering theorem, a claim that this is the lowest mode, or a nonlinear stability statement. Its assumptions and background-preserving Hessian idea have close literature precedents; the claimed added value is this action-specific regular continuation and its connection to the independently certified finite response and upper-wall saturation bounds.
