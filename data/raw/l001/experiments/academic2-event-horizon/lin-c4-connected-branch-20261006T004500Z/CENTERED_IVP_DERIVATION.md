# Centered interval implementation

All variables refer to the exact certified background and a physical mode
admitted by its spectral certificate. Interval rectangles enclose that exact
source; an arbitrary point of a rectangle is not asserted to satisfy a wall
or spectral condition.

Set A=W+epsilon psi+w, A_s=H+epsilon psi_s+v and
d=C7+b0 H0+b1 H1. The scalar is Phi+epsilon f+d and ell=-2epsilon psi.
Write q0=k exp(-2W), E1(x)=exp(x)-1, E2(x)=exp(x)-1-x. Subtracting the
exact static and linear Hamiltonian equations gives w_s=v and

    v_s = -4H v-2q0 w
       -2epsilon psi_s(epsilon psi_s+v)-2(epsilon psi_s+v)^2
       +q0 E2(-6epsilon psi-2w)+2E2(-4epsilon psi)
       -m2/6 [Phi^2 E2(-4epsilon psi)
          +2Phi epsilon f E1(-4epsilon psi)
          +exp(-4epsilon psi){(epsilon f)^2+2(Phi+epsilon f)d+d^2}]
       -T d_s/3-(epsilon f_s+d_s)^2/6.

For each parameter x_j=(a,b0,b1), let (u_j,r_j)=partial_j(w,v).
With A_s=H+epsilon psi_s+v, the exact variation is

    (u_j)_s=r_j,
    (r_j)_s=(ell_s-4A_s)r_j-2q0 exp(-6epsilon psi-2w)u_j
       -[m2 exp(-4epsilon psi)(Phi+epsilon f+d)H_j
                       +(T+epsilon f_s+d_s)(H_j)_s]/3,

where H_a=0. Initial columns are (1,0),(0,0),(0,0), since the initial
Israel slope is fixed by the scalar endpoint value, unchanged by b0,b1.

At either physical wall, deltaPhi=epsilon f,
delta t=c deltaPhi and delta p=-T deltaPhi/3-sigma gamma deltaPhi^2/12.
The exact target slope after subtracting H+epsilon psi_s is

    Rwall=H E2(ell)-sigma gamma deltaPhi^2/12+E1(ell)delta p.

Thus initial w=a, v=Rwall_lower and G0=v_upper-Rwall_upper. The background
Israel/Robin identities and psi_s=-2H psi-Tf/3 establish this cancellation.

The independent nonlinear endpoint derivation proves that retaining G0 and
using its reduced proper fourth-time rows preserves precisely the zeros of
the original coupled map. Its curvature terms are not deleted. Writing
r=pwall^2-1-twall^2/12+m2 Phiwall^2/12 and Delta=q-r,

    G_i=b_i+W_i(epsilon)+L_i^5[-12c_i S_i Delta_i-24t_i Delta_i^2].

W is computed at q=r using the full degree-seven lift and fifth coordinate
derivative transformation. It is not an alternate physical curvature. The
actual q is retained through Delta=q0 E1(-2(epsilon psi+w))-delta r,
with delta r expanded exactly about the certified static wall. Similarly
S=Phi_ll+4pt-m2Phi is evaluated by exact centered increments. The full row
Jacobian is

    partial_j G_i = Kronecker(i,j)
       +L_i^5[-12c_i S_i-48t_i Delta_i](-2q_i)partial_j A_i.

The explicit Kronecker term occupies the appropriate b column only. At the
lower wall partial_j A=(1,0,0), at the upper wall it is the propagated u_j.
This includes the metric response induced by both fifth controls.

## Source and preparation remainder coverage

A fresh strict Picard/Taylor integration encloses the full root, mode-mass
and event intervals. It uses the source equations from the sealed initial
data. There is no dense-source approximation. Endpoint intervals may be
intersected with exact wall identities of the admitted source; source jet
coefficients are then computed from the regular ODE.

At epsilon=0 the unchanged preparation has C7=0 and its first derivative is
zero because the physical mode satisfies the linear wall/time conditions.
The reduced fourth-time W likewise has zero constant and linear coefficients.
These identities justify removing only those exact terms in the epsilon-zero
Taylor expansion. All coefficients of degree 2 through 7 are outward interval
enclosures. Coefficient 8 is evaluated with epsilon's center replaced by the
entire segment between zero and the target, derivative one, and no removed
terms; Taylor's theorem encloses the remainder. The scalar parameter is real.
The global C7 coefficient and W remainder calculations both retain full
source, event, mode and arithmetic uncertainty.

The center and box integrations independently enclose their full nonlinear
metric solutions. A parameter box is accepted only by strict self-mapping and
weighted contraction of the actual original-root-equivalent map, not by a
small sampled residual. Boundary-row equivalence preserves local uniqueness.
