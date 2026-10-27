# Double Dirichlet ceiling for the persistent mode

Measure the strongest-boundary limit on this same fixed concave background. The accepted negative-band count and stiffness monotonicity imply exactly one persistent mode below mu=-12 even at double Dirichlet, and its eigenvalue bounds the corresponding mode for every nonnegative finite wall pair. This test quantifies that ceiling, not a new stability theorem or new physical action.

At both walls impose f=0. Normalize psi(a)=1, giving L(a)=3 lambda/(a(a)^2 T(a)) and g(a)=L(a)-2T(a), where g=f' and lambda=mu+12. The lower endpoint T is certified strictly negative; no division by the interior turn or lambda is used. The upper residual is f(b). Search mu in [-12.001,-12.000001] for strict opposite signs, target width 1e-5. This starting bracket is a prospective feasibility choice, not a known root. Failure to bracket or contract is technical incompleteness; no in-run widening.

Search the full regular (psi,f,L) system at n=4096,8192. Audit both final endpoints with independently represented (psi,f,g) equations at n=16384:
psi'=-2H psi-T f/3, f'=g,
g'=-4H g+(V''-mu/a^2+2T^2)f+(12HT-4V')psi.
Require whole-cell strict tube inclusion, background box/Hamiltonian, constraint at launch and every step, strict endpoint signs, coarse/fine overlap, nonincreasing bracket width and cross-representation residual overlap. Fixed foreground rates (10,1,10), inherited background rates (3,5,.1,2), 256 fractional bits. Rational chain-rule controls connect the two representations without relying on spectral constraint cancellation. Independently evaluate lambda=0 in the regular g representation and require a nonzero residual; the inherited exact exclusion remains the theoretical premise, not merely that one numerical sample.

The result reports gap -mu-12>0, conditional homogeneous growth sigma/H=(-3+sqrt(9-4mu/3))/2>1, and maximum mass-squared suppression relative to accepted soft and .018 persistent modes. Near lambda=0 is not lambda=0: the growing harmonic remains generic, not the exceptional sigma=H harmonic. No short-interval quadratic prediction is extrapolated to infinite stiffness.

One CPU with inherited line and core leases, 1GiB cap, 590s child/600s wrapper, no queue/retry, frozen last-start deadline17:50:51Z. Source/parent/runtime hashes checked before and after. Atomic nonoverwriting outputs, failures preserved, independent prospective and terminal reviews. No writes to parents or papers.
