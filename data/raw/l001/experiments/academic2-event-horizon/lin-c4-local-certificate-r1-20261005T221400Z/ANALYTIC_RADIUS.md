# Prospective analytic radius proof and its explicit premises

This is the quantitative secondary objective of CONTRACT.md. Its inequalities
must be checked, not inferred from a passing finite-amplitude example.

## Fixed exact coefficients, complex amplitude parameters

The exact static background is real on [0,D]. Its certified mode is a fixed
real solution of the regular linear ODE. Only z=(epsilon,a,b0,b1), with
A(0)=epsilon+a, is complexified. No complex spatial continuation or complex
eigenvalue branch is required. The same exact mode is retained throughout.

Under the prospectively stated background bounds, the mode's initial infinity
norm is less than 8. Its first-order coefficient matrix has row-sum norm less
than 128: the largest row is bounded by

    4|H| + |m2| + |mu| exp(-2W) + 2|T|^2
       + 12|HT| + 4|m2 Phi| < 74 < 128.

Thus its norm on D<=3 is less than 8 exp(384)<2^771<2^1024, using e<4.
Positive coefficient recurrences, with exact rational arithmetic, bound its
spatial derivatives through order five by 2^1536. These are comparison bounds,
not claims of an actual large mode amplitude.

The Hermite preparation is analytic in epsilon: it uses polynomials and
exponentials with D>=1, never a division by the scalar gradient. Its endpoint
corrections vanish at zero. Forward analytic differentiation and exact Hermite
coefficient norms give a bound on each scalar/ell perturbation spatial jet
through fifth order of C r0, C=2^1800, for |z_j|<=r0=2^-4096. The two fifth-jet
shapes are included in this bound. The executable majorant check must verify
these inequalities from the actual preparation formulas.

## Complex Hamiltonian IVP continuation

Put u=A-W, v=A_s-H. Work in the tube max(|u|,|v|)<=1/16 with prescribed
|ell|,|ell_s|,|Phi-Phi_star|,|Phi_s-T|<=1/16. The nonlinear metric equation is

    A_s=P,
    P_s=ell_s P + k exp(2ell-2A) + 2exp(2ell)
        -m2 exp(2ell)Phi^2/6 -Phi_s^2/6 -2P^2.

Since q=k exp(-2W)<=1, exp(2|ell|+2|u|)<2, |H|<=2, the metric Jacobian
infinity norm is less than 16 throughout this complex tube. Holding (u,v)=0,
the forcing defect is at most 2^8 C r0. The lower Israel initial derivative
defect and |A(0)| are bounded by the same number. Gronwall on D<=3 gives

    max(|u|,|v|) <= (1+3) 2^8 C r0 exp(48)
                 < 2^1906 r0 < 2^2000 r0 < 1/16.

The strict bootstrap keeps the solution in the tube for the whole compact
interval. The vector field is entire in its dependent variables and analytic
in z, so standard analytic ODE dependence gives a holomorphic boundary map
on the whole polydisc, not just a numerical solution at its center.

The exact positive jet recurrence also bounds the finite spatial derivatives
entering the original second/fourth time equations. It must prove a uniform
bound M=2^512 for each component of the normalized boundary map F on that
polydisc. The normalization is exp(5ell-4A), an entire nonzero factor; no new
denominator singularity is introduced. Endpoint orientation and wall data are
unchanged.

## Cauchy remainder and contraction

Analytic zero-amplitude recovery gives F(0,0)=0. The exact physical-mode tangent
must establish F_epsilon(0,0)=0 in the shifted a=A(0)-epsilon chart. Let J be
the certified three-variable Jacobian and suppose ||J^-1||_infinity<=B=2^64.

Cauchy's coefficient estimate on the four-variable polydisc bounds every
coefficient of total degree n by M/r0^n. The number of multiindices of degree
n is at most 4^n. For delta/r0<=1/8 this gives the conservative bounds

    ||F(epsilon,x)-Jx||_infinity <= 32 M delta^2/r0^2,
    ||D_x F(epsilon,x)-J||_infinity <= 128 M delta/r0^2,

uniformly when |epsilon| and ||x||_infinity are at most delta. The second bound
includes the row sum over all three x derivatives. It follows by summing
sum_{n>=2} n(4delta/r0)^(n-1), not by pointwise samples.

For the fixed choice delta=2^-9216,

    128 B M delta/r0^2 = 2^-441 < 1/2,
    32 B M delta/r0^2 = 2^-443 < 1/2.

Consequently x -> -J^-1[F(epsilon,x)-Jx] maps the closed x-ball of radius
delta strictly into itself and is a contraction. It gives a unique real root
for each real |epsilon|<=delta; analytic dependence and the vanishing linear
epsilon term give x=O(epsilon^2). Reality follows by conjugation and uniqueness.

The bound is intentionally very conservative. It certifies no inclusion of the
finite +/-1e-5 or +/-5e-6 examples. An interval-certified practical radius would
be a separate later task. This argument concerns the exact continuum constraint
family and the retained fourth-time wall compatibility only, not all-order
compatibility or existence of a hyperbolic spacetime development.
