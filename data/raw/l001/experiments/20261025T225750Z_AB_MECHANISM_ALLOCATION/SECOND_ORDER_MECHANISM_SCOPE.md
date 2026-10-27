# Full second-order current mechanism: buildable prospective specification

Status: preparation and analytical derivation, not an admitted computation or proved numerical result. No new flow, symbolic evaluation or second-order solve was executed by this author. The intended next physical question is whether the current-induced proper-separation response bends toward stronger shortening or toward saturation at second order. The first-order negative coefficient and required negative c2 do not answer that question separately.

## 1. One action, direction, chart and observable

Authority: `papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md`, selected action (21), background (9), S2, Q1–Q7 and S6–S7. Retain exact authenticated AB background, selected centered oscillator parameters, c(Phi)=1-(Phi-Phi*)/1000, original reflected orientation sigma_a=+1,sigma_b=-1 and all existing numerical premises. Do not substitute the concave example or pure-potential mode.

Proposed first direction, fixed before data: **Na²=1,Nb²=0**, as a formal conserved-current coefficient direction. This is not a finite charge choice. Amplitudes are powers of z=delta² exp(-6 h t), h=sqrt(k), with no factorial convention: p=z p1+z² p2+..., and similarly b,f,xi,chi. The desired coefficient is d_sep,2 in Dproper(z)=D0+z d_sep,1+z² d_sep,2+..., not an estimate of a finite-charge radius.

Freeze the manuscript's **pulled chart**: physical radial coordinate s=r+X(z,r), fixed reference r in [0,D0],

    Xn(r) = xi_a,n + (r/D0)(xi_b,n-xi_a,n),
    Jr=1+X_r, D0op=-6hz partial_z,
    W=(D0op X)/Jr, D=D0op-W partial_r, L=Jr^-1 partial_r.

`D0op` is the temporal differential operator and is not the interval length D0. Use code names `background_length`, `time_operator`, `constraint_coefficient_n2`, and `distance_coefficient_n2`; never overload D2. Background functions are composed with s=r+X. At the walls r=0,D0, X equals the physical xi_i exactly. X1 is this affine interpolant, not a fitted mesh deformation; X1'=(xi_b,1-xi_a,1)/D0 and X1''=0.

The simultaneous spatial proper distance on the specified redshift cut is exactly

    Dproper(z)=integral_0^D0 (1+X_r) exp(b(z,r)) dr.

Consequently

    d_sep,2 = xi_b,2-xi_a,2
              + integral [b2+b1²/2+X1' b1] dr
            = xi_b,2-xi_a,2
              + integral [c2-2p2+2p1²-2X1' p1] dr.

This follows by coefficient extraction, not by interpreting c2 as distance. Both new wall graphs and p2 are indispensable.

## 2. Chart bridge and mandatory invariance control

Let Eulerian perturbation coefficients be defined at fixed physical s with the same coordinate time. Pullback gives

    p2_P = p2_E + X1 p1',
    f2_P = f2_E + X1 f1',
    b2_P = b2_E + X1 b1',
    (f2_P)' = (f2_E)' + X1' g1 + X1 g1'.

Since c1=b1+2p1=0, c2_P=c2_E. Substitution into the pulled distance formula yields

    d_sep,2 = xi_b,2-xi_a,2 + integral(b2_E+2p1²) ds
              + [b1 xi1]_a^b,

because integral(X1 b1'+X1' b1)=[X1 b1]_a^b. This is the same physical length, not a different observable. An independent exact manufactured control must check the equality with nonconstant polynomial p1, a nontrivial affine X1, arbitrary b2_E and nonzero endpoint graphs. The production chart remains pulled throughout; a validated Eulerian bulk-source calculation is only a cross-check after this explicit coefficient transformation.

## 3. Fresh first-order information required

Accepted T10 cells contain p1/f1 basis boxes and E but not the derivative jets needed for complete second-order sources. Reconstructing derivatives by finite differencing those boxes is not admissible.

Run fresh validated first-order flows with the accepted current direction and same frozen action/background/branch. Retain whole-cell background W,H,Phi,T,E and mode p1,f1,g1=f1', plus Taylor coefficients/remainder enclosures sufficient for the direct source algebra. Background derivative relations:

    H'=-T²/3-k E², Phi'=T,
    T'=m² Phi-4HT, E'=-HE.

The first-order regular system gives

    u=p1'=-2Hp1-Tf1/3,
    g1'=-4Hg1+(m²-mu1 E²+2T²)f1+B0 p1,
    B0=12HT-4m²Phi, mu1=-18k.

Differentiate these analytic ODE expressions, not numerical samples, to obtain necessary higher radial jets. Direct composition of T'(r+X) through z² requires derivatives through T''' unless background identities are substituted before coefficient extraction; freeze which route is used and validate equivalence. Needed endpoint records include first-order xi_i,chi_i, p_i,f_i,g_i, background jets, their exact time rates, and full uncertainty in D0. All endpoint traces must enclose the actual uncertain wall, not merely its upper bounding coordinate.

## 4. Source extraction algorithm (implementation specification)

Implement degree-two formal series with interval coefficients. Addition/multiplication are exact truncated convolutions; reciprocal, exp and sqrt use coefficient recurrences with nonzero/positive constant-term gates. This is a z-coefficient computation, not evaluation at a small numerical z. `D0op` multiplies coefficient n by -6nh. Radial differentiation operates on validated derivative jets. Define L,D from S2 as series-valued operators, preserving their noncommutation and the derivative of W when D is applied twice.

For q_{j,2}, set p=z p1, b=-2z p1, f=z f1, X=z X1 and all explicit order-two unknowns to zero. Compose every background B with r+zX1 via B+zX1 B'+z² X1² B''/2. Evaluate the four **exact** S6 expressions, then extract coefficient z². Independently verify that coefficients z0 and z1 are zero using the actual background/first-order equations; do not silently overwrite residuals with zero. An independent extraction implementation should form the formal exact expressions rather than call the same simplified source functions.

Compute r2=-12h, mu2=-108k and

    c2 = -qT2/[r2(r2-h)] = -(3/13)(6p1²+f1²),
    Sp2 = H c2-qM2/r2,
    Sc2 = 12H Sp2-(12H²-T²)c2+qR2,
    Sg2 = T c2'+2m²Phi c2-6T Sp2-qK2.

Use the exact derivative c2'=-(6/13)(6p1 u+f1 g1). The required bulk compatibility is

    Sc2'+4H Sc2 = T Sg2 + constraint_coefficient_n2 Sp2,
    constraint_coefficient_n2=2T²-3(mu2+4k)E².

An exact symbolic reduction against first-order and background equations must qualify this identity independently. A pointwise small residual is not a replacement. The numerical solver must additionally enclose the corresponding residual over every cell.

### Eulerian source cross-check, not production substitution

At X=0, let R=-6h,p=p1,f=f1,g=f1',u=p1'. Manual expansion gives

    qM2 = R(2pu+fg/3),
    qK2 = (4m²-6mu1 E²)pf+6ug-8m²Phi p²,
    qR2 = 6u²-g²/2+4p(12Hu-Tg)
          +8p²(6H²-T²/2)+m²f²/2-E²(12kp²+18kf²),
    Sp2 = Hc2-pu-fg/6.

These are manually checked candidate formulas, not yet executed qualifications. Compare them to independent direct S6 series extraction and exact compatibility reduction. Their pulled counterparts must include the chart bridge above. For example Sp2_P=Sp2_E+X1' u-X1(2H' p+T' f/3), obtained from the transformed regular momentum equation. Do not substitute Eulerian q values directly into the pulled computation.

## 5. Full wall sources and material data

At each endpoint use the truncated **actual graph** S_i=s_i+z xi_i,1, not a frozen-wall evaluation. Let all quantities below be pulled to that wall:

    N=a(S) exp(p), B=exp(b), v=(B/N) S_t,
    ell=N sqrt(1-v²), chi=z chi1, S_t=D0op(z xi1).

Wall total time derivatives (including chi_t and p_t^wall) are D0op at fixed reference endpoint. Bulk Db,Dp,Df are the physical S2 D operator. Do not interchange them at second order. Reconstruct conserved current exactly as a series:

    nu²=z Ni² a(S)^-6 exp(-6p), rho_m=c(Phi_wall)nu²,
    Phi_wall=Phi0(S)+f, c=1-(Phi_wall-Phi_i*)/1000.

With deltaPhi1=T_i xi_i,1+f1_i and A_i=H_i xi_i,1+p1_i, useful independent controls are

    [z]nu²=Ni² Ei^6,
    [z²]nu²=-6 Ni² Ei^6 A_i,
    [z²]rho_m=Ni² Ei^6[-6A_i-deltaPhi1/1000],
    [z²](c_Phi nu²)=6 Ni² Ei^6 A_i/1000.

For the selected quadratic wall/centered oscillator, tau_Phi+W_Phi=2sigma_i T_i+21(Phi_wall-Phi_i*)-chi. Preserve the displaced neutral trace. W=chi²/2+[chi-(Phi_wall-Phi_i*)]²/2 contributes at z² to surface stress; oscillator kinetic stress chi_t²/(2ell²) also first contributes at z² and **must not be omitted**.

Extract qI2 as coefficient z² of S7 minus rho_m minus chi_t²/(2ell²):

    S7 = sigma/[N sqrt(1-v²)] * [v_t/(1-v²)+v(Db-h-Dp)].

Then xi_i,2=-qI2/[sigma_i Ei² r2(r2-h)]. Extract o_i,2 and j_i,2 directly from the exact Q5 oscillator and normalized scalar residuals using the same truncated graph/material data. In particular retain:

    oscillator = ell^-2 {chi_tt + [3h+2H(S)S_t+2p_t^wall
                                   +v v_t/(1-v²)]chi_t}
                 +2chi-[Phi0(S)-Phi_i*+f];
    scalar_normal = [exp(-b)(T+Lf)+v exp(-p)E Df]/sqrt(1-v²)
                    -sigma/2[tau_Phi+W_Phi+c_Phi nu²].

All sources use order-one data only. Once xi2 is obtained, form the full Q6 load

    d2_i=2-mu2 Ei², Gamma2_i=21-1/d2_i,
    R2_i=2sigma_i {T_i c2_i
          -(T_i'-sigma_i Gamma2_i T_i/2)xi_i,2
          -j_i,2+sigma_i o_i,2/(2d2_i)}.

Reconstruct chi_i,2=(f2_i+T_i xi_i,2-o_i,2)/d2_i. Reconstruct the phase from the conserved-current equation and current–scalar exchange; do not treat a phase integration constant as a source for the geometric coefficient. Independently evaluate original scalar, oscillator, tracefree Israel and spatial Israel coefficients at order2 after assembly, plus the material exchange law. Bianchi/Codazzi identities may justify redundant equations only after their actual prerequisites are established; they are not permission to omit the wall sources.

## 6. Concrete regular solver architecture

Retain the regular p,f,g system, never divide by T at its turn:

    p2'=-2Hp2-T f2/3+Sp2,
    f2'=g2,
    g2'=-4Hg2+(m²-mu2 E²+2T²)f2+B0 p2+Sg2,
    T g2-T' f2+constraint_coefficient_n2 p2=Sc2.

Integrate a homogeneous n2 basis and a loaded particular basis with the same background/first-order source jet flow. A coupled augmented Taylor/Picard enclosure can share those source states; importing the old homogeneous engine without extending its validated RHS/remainder argument is insufficient. Independently implement the second engine's variable convention and source evaluation.

At the lower wall choose p2_a=1 for homogeneous and0 for particular. With B_a=Gamma2_a T_a/2-T_a', lambda2=mu2+4k, launch the loaded basis by

    f2_a=[Sc2_a+3lambda2 Ea² p2_a-T_a R2_a/2]/B_a,
    g2_a=Gamma2_a f2_a/2+R2_a/2-2T_a p2_a.

The homogeneous launch sets all second-order sources and R2_a to zero. Gate B_a away from zero. At the upper wall use F=g2+2T p2+Gamma2 f2/2. The multiplier is (-R2_b/2-F_particular)/F_homogeneous; require the entire uncertain-wall homogeneous determinant to exclude zero. No endpoint rescue or changed normalization if it does not.

## 7. Uncertain domain and integration

Retain the authenticated interval D0 in X1', X2' and all boundary maps. The actual D0 is one common parameter, not independent walls chosen separately. Interval arithmetic may drop correlations only outwardly. Either integrate in physical-reference r with interval D0 as a fixed parameter and the existing endpoint strip, or redesign prospectively for x=r/D0; the latter changes the ODE scaling and requires independent qualification. Recommended first implementation: existing r plus parameter interval, no coordinate redesign.

Integrate the complete signed distance integrand over mandatory [0,Dlo] and optional [Dlo,Dhi] with interval width [0,Delta]. Include zero in every optional contribution. Keep xi_b,2-xi_a,2 outside the integral. Save per-cell outward rational contributions and sum those exact exported intervals in the producer. Whole-cell endpoint/graph and source values must enclose the same actual D0. Check the Eulerian/pulled integrated identity independently without intersecting estimates to obtain a preferred sign.

## 8. Admission, failures and intended conclusion

Before launch require: independently audited exact source extractor; full wall source checks; first-order parent replay and matching normalization; analytic compatibility identity; new augmented-engine enclosure/remainder validation; both engine whole-cell residual and denominator gates; manufactured zero-source and nonzero polynomial graph controls; prospective runtime/memory probe and fixed resource cap. Freeze one direction, all source bytes, exact parents/runtime and acceptance criteria. Runs longer than one hour need atomic exact-resumption checkpoints; do not promise a subhour full run until sized.

After both engines pass, report d_sep,2 and its uncertainty, with the chart contributions labeled diagnostic only. A sign can identify local curvature of the formal distance-versus-current response at zero charge. It cannot establish saturation at a finite charge, a convergence radius, a stable end state, neutral-mode excitation or an event horizon. Any source compatibility or technical failure is incomplete qualification, not a physical adverse result. At present all production source formulas and new solver architecture remain prospective; the manuscript and accepted first-order packets supply inherited premises, not an already executed second-order certificate.
