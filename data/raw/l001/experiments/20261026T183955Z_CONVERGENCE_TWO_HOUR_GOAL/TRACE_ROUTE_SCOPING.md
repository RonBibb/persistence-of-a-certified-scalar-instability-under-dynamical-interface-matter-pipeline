# Prospective retained-transport trace estimate

Disposition: analytically pre-reviewed by `/root/jet_bound_review` during this goal; **not inserted into a production certificate and no new radius is claimed**. This note is useful groundwork, not authorization to run a successor.

## A closed candidate envelope

Keep the current affine chart, `D=D0-W partial_u`, and the same norm

`U_n(v)=n²||v||_(2n)+n||v_u||_(2n+1)+||v_uu||_(2n+2)`.

Let `Y` majorize the existing aggregate norm, and write `c=b+2p`. Thus `U_n(c)<=2Y_n`. The neutral seed has `c1=0`. Assume `rho<=1` and `r>h>0`, as in the current certificate.

Nagumo's inequality gives safe higher-jet bounds

`||v_uuu||_(2n+3)<=15n U_n(v)/rho`,

`||v_uuuu||_(2n+4)<=300n² U_n(v)/rho²`.

Because the graph `X` is affine in `u`, `J=1+X_u` is independent of `u`, and `W=D0X/J` is affine. In particular, `W_uu=0` exactly. Preserving the graph's harmonic weight `n^-3` and counting primitive positive-order factors gives

`Ws(Y)=4Y(1+2Y)/(1-2Y)^3`,

with `n²||W_n||<=r Ws_n`, `n²||W_u,n||<=r Ws_n`, and `n||D0W_n||<=r² Ws_n`. The factor arises from `sum_(m>=1) m² z^(m-1)=(1+z)/(1-z)^3`; composite reciprocal factors cannot be counted as one primitive factor.

For a field controlled by `Y`, a sufficient envelope for its temporal two-jet sum, divided by `r`, is

`V(Y)=3Y+22 Ws(Y)Y/rho`.

Here the sum is `n||Dv||_(2n)+||(Dv)_u||_(2n+1)+n^-1||(Dv)_uu||_(2n+2)`. The added radial indices fit because every transport term contains a positive-order graph factor.

## Separate the trace response from its source

The exact trace equation is

`D²c-hDc+(Dc)^2-6(Dc)(Dp)+6(Dp)^2+(Df)^2=0`.

For `lambda=nr`, `lambda(lambda-h)>=r² n²/2`. Applying its inverse to a product of two temporal jets costs at most six times the convolution of their two-jet envelopes. Since the envelopes for `c,p,f` are bounded respectively by `2V,V,V`, the physical quadratic part has response envelope

`(4+12+6+1)*6 V²=138 V²`.

Retain, rather than discard, all five transport terms in

`D²c-hDc = D0²c-hD0c -(D0W)c_u-2W D0c_u +WW_u c_u+W²c_uu+hWc_u`.

If `C` bounds the trace norm, the first, second and last transport terms have response bounds respectively

`(10+30/rho) Ws C`, `(20+60/rho) Ws C`, `(10+30/rho) Ws C`.

Their sum is at most `160 Ws C/rho`. The remaining two terms cost at most

`(10+30/rho) Ws² C` and `(10+150/rho+600/rho²) Ws² C`.

Their sum is at most `800 Ws² C/rho²`; using840 leaves slack. Therefore the positive formal envelope

`C(Y)=138 V(Y)² / [1-160 Ws(Y)/rho-840 Ws(Y)²/rho²]`

closes near zero, with the denominator required to remain explicitly positive. It starts at quadratic order. Induction uses lower-order truncated inputs, so this does not assume the trace coefficient being solved already satisfies its own bound.

The derivative estimates use only the existing norm plus paid Nagumo factors. This route does not silently substitute the Eulerian trace equation for the pulled one, and it does not require an unproved hybrid coordinate norm.

## What still must be done before using it

Replace the old `Cc*qT` entry in the *entire* positive response map by this trace envelope, retaining the other six sources and every wall/harmonic factor. Choose an evaluation amplitude inside all denominator domains. Recompute the majorant and observable bounds in a separately reviewed packet. No such numerical certificate was run here.

## Why a trace-only run is not the next priority

The existing weighted result already supplies a cheap feasibility warning. Let `M` be its weighted source mass, `B_T` the weighted trace contribution, `a` its evaluation point and `K_old` its rounded majorant constant. Holding every other row and `a` fixed, even deleting the trace contribution entirely leaves

`K_new >= 2(M-B_T)/a²`.

Thus its possible radius gain is at most `K_old*a²/[2(M-B_T)]`, approximately522 for the recorded budget. Ignoring the negligible integer rounding gives the familiar share ratio `M/(M-B_T)`. This is an upper limit for this *fixed-other-estimates comparison*, not for all possible future methods. Allowing a different evaluation point changes the comparison and must be recalculated.

The radial-constraint source is the next significant budget term. Consequently a joint trace/radial-source feasibility study is preferable to another stand-alone trace-conditioning run. For example, a low-order background-jet-aware composition estimate may avoid applying a worst-case Cauchy coefficient to every low-order term, but that idea has not been derived or certified here. A useful-amplitude certificate may ultimately need a directly conditioned coupled response or an a posteriori construction, rather than successive scalar constant improvements.

These source shares describe proof estimates only. They do not measure physical energy, force or the mechanism driving the instability.
