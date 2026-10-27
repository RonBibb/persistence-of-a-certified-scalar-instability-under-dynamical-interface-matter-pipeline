# An explicit background-bound spectral gap

Status: proposed quantitative corollary for independent review. It strengthens the qualitative compactness gap in the seed-free theorem to a finite explicit expression in exact background bounds. No spectral integration or numerical value is supplied. The estimate is deliberately sufficient and can be very conservative.

Use the original orientation `T_a<0<T_b` and all hypotheses of GENERAL_THEOREM_PROPOSAL.md. A field reflection gives the corresponding result for the opposite orientation. Let q0 satisfy the strict cone bounds (6), and consider the compact trial interval

    I=[-4k-q0²,-4k].

Write

    A=max a,       a_*=min a>0,
    c_a*=1/κ_a0,   c_b*=1/κ_b0,
    d_*=min(|T_a|/2, |B_a0|/κ_a0)>0.

Because d(c_a) is affine and negative, `|d(c_a)|>=d_*` on its interval.

## Explicit zero-shift margin

The auxiliary equation and its positivity proof give

    a²v'>=2,       v_b>=2∫₀ᵇ a^-2 ds>=2b/A².

At zero shifted mass, `f_b/2=-T_bv_b/2` and `R_b/κ_b0=β_b0 v_b/κ_b0`. Its convex-combination residual therefore obeys, uniformly in both wall coordinates,

    G(-4k,c_a,c_b)<=-m0,
    m0=(b/A²) min(T_b, 2|β_b0|/κ_b0)>0.          (1)

## Explicit mass-derivative bound

Use the vector `y=(ψ,f,g)^T`. The regular equation is `y'=M(s,μ)y`, with

             [ -2H          -T/3                 0  ]
    M =      [  0             0                  1  ]
             [  E     V''-μ/a²+2T²             -4H ],
    E=12HT-4V'.

All norms below are suprema over the proper interval. A sufficient bound for the induced infinity norm of M on I is

    L=max(2||H||+||T||/3,
          1,
          ||E||+||V''||+(4k+q0²)/a_*²
                  +2||T||²+4||H||).

Moreover `||M_μ||∞<=B:=a_*^-2`. Uniform launch bounds from (3) are

    Y0=max(1, 3q0² c_a*/d_*,
                  3q0²/(2d_*)+2|T_a|),
    Y1=max(3c_a*/d_*, 3/(2d_*)).

Thus `||y(0)||∞<=Y0` and `||y_μ(0)||∞<=Y1`. Gronwall and variation of constants give

    ||y(s)||∞<=Y0 e^(Ls),
    ||y_μ(b)||∞<=e^(Lb)(Y1+B b Y0).

The second inequality follows by integrating
`e^(L(b-s)) B Y0 e^(Ls)` from 0 to b, along with the initial derivative term. No derivative of the background with respect to μ is present because the background is fixed.

The residual row is `(2c_b T_b, 1/2, c_b)`, whose one-norm is at most

    R0=2c_b*|T_b|+1/2+c_b*.

Consequently

    |G_μ(μ,c_a,c_b)|<=M1,
    M1=R0 e^(Lb)(Y1+B b Y0)>0                  (2)

uniformly on I and the wall rectangle.

## Protected interval

Define

    δ_exp=min(q0²/2, m0/(2M1))>0.              (3)

For `-δ_exp<=λ<=0`, the mean-value estimate using (1),(2) gives

    G(-4k+λ,c_a,c_b)<=-m0+M1|λ|<=-m0/2<0.

The seed-free theorem supplies a root for each wall pair, and its cone argument excludes all roots with λ<=-q0². Therefore every real negative-shifted root lies in the explicit interval

    -q0²<λ<-δ_exp,
    -4k-q0²<μ<-4k-δ_exp.                       (4)

All constants in (3) use exact background values or valid one-sided bounds on them. A rounded exploratory background cannot certify (4). No numerical magnitude is asserted for δ_exp on the inherited model; a very small bound is still a strictly positive analytic separation. On compact exact-background families, uniform coefficient bounds can be substituted throughout to produce one uniform δ_exp.

This provides an explicit sufficient spectral margin and growth-rate margin without locating an eigenvalue. It neither estimates a sharp eigenvalue nor substitutes for the action/background existence and regularity hypotheses.
