# Independent R1 preflight review

Decision: PASS FOR A NEW FREEZE AND THE SAME CONTRACTED TWO-ENGINE RUN.
This approves the disclosed implementation repair, not a physical result.
The qualitative theorem and explicit-radius conclusion remain subject to the
unchanged physical gates and independent postrun audit. No physical D1
integration was performed by this review.

## Repair and preserved failure

The original packet `lin-c4-local-certificate-20261005T214000Z`, guard
`b0553d447eff6ddba8479ae887aeaa804c39f7ced8fd5518e9c55d737b307709`, stopped at
its first validated cell with the 32-iteration Picard construction limit.
Its frozen source and failure receipt are preserved and bound as R1 inputs.
The exact frozen first-cell replay showed that the background, the A(0)
variation and the affine coordinate already satisfied inclusion, while the
four zero-launch shape-response components did not. Repeatedly inflating all
components unnecessarily enlarged the affine coordinate's box and amplified
its high-degree polynomial forcing. The original attempt is a technical
enclosure-construction failure, not a physical exclusion or a certified cell.

I read the complete diff against the previously reviewed source. R1 changes
only the contract's repair disclosure, the Picard box-construction update,
the analytic polynomial-forcing fixture, and bindings to the failed attempt.
The update retains an already-contained component and inflates the hull only
for a component that fails the current inclusion test. Crucially, every
component is tested again against the entire updated box on the next
iteration. Acceptance still requires one simultaneous strict inclusion of
all components. Retention is not an assumption that a component stays valid
after another component expands.

This is a sound implementation repair. No component box is shrunk; the final
mathematical inclusion condition and Taylor remainder construction are
unchanged. The exact input domains, equations, shapes, boundary map, precision,
step sizes, 32-iteration cap, inflation amount and scientific gates remain
unchanged. No physical refinement, retuned tolerance or changed model is
introduced.

## Preserved mathematical review

The direct and flux kernels, series primitives, endpoint dual-number map,
exact rational majorants, analytic-radius argument and independent symbolic
derivation are byte-identical to the previously reviewed versions. The full
Hamiltonian first variation remains

    h_ss+4H h_s+2k exp(-2W)h = -(m2 Phi eta+T eta_s)/3.

Both shape-induced metric responses are retained. With `d=u_s(D)`,
`cj=wj_s(D)` and `beta=8k exp(-2W)B_upper`, the complete Jacobian remains

    [ d       c0       c1       ]
    [ 0       1        0        ]
    [ beta*d  beta*c0  1+beta*c1 ].

The exact row reduction proves `det J=d`; the numerical certificate still
encloses the full matrix/inverse and independently evaluates the original
time-jet equations. The nonlinear mixed-Einstein identity establishes fourth
Israel compatibility from scalar Robin and its second-time condition. The
physical-mode tangent, including `b0'(0)=b1'(0)=0`, follows analytically, with
closed-chart factor `Q''''(0)=mu(mu+6k)`. These claims are derived in the
unchanged `INDEPENDENT_C4_DERIVATION.md`, not inferred from finite differences.

The complex-radius premises retain their previous code-level verification:
absolute-value/epsilon-derivative propagation, exact Hermite operator bounds,
the two fifth-jet shapes, strict metric-tube continuation, complete spatial and
time-jet recurrence, and the entire normalization `exp(5ell-4A)` are included.
Exact rational ceilings remain 1578 for the prescribed-deviation coefficient,
92 for the full normalized boundary map, and -2412 for the metric displacement.
The conservative prescribed constants and radius remain `2^1800`, `2^512`
and `delta=2^-9216`; the contraction and self-map ratios remain `2^-441` and
`2^-443`. Runtime background/model/denominator/inverse bounds must still pass.
An unsupported quantitative premise must produce the separate qualitative
classification rather than an inferred or relaxed radius claim.

The full certified root/event intervals and accepted physical-mode receipt
remain controlling. Both full event-time subintervals must be enclosed. The
expected counts remain 8,183 primary cells and 16,365 flux cells. Native
checkpoint canonicalization, exact fresh-process continuation, source/input/
runtime authentication and guard-bound result recovery are unchanged.

## Analytic preflight evidence

The current staging `preflight-control-01/RESULT.json` has SHA-256
`980e2c07b6d2a19789e0472408b8dbb93302a30de78f77b238b01304992eb603`.
All 15 controls pass, and its source hashes match the files below. The new
fixture is the analytic system `s'=1, u'=v, v'=s^4`, with zero initial data;
the checked exact solution is `s=t, v=t^5/5, u=t^6/30`. Each of its eight
cells needed three Picard iterations. This targets the disclosed zero-launch
polynomial-forcing construction problem without evaluating a D1 outcome.

The other controls retain both vacuum flows, native restoration, fresh-process
next-step equality, changed-guard refusal, ignored partial files, exact
independent algebra, two dual vacuum rows and rational complex majorants.
The receipt records Python 3.12.3, python-flint 0.9.0, 768 bits, one numerical
thread and `physical_model_evaluated=false`. The isolated production packet
must authenticate its own final source-bound preflight before freeze.

## Reviewed final hashes

```text
cfe0bb5ce244eaf0e88291a951a42961f13ee6eb8bf1be2a3f0cb7a316942f6e  CONTRACT.md
17f31b2e9fd0bc703bd3860d224e83013062c05f14c341ca02687764418c42bb  ANALYTIC_RADIUS.md
d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603  series.py
57235737768737b5d159f20b60a67174f5099ec3c2513d0bce66b934fbd62973  primary.py
aacbcf5d9c98d4286f78ae9cb206636dd4358297d14c91d44addd2b8e3b4f00f  flux.py
0a48f058b282197b9b4e6d5a99e36af578bcb9e6d036d9848d5513adc009c7d3  validated.py
3135091e7dd35cbda4cfad77261553aaf11e18bf7f011ba8336ebd0f10014f2d  jetmap.py
e3a97644a5296324bb1e166433a22c3e016f4ebf98aab26261039a9e262e57d5  majorants.py
081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e  records.py
86e875df859f402e59f111c1728792f1230ef0f8171b5d30f3119931fdb01875  runner.py
f04d52327cf7581f2a7dc6edf7235ad6d2b02a938c56cebc397e3939100992aa  INDEPENDENT_C4_DERIVATION.md
a4670fc0b0a557aba810c7f60648879570b2f6c36b62653ba12df98364a0473f  independent_boundary_algebra.py
1567943705a50be570248a0601eb461183d36da207efea4f9d716d80a80bcb10  INDEPENDENT_BOUNDARY_ALGEBRA.json
```

Both finite formulations share Arb arithmetic, series/shape primitives and
the repaired Taylor/Picard driver. Their corroboration is not disjoint software
verification. The admitted prospective claim remains only the exact local
three-variable C4 Cauchy-data family, with the explicit tiny radius conditional
on all quantitative gates. It includes none of the predecessor's finite
amplitude samples and proves no all-order compatibility, evolution interval,
nonlinear endpoint or horizon. No successor is authorized by this review.
