# Two local wall stiffness coefficients from saved interval data

The prospective quantities are C_a=f_a^2/Z and C_b=a_b^4*f_b^2/Z on the accepted central exact background and physical eigenmode, with psi(0)=1. They are the local derivatives for the already reviewed action deformation eta_i*(Phi-Phi_i_star)^2/2. The background is unchanged. No finite stabilization threshold follows.

Sources are the accepted central mode result, original exact bindings and two complete mass-strip records; all 94 nonzero-index strip checkpoint nodes; the original producer sources for state conventions; the wider central static independent root enclosure; and the accepted finite-stiffness analytic review. Every file is hashed in SOURCE_BINDINGS.json before execution. Original validated-flow correctness and original model provenance remain inherited. The native final state is not treated as the physical wall value.

## Analytic bridge and enclosure construction

Use proper coordinate s, log warp W, T=Phi_s. The inherited equations give H_s=-T^2/3-k exp(-2W)<0. Hence H_b<=H<=H0<0 on the actual domain. Positive scalar endpoint values and m2>0 imply 0<Phi<=max(Phi0,Phi_b) by the ordinary interior-extremum argument for Phi_ss=m2*Phi-4H*Phi_s. The first integral then gives

    T^2 <= 12*H_b^2 - 12 + m2*Phi_max^2.

The exact test requires that this upper bound is strictly less than 1/4, proving |T|<1/2. Using the strip's global psi and f intervals, the proper mode equation gives

    psi_s >= -2*H0_upper*psi_global_lower - abs(f)_global_upper/6.

Require this to be positive. Thus W decreases and psi increases on [0,D]. All monotonicity hypotheses are tested before any slope is classified. If one fails, retain INCOMPLETE rather than substituting numeric profiles.

Decode native Arb mid/radius tuples as exact dyadic endpoint intervals at each saved checkpoint node; require strip task identity, guard, mass range, unique increasing node indices, checkpoint spacing256 and correct state dimension. Combine launch W=0,psi=1 with all nodes before D_lower. On each full slab [s_j,s_j+1], monotonicity gives

    12*ds*exp(2*W_right_lower)*psi_left_lower^2 <= Z_slab
    Z_slab <= 2*ds*exp(2*W_left_upper)*(f_global_abs^2+6*psi_right_upper^2).

The final tail lower bound uses length D_lower-lastnode, global W_lower and lastnode psi_lower; its upper uses length D_upper-lastnode, lastnode W_upper and global psi_upper. This covers the unknown exact endpoint without evaluating the final native state there. The resulting upper-wall psi interval is [lastnode psi_lower, global psi_upper]. Both producers are handled separately; their valid intervals may be intersected only after checking overlap. The exact mode belongs to both strip enclosures.

For positive exponential arguments up to5, sum the rational Taylor series through degree64 and bound the positive tail by first_omitted_term/(1-x/66). Obtain negative exponent bounds by reciprocal. Inputs are rounded outward to dyadic grid2^-40; exponential outputs are rounded outward to grid10^-18. All these operations widen rigorously; binary float arithmetic is not used for scientific evaluation.

At the lower wall B0 and lambda=mu+4k are saved uniform enclosures, and f_a=3*lambda/B0. At the upper wall the regular constraint and Robin condition imply

    b_b=(-gamma/2+4*H_b)*T_b-m2*Phi_b,
    a_b^2*b_b*f_b=3*lambda*psi_b.

Therefore C_b=(3*lambda*psi_b/b_b)^2/Z, with the warp canceling exactly. Require B0 and b_b nonzero. A normalization- and norm-free dominance ratio is C_b/C_a=psi_b^2*B0^2/b_b^2; intersect its direct interval with any interval quotient of the coefficient bounds only if both valid. Both coefficients concern the same exact central eigenmode, although uniform mass-strip enclosures are used.

## Frozen outcomes and controls

USEFUL requires both coefficients to have finite strictly positive enclosures, each upper/lower ratio<=64, norm upper/lower<=2, the ratio C_b/C_a upper/lower<=2, and its lower bound>1. WIDE means valid finite positive coefficient bounds but at least one usefulness criterion fails. INCOMPLETE means a source, domain, monotonicity, denominator or overlap gate fails. These criteria will not be changed after execution. Relative dominance is claimed only if the direct ratio lower bound exceeds1; no stabilization threshold or scan is performed.

Six semantic controls bypass hashes on deep copies: zero-reaching B0 (LOWER_DENOMINATOR), changed uniform mass parameter in a checkpoint (CHECKPOINT_MASS), missing checkpoint node (CHECKPOINT_GRID), nonpositive global psi minimum (POSITIVE_PROFILE), upper wall b interval forced to contain0 (UPPER_DENOMINATOR), and doubled norm lower bound beyond its upper bound (NORM_ORDER). Each must reject at its intended predicate. Mutation flags for the last two are confined to their explicit check boundaries and do not alter saved files.

One standard-library Python worker, BLAS1, no producer imports, timeout120seconds; resource estimate under30seconds and under256MiB. Separate reviewer gate and coordinator execution permission precede the single run. Independent terminal reconstruction and interpretation review follow it.
