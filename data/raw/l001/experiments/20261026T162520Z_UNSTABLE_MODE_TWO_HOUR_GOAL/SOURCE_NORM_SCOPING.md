# Source-norm ledger for the next bridge

Prospective scoping only; not a proof of the analytic inverse or nonlinear source bounds. It makes the needed harmonic powers explicit so the next session does not mistake the completed real-axis response estimate for the required analytic theorem.

Let `||.||_p` denote the proposed Nagumo norm at radial index `p`. Its collar and distance function must be defined in the successor; endpoint trace bounds must be justified there. The candidate bulk norm is

\[
U_n(v)=n^2\|v_n\|_{2n}+n\|v_n'\|_{2n+1}
+\|v_n''\|_{2n+2}.
\]

For graph and oscillator variables use cubic weights, `n^3*|xi_n|` and `n^3*|chi_n|`. Those stronger wall weights are intentional: the existing raw response certificate states quadratic wall weights, but the nonlinear source estimate needs the extra harmonic factor at the wall.

## Required source budget

For a single majorant coefficient `B_n`, seek bounds with constants independent of `n`:

| Source | Required form | Why |
|---|---|---|
| Trace source `QT_n` | `||QT_n||_(2n) <= C B_n` | Division by `lambda*(lambda-h)` pays two harmonic powers. One/two Nagumo derivatives cost order `n`/`n^2`. |
| Mixed source `QM_n` | `||QM_n||_(2n+1) <= C B_n` | Division by `lambda` yields `n*||Sp_n||_(2n+1) <= C B_n`, with the separately controlled trace term. |
| Reconstructed mixed source derivative | `||Sp_n'||_(2n+2) <= C B_n` | Pays the source derivative needed by the second derivative of the metric. A Nagumo derivative costs order `n`; the preceding `1/n` gain is essential. |
| Scalar and radial loads | `||Sg_n||_(2n+2)+||Sc_n||_(2n+2) <= C B_n` | Inputs for reduced scalar inversion and algebraic metric reconstruction. Compatibility must be used consistently. |
| Raw graph/Israel load `QI_n` | `n*max|QI_n| <= C B_n` | The graph divisor is order `n^2`; to control `n^3*|xi_n|` the raw load must have one additional inverse power. |
| Scalar normal load `j_n` | `n*max|j_n| <= C B_n` | Required by the reduced Robin load. |
| Oscillator load `o_n` | `n*max|o_n| <= C B_n` | Needed for the cubic wall oscillator norm, not merely quadratic response. |

These are targets. The completed real-axis estimates do not establish these Nagumo source bounds or the corresponding analytic inverse.

## Explicit wall scaling check

Under a uniform bound on background coefficients and the candidate bulk estimate, the exact linear wall rows give schematically, with constants independent of `n`,

\[
|\xi_n|\le C|QI_n|/n^2,
\qquad
|\chi_n|\le C\bigl(|f_n|+|\xi_n|+|o_n|\bigr)/n^2.
\]

Consequently,

\[
n^3|\xi_n|\le Cn|QI_n|,
\quad
n^3|\chi_n|\le C[n|f_n|+n|\xi_n|+n|o_n|].
\]

The table's wall budgets and `n^2` bulk value control would supply these cubic weights. This check does not derive the raw wall source bounds; it explains why the extra outer factor `n` is indispensable in the source-counting proof.

## Metric derivative caution

Do not differentiate the algebraic formula for `p_n` twice and assume the resulting higher source derivatives are free. The existing compatible reconstruction instead uses the mixed equation for `p_n'` and its derivative for `p_n''`, explicitly paying `Sp_n'`. The compatibility identity contains `Sc_n'` but is an identity of the actual sources; the successor must state precisely where that derivative is needed for regularity and where no independent norm estimate is used.

## Most informative first decision

Attempt the common-collar inverse together with this ledger. If a proposed estimate only controls unweighted wall loads or only real-axis suprema, it has not closed the nonlinear majorant. Conversely, if every row and the analytic inverse are proved with explicit constants, the conditional scalar lemma already supplies a conservative convergence-radius recipe. Proper-separation and proper-clock tails still need their own analytic observable bounds.
