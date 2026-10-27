# Full cubic propagation and boundary matching

Both numerical representations completed the full inherited interval and resolved the upper cubic matching denominator away from zero. Their cubic shooting-multiplier intervals overlap, and the matched lower and upper boundary rows enclose zero. The independent saved-certificate audit passed. This establishes full-interval formal cubic propagation and nonsingular boundary matching for the fixed accepted inputs; it does not yet determine the cubic proper-distance correction.

## Completed checks

- Primary completed 8,183 cells; independent completed 16,365, with half the primary step size. The two formulations retain polynomial E and direct W respectively.
- All 151 source, recurrence and unchanged-lower-RHS controls passed. Each representation reproduced its sealed short-probe endpoint bitwise.
- Every cell passed strict Picard inclusion, finite-state checks and zero-inclusive whole-cell background and first-, second- and third-order constraint checks.
- Each uncertain upper endpoint was covered by two validated cell pieces without a gap. The inherited lower-order endpoint fields overlap the accepted full second-order result.
- Both homogeneous upper Robin denominators exclude zero. A single A3 interval per engine is used at both walls; the engines' A3 enclosures overlap without intersection narrowing.
- The exact-Fraction streaming auditor checked all 24,548 cells across 768 immutable chunks, their checkpoint chains, endpoint polynomial enclosures, uncertain-domain coverage and boundary-matching algebra.

The audit verifies recorded RHS/derivative/constraint witnesses and their exact algebraic use; it does not independently re-evaluate every ODE derivative enclosure or the direct-W exponential. Its scope is preserved in AUDIT_RESULT.json.

Production and publication took 609.965702 seconds; the certificate audit took 188.750369 seconds, as recorded in the terminal receipts. Source preparation, prospective review and final integrity review are separate from those durations. Peak RSS was 167908 KiB. Streamed certificates kept the calculation within the inherited 2 GiB process cap.

## Numerical meaning

The independent terminal integrity review passed all 1336 bindings and 768 chunk/checkpoint pairs. Both homogeneous upper matching denominators have outward decimal enclosure [497495, 497796], well away from zero. The combined outward shooting-multiplier enclosure is

    A3 in [-16.8465, -8.94145].

Its sign is resolved, but its width is about 7.90504. It is a normalized shooting multiplier, not a distance coefficient. The assembled upper cubic fields remain broad and sign-unresolved: across both representations their displayed bounds fit within p3 in [-315.308, 315.496], f3 in [-257101, 258414], and g3 in [-1254280, 1239440]. These are interval-enclosure limitations, not evidence that the physical fields fluctuate across those ranges. A nonsingular matching denominator therefore resolves one obstruction without resolving the accuracy of every derived observable. The next distance calculation must propagate these full uncertainties; it may legitimately return a sign-unresolved interval.

The measured primary and independent chunk archives occupy 1,603,893,467 and 3,051,516,926 bytes respectively. FINAL_REVIEW.md, READOUT.json and INDEPENDENT_TERMINAL_CHECK.json record the independent integrity acceptance and outward numerical displays.

## What remains

The next test is the complete proper-separation budget, using the archived flow and the same A3 throughout:

    d_sep3 = xi_b3 - xi_a3
           + integral[c3 - 2p3 - 2p1*c2 + 4p1*p2 - (4/3)p1^3] ds
           + [-2p1*xi2 + (c2 - 2p2 + 2p1^2)*xi1 - p1prime*xi1^2]_a^b.

The boundary graph contribution alone cannot supply this answer, nor can the sign of the shooting multiplier A3. The archived whole-cell fields and Taylor coefficients allow prospective integration without repeating the ODE propagation. That separate test must retain the full A2 and A3 uncertainties, check an independent transport reconstruction and require overlap between both distance enclosures. Even a resolved cubic distance coefficient would remain a formal-order result, not a finite-amplitude convergence radius or nonlinear dynamical formation result.

No successor calculation has been launched by this packet. The exact chunk checkpoints are durable evidence; they are not advertised as a tested bitwise-resume interface.

## Provenance

Frozen manifest: `625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e` (1,336 bindings).

Result: `a7691eebbe0b867ea8bc74874158758589548292265d6225f4d79c0383b15e68`.

Audit: `a1b306856f98c6279b9915c096b3be7175c632a61f6f0e3f9e020a1e9adbe583`.

The accepted short-flow parent is 20261026T033000Z_CUBIC_PROBE_R1. Its source equations, parameters, precision and step sizes were preserved. Scientific execution was Linux-only under the inherited single-core lease and aggregate-resource policy. See terminal receipts, FLOW_primary.json, FLOW_independent.json and the streamed chunk manifests for exact witnesses.
