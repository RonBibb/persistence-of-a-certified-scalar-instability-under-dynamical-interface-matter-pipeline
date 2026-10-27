# Independent cubic Eulerian bulk and distance derivation

Analytical source reading only; no symbolic/numerical execution or new flow. These expressions are candidates for independent exact qualification against S6, not an already executed proof. Read manuscript Appendix C S6 and Q1–Q4, plus the accepted T15 source extraction. The representation is fixed physical s, with moving walls treated separately.

## Notation and lower-order derivative substitutions

Use m=model_exact.m2 (already the mass-squared parameter), k=h², e=E², r=−6h, mu1=−18k, mu2=−108k, mu3=−270k. Set

```
p=p1, P=p2, f=f1, F=f2, c=c2,
u=p1', U=p2', g=f1', G=f2',
b1=-2p, b2=c-2P.
```

The full assembled second-order fields P,F,G are required, not the particular shooting block alone. Evaluate derivatives by the validated lower-order ODE:

```
H'=-T²/3-k e, Phi'=T, T'=m Phi-4HT, e'=-2He,
u=-2Hp-Tf/3,
g'=-4Hg+(m-mu1 e+2T²)f+(12HT-4mPhi)p,
U=-2HP-TF/3+Sp2,
G'=-4HG+(m-mu2 e+2T²)F+(12HT-4mPhi)P+Sg2,
c=-(3/13)(6p²+f²), c'=-(3/13)(12pu+2fg).
```

## Cubic trace and mixed sources

With all new third-order fields set to zero, direct multiplication of the first two orders in S6 gives

```
qT3 = 4r²(6pP+fF-3pc),
qM3 = r[2pU+(4P-2c)u+(fG+2Fg)/3].
```

The new trace divisor is r3(r3-h)=342k, where r3=3r. Therefore the regular reduced formulas are

```
c3 = -(8/19)(6pP+fF-3pc),
Sp3 = Hc3-[2pU+(4P-2c)u+(fG+2Fg)/3]/3.
```

These avoid dividing by h or T. In a direct symbolic check, preserve the explicit r factor of qM3 and verify r3(Sp3-Hc3)+qM3=0.

## Efficient independent qK3 and qR3 expressions

Rather than fully expanding a large polynomial, use the following scalar product formulas, independently derived by expanding the two exponential factors in S6. Their labels do not denote new physical fields:

```
B1=4p,
B2=-2c+4P+8p²,
B3=-8pc+16pP+(32/3)p³,       # exp(-2b) coefficients
A1=-2p,
A2=-2P+2p²,
A3=4pP-(4/3)p³.             # exp(-2p) coefficients
```

For the radial KG kernel define

```
K0=m Phi,
K1=g'+4Hg+6uT,
K2=G'+4HG+(6U-c')T+6ug,
K3=6uG+(6U-c')g.
```

For the temporal KG kernel define

```
V1=-mu1 f,
V2=-mu2 F,
V3=2r² c f.
```

Then

```
qK3=K3+B1*K2+B2*K1+B3*K0-e*(V3+A1*V2+A2*V1).
```

V3 comes from (2Dp+Db)Df=(Dc)Df. It is nonzero at cubic order even though c1=0. Omitting it is a useful mutation control.

For the radial Einstein kernel and temporal Einstein kernel define

```
J0=6H²-T²/2,
J1=12Hu-Tg,
J2=12HU-TG+6u²-g²/2,
J3=12uU-gG,
V0R=6k,
V1R=-3mu1 p,
V2R=-3mu2 P+3r²p²+r²f²/2,
V3R=12r²pP+2r²fF.
```

Then

```
qR3=J3+B1*J2+B2*J1+B3*J0+m*f*F
     -e*(V3R+A1*V2R+A2*V1R+A3*V0R).
Sc3=12HSp3-(12H²-T²)c3+qR3,
Sg3=T*c3'+2mPhi*c3-6TSp3-qK3.
```

The m*f*F term is the cubic coefficient of m(Phi+f_total)²/2. All divisions above are exact rational divisions, never floating constants. c3' must be obtained by differentiating the displayed polynomial using the complete lower-order ODE, including Sp2 and Sg2.

## Compatibility qualification strategy

Independently extract degree-three coefficients of all four original S6 residuals with p=zp1+z²p2, b=−2zp1+z²(c2−2p2), f=zf1+z²f2. Replay lower coefficients. Compare each cubic source to the closed expressions above before checking the compatibility identity.

The compatibility residual is

`Sc3'+4HSc3-T*Sg3-Dn3*Sp3`, where `Dn3=2T²-3(mu3+4k)e`.

It must vanish modulo the exact background constraint and BOTH lower-order scalar constraints:

```
Cbg=6H²-T²/2-6+mPhi²/2-6ke,
C1=Tg-T'f+[2T²-3(mu1+4k)e]p,
C2=TG-T'F+[2T²-3(mu2+4k)e]P-Sc2.
```

Do not divide by T to eliminate g or G. Either exhibit explicit polynomial multipliers for Cbg,C1,C2 or use a verified polynomial-ideal reduction with exact rational arithmetic. The T15 two-generator coprime-leading-monomial argument does not automatically carry over: C1 and C2 can have leading monomials sharing T. A nonzero remainder from an uncompleted division basis is not a scientific incompatibility result. Preserve raw residual, generators, multipliers and verified final remainder.

## Complete third-order proper distance

Expand exp(b) in the Eulerian chart and move both integration endpoints. No factorial coefficients are used:

```
d_sep3 = xi_b3-xi_a3
       + integral[c3-2p3-2p1*c2+4p1*p2-(4/3)p1³] ds
       + [-2p1*xi2+(c2-2p2+2p1²)*xi1-p1'*xi1²]_a^b.
```

The term `-p1'*xi1²` is half the derivative of the first-order integrand times the squared first-order endpoint shift. The second-order integrand times xi1 and first-order integrand times xi2 are separately necessary. Retain xi_b2 and xi_b3 even though the accepted lower-current direction has xi_b1=0. Unknown p3 remains an essential bulk term, so no graph-only calculation yields d_sep3.

For an exact manufactured endpoint-transport control, integrate a generic cubic polynomial-in-z integrand with an analytically integrable polynomial-in-s coefficient, substitute both endpoints through z³, and compare the coefficient with this formula. That control is independent of any AB numerical trajectory and should include nonzero derivatives and shifts at both endpoints.
