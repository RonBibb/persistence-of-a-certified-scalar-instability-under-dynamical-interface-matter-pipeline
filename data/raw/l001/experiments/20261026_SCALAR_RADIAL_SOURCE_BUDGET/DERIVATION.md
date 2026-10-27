# Scalar and radial nonlinear source bounds

These estimates cover the Klein–Gordon and radial constraint sources and the compatible reconstructed loads S_c, S_g and F. They complete the four raw bulk source budgets, conditional on the inherited recursion and analytic estimates. Wall sources, response constants on this working collar, and full nonlinear closure remain separate requirements.

## Common domain and notation

Use the fixed working collar rho=1/40000 inside the authenticated background collar R=1/20000. Let y=Y_<n be the nonnegative lower-order envelope in the working-collar norms, a=2/rho=80000 and G=(1-a*y)^(-1). All perturbations have positive order. Write Hbar,Tbar,Pbar,Ebar for the prior background suprema, m for an upper bound on the absolute potential coefficient, and kplus for the upper k bound. Exact equations below use the signed coefficient mathfrak_m; absolute estimates use m. Superscript s means evaluation at r+X. Unmarked background coefficients in linear rows are evaluated at r.

Every prior analytic background function with supremum M has composition bound M*G and difference bound M*a*y*G. This applies separately to E^2 and A=6H^2-T^2/2 with bounds Ebar^2 and Abar=6Hbar^2+Tbar^2/2. No multiplication of background suprema is treated as a new physical parameter.

## Shared jet bounds

Set hstar=1/50 and g=6hstar=3/25. The inherited affine graph gives Jinv <= (1-y)^(-1) <= G, W <= 2g*y*G and W_r <= g*y*G. Because X_rr=0, L^2 v=Jinv^2 v_rr. In coefficient norms, with indices accounted for before simplification,

    exp(-2u) <= G,
    exp(-2u)-1 <= 2yG,
    exp(-2u)-1+2u <= 4y^2G,
    Lv-v_r <= y^2G,
    L^2v-v_rr <= 2y^2G^2,
    Dv <= 2g*y*G.

These comparisons mean absolute-coefficient bounds, not signed inequalities between functions. Define A_v=D^2v+3hDv and A0_v=D0^2v+3hD0v. Then

    A0_v <= t*y,                  t=g^2+3hstar*g,
    A_v-A0_v <= d*y^2*G^2,       d=14g^2+6hstar*g.

Indeed the transport difference is -2W D0v_r+(W W_r-D0W)v_r+W^2v_rr-3hWv_r. Its bound before simplification is (6g^2+6hstar*g)y^2G+8g^2y^3G^2. The coefficientwise inequality y*G^2<=G^2, valid because a>=1, gives d. Extra radial indices are supplied by the positive-order graph factors; the bulk target index is 2n+2. Nontransport products of two first radial jets already fit that index.

For P_E=(E^s)^2 exp(-2p), P_E <= Ebar^2 G^2 and P_E-E^2 <= Ebar^2(a+2)yG^2. All estimates are formal coefficientwise. Numerical evaluation of the rational majorants requires a*y<1.

## Exact background cancellation

Using T'+4HT=mathfrak_m*Phi, the exact Klein–Gordon row is

    -P_E[A_f+(2Dp+Db)Df]
    + exp(-2b)[L^2f+4H^s Lf+(4Lp-Lb)T^s+(4Lp-Lb)Lf]
    + mathfrak_m*Phi^s[exp(-2b)-1] - mathfrak_m*f.

The exact radial row, after subtracting its vanishing background identity, is

    A^s[exp(-2b)-1]
    + exp(-2b)[12H^s Lp-T^s Lf+6(Lp)^2-(Lf)^2/2]
    + mathfrak_m*Phi^s*f + mathfrak_m*f^2/2
    -6k(E^s)^2[exp(-2p)-1]
    -3P_E A_p - P_E[3(Dp)^2+(Df)^2/2].

For each row remove its full linearization about the neutral solution. Its order-n coefficient on a lower-order truncation is zero. Pure background graph terms have already canceled identically, not merely been bounded.

## Raw source constants

Both raw sources at index 2n+2 are bounded by their respective constants times [z^n]y^2G^4. The Klein–Gordon constant is

    C_K = Ebar^2[(a+2)t+d+12g^2]
          +9+(4Hbar+5Tbar)(a+3)+m*Pbar(4+2a).

The temporal coefficient change and transport remainder supply Ebar^2[(a+2)t+d]; the temporal quadratic product supplies 12Ebar^2g^2. The L^2 term supplies 4, the purely spatial bilinear term supplies 5, H and T terms supply (4Hbar+5Tbar)(a+3), and the displaced potential term after linear removal supplies m*Pbar(4+2a).

The radial constant is

    C_R = Abar(4+2a)+(12Hbar+Tbar)(a+3)+13/2
          +m*Pbar*a+m/2+6kplus*Ebar^2(4+2a)
          +3Ebar^2[(a+2)t+d]+14Ebar^2g^2.

The terms respectively bound the background A times the exponential remainder and composition difference, spatial linear-jet coefficient changes, spatial quadratic products, potential terms, the background temporal exponential term, the threefold temporal linear-jet remainder, and temporal quadratic products. Denominators of degree below four are increased to G^4 coefficientwise. No finite order scan is used to infer these all-order bounds.

## Reconstructed bulk loads

Let C_T and C_Sp be the audited tracefree and mixed constants on this same working collar. The compatible identities give

    C_Sc = 12Hbar*C_Sp+(12Hbar^2+Tbar^2)*C_T+C_R,
    C_Sg = (Tbar+2m*Pbar)*C_T+6Tbar*C_Sp+C_K,
    C_F = C_Sg+(12Hbar*Tbar+4m*Pbar)*C_Sc/dcomplex.

Here dcomplex is the authenticated positive lower bound on |D_n|/n^2 from the background collar. These constants bound S_c, S_g and F at index 2n+2 against the same [z^n]y^2G^4. Factors 1/n and 1/n^2 are discarded only using n>=1. No analytic-index gain from division by D_n is asserted. The reconstruction uses the established compatible source identities rather than proving solvability for arbitrary loads.
