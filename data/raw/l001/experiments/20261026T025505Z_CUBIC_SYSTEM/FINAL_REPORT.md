# Cubic system sources qualified

The complete cubic bulk forcing and moving-wall scalar/oscillator sources passed their qualification stage. The bulk compatibility identity closes exactly under the accepted lower-order equations, and the wall coefficients agree with a separately derived closed expression. This clears the source-equation gate toward the full cubic proper-separation calculation; the cubic field and distance have not yet been solved.

## What this adds

The prior result supplied only the negative cubic graph contribution. This packet derives the forcing needed for the missing bulk solution, the actual scalar boundary loads and the moving-endpoint distance correction. It retains the cubic Dc*Df coupling, velocity/normal effects, affine material force and second-order boundary motion. It uses the full assembled second-order fields, not their shooting particular alone.

The cubic tracefree field combination is fixed algebraically:

    c3 = -(8/19)(6 p1 p2 + f1 f2 - 3 p1 c2).

The new scalar mass is mu3=-270k. The source compatibility was verified by an explicit exact polynomial multiplier identity using the background and both lower-order scalar constraints. No division by the scalar gradient was used. The same regular equations therefore do not introduce an artificial singularity at its zero.

The actual distance still requires the unsolved p3 field:

    d_sep3 = xi_b3-xi_a3
           + integral[c3-2p3-2p1*c2+4p1*p2-(4/3)p1³] ds
           + [-2p1*xi2+(c2-2p2+2p1²)*xi1-p1'*xi1²]_a^b.

In particular, the last term cannot be inferred from the graph coefficient alone. The negative graph result is preserved as a fixed control, not promoted to the sign of the full distance.

## Checks and outcome

- 24 exact bulk checks passed, including direct/closed cubic expressions, lower-order replay, divisors, compatibility and omission controls.
- 59 exact wall/transport checks passed, including independent cubic Q5 formulas, source/new-field separation, Q6 elimination, lower-order replay, sensitive omissions and a manufactured moving-endpoint antiderivative check.
- Both accepted endpoint engines yielded overlapping boundary-load enclosures. The upper Robin load remains sign-unresolved; no sign was forced.
- A separately authored audit verified the saved polynomial compatibility certificate and reconstructed the Robin load assembly using exact Fraction intervals. It did not rerun the parent ODE or independently repeat every source extraction.
- Independent terminal review verified all 1,287 frozen bindings, result digests and runtime inventories. No failure artifact exists.

Production scientific execution took 2.189759 seconds; the independent certificate/load audit took 1.911831 seconds. Those durations exclude preparation and review. Scientific calculations were Linux-only under the shared single-core lease policy. Leases were released; no full cubic flow or successor is running from this packet.

## Next step

The next executable stage is a short, two-engine feasibility probe of the augmented cubic flow: verify its launch divisor, validated stepping, constraint preservation, interval growth and measured cost before admitting a full solve. NEXT_FLOW_PLAN.md records the state layout, launch equations, shooting relation and complete distance budget. It is a prospective plan, not a run receipt.

The eventual full cubic coefficient will answer whether the negative boundary trend survives after adding the bulk and transport terms. A finite-amplitude validity range still needs a separate quantitative remainder argument.

## Provenance

Frozen manifest: `98edf139b697e6cc9665167bbf27594a2f9a39da4957fbd8e190f1895c7b83d9`.

Result: `a51ca19ce8db36dc13d60d4149aa76e98d9f3d785e55bbbd270465a88f57664e`.

Audit: `4f1fb3491b33ec9ad33bd735bd0c97981842af1c4fcf6f797b7cd305d7f44daf`.

The accepted cubic graph parent is 20261026T023331Z_CUBIC_GRAPH; its accepted full second-order parent is 20261026T015206Z_FORCED_SECOND_ORDER_R1. Original sources and accepted records were not changed. See FINAL_REVIEW.md, both terminal receipts, RESULT.json and AUDIT_RESULT.json for acceptance and exact rational witnesses.
