# Cubic moving-wall source construction

Prospective source derivation only: no symbolic or numerical execution has occurred in preparing this file. `wall.py` implements direct Q5 coefficient extraction and requires the caller to supply the authenticated degree-three `S` class from the accepted cubic graph packet. Both wall orientations are the integer values sigma=+1 and -1. Ordinary powers of z are used throughout.

Let X=xi1 z+xi2 z²+xi3 z³, r=-6h. For a background A, the coefficient of z³ in A(s+X) is A' xi3+A'' xi1 xi2+A''' xi1³/6. For a perturbation z v1+z² v2+z³ v3 it is v3+xi2 v1'+xi1² v1''/2+xi1 v2'. These identities fix every displacement term in the code rather than importing a pulled-chart load.

In particular, the radial metric trace is b1=-2p1, b2=c2-2p2, b3=c3-2p3. Its composed cubic coefficient is c3-2p3+xi1(c2'-2p2')-2xi2 p1'-xi1² p1''. The scalar-normal radial trace needs f1''' and f2'', while its background part needs T'''. The log-warp trace needs H''. Intrinsic wall chi_j must not be radially composed a second time.

The oscillator equation uses total wall derivatives of pwall, chi and v. The normal scalar equation uses fixed-physical-s time differentiation of f before wall composition. Confusing these differentiations would introduce incorrect xi-dot f' terms. The exact factors 1/(1-v²) and 1/sqrt(1-v²) reduce through this order to 1+v² and 1+v²/2; v begins at order one. All surviving products are retained. The current scalar force is -nu²/1000 because the selected coupling is affine, not exponential; nu²=z n exp[-6(log a(S)/a_i+pwall)] with n=Ni² E_i^6.

Setting all six new placeholders (p3,f3,g3,chi3,xi3,c3) to zero defines the lower-order sources o3 and j3. Keeping them arbitrary gives

    O3 = d3 chi3 - f3 - T xi3 + o3,
    J3 = g3 + T' xi3 - T c3 + 2T p3
         - sigma [21(f3+T xi3)-chi3]/2 + j3,
    d3 = 2 + 270 h² E².

Although c3 and xi3 are eventually known source data from the tracefree bulk and graph subsystems, treating them as arbitrary new coefficients here tests their signs in the boundary assembly. Eliminating chi3 without division gives

    d3 R3 = 2 sigma d3(T c3-T' xi3-j3)
            +(21d3-1)T xi3+o3,
    2 sigma d3 J3 - O3
      = 2 sigma d3(g3+2T p3) -(21d3-1)f3 - d3 R3.

The returned polynomial identities must vanish exactly in qualification. Numeric interval checks require zero containment, not narrowing through intersection. This is Q6, not reduced Q7: a later Q7 conversion must also carry the actual cubic bulk constraint source Sc3. No division by T is used.

Mandatory caller qualification remains: replay first/second rows against accepted formulas; certify arbitrary-new-field identities and Q6 for both orientations; compare independently derived cubic source expressions; detect missing normal tilt, boost, displacement derivative and affine-force mutations; authenticate parent S and accepted endpoint fields. This authored source is not its own independent qualification or execution admission.
