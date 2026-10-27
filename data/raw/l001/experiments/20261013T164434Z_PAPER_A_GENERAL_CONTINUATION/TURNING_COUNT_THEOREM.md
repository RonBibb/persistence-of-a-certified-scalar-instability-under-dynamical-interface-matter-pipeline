# Exact negative-shifted index from the scalar turning count

Status: proposed theorem for independent review. This strengthens the previously accepted finite-odd-count result. It uses only the exact background/action/sector and endpoint hypotheses of GENERAL_THEOREM_PROPOSAL.md. It counts real regular eigenvalues with λ=μ+4k<0; it does not count masses in -4k<=μ<0 or claim a complete operator-domain theorem.

## Statement

Let n be the number of interior zeros of the background scalar derivative T on (0,b). Under the main theorem's hypotheses, n is finite, every such zero is simple, and n is odd. For every pair of allowed Robin or limiting Dirichlet wall conditions, there are exactly n real regular eigenvalues with λ<0, all simple. They are the n ordered compact response branches of the previous theorem.

In particular, an exact background with a single scalar minimum and the stated endpoint conditions has exactly one negative-shifted mode for every permitted wall pair, including DD. This is an index statement for that spectral sector, not a count of the complete tachyonic spectrum or a nonlinear result.

## 1. Interior zeros are simple and finite

At any zero of T, its background equation gives `T'=V'(Phi)`. If T and T' vanished together at a point, then V'(Phi)=0 there. The full smooth first-order background system

    a'=Ha,  Phi'=T,
    H'=-T²/3-k/a²,  T'=V'(Phi)-4HT

has unique local solutions while a>0. The solution with that same initial data and Phi constant, T identically zero, exists and solves this system. Uniqueness would make the supplied scalar constant throughout its connected regular interval, contradicting `T_a<0<T_b`. Therefore T'≠0 at every zero of T.

Every interior zero is consequently isolated and changes sign. Infinitely many zeros on the compact interval would have an accumulation point; nonzero endpoint T excludes the endpoints, and an interior accumulation would force T=T'=0 by differentiability. Thus n is finite. The opposite endpoint signs make n odd.

## 2. A regular phase with positive spectral derivative

Fix a wall pair c_a,c_b. For the lower-launched regular solution set `L=g+2Tψ` and define the phase of the vector `(L,f)` by

    θ=arg(L+i f),

using a continuous real lift, not a principal-value angle after every step. For λ<0 this vector never vanishes anywhere on [0,b]. Indeed if f=L=0, the constraint `TL-T'f=3λψ/a²` forces ψ=0 and hence g=0; regular IVP uniqueness contradicts the launch.

At the lower endpoint for λ<0,

    L_a=3λ/(2d)>0,
    θ_a=atan(2c_a)∈[0,π/2).

The Green identity applies to two nearby masses satisfying the same lower condition even when neither satisfies the upper condition. Integrating only to an arbitrary s>0 and differentiating in the second mass gives

    a(s)^4 [f L_μ-L f_μ]=-Z_s/2,
    Z_s=2∫₀ˢ a²(f²+6ψ²)dr>0.

Consequently, for each fixed s>0,

    θ_μ(s,μ)=Z_s/[2a(s)^4(f²+L²)]>0.            (1)

This off-shell identity is stronger than the derivative formula at an eigenvalue. Because λ differs from μ by a fixed constant, the same sign holds for θ_λ.

The vector is continuous and nonzero also at λ=0 for every s>0: the auxiliary solution gives

    (f,L)=-v(s)(T,T'),       v(s)>0,             (2)

and section 1 excludes T=T'=0. Hence the phase has a continuous lift on the rectangle `0<=s<=b`, `-q0²<=λ<=0`, with only the corner (s,λ)=(0,0) removed. This domain is simply connected (indeed convex because the removed corner is an extreme point). Anchor the lift at the displayed lower angle for λ<0. A continuous lift exists and is unique after one value is fixed.

## 3. The two endpoint phases

Choose q0 large enough for the cone theorem, with the additional sufficient inequality

    3q0² r/A²>2||TT'||∞,

where r and A are the main theorem's positive constants. The cone gives f>0 and g>=rf for s>0, and the constraint expression for L then gives L>0 for s>0. Thus at λ=-q0² the anchored phase obeys

    0<θ_b(-q0²)<π/2.                            (3)

No additional spectral integration is used; q0 can always be enlarged to meet this finite bound.

We next determine the same lift at λ=0. Near the omitted lower corner, the regular IVP has `f_a>=0` for λ<=0 and

    f_s(0,0)=g_a(0,0)=-2T_a>0.

By continuity there is a small corner rectangle on which f_s>0. Thus f(s,λ)>0 for s>0 throughout that rectangle. This anchors the auxiliary phase in (0,π), continuously with the lower phase θ_a in [0,π/2), and excludes an unobserved 2π winding at the vanishing lower vector. In particular the auxiliary phase starts between 0 and π before its first T zero.

Along λ=0, f=-Tv. At a zero of T, f=0, `L=-T'v≠0`, and `f'=L`, so

    θ_s=(L f'-f L')/(f²+L²)=1>0.                (4)

The phase crosses each successive multiple of π upward. Between those zeros f has fixed nonzero sign, so the continuous phase cannot cross any other multiple of π. After exactly n scalar turns, therefore

    nπ<θ_b(0)<(n+1)π.                           (5)

Put α_b=atan(2c_b)∈[0,π/2). For c_b>0, the upper endpoint hypothesis at its current Hessian gives

    β_b=-κ_b T_b/2-T'_b<0,
    T'_b/T_b>-κ_b/2=-1/(2c_b).

From (2), `cot θ_b(0)=T'_b/T_b`. The cotangent is strictly decreasing on `(nπ,(n+1)π)`, so

    θ_b(0)<(n+1)π-α_b.                          (6)

At c_b=0 the same inequality is exactly the upper bound in (5). Also (5) gives `θ_b(0)>nπ>=nπ-α_b` in both cases. The current β_b sign follows from its baseline sign because κ_b>=κ_b0 and T_b>0.

## 4. Counting the crossings

The upper wall equation `c_b L_b+f_b/2=0` is equivalent to

    θ_b=jπ-α_b,       j an integer.

At the low-mass endpoint, (3) lies strictly below the first positive such angle `π-α_b>π/2`. At zero shifted mass, (5),(6) place the phase strictly between the nth and (n+1)th such angles. The phase is continuous and strictly increasing in μ by (1). Therefore it crosses each of the angles with j=1,...,n exactly once and crosses no other upper-wall angle while -q0²<λ<0.

The cone theorem excludes roots at every λ<=-q0². Consequently the entire real λ<0 sector contains exactly n roots. Their simplicity follows either from (1) or the main theorem's norm identity. The compact continuation and strict wall responses already established apply to all of them.

## Boundaries and use

No numerical value of n for the inherited background is asserted here. Applying the single-turn conclusion to it requires an exact single-turn premise or a separately certified background fact. The theorem does not identify the number of μ<0 modes with λ>=0, assert completeness, or equate a mode count to nonlinear fate. The possibility of degenerate interior turns mentioned as an unneeded hypothesis in earlier notes is now resolved within this smooth canonical background class: such a turn would force a constant scalar and is incompatible with the endpoint signs.
