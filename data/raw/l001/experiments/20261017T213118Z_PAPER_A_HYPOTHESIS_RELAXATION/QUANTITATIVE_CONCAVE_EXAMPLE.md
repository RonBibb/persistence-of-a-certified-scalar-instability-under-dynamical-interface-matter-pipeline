# An exact concave example on a specified finite interval

Status: analytical proposal for independent terminal review. A rational first-exit estimate makes the second example in RELAXED_HYPOTHESIS_THEOREM.md quantitative: its exact background exists on the prescribed proper interval [-1/100,1/100], not merely on an unspecified neighborhood. No ODE integration or sampled enclosure is used. The wall potentials are constructed from this unique exact solution; they are not Paper A's original fixed walls.

## 1 Exact problem and bounding rectangle

Use the same canonical doubled-cover action and background equations, with

    V(Phi)=Phi-Phi²/2+Phi⁴,
    a(0)=1, H(0)=-2, Phi(0)=0, T(0)=0, k=3.

The initial Hamiltonian constraint is exactly 4-1-3=0. Smoothness and its exact propagation preserve it. Let h=1/100, and use the closed rectangle

    a in [9/10,11/10],  H in [-21/10,-19/10],
    Phi in [-1/100,1/100],  T in [-1/50,1/50].        (1)

The initial state is strictly inside (1), whose distances from that state to its faces are respectively 1/10,1/10,1/100,1/50. The vector field is smooth on an open neighborhood of this compact positive-warp rectangle.

## 2 First-exit estimate in both directions

Throughout (1), the absolute derivatives satisfy

| State | Bound M on its absolute derivative | h M | Distance to face |
|---|---:|---:|---:|
| a | 231/100 | 231/10000 | 1/10 |
| H | 100/27+1/7500 = 250009/67500 | 250009/6750000 | 1/10 |
| Phi | 1/50 | 1/5000 | 1/100 |
| T | 294501/250000 | 294501/25000000 | 1/50 |

Every displacement is strictly smaller than the corresponding face distance. The first row follows from |Ha|. The second uses |H'|=T²/3+3/a². The last uses

    |1-Phi+4Phi³-4HT|
      <=1+1/100+4/1000000+4(21/10)(1/50)
      =294501/250000.

If the exact solution first reached a face at some |r|<=h, integrating its derivative from 0 to that r while the solution remains in (1) would place it strictly inside every face, a contradiction. This works identically backward because it uses absolute derivatives and |r|. A solution that remains in a compact subset of the smooth ODE domain extends through any purported finite maximal endpoint. Thus the unique exact background exists throughout [-h,h] and stays strictly inside (1). This is an analytic a priori enclosure, not a numerical Picard iteration or a replacement for the original background certificate.

## 3 Strict geometry and coefficient bounds

On the entire interval,

    T'=1-Phi+4Phi³-4HT
       >=1-1/100-4/1000000-4(21/10)(1/50)
       =205499/250000>0.                             (2)

Therefore T is strictly increasing, with its unique zero at r=0, and

    T(-h)<=-205499/25000000<0,
    T(h)>=205499/25000000>0.                         (3)

At every traversed point,

    V''=-1+12Phi² <= -2497/2500 <0,                   (4)
    Q=V''+12/a²+4T²/3
       >= -1+1200/121 =1079/121>0.                   (5)

Thus the scalar potential is strictly concave across the entire traversed range, while the weaker background coefficient criterion holds with a substantial positive margin. The potential is globally bounded below because its leading quartic coefficient is positive. Warp is positive and curvature k=3>0. These conclusions follow from exact rational inequalities, not floating approximations.

## 4 Normalization and exact wall construction

Put s=r+h and normalize at the lower wall:

    a_new(s)=a(r)/a(-h),  k_new=3/a(-h)².

This preserves k/a², H, Phi,T and all proper-distance equations. The exact interval length is D=2h=1/50. The bounds imply

    9/11 <= a_new <= 11/9,
    300/121 <= k_new <= 100/27.

Define Phi_a=Phi(-h),Phi_b=Phi(h), and likewise H_i,T_i from the unique exact IVP. For any nonnegative finite Hessians kappa_i, set

    tau_a(Phi)=-6H_a+2T_a(Phi-Phi_a)+kappa_a(Phi-Phi_a)²/2,
    tau_b(Phi)= 6H_b-2T_b(Phi-Phi_b)+kappa_b(Phi-Phi_b)²/2.

These are exact smooth pure wall potentials defined by the uniquely specified IVP values; no rounded endpoint values are substituted. They satisfy the two junction conditions at each endpoint. H remains negative, so tau_a(Phi_a)>0 and tau_b(Phi_b)<0. Changing kappa_i preserves the background wall values/slopes. Dirichlet limits refer to the limiting perturbation problem.

The relaxed index theorem now gives exactly one regular scalar eigenvalue below -4k_new for every nonnegative wall-Hessian pair and both Dirichlet faces, with the stated symbolic gap and monotone response. The explicit finite interval and negative V'' demonstrate an actual exact nonconvex example, not just a formally weaker inequality on an unexhibited background.

## 5 Scope of the construction

The action's bulk potential and the wall construction differ from the original certified model. There is no claimed astrophysical calibration, global bulk completion, fixed-original-wall realization or total physical tachyon count for this example. The current proof counts only the sector below -4k_new. Its purpose is to establish constructively that the reusable theorem need not assume potential convexity, even with a positive lower and negative upper wall tension and the original negative cosmological term at the central scalar value.

No new numerical test, parameter scan or interval trajectory was run. A future explicit metric plot or remaining-band count would be a distinct computation; neither is required for this exact existence and restricted-index argument.
