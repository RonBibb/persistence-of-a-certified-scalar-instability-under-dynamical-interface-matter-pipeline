# Weighted all-k response estimate without the alpha ratio

Existing reviewer seed_gate_review; hand derivation only. No new background, response, parameter, CAS or numerical evaluation has been executed. Sources are the 17 frozen packet inputs. This improves the sealed predecessor's deliberately conservative sufficient bound; that prior bound and its untested status remain unchanged. The present proof is CONDITIONAL on the exact background gates stated below until the prospectively admitted interval stage certifies them.

## 1. Actual canonical response and both walls

At the zero-charge anchor take reference time zero and instantaneous isothermal r. The actual mean retains q/Pq with deltaPq=2 average_r(deltaA); all four wall canonical momenta and both bulk canonical fields remain inputs. Set

    alpha=a^3, h^2=k_dS>0, g=alpha'/alpha,
    t=deltaA+h alpha w, P_sigma=delta p_sigma-24h alpha w,
    Q=partial_r-g, v=Qw=alpha y', y=w/alpha.

The exact C8/K1 identity on the ACTUAL coupled constraint response is

    (Qdagger Q+k^2-3h^2)w=f,
    f=(h/alpha)(-t+P_sigma/2).

At this zero-background wall momentum, the linear energy endpoints imply Qw=0 at BOTH walls, hence v is Dirichlet. This includes pure wall momentum inputs: their first-order energy source vanishes, while their kinetic squares remain positive. The physical supplied mean changes the momentum solution, not this scalar identity or its Robin law.

The previous scalar-only ground crossing is not inverted. Applying Q removes the alpha ground and yields the regular Dirichlet equation

    (Q Qdagger+k^2-3h^2)v=Qf.

Initially use smooth inputs; the source Qf is a distribution for general L2 momenta. Its weak pairing below uses only f in L2 and v in H1_0, so the extension to the canonical form domain is continuous. The C5/R2 coupled inverse supplies the actual response and the necessary regularity; no scalar-only existence assertion replaces it.

## 2. Weighted cancellation

Exact background equations give

    g'=g^2/3-a^2 T^2-3h^2,
    Vplus=g^2-g'=6a^2 H^2+a^2 T^2+3h^2,
    H_s=-T^2/3-h^2/a^2,
    H^2=1+T^2/12-m Phi^2/12+h^2/a^2.

Test the Dirichlet equation with alpha v. Boundary terms vanish because v=0, not because the original pressure endpoints were omitted. Its exact real/Hermitian identity is

    A=integral alpha[|v'|^2+(k^2+3h^2/2+3a^2 T^2/2)|v|^2]
     =-Re integral alpha conj(f)(v'+2g v).

Put u=sqrt(alpha)v and E=integral|u|^2=integral alpha^3|y'|^2. A second integration by parts gives the especially useful equivalent form

    A=integral[|u'|^2+(k^2+15a^2 H^2/4+a^2 T^2)|u|^2],
    A=-Re integral sqrt(alpha)conj(f)(u'+3g u/2).

This eliminates the previous alpha_max/alpha_min loss. It is an exact same-background identity, not a weighted norm guessed from the unweighted real estimate.

Let N=||u'+3g u/2||^2. The same identities give

    N=integral[|u'|^2+(7g^2/4+3a^2 T^2/2+9h^2/2)|u|^2]
      <=(21/5)A+(9/2)h^2 E.

Indeed A's g^2 coefficient is 5/12, so multiplication by 21/5 exactly matches 7/4; its derivative, T^2 and k^2 coefficients dominate the remainder. No profile derivative sign assumption, Phi-gradient denominator, oscillator division or spatial-frequency restriction is used.

The canonical source Cauchy-Schwarz estimate has the matching weight:

    ||sqrt(alpha)f||^2
      =h^2 integral alpha^-1|-t+P_sigma/2|^2
      <=(13/2)h^2 S.

All omitted terms of S are nonnegative; none is removed from the physical datum space.

## 3. All-radial/all-k comparison

If A>=lambda E for some lambda>0, then

    N <= [21/5+9h^2/(2lambda)]A,
    A <= [(13/2)h^2 S N]^(1/2).

For A nonzero, divide only by positive A and lambda. For A=0, E=0 and the response estimate is immediate. Therefore, with x=h^2/lambda,

    E <= theta S, theta=(13/2)x[21/5+(9/2)x].

Both original wall remainders enter the predecessor's exact completion

    R=integral alpha^3 Vplus|y+(g/Vplus)y'|^2
                     -integral alpha^3(g^2/Vplus)|y'|^2
      >=-(3/2)E.

It follows for EVERY real tangential k and every admitted radial input that

    K=S+R >=(1-Delta)S,
    Delta=(39/4)x[21/5+(9/2)x].

This applies to nonzero Fourier modes and the actual supplied physical mean separately. The proof is uniform in k because the k^2 term in A was only used positively. It covers the full radial domain, not a finite polynomial span or a sampled frequency band.

## 4. Coarse exact-background gates sufficient for a strict margin

Proposed gates, not evaluated by this hand note:

    a>1/8 on the whole actual collar,
    m Phi^2<1 on that collar,
    0<h^2<1/3000.

The source-bound scalar maximum principle already supplies a qualitative route to m Phi^2<1; a rigorous interval propagation can independently enclose all three on the exact-root parameter boxes. The a gate is the same as Ewarp=1/a<8. The constraint identity implies H^2>11/12, hence

    A >=lambda E, lambda=55/1024.

Thus x<1024/165000<1/100. Without any evaluation of actual profile parameters, integer rational comparison gives

    Delta < (39/4)(1/100)[21/5+9/200]
          =33111/80000 <1.

In particular the coarse gates already imply K>(46889/80000)S. Using the displayed unsimplified rational x bound would give a stronger margin. This is a theorem conditional on rigorous gates; neither floating midpoint samples nor predecessor diagnostic matrices certify those gates or this conclusion.

The background error issue is handled prospectively by enclosing every exact solution on the inherited A,D boxes and using the exact upper-wall identities at the accepted root. Arbitrary box members need not satisfy the upper Robin law; the proof is applied to the inherited exact root within the box, whose pressure endpoints are exact. A new BVP/root choice is neither needed nor allowed. Interval gate failure is inconclusive, not a negative kinetic witness.

## 5. Input norm, mean and limits

S is a bounded positive bare multiplication plus compact response on the canonical bulk L2 inputs and the finite wall coordinates. The physical homogeneous fiber additionally retains the finite independent Pq slot. It is not identified with the limiting auxiliary zero fiber.

If S=0, all residual squares vanish, hence f=0. The weighted identity and lambda>0 force u=Qw=0, so w=c alpha. At a nonzero k, b=ik zeta=0 and deltaA=zeta'=0; t=0 then forces c=0. In the actual mean at k=0, the scalar identity becomes -3h^2 c alpha=0, so c=0 as well. Every input momentum and its mean therefore vanishes. The same separate argument applies to the auxiliary zero-mean family used for nonzero-k compact-band limits.

Positive essential spectrum, nonnegative S and absence of a kernel yield a positive input-norm lower bound at each fixed fiber. The accepted coupled inverse's common-domain operator continuity and compactness give a uniform bound on each compact k/time band; the high-k parameter estimate supplies the remaining tail. The physical mean is included separately, not by continuity across fibers of different dimensions. This produces an honest uncomputed coercive canonical norm once the exact gates are certified, rather than merely pointwise positivity on smooth vectors. Time rescalings must be carried explicitly; no all-future unweighted uniform norm is claimed.

Small-charge transfer would additionally require the actual common-chart form/inverse continuity on a fixed compact slab and uniform high-k coefficient bounds. One can split a compact low-k band from the uniform ultraviolet tail; coefficient continuity alone is insufficient. This note does not by itself certify an explicit charged amplitude, old-cap equivalence, global infrared gauge map, nonlinear stability or absence of the inherited growing stiffness direction.

Current result: WEIGHTED HAND DERIVATION PASS, CONDITIONAL ALL-MODE CANONICAL LOWER BOUND; ACTUAL BACKGROUND GATES NOT YET NUMERICALLY CERTIFIED. No scientific execution or successor is authorized by this note.
