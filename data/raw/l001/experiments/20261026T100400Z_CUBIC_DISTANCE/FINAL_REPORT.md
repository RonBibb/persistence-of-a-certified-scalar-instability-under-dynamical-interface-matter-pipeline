# Complete cubic proper distance is negative

The complete cubic proper-separation coefficient is strictly negative for the accepted lower-unit conserved-current direction. Both numerical representations agree; the independent exact saved-budget audit and final integrity review passed. The bulk and moving-endpoint transport corrections cannot reverse the negative graph contribution. This closes the distinction between the earlier graph-only result and the full cubic distance coefficient.

The outward-rounded combined enclosure is

    -402306 <= d_sep,3 <= -401703.

The exact rational endpoints are in RESULT.json. The displayed decimal endpoints are outward-rounded on Linux, not midpoint estimates or intersections of the two engine bounds.

## What the result means

Using the unchanged action/background, physical clock, lower-current normalization (Na^2,Nb^2)=(1,0), and no-factorial convention, the formal expansion has coefficients

    Dproper(z) = D0 + d_sep,1*z + d_sep,2*z^2 + d_sep,3*z^3 + remainder,
    z = delta^2 exp(-6 h t).

The accepted first-order coefficient is approximately -72.9214; the accepted full second-order enclosure is [-4490.546,-4490.267]. The new full cubic coefficient therefore reinforces shortening in the same fixed perturbation direction, rather than opposing it at third order.

At fixed time this is a statement about the amplitude expansion. It does not imply accelerating contraction in time: the retained z factor decays with time. No quantitative remainder bound, finite-amplitude validity interval, nonlinear stability, horizon or child-formation result is supplied here. The next unresolved question is the controlled range of the expansion, not the sign of the cubic coefficient.

## Signed budget

Primary-engine outward decimal displays from READOUT.json:

| Contribution | Enclosure |
| --- | --- |
| Cubic moving-boundary graph | [-402025, -402022] |
| Complete bulk integral | [-292.268, 307.678] |
| Endpoint transport | [11.3757, 12.1229] |
| Complete cubic distance | [-402306, -401703] |

The bulk sign remains unresolved, but its entire allowed range is too small to reverse the total. Endpoint transport is positive and also too small to reverse it. These components are chart-dependent accounting terms, not separately observable or independently variable physical causes. Their complete sum is the distance coefficient. Rounded component displays need not sum to the separately rounded total endpoints.

The independently integrated transport enclosure is [0.215441,23.2832] in primary and [0.487215,23.0114] in the independent representation; each overlaps the direct endpoint enclosure. Independently grouped and direct bulk integrals also overlap. No intersection was used to narrow the reported distance.

## Calculation and verification

The calculation streamed all 24,548 accepted flow cells without a new ODE solve. Full inherited A2 and A3 intervals were preserved. The homogeneous cubic field was integrated separately before multiplying its total by the same A3, maintaining its role as one global shooting multiplier. Whole-cell enclosure quadrature covered the complete uncertain terminal interval with mandatory and optional lengths. Exported dyadic bounds were rounded outward at 2^-80.

The evaluated budget was

    graph = xi_b3 - xi_a3
    bulk = integral[c3 - 2p3 - 2p1*c2 + 4p1*p2 - (4/3)*p1^3] ds
    transport = [-2p1*xi2 + (c2-2p2+2p1^2)*xi1 - p1prime*xi1^2]_a^b.

Exact polynomial controls verified the cubic exponential-density coefficient, the full transport product rule and sensitivity to omitted terms. A separately authored Fraction-interval auditor independently reconstructed all saved densities, integration weights, contributions, totals, endpoint transport, distance forms and the final un-intersected hull. It also independently checked the generic product-rule and exponential identities.

This audit does not repeat the inherited ODE validation or independently exponentiate direct-W inverse-warp exports. Acceptance combines the accepted validated parent flow, reviewed producer expressions, exact budget reconstruction and final binding checks. It retains the inherited mathematical/model premises rather than constituting a new derivation of every governing field or junction equation.

Production took 85.470583 seconds and the exact budget audit took 72.383951 seconds. Final integrity verification checked all 1356 frozen bindings and 768 budget/parent chunk pairs. Scientific execution and readout were Linux-only under the inherited single-core lease and resource limits. No successor calculation is running; sealed parents and manuscripts were not changed.

## Next useful question

Establish a controlled finite-amplitude range by bounding the remainder or designing an independently controlled finite-amplitude comparison under the same governing equations and boundary contract. Another negative formal coefficient alone would not establish that range. Coefficient growth and coefficient ratios are not convergence-radius or tail estimates. This is a prospective next question, not an automatically launched test.

## Provenance

Frozen manifest: `a01370aeb9137311dbb2e9a2d7814261618d54732e7ba0915509b2154344505d`.

Result: `a9d4b4bc67b65021fbd3ecfdcbfe0ceb49bfa1572e9821e7e45b9bebf6940647`.

Audit: `0b11deb93d18e7e1f3bae9b66d5f8245327a07e51fc822c26536834c630c0a02`.

Full-flow parent: 20261026T033400Z_CUBIC_FULL_FLOW. Graph parent: 20261026T023331Z_CUBIC_GRAPH. Full second-order parent: 20261026T015206Z_FORCED_SECOND_ORDER_R1. See FINAL_REVIEW.md, READOUT.json, INDEPENDENT_TERMINAL_CHECK.json, both terminal receipts and the per-engine distance ledgers for exact records and scope.
