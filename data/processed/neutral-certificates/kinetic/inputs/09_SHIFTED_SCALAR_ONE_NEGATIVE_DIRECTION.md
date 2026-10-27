# Independent shifted-scalar discriminator

Hand-only supplement to ZERO_ANCHOR_CONTROL_AND_FULL_SIGN_GATE.md; same frozen inputs, no new scientific execution. This is an auxiliary operator result, not a sign classification of the physical canonical pp form.

At the zero-charge t=0 anchor in instantaneous isothermal r, alpha=a^3 and the actual homogeneous Robin condition is

    Qw=0 at both ends, Q=partial_r-alpha'/alpha.

The ordinary L2(dr) adjoint differential expression is Qdagger=-partial_r-alpha'/alpha. The closed Robin realization of Qdagger Q has quadratic form integral|Qw|^2 and operator

    Qdagger Q=-partial_r^2+alpha''/alpha.

Since alpha''/alpha=9h^2-alpha^2 Bpotential, the unshifted lapse/conformal scalar operator and the C8 shifted scalar operator are exactly

    L=Qdagger Q+10h^2,
    Lshift(k)=L+k^2-13h^2=Qdagger Q+k^2-3h^2.

Thus alpha is an exact Robin eigenfunction with shifted eigenvalue k^2-3h^2. In particular Lshift(0) has a negative direction, and Lshift(k) has an exact kernel at |k|=sqrt(3)h. This scalar-only inverse cannot be used as an everywhere positive or pole-free replacement of the FULL coupled metric constraint response.

There is also an exact nonzero spectral pairing. Q maps nonzero Robin eigenfunctions of Qdagger Q to Dirichlet eigenfunctions of Q Qdagger, and Qdagger divided by the nonzero eigenvalue maps back. Both endpoint/domain conditions follow from Qw=0, as in the standard first-order factorization; the connected finite interval leaves the sole zero mode proportional to alpha. The Dirichlet partner potential is

    Vplus=(alpha'/alpha)^2-(alpha'/alpha)'
         =2(alpha'/alpha)^2-alpha''/alpha
         =a^2(6+3T^2/2-m Phi^2/2)+9h^2
         > (11/2)a_min^2+9h^2.

The final strict coarse inequality uses the same source-bound 0<m Phi^2<1 and a_min>0. Hence all nonzero eigenvalues of Qdagger Q exceed 9h^2+(11/2)a_min^2, with a further positive Dirichlet Poincare term if desired. It follows that Lshift(0) has exactly one negative eigenvalue -3h^2, no zero eigenvalue, and all its other eigenvalues exceed 6h^2+(11/2)a_min^2. At general k only the exact alpha eigenvalue can fail positivity.

This does NOT produce a physical negative kinetic direction: the source of the shifted scalar equation contains the residual canonical momenta, which also obey the actual momentum constraint and the supplied physical mean condition. On the explicit admissible w=c alpha control plane, the COMPLETE pp form, including both wall terms, is strictly positive. The full coupled C5 inverse remains invertible at the scalar-only crossing. Any argument replacing it by Lshift inverse across that crossing would be invalid.

Potential value for the next proof: isolate this single auxiliary scalar direction in a coupled Schur reduction while estimating the positive complementary Robin subspace. Its cross couplings and the actual finite mean must still be controlled; this note supplies neither that Schur sign nor a continuum pp positivity claim.
