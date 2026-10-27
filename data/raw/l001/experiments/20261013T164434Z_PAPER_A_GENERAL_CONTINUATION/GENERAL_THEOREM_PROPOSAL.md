# Seed-free curved Einstein–scalar wall-response theorem

Status: proposed analytic theorem for independent review. No numerical execution. This extends the predecessor response theorem by proving existence without an inherited numerical eigenvalue, using an explicit large-negative-mass cone argument. The extension to general bulk potentials is part of its reusable formulation, not a priority claim.

## Hypotheses and equations

Consider the canonical doubled-cover action with bulk density
`(R+12)/2 - (∇Phi)^2/2 - V(Phi)` and pure wall potentials `tau_a,tau_b`, with no wall kinetic or induced Einstein terms. Use the same straight-wall generic scalar sector and normalizations as the independently accepted formulation. Suppose an exact smooth finite background exists on `0<=s<=b`, with `b>0`, `a>0`, `a(0)=1`, `H=a_s/a`, `T=Phi_s`, and `k>0`. The action's background equations include

    H_s = -T²/3-k/a²,       T_s = V'(Phi)-4HT.

Take V at least C³ on a neighborhood of the background scalar range. This is sufficient for the identities below; smooth V is allowed. Existence of this background and its background wall junctions are hypotheses, not conclusions. Fix positive baseline Hessians `κ_a0,κ_b0` and suppose

    T_a<0<T_b,
    B_a0=κ_a0 T_a/2-T'_a<0,
    β_b0=-κ_b0 T_b/2-T'_b<0.                       (H)

Here and below prime on a background quantity denotes proper-distance derivative. Add `(κ_i-κ_i0)(Phi-Phi_i*)²/2` to each wall potential, with `κ_i>=κ_i0`. This preserves the entire given background. Put `c_i=1/κ_i` and include `c_i=0` as a Dirichlet boundary limit only. The parameter rectangle is `K=[0,1/κ_a0]×[0,1/κ_b0]`.

For physical mass squared μ and shifted mass λ=μ+4k, the regular equations are

    ψ'=-2Hψ-Tf/3,       f'=g,
    g'=-4Hg+(V''-μ/a²+2T²)f+(12HT-4V')ψ,
    C=Tg-T'f+(2T²-3λ/a²)ψ=0.                       (1)

These follow from the same scalar and Einstein variations as the predecessor: scalar variation replaces the potential slope by V' and its linear variation by V''f. Differentiation gives `C'=-4HC` using the two background identities. Thus an initially constrained regular solution stays constrained; no interior division by T occurs. The regular kinetic norm is

    Z=2∫₀ᵇ a²(f²+6ψ²)ds>0                       (2)

for nonzero real profiles. Potential replacement does not change the tangential kinetic terms of the action. The theorem is conditional on this action/sector interpretation; it is not a theorem about arbitrary modified gravity or additional wall degrees of freedom.

Define `L=g+2Tψ`, `d(c_a)=T_a/2-T'_a c_a`. Hypotheses (H) make d strictly negative on its compact interval. The normalized launch and residual are

    ψ_a=1,
    f_a=3λ c_a/d(c_a),
    g_a=3λ/[2d(c_a)]-2T_a,
    G(μ,c_a,c_b)=c_b L_b+f_b/2.                    (3)

They enforce `L_a=κ_a f_a/2` at finite κ_a and `f_a=0` at c_a=0, and G=0 enforces the upper Robin/Dirichlet condition. The launch is constrained. Every nontrivial retained mode admits this normalization when λ<0: if ψ_a=0, the lower constraint and d≠0 force f_a=0, then g_a=0. At c_a=0 use T_a≠0 and the constraint. The regular finite-interval IVP implies G is analytic in μ,c_a,c_b near the compact rectangle, even when V is only smooth: its s-dependent coefficients are fixed and its spectral dependence is polynomial. No claim of analyticity in a merely smooth background-family parameter is made.

## Lemma 1: uniform negative auxiliary sign

At λ=0 set `f=Tu`, `ψ=-u'/2`, with

    u''+2Hu'-(2/3)T²u=0,       u(0)=0, u'(0)=-2.

The background identity needed for direct substitution is

    T''=-4HT'+(V''+4k/a²+4T²/3)T.

Substitution into (1) verifies both regular dynamical equations, and the constraint follows directly. This gives the launch (3) independently of c_a. With v=-u,

    (a²v')'=(2/3)a²T²v,       v(0)=0,v'(0)=2.

A first-loss-of-positivity argument gives v,v'>0 on (0,b]. Hence ψ_b>0 and f_b=-T_bv_b<0. At λ=0 the upper baseline residual `R_b=L_b+κ_b0 f_b/2` obeys `T_b R_b+β_b0 f_b=0`, so R_b<0. Consequently

    G(-4k,c_a,c_b)
      =(κ_b0 c_b)(R_b/κ_b0)+(1-κ_b0 c_b)f_b/2<0. (4)

The auxiliary profile supplies an endpoint sign; no exceptional-sector physical eigenmode assertion is needed. Compactness gives a uniform root-free neighborhood of μ=-4k on K.

## Lemma 2: explicit uniform positive sign at sufficiently negative mass

Set λ=-q² with q>0 and `D=2T²+3q²/a²>0`. For the already-existing constrained regular IVP, the constraint gives

    ψ=(T'f-Tg)/D.

This is division by a strictly positive quantity, including at every scalar turn. Put `E=12HT-4V'=-4(T'+HT)`. Along that same regular solution,

    f''=P_q f'+Q_q f,
    P_q=-4H-E T/D,
    Q_q=q²/a²+V''+4k/a²+2T²+E T'/D.             (5)

No converse reconstruction is required: (5) is a consequence of the propagated constraint and the original IVP. For explicit sufficient bounds define suprema over [0,b],

    A=max a,
    P0=4||H||∞+(A²/3)||ET||∞,
    Q0=||V''+4k/a²+2T²||∞+(A²/3)||ET'||∞,
    r=min(κ_a0/2,1)>0.

Choose any q satisfying

    q²>=1,
    q²>A²(Q0+r P0+r²),
    3q²r/a_b²>2|T_b T'_b|.                       (6)

All constants are finite because the background is smooth, finite and has positive warp factor. Since D>=3q²/A², (6) gives `|P_q|<=P0`, `Q_q>=q²/A²-Q0`, and `Q_q+rP_q-r²>0` uniformly.

At finite c_a, f_a>0 and

    g_a-r f_a=(1/(2c_a)-r)f_a-2T_a>0.

At c_a=0, f_a=0 and g_a>0. For `h=g-rf`, a boundary point h=0 with f>0 has

    h'=(Q_q+rP_q-r²)f>0.

The cone f>=0,h>=0 is forward invariant, and the initial data enter its interior immediately when f_a=0. Thus f>0 and g>=rf>0 for s>0. At b,

    L_b=(3q²g_b/a_b²+2T_bT'_b f_b)/D_b>0.

Therefore

    G(-4k-q²,c_a,c_b)>0 for every (c_a,c_b)∈K, (7)

including c_b=0. Conditions (6) are an explicit sufficient mass bound, not a sharp estimate or a numerical certificate.

## Theorem: seed-free existence and compact continuation

Equations (4),(7) and the intermediate value theorem give at least one real root

    -4k-q²<μ<-4k

for every reciprocal-Hessian pair in K, without an inherited eigenvalue or a spectral integration. Every such root has positive regular norm and is simple.

For completeness, the general-V regular Green identity follows in proper distance as follows. For two constrained profiles set `U=ψ_i f_j-f_i ψ_j`, `W=f_i g_j-g_i f_j`, `Δμ=μ_i-μ_j`. The equations give

    W'=-4HW+Δμ f_i f_j/a²+4(T'+HT)U,
    TU'=(T'-2HT)U-3Δμ ψ_iψ_j/a².

Consequently `J=a⁴(W-2TU)` obeys

    J'=Δμ a²(f_i f_j+6ψ_iψ_j).                 (8)

No T division occurs. At equal lower boundary parameters the lower J vanishes, including c_a=0. At an upper root, L_b≠0: if L_b=0, G=0 forces f_b=0, and the constraint with λ<0 forces ψ_b=0 and hence g_b=0, contradicting the launch. Comparing the root with nearby masses gives `J_b=-2a_b⁴L_b G`, so

    G_μ=Z/(4a_b⁴L_b)≠0.                         (9)

The same boundary identity, allowing wall Hessians to differ, gives on finite walls and by continuity on the faces

    μ_ca=-9λ²/(d(c_a)²Z)<0,
    μ_cb=-4a_b⁴L_b²/Z<0.                         (10)

Choose any root at the baseline corner (one exists by the preceding argument). Along each straight segment from that corner towards a target in K, both c coordinates decrease, so μ increases. The branch is bounded below by its starting mass and above by the uniform root-free neighborhood from Lemma 1. Any finite obstruction has a limiting normalized root in this compact mass interval; (9) makes it simple and the implicit-function theorem extends it. A finite chain of overlapping simple-root neighborhoods along the segment gives smooth target dependence and compatibility for nearby targets. Thus this chosen root defines a single analytic response surface on K, locally extending through each face and corner. Other roots are not excluded or identified with this branch.

Write μ_DD for its double-Dirichlet corner value. For every finite κ_a,κ_b at or above baseline,

    μ(c_a,c_b)<=μ_DD<-4k<0,

with strict first inequality away from the DD corner and strict response to either stiffness. In particular every background satisfying (H) admits a regular positive-norm negative scalar mode under every such wall stiffening, including the Dirichlet limits. This is a sufficient instability theorem for the stated generic scalar sector. It does not classify all modes, identify the lowest eigenvalue, construct nonlinear evolution, or establish any horizon claim.

## Remaining review questions

Independent review should check the general potential variation/constraint propagation; signs and factors in (5),(8); the uniform cone bound (6); the auxiliary endpoint signs; face simplicity; and global continuation compatibility. A further corollary may quantify the stiff-limit deficit and fixed-budget allocation after this theorem is admitted. No numerical test has been launched and no action/background existence claim has been substituted for the explicit hypotheses.
