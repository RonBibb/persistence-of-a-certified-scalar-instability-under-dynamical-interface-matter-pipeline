# Common-domain norm and sufficiently-small-charge continuation

Hand-only supplement to WEIGHTED_PARTNER_ALL_K_HAND_PROOF.md. No new computations or sources. The conclusion remains conditional on a prospectively admitted certificate of the exact zero-anchor gates. The analytical branch and previous exact canonical reconstruction are inherited hypotheses, not constructed anew here.

## 1. Hilbert input fibers and coercive zero anchor

Pull the actual radial width to a fixed rho in [0,1]. At each nonzero real tangential Fourier k use the canonical input Hilbert space

    Hmom=L2(rho; Pi_sigma,Pi_Phi) plus R4(wall momenta).

The four wall slots comprise chi and phase at EACH wall; neither Noether density is frozen or Routh-eliminated. The actual homogeneous fiber is a separate space Hmom plus the independent scalar deltaPq, with deltaq=0 along a pp direction. Its response obeys the supplied mean 2 integral deltaA d rho=deltaPq. The auxiliary nonzero-mode family continued to k=0 is a different fiber and never removes that mean.

At zero charge, S is a bounded nonnegative quadratic form. C5/R2 map the L2 momentum inputs and finite wall/mean data into w in H2 and deltaA in H1 at fixed bounded k; the output is compact into L2 and traces. Consequently its self-adjoint representative is positive bare multiplication plus a compact operator; finite wall and mean blocks do not affect its positive essential spectrum. The weighted hand proof excludes its kernel on every nonzero mode, the auxiliary zero endpoint and the physical homogeneous mean separately. Thus each has a strict positive lower bound in the indicated canonical input norm, not merely positivity for each nonzero smooth vector.

C5's common-domain inverse is continuous on compact (k,t) sets after flattening. The bare positive weights and response operators are continuous there in operator norm. A compact parameter family of these strictly positive operators has a uniform positive lower bound: otherwise choose a convergent parameter sequence and unit vectors, and operator-norm convergence contradicts the strict lower bound at the limit. The physical mean is treated separately on its compact t interval. This is not an inference from C5 inverse positivity or from spin2/scalar degree counting.

For high k, the inherited C8 parameter estimate supplies a uniform comparison of S with canonical inputs. Once exact gates imply K0>=(1-Delta)S with Delta<1, this gives a whole radial/all-k zero-anchor canonical pp norm. Constants may be uncomputed, while the relative S margin can be an explicit rational. Time-dependent coordinate/conformal factors are retained and are bounded above/below on each fixed compact slab; no all-future unweighted constant is inferred.

## 2. Actual charged compact-band input-to-response maps

Let c denote the background charge parameter vector, so it is not confused with a canonical momentum perturbation. Use the admitted analytic branch in a preliminary small neighborhood c=0 and a fixed finite time slab within its collar. Positivity of lapse, width, conformal factor and target matrices persists. Both independent wall charge directions remain parameters; do not restrict their ratio to a fitted path.

For a pure-momentum datum the canonical configurations X,psi,q,kappa and new-cut angle are fixed. The exact linear scalar constraint source is smooth bounded background coefficients times the L2 canonical bulk momenta; there is no derivative of an input momentum. The radial momentum source is likewise a coefficient times momentum. In particular a nonzero background Phi time momentum changes the coefficients but introduces no input derivative.

The wall energy source is proportional to p_wall,bg^T H^{-1} delta p_wall. It vanishes at the zero anchor, but must be retained at nonzero c. It is a bounded finite-dimensional endpoint functional on H1, uniformly on compact parameter sets. The background lapse satisfies the actual pressure Robin law. Substituting w=alpha_c y therefore gives a COMMON homogeneous Neumann operator domain after lifting that supplied boundary load. Its lifting can be chosen continuously on a compact k band; no trace of an L2 bulk input is required.

The wall tangential traction has p_wall delta(psi_x)+delta p_wall psi_x plus the known boost/graph terms. For this pp test psi_x=delta psi=delta eta=0. Thus it supplies no new tangential boundary traction, and the nonzero-mode zeta Dirichlet domain stays homogeneous. This statement does not freeze wall phase momentum: its energy load remains above and its kinetic square is retained.

C5 gives the resulting common-domain compact-band operator L_c and inverse at small c. Write the response schematically R_c=L_c^{-1}J_c, including the continuous boundary lifts. The exact source maps J_c are bounded from Hmom to the weak bulk/endpoint codomain and converge in operator norm, not merely coefficientwise. The normalized operators converge in their common-domain norm, so

    L_c^{-1}-L_0^{-1}
       =L_c^{-1}(L_0-L_c)L_0^{-1}

converges uniformly on a compact (k,t) band. Hence R_c tends in B(Hmom,H2 x H1) to R_0 for the pure-momentum class, using ordinary one-dimensional elliptic regularity with the explicitly supplied endpoint loads. Weak H1 estimates alone are not being used to justify alpha'' or endpoint evaluations of an arbitrary L2 input.

For the physical mean, use R2's distinct operator with its TWO bulk rows, two energy endpoints and actual finite mean row. Its fixed-rho coefficients, true-density conversion Pi/q, mean functional and common trace lifts depend continuously on c,t with q>0. The zero-anchor inverse is already established. The same inverse identity/Neumann perturbation yields its actual small-c bounded inverse and response continuity, keeping deltaPq as data. No k->0 replacement or width freezing occurs.

The exact K_c=S_c+R_canonical,c is made of smooth bounded bulk multiplications, the continuous response in L2/H1, finite endpoint traces and finite wall squares. In particular its pressure and alpha'' coefficients converge uniformly. Thus on the compact band and on the actual mean fiber,

    ||K_c-K_0||_B(Hmom,Hmom*) ->0

uniformly on the finite time slab. This establishes the required bounded FORM continuity from actual source/inverse/trace maps; coefficient continuity alone would not suffice. The common space is defined using TRUE Pi densities per rho; delta barp=deltaPi/q at fixed configuration q is only a positive uniformly bounded congruence.

## 3. Noncircular all-k continuation

First fix the preliminary branch neighborhood and finite time slab. It gives common upper/lower bounds for the exact C8 shifted scalar coefficients, target weights, width and Robin coefficients. The canonical residual source obeys ||f||^2+|g_boundary|^2<=C S with one constant for that neighborhood. Both wall loads are retained; the parameter trace estimate controls them with their proper k^{-1/2} weight.

Choose one finite K0 large enough that the C8 ultraviolet remainder bound is <=S/2 throughout this preliminary neighborhood. Its canonical-input comparison and upper response bounds are also uniform there. Hence every |k|>=K0 has a positive lower canonical pp bound without any charge-radius choice based on a low-band cutoff that later moves.

Now keep this K0 fixed. If the exact zero-anchor certificate passed, Section1 gives a strict lower bound on the full complementary compact band and the separate physical mean. Section2's bounded-form continuity permits shrinking the charge neighborhood ONCE so its form difference is less than half that lower bound. The UV bound remains valid because its cutoff was chosen on the larger preliminary neighborhood. This proves positivity and norm equivalence for ALL nonzero k, all radial inputs and the actual homogeneous mean in some sufficiently small background charge neighborhood on the fixed slab.

One can equivalently obtain full bounded-form continuity by combining compact-band continuity with the uniformly small high-k response correction and continuous positive bare multiplications. The split proof above needs only uniform UV positivity and is simpler. It supplies no explicit numerical charge radius, and is not a finite-charge profile evaluation or a parameter scan.

## 4. Exact layer and exclusions

Conditional conclusion: once the zero-anchor background gates are rigorously certified, the same-action canonical ENERGY-FORM pp coefficient has a whole-domain zero-anchor coercive bound and an existential sufficiently-small-charge continuation, with actual physical mean and both independent wall currents retained. It is stronger than the predecessor's restricted plane and finite diagnostic, and depends on the new weighted inequality rather than borrowed generic separated norms.

It does not produce a numerical nonzero-charge amplitude, a uniform all-future or infrared spacetime gauge norm, equivalence to old fixed caps, positivity of the full Hamiltonian stiffness, removal of the inherited growing mode, nonlinear stability/formation, or an unrestricted physical no-ghost/Cauchy theorem. Strong corner compatibility still belongs to the operator/evolution domain; the canonical energy form is its distinct layer. The fluid interpretation retains its timelike/future current domain on the admitted charged branch. No successor or scientific execution is authorized by this hand note.
