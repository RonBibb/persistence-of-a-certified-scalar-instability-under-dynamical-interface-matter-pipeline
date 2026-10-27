# Scalar normal wall source bound

This estimate controls the scalar-normal residual at both moving walls, including the outer expansion-order weight required by the boundary reconstruction. It uses the selected quadratic wall action and linear current coupling, not an arbitrary wall model. The Israel and oscillator source estimates remain separate.

## Selected action and endpoint norms

The manuscript's selected action has tau_PhiPhi=20, W_Phi=Phi-Phi_star-chi and c_Phi=-1/1000. Hence tau_Phi+W_Phi is its neutral constant plus 21(Phi-Phi_star)-chi. The scalar-normal equation contains one half of this expression, with the inward orientation sign. The neutral scalar boundary law cancels its constant term.

At fixed-chart real endpoints, d=1. For order i>=1, each of the primitive jets p,b,f,f_r,xi,X_r,S_t,D0f has both its absolute coefficient and i times that coefficient bounded by its indicated constant times Y_i: constant 1 for the first six, and g=3/25 for S_t and D0f. These follow from the bulk quadratic and graph cubic weights, and D_min>1. They are not assumed for arbitrary second bulk time derivatives. All wall fields are already pulled to the moving wall in the fixed chart; only background functions require explicit composition.

Use the fixed working collar rho=1/40000 and prior collar R=1/20000. Set a=2/rho=80000, Ebar=8+1/1000, c=Ebar*g<1, A=2a+1 and H(y)=(1-A*y)^(-1). Here H is an auxiliary generating function, not the background warp gradient. The nonnegative lower-order coefficient envelope is y=Y_<n. Formal coefficient comparisons are distinct from numerical evaluation, which requires A*y<1.

## Velocity and normal factors

The physical wall speed is v=exp(b-p)E(S)S_t. Its absolute-coefficient bound is c*y/(1-a*y)^2. Since m<=2^(m-1) for m>=1, the latter is coefficientwise bounded by v0=c*y/(1-2a*y), and hence by c*y*H. The binomial coefficients of the inverse square root are at most one, so

    boost=(1-v^2)^(-1/2) <= (1-v0)^(-1) <= H,
    boost-1 <= v0^2/(1-v0) <= c^2*y^2*H^2.

The sharper second bound uses the exact majorant cancellation v0^2/(1-v0)=c^2*y^2/[(1-2a*y)(1-(2a+c)*y)]. Replacing the three original denominator factors separately would lose this improvement.

The denominator scale A absorbs 2a+c because c<1. Exponential and inverse-Jacobian factors are also dominated by H, and the physical derivative Df=D0f-W f_r is bounded by 2g*y*H. These constructions use analytic series with nonnegative majorant coefficients in the primitive jets; they retain the counting needed for the outer order weight.

## Scalar residual after linear subtraction

The geometric normal is

    boost*[exp(-b)(T(S)+Jinv*f_r)+v*exp(-p)*E(S)*Df].

After subtracting its neutral and complete linear rows, the five groups have the following sufficient constants against y^2*H^5:

| Group | Constant |
| --- | --- |
| exp(-b)T(S) remainder | Tbar*(a^2+a+1) |
| exp(-b)Jinv*f_r minus f_r | 2 |
| boost minus one times the normal numerator | c^2*(Tbar+1) |
| velocity times the scalar time derivative | 2c*Ebar*g |
| quadratic-and-higher Phi(S) trace in the wall potential | (21/2)*Pbar*a^2 |

Here Tbar=T0+epsilon and Pbar=P0+epsilon are the verified prior background bounds. The first group uses the background Taylor tail after its linear displacement term, plus the exponential remainder and their cross term. The last uses the exact selected action; f and chi enter that part only linearly and contribute no lower-order nonlinear remainder. Let Cj be the sum of these five constants.

The explicit current is different: nu_i^2=z*N_i^2*E(S)^6*exp(-6p). Applying Cauchy directly to the analytic background function E^6 gives the current load bound

    Ccur*z*|N_i|^2*H^2,     Ccur=Ebar^6/2000.

The factor 2000 includes both c_Phi and the scalar equation's half-factor. This source begins at order one and must not be discarded with the removed linear unknown row.

## Outer order weight

Before substituting y=Y_<n, retain y as an auxiliary primitive-count degree. For a monomial containing m positive-order primitive jets of orders i_1,...,i_m, distribute n=sum(i_j) across its factors. The endpoint bounds above control each resulting term, giving at most m times the scalar majorant monomial. For an explicit current factor z, n=1+sum(i_j) gives m+1 instead. The auxiliary operation y*d/dy therefore counts primitive factors; it is not a claim that the physical Euler derivative of Y is bounded by Y.

All simplifications above are coefficientwise in this auxiliary y, so applying y*d/dy preserves their inequalities. With y*H^m<=H^m/A coefficientwise,

    y*d/dy(y^2*H^5) <= 7*y^2*H^6,
    H^2+y*d/dy(H^2) <= 3*H^3 <= 3*H^6.

Summing the two walls and writing C_N=|N_a|^2+|N_b|^2 gives

    n*sum_i |j_i,n| <= [z^n] {14*Cj*y^2 + 3*Ccur*z*C_N}*H^6.

The factor two is used only for the generic geometric per-wall bound. The current terms already sum through C_N. The resulting bound retains both independent current labels and is valid at all positive orders, conditional on the selected action and inherited endpoint norms. It is not the full wall budget or an allowed numerical charge amplitude.
