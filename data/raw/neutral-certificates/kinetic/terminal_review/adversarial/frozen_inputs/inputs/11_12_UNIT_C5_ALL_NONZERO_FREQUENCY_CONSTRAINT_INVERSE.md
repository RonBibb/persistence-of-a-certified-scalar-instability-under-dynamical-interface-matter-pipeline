# Unit C5: actual coupled metric-constraint block inverse at every nonzero spatial frequency

Conditional on the same selected analytic charged branch, each fixed finite time slab admits a sufficiently small, unquantified charge neighborhood in which the TWO coupled conformal/momentum metric-constraint blocks have a unique inverse for every nonzero tangential Fourier mode. Canonical bulk/wall fields, prescribed-curvature variation, reference/modulus and corner-boost loads are GIVEN data. The physical exact-zero-mode TT/modulus/edge sector and the remaining scalar-normal/gauge/evolution/kinetic domain are not supplied by this inverse.

The proof closes C4's finite-frequency gap by an exact zero-charge cooperative transformation, then a common-domain compact-parameter perturbation. No profile bound, numerical flow, sampled frequency, action change, inverse scalar gradient or oscillator division is used. UNIT_C5_TEST_SCOPE.md records this justified continuation within the original allocation.

## 1. Exact zero-charge block and boundary domain

Use the actual isothermal spatial background from C2, gamma=exp(2lambda)(dr^2+dx^2), with its positive actual width ell(t) retained. Put

    alpha=a^3 exp(2ht), B=alpha^2,
    M=10h^2 exp(2ht)>0, K=k^2+M,
    A0=-(h exp(2ht)/2)alpha.

Here M is a clock-dependent coefficient, NOT the bulk scalar mass or the spin2 radial mass. Direct differentiation of kappa=5h/alpha gives

    exp(2lambda)kappa'=10 A0',
    exp(2lambda)L_gamma alpha/alpha=M.

For the homogeneous coupled block set w=alpha y. The equations in C2/C4 become EXACTLY

    -(B y')'+B(k^2+M)y+h zeta'=0,
    -zeta''+k^2 zeta-[M/(4h)]B' y=0,
    y'(0)=y'(ell)=0, zeta(0)=zeta(ell)=0.           (Z)

The Robin row becomes Neumann because the ACTUAL lapse obeys the same pressure Robin condition. Endpoint signs and the adverse wall term have not been dropped. This is a homogeneous-kernel test AFTER supplied boundary loads are lifted; no matter/boost perturbation is being physically frozen in the full system.

For the following auxiliary operator allow k=0 in(Z). This is the continuous Dirichlet-zeta continuation of the NONZERO-mode block. The actual physical k=0 momentum equations have an extra diagonal-TF/modulus datum; they are not selected by declaring zeta Dirichlet there.

## 2. Exact cooperative transformation

Define

    a_c=M/(4h), V=B y'-h zeta,
    eta=zeta+(a_c/K)V,
    d1=k^2+3M/4, d2=k^2+M/4,
    q=-hK eta/d1, b=B'/B.

All denominators are strictly positive since M>0. The first equation in(Z) gives V'=KB y, and V is Dirichlet at both ends. Differentiating y=V'/(KB) gives

    -V''+bV'+K V+hK zeta=0.

Substituting eta and then using the second equation gives

    -V''+bV'+d1(V-q)=0,
    -q''+d2 q-d3 V=0,
    d3=3M^2/(16d1)>0,
    d2-d3=k^2 K/d1>=0.                              (C)

Both V and q are Dirichlet at both endpoints: zeta and V vanish, hence so do eta and q. These formulas retain every first-derivative coupling; they do not estimate it by a guessed small profile coefficient. A solution of the original homogeneous system maps to(C). If V=q=0, then eta=zeta=0 and V'=KB y implies y=0, so the map detects every original kernel element.

## 3. Positive common barrier rules out the kernel

At a fixed time choose c_b>||b||_infty and let

    F(r)=1+cosh(c_b ell/2)-cosh(c_b(r-ell/2))>0.

It equals1 at the endpoints. Its first-row and second-row common-barrier residuals are

    -F''+bF'>0,
    -F''+(d2-d3)F>0.

Indeed -F''=c_b^2 cosh, |bF'|<c_b^2 cosh, and d2-d3>=0. If either V/F or q/F had a positive maximum, choose the largest such maximum. It lies in the interior since both fields vanish at the endpoints. At the selected component its first derivative agrees with the barrier multiple, its second derivative is no larger, and the other component is bounded above by the same multiple of F. The corresponding cooperative equation would then have strictly positive residual, contradicting(C). Repeating for -V,-q rules out negative minima. Thus V=q=0 and y=zeta=0.

This works for every real k, INCLUDING the auxiliary k=0 operator, without a quantitative warp/profile bound. Complex Fourier kernels vanish by applying it to real and imaginary parts. The theorem is kernel triviality/invertibility, not positivity of a physical scalar kinetic quadratic form.

## 4. Existence and uniform compact-band inverse

On the fixed radial interval use the weak form domain

    Vspace=H1(interval) x H1_0(interval)

for y and zeta. The first Neumann condition is natural; the second is Dirichlet. The zero-charge operator is a regular strongly elliptic second-order two-component ODE. Relative to an invertible positive diagonal reference with added positive zeroth-order terms, its lower-order and first-order cross terms are compact from Vspace to its dual. Equivalently one can use its regular separated four-boundary-row ODE realization. Its index is zero. The homogeneous-kernel theorem therefore gives a unique bounded inverse, not merely uniqueness for a solution assumed to exist. Smooth data have the corresponding H2/classical regularity; boundary loads can be included by the usual compatible lifts.

Flatten ell(t) to one reference interval. For k in ANY compact band0<=|k|<=K0 and time in a fixed compact slab, coefficients and domains then vary continuously and all zero-charge operators are invertible. The inverse map is continuous in operator norm, so compactness gives ONE finite uniform inverse bound. This includes the auxiliary zero value and hence controls the nonzero-mode limit without inventing an inverse k. It does not remove the actual zero-mode modulus.

## 5. Actual charged family on a common Robin domain

For the actual small-charge branch retain its physical positive lapse alpha_z. Set w=alpha_z y, B_z=alpha_z^2, qbar_z=exp(2lambda_z)L_gamma,z alpha_z/alpha_z>0. After multiplying the first C4 row by alpha_z/2 the actual homogeneous two-block operator is

    -(B_z y')'+B_z(k^2+qbar_z)y+C_z zeta',
    -zeta''+k^2 zeta+E_z y,
    C_z=-2alpha_z exp(-2lambda_z)A0,z,
    E_z=exp(2lambda_z)kappa_z' alpha_z.               (A)

Its boundary domain is ALWAYS y'=0, zeta=0 after the supplied loads are lifted. This follows exactly from the lapse/pressure Robin equality, not from an approximate boundary coefficient replacement. At zero charge C_0=h and E_0=-(M/(4h))B_0', so(A) reduces to(Z).

On a fixed finite time slab the actual isothermal map, width, lapse and coefficients are analytic small-charge perturbations after fixed-collar pullback. With the known expansion factors kept, all required coefficient/derivative differences tend to zero uniformly as the physical charge parameter tends to zero. Thus the normalized operators differ by O(z) in the Vspace-to-dual operator norm on a compact k band. No assertion of an all-future ordinary Sobolev bound is made.

## 6. Noncircular high/low split and one small-charge neighborhood

First choose a PRELIMINARY small analytic branch neighborhood and the finite time slab. It supplies positive lower bounds on B_z,qbar_z,width and finite upper bounds on C_z,E_z and the required coefficients. These bounds are existential inherited smooth/analytic constants, not numerical optimizations.

There are two equivalent high-frequency controls. C4's feedback estimate can be made uniform using these preliminary bounds. Directly in(A), put

    Ey=integral B_z[|y'|^2+(k^2+qbar_z)|y|^2],
    Ez=integral[|zeta'|^2+k^2|zeta|^2].

The cross terms in the normalized coupled weak form obey

    |integral C_z zeta' conj(y)+E_z y conj(zeta)|
      <=[Cmax/(sqrt(Bmin)|k|)
           +Emax/(sqrt(Bmin)k^2)] sqrt(Ey Ez).

Choose ONE finite K0>0 making the bracket<=1 for all |k|>=K0 throughout that PRELIMINARY neighborhood. The real part of the block form is then at least(Ey+Ez)/2. This gives a uniform high-frequency weak inverse with the actual domains. It is a coercive normalized SPATIAL constraint form, not the physical time-kinetic Hessian.

Now fix the complementary compact band0<=|k|<=K0. Section4 gives a uniform zero-charge inverse there. Shrink the charge neighborhood ONCE until its operator-norm difference times that inverse bound is <1/2. The Neumann inverse proves actual charged invertibility on the whole compact band. The high-frequency bound persists under this shrinkage because its cutoff came from the larger preliminary neighborhood. There is no circular frequency-cutoff/amplitude choice and no omitted intermediate band.

Together these steps prove the claimed actual nonzero-k metric-constraint-block inverse on the finite slab, uniformly in the normalized weak norms after compatible data lifts. Smooth compatible canonical/profile/boost/reference loads give smooth spatial responses. The allowed charge radius and constants remain positive but uncomputed; each finite independent charge direction pair is retained. Frequency-dependent boundary trace weights must be used for a statement about a full spatial Fourier superposition. A bounded spacetime coordinate map is not inferred from per-mode inverse bounds.

## 7. Closed versus remaining gates

NEWLY CLOSED: the finite-frequency coupled conformal/momentum block left by C4, and its actual sufficiently-small-charge continuation at every NONZERO spatial mode on finite time slabs. This uses BOTH physical metric Israel constraint rows and the canonical pressure Robin condition, with normal/corner/reference variations supplied as loads. It is a genuine coupled inverse, going beyond two positive diagonal operators.

STILL OPEN: the full exact-zero-mode TT/modulus/edge selection; a simultaneous cap-compatible spatial/PMC/time/boundary gauge; how scalar-normal and all remaining wall evolution conditions fit that domain; the bounded time-dependent shift/IR map; the action-derived kinetic Hessian and norm equivalence in C3; a full uniform hyperbolic scalar evolution estimate. Given canonical field/boost loads are not a constructed arbitrary-data Einstein-scalar initial-boundary problem. Invertibility, inverse positivity of a transformed cooperative system and physical kinetic positivity are distinct statements.

The current result preserves A's scalar turn, the accepted growing scalar direction and both independent material-current laws. It does not establish scalar stability, full no-ghost, nonlinear formation, persistent sources, projection, halo or cosmology.
