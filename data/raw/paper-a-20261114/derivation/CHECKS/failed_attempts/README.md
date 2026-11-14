# Failed attempts (kept as required by the request)

## attempt1 (curvature jets), run 2026-11-14T06:21:26Z on linux.vm

`attempt1_check_curvature_jets.py` with outputs `attempt1_curvature.stdout` and `.stderr`.

Result: every check passed except C8, the radial ADM/Gibbons-Hawking identity.

Cause: the checker, and DERIVATION.md P3.4, used the timelike-normal acceleration a^mu = +q^{mu nu} d_nu N / N. For the spacelike normal n = N^-1 d_s we have n_A = +N delta^s_A, so a_mu = -Gamma^s_{s mu} = -d_mu ln N.

A debug run between attempt1 and the 06:23:05Z rerun gave (it was not timestamped, so no time is claimed) lhs = bulk - 2 div(nK) - 2 div(a_code) exactly at e^0, e^1 and e^2. That is the stated identity with a_correct = -a_code.

The identity R = R4 + K^2 - K.K - 2 div(n K - a) itself is correct. Only the sign of a^mu was wrong. The a-term is a pure 4D divergence either way, so no kinetic or radial result changes. An erratum is appended to DERIVATION.md.

The fix also forces nonzero perturbation values (A, psi, f, xi at s0). In the debug draw one case had A(s0) = 0, which made the a-term vanish and hid the sign.

Recorded 2026-11-14T06:23:05Z.
