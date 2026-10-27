# Prospective round-trip clock response — derivation for review

Not an admitted calculation. The purpose is to compare the proper-separation response with a genuine elapsed-clock readout, rather than calling a lapse ratio an observed redshift. No new matter source, finite-charge amplitude or horizon is introduced.

## Defined experiment

An ideal negligible-energy radial light pulse leaves the lower interface at construction time t_e, reflects instantaneously at the upper interface, and returns to the same lower-interface comoving observer. The measured quantity is elapsed proper time on that observer's clock. Reflection is an explicit kinematic idealization, not a prediction of the wall's electromagnetic properties. The pulse has fixed three-dimensional comoving spatial coordinates and travels in the radial direction. Assume the small perturbation regime in which both walls remain timelike and the round trip stays in the common local patch/collar.

The metric is the actual AB ansatz with radial null equation

`dt/ds = ± E(s) exp(b−p)`, `E=1/a`.

Let `tau(s)=integral[a,s] E(u)du` and `L=tau(b)`. At zero amplitude the round-trip coordinate duration is 2L and lower-clock duration is 2a_a L. These are neither an event-horizon test nor propagation along the 3D expanding directions.

## General first-order separated response

Take perturbations `p=epsilon exp(r t) P(s)`, `b=−2p` and endpoint graphs `S_i=s_i+epsilon exp(r t) xi_i`. Denote the emission amplitude by `epsilon_e=epsilon exp(r t_e)`. Null transport at first order samples the outbound background time `tau(s)` and return background time `2L−tau(s)`; it must not freeze the metric at emission.

The proposed coefficient of coordinate round-trip duration is

`C_coord = −E_a(1+exp(2rL))xi_a + 2E_b exp(rL)xi_b`

`          −3 integral[a,b] E(s)P(s)[exp(r tau(s))+exp(r(2L−tau(s)))]ds`.

The factors of two at the reflecting endpoint and the two different emitter times must be independently derived. A moving emitter's radial velocity contributes only quadratically to its proper-clock factor at this order. Its first lapse variation is `P_a+H_a xi_a`. Therefore the proposed coefficient of elapsed emitter proper time is

`C_radar = a_a { C_coord + (P_a+H_a xi_a) J(r,2L) }`,

where `J(r,x)=(exp(rx)−1)/r`, with continuous limit `J(0,x)=x`.

Two distinct applications are possible, and must not be conflated:

- Neutral growing mode: `r=gamma_g`, `mu=−gamma_g(gamma_g+3h)`, `xi_a=xi_b=0`, `P=psi` with accepted normalization. Its free amplitude is not selected by this calculation.
- First-current particular branch: `r=−6h`, P and xi from each independent T4 current channel. Its amplitude is a conserved-density square times the decaying redshift factor. Equal local proper density and equal current labels require separate normalization.

## Required qualification before any implementation or execution

Independent analytical review confirms a more general transverse-gauge control. Write the metric cross term as `2 epsilon exp(rt) C dt ds`, so C is the coefficient of g_ts, not of the full cross term. For general independent radial and lapse perturbations B and P, replace the −3P integrand by B−P and add

`integral[a,b] C E² [exp(r tau)−exp(r(2L−tau))]ds`.

Under the radial generator alpha(s)exp(rt), the pure coordinate perturbation has `P=−H alpha`, `B=−alpha_prime`, `C=−r alpha`, and `xi=alpha`. Each null-leg integrand is then the negative derivative of `E alpha` times that leg's exponential weight. The integrated endpoint values cancel the explicit graph terms, and `P_a+H_a xi_a=0`. This checks time-dependent transverse relabeling without wrongly forcing an arbitrary gauge perturbation to obey B=−2P. The scientific neutral-mode computation itself remains in the original diagonal gauge.

1. Independently derive both moving-boundary null legs and the emitter-clock conversion. Check all signs, the reflection matching time, and whether additional chart or clock terms are required.
2. Exact or analytical controls: static r=0 limit; flat constant P with zero graphs; moving endpoints with zero bulk perturbation; temporal variation sampled along both legs; a pure coordinate relabeling in a formulation broad enough to retain the lapse/metric relation correctly. Do not apply b=−2p to an arbitrary gauge perturbation that does not preserve that gauge.
3. Compute tau and L as validated integrals over the same uncertain AB background and endpoint. Enclose exp(r tau) over whole cells and all input uncertainty. No interpolation-only time sampling, midpoint mode, or endpoint substitution.
4. Enclose the weighted P integral and preserve signed optional tails. If using saved interval coefficients, verify they enclose the same exact branch and mode as the clocks/background.
5. Require two regular engines and independent terminal audit, preserving unresolved signs. An equality between radar half-duration and spatial proper distance is not assumed.
6. Select one application prospectively, within the remaining allocation and ordinary Linux leases. A comparison of the two applications would require both to be separately qualified, with no mixed-amplitude claim.

## Decision value

This would test whether the established spatial separation change corresponds to a shorter or longer operational light-clock round trip. It measures one defined relationship between geometry and time, not a universal minimization principle, causal redistribution law, or finite-amplitude end state.
