# Independent mathematical review: the C4 family and conformal evolution inputs

Status: constructive analytic bridge derived; final source-bound preflight and numerical admission pending. No physical integration, evolution, or new amplitude has been run by this reviewer. The scope is exactly `epsilon in [-1/200000,1/200000]`, with numerical readback restricted to existing cases 0, 3 and 4.

## Outcome and necessary qualification

There is no scalar-C4 obstruction from the stated conformal lapse completion. Its third endpoint derivative removes a specific temporal-versus-angular Israel defect which would otherwise enter the scalar fourth-time row. The fifth derivative fixes the next Israel compatibility condition; it does not enter the scalar fourth-time row. Thus the same three-variable physical correction root is retained, provided the exact background/mode, constraints and lower-order wall conditions are the same. This is a finite-jet coordinate and initial-family identification, not an assumed spacetime existence theorem.

The remaining substantive identification gate is source selection. The inherited spectral result supplies existence, not uniqueness of the eigenvalue in its bracket. A shared approximate mass or bracket is insufficient. The proposed one uniform negative determinant-mu derivative, combined with the inherited endpoint signs for the same exact background and event, is sufficient to select the same exact normalized mode within that bracket. No uniqueness outside it is implied.

## Exact scalar fourth-row bridge

Use material coordinates `(T,s)` with `alpha=exp(A)/cosh(sqrt(k)T)`, radial logarithmic metric `ell`, zero shift and time reflection. Let `l` denote initial proper distance. At either wall put

    p=A_l, u=Phi_l, u_l=Phi_ll, c=sigma gamma/2,
    eta=ell_TT-A_TT+k.

Material Robin is `R=exp(-ell) Phi_s-c(Phi-v)`. Write `R2,R4` for its second/fourth material time derivatives from the original equations. In conformal coordinates the corresponding wall residual is `RC=exp(-B) Phi_x-c(Phi-v)`, with `B=A+q` initially and `x_s=exp(ell-B)`.

Define `D2` to be the conformal second-time temporal-minus-angular Israel row, namely the second derivative of `exp(-B)(B_x-A_x)`. Under the exact initial Hamiltonian and its spatial derivatives, time reflection, and endpoint `q=q_s=q_ss=0`, direct substitution of the two time PDEs gives

    RC2 = R2,
    RC4 = R4 + 4 eta R2
                + exp(2A) [5 u_l+(16p-c)u-4 m2 Phi] D2.        (1)

The Hamiltonian is essential; independent arbitrary endpoint rectangles need not obey this identity without their constraint premise. The wall scalar value, second spatial derivative, or fifth-jet coefficient is not retuned to obtain (1). Neither scalar Robin nor second-time Robin is needed merely to derive the displayed off-defect identity. To identify its zero sets, use the existing preparation and Israel root, which imply `R2=0`, then the prescribed lapse completion `D2=0`.

In initial proper-distance coordinates the same substitution yields

    D2 = (ell_TT-A_TT)_l + exp(2A) q_lll.

Consequently the unique third lapse jet is fixed by this equation. In the actual material coordinate its positive coefficient is `exp(2A-3ell)`, exactly the denominator used by the inherited producer. The fourth-time difference `D4` is affine in `q_sssss` with positive coefficient `exp(4A-5ell)`, after the lower jet choice. The scalar fourth row is independent of the fourth and fifth lapse jets. The material condition `q_ssss=0` is a specified Hermite convention, not an additional scalar physical constraint. Notice that it does not in general mean `q_llll=0` after converting to proper distance; the independent algebra keeps that fourth proper jet free.

At either wall `B=A`, so the material and conformal scalar-row normalizations also agree. On the constrained physical root, both scalar C4 rows vanish in one gauge if and only if they vanish in the other. All interior scalar corrections and their Hamiltonian backreaction remain in this assertion. No nonlinear block-diagonal metric response is presumed.

### Coordinate explanation and clock term

The conformal spatial coordinate satisfies the quotient scalar wave equation. With `J=x_s=exp(ell-B)` and `K0=exp(2A-2ell)` on the initial slice,

    x_TT = -K0 J q_s,
    x_TTTT = K0 J [(A_TT-ell_TT)_s-K0 q_sss]
             = -exp(2A-ell) J D2                         (at the wall).

Here `q_s=q_ss=0`; the second formula follows by twice differentiating the wave equation before restricting to the wall. Setting `D2=0` keeps the old physical wall at fixed conformal x through fourth time order. The fifth lapse choice supplies the next temporal Israel compatibility, not a new scalar completion.

The initial coordinate Jacobian has `T_t=1`, `s_t=0`, and the inverse wall clock has `T_ttt=eta`. Thus composition of an even wall residual gives the term `4 eta R2` in (1). If the fourth wall-position defect is not removed, the boundary moves by `s_tttt=exp(2A-ell)D2` and its normal tilts. These two effects give the remaining coefficient in (1): `R_s+4 exp(ell-2A) Phi_TT`, converted to proper derivatives. This also explains why simply assigning a different lapse without completing its wall jets would not suffice.

The initial wall clocks agree because q vanishes there; their coordinate accelerations need not agree. Proper time satisfies `d tau=alpha dT=exp(B)dt` along the matched wall, to the stated jet order. In particular `B_tt=ell_TT` while `alpha_TT/alpha=A_TT-k`; the term `T_ttt=eta` reconciles them. Subsequent numerical wall-clock observables must retain their actual integrated lapse and cannot replace t by T without this map. For the customary normalization `sigma=tau/exp(W_i)`, the perturbed initial rate is `exp(A_i-W_i)`, not automatically one.

### Independent exact corroboration prepared

`independent_gauge_bridge.py` separately implements the material and conformal time PDEs in exact differential algebra, eliminating Hamiltonian metric derivatives. It checks (1), the second row, fourth scalar value pullback, third/fifth lapse coefficients and absence of fourth/fifth lapse jets from scalar C4. It imports no producer code. Initial proper distance is only an algebraic coordinate convenience, and q's higher jets remain independent before reduction. All 15 exact checks passed on the authorized serialized Linux slot under SymPy 1.14.0, in 1.643 seconds, with one arithmetic/BLAS thread, bytecode disabled and a 4 GiB address-space limit. The prior read-only capacity check found 30,227,920 kB available and 0.19 one-minute load, and no worker for this packet. No physical IVP ran. Source SHA-256: `6426cc83707081c1d262e93ba0cc90d696d7d76aa519fa6097d9908f81e61562`; successful stdout is preserved in `INDEPENDENT_GAUGE_BRIDGE.json`.

## Initial field map and physical family

The unchanged preparation is `ell=-2 epsilon psi`, `Phi=Phi_star+epsilon f+C7+b0 H0+b1 H1`, with metric A determined by the full Hamiltonian IVP and both Israel walls. The degree-seven first/third endpoint lift is the same unique Hermite interpolation in the two constructions. The fifth-jet shapes are exactly

    H0=s^5(D-s)^6/(120 D^6),
    H1=s^6(s-D)^5/(120 D^6).

They preserve endpoint jets zero through four and have unit own-wall fifth derivative. The unknown coordinates agree as `a=A(0)-epsilon`, b0 and b1, with `psi(0)=1`. The inherited material fourth-Israel identity follows from the original mixed equation: `J_T=-Phi_T R/3`, hence `J_TTTT=-Phi_TTTT R/3-Phi_TT R_TT`. Thus the physical scalar Robin and second-time conditions supply that compatibility without another free physical correction.

For real finite fields, `x_s=exp(ell-B)>0`. The pullback gives radial metric `exp(2B) dx^2=exp(2ell) ds^2`, the same angular radius `exp(A)/sqrt(k)`, the same scalar, and `K_ij=Pi=0`. Proper separation is invariant as an integral; coordinate separation X is not fixed across the family. Wall orientation is fixed by `sigma=+1` below and `-1` above: the outward normal is `-sigma exp(-B) partial_x`. These signs reproduce both full Israel and scalar wall conditions.

The material mode, not fixed-x array differences, retains tangent `(psi,-2psi,f)`. If `q=epsilon q1+...`, its coordinate displacement is `delta x(s)=integral exp(-W)(-3psi-q1) ds`; at fixed x the relabeling is `delta s=-exp(W) delta x`, and at fixed x/X it is `exp(W)[(x/X)delta X-delta x]`. Norm and separation overlap require the transformed measure ds/dx. The second-amplitude coefficient convention is coefficient-of-epsilon-squared, not the full second derivative. The inherited second-order construction implements the differentiated same C7, metric IVP, three wall-root equations, sequential lapse and map; identification is of those analytic targets, not literal equality between a finite history and its quadratic truncation.

## Review of proposed bounded gates

The staged `mode_flow.py` differentiates at fixed exact background and D correctly. With `(u,v,w)=(psi_mu,f_mu,g_mu)`, its equations are

    u'=-2H u-Tv/3, v'=w,
    w'=-4H w+(m2-mu E^2+2T^2)v-E^2 f
        +(12HT-4m2 Phi)u.

The launch `(0,3/B0,gamma*3/(2B0))`, where `B0=gamma*T/2-m2*Phi+4HT`, and upper determinant derivative `w+2Tu+gamma v/2` agree with the regular source and wall equations. Do not differentiate the event with respect to mu: the exact background/event are fixed. Full a/D/mu rectangles may be carried conservatively. The inherited endpoint signs plus a strictly negative uniform derivative select a unique mu in the unchanged bracket; launch normalization then fixes the mode. The lower denominator and nonexceptional sector must remain authenticated.

The present CONTRACT appropriately separates exact-family identity from numerical admission. Its prospective two additional signed spatial enclosure flows use the already certified root-image boxes; these are not time evolutions or newly fitted corrections. Final review must still verify: complete event-cell coverage; rigorous saved-seed and signed bulk-field comparison in common `u=s/D` including every overlapping polynomial segment; positive coordinate-map bounds and correct inversions; all six stated grid readbacks against bound dense representations; inherited admission receipts; exact signed root-image reconstruction within the common correction box; and unchanged action, source, runtime and parent bindings. Whole-domain source bounds must use the exact background/mode/event uncertainty, not measured source-level changes. Finite numerical arrays remain approximations with stated errors, not exact roots. A derivative certificate alone does not bound their evolution error. Rigorous material-field bounds also do not automatically bound the completed conformal lapse, map inverse or later histories; those distinctions must remain explicit if not additionally enclosed.

The old rounded epsilon strings must have their offsets recorded while the exact target remains `+/-1/200000`. No data at magnitude 1e-5 belongs to this admission claim. Uniqueness in the certified correction box identifies the exact completion once the source and gauge bridge agree; proximity or overlapping error boxes alone does not. If conservative full-field bounds do not support a sharper numerical claim, report exact-family identity with that admission limitation, as the contract allows.

Sources actually inspected for this preliminary review: the connected certificate's sealed RESULT and prior independently reviewed construction; native `DERIVATION.md`, `HIGHER_TIME_DERIVATION.md`, `core.py`, `time_jets.py`, `higher_run.py` and fine seed metadata; conformal `FORMULATION.md`, `COORDINATE_MODE_DETAILS.md`, `producer.py`, `jet.py`, `original_equations.py`; spatial `METHOD_RECORD.md` and relevant result scope; second-order `DERIVATION.md`, `initial.py` and relevant result scope; inherited `INDEPENDENT_C4_DERIVATION.md`; new `CONTRACT.md` and `mode_flow.py`. Final execution-source and receipt hashes belong to the later source-bound preflight, not this preliminary mathematical acceptance.
