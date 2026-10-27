# R1: exact-decimal reader compatibility, unchanged identity experiment

The original packet lin-c4-evolution-identity-20261006T044000Z is preserved with
its frozen sources, guard 84d1e800ebb5deedae8e175dcf6b162a08938977f77752080f75f33be240f3ab,
control receipts, review and RUN_FAILURE.json. It stopped while loading the
first saved numerical seed, before accepting any physical cell or checkpoint.
No physical result exists in that attempt.

The repair routes every input decimal/scientific literal through exact Python
Fraction numerator/denominator construction before python-flint fmpq. No
binary64 conversion, rounding, changed input or narrowed enclosure is involved.
The constructor's integer/rational-string limitation was missed by rational-
only fixtures. New fixtures cover decimals, scientific notation and rationals.
A failed-closed top-level receipt now also covers pre-loop loading exceptions.

All mathematical equations, physics, domains, grids, amplitudes, precision,
step counts, stopping criteria and acceptance gates are byte-identical to the
first contract. The entire synthetic/recovery preflight and source-bound review
must be repeated for this new namespace before freezing and starting its
unchanged three-flow graph. No predecessor or first-attempt frozen file is edited.
