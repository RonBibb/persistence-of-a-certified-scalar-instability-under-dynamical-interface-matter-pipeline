# A certified isolated separation in a five dimensional Einstein scalar two wall model

For one fixed Einstein–scalar two-wall model, the static equations admit exactly one positive-curvature solution on the declared first-event shooting branch. Its proper wall separation is near 1.9975, and the simultaneous wall equations isolate both its launch value and separation. At the separately prescribed separation 0.9996389747145851, an exhaustive cover excludes positive-curvature solutions throughout the same launch interval. The physical content is a certified compatibility distinction between two boundary placements in one reduced model. The selected separation is not a free modulus of that fixed problem.

## Action and exact conventions

Work on the doubled \(S^1/\mathbb Z_2\) cover, with \(\ell=\kappa_5=1\), \(\Lambda_5=-6\), and the independent collapse scalar \(\chi=0\). The action is

\[
\mathcal S=\frac12\int_{\widetilde{\mathcal M}}\!\sqrt{-g}(R-2\Lambda_5)
-\frac12\int_{\widetilde{\mathcal M}}\!\sqrt{-g}\bigl[(\nabla\Phi)^2+m^2\Phi^2\bigr]
-\sum_{i=a,b}\int_{\Sigma_i}\!\sqrt{-h_i}\,\tau_i(\Phi),
\]

where \(\tau_a=\lambda_a+\gamma(\Phi-v_0)^2/2\) and \(\tau_b=\lambda_b+\gamma(\Phi-v_1)^2/2\). Each decimal literal below denotes its exact IEEE binary64 dyadic value, not the corresponding exact decimal rational or a fitted uncertainty interval.

| Input | Exact binary64 literal |
| --- | --- |
| \(m^2\) | `0.41` |
| \(\gamma\) | `20` |
| \(v_0\) | `0.1` |
| \(v_1\) | `0.09048374180359596` |
| \(\lambda_a\) | `5.999990376773895` |
| \(\lambda_b\) | `-6.052844277744164` |

The upper tension and upper scalar target were independently frozen in the source model. The lower tension was reconstructed from the unchanged constructor's explicit \(6-U_a\) rule at the bound N65 solution; it was not an independently archived input. This provenance is an assumption of the theorem and must accompany its parameter table.

Use \(ds_5^2=e^{2A(s)}\gamma_k+ds^2\), \(\operatorname{Ric}(\gamma_k)=3k\gamma_k\), and \(\Phi=\Phi(s)\), where proper distance \(s\) increases from the lower to the upper wall. With \(H=A_s\), \(S=\Phi_s\), and inward normals \(n_a=+\partial_s\), \(n_b=-\partial_s\), the doubled-cover one-sided junction equations are \(K^{(i)}_{\mu\nu}=-\tau_i h_{\mu\nu}/6\) and \(n_i\cdot\nabla\Phi=\tau_{i,\Phi}/2\). Thus

\[
A_s=H,\quad H_s=-S^2/3-ke^{-2A},\quad \Phi_s=S,\quad S_s=m^2\Phi-4HS,
\qquad H^2-1-S^2/12+m^2\Phi^2/12-ke^{-2A}=0.
\]

For \(a=\Phi(0)\), fix \(A(0)=0\), \(H(0)=-[\lambda_a+\gamma(a-v_0)^2/2]/6\), \(S(0)=\gamma(a-v_0)/2\), and \(k(a)=H(0)^2-1-S(0)^2/12+m^2a^2/12\). Define

\[
G(s,a)=H(s,a)-[\lambda_b+\gamma(\Phi(s,a)-v_1)^2/2]/6,
\qquad h(s,a)=S(s,a)+\gamma(\Phi(s,a)-v_1)/2.
\]

The first-event problem sets \(D(a)\) to the first transverse zero of \(G\) and solves \(q(a)=h(D(a),a)=0\). The prescribed-distance problem instead solves \(F(a,D_0)=(G(D_0,a),h(D_0,a))=0\). These definitions distinguish proper separation from the conformal length \(\int_0^D e^{-A}\,ds\). The [formal reduction lemma](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-theorem-causal-readiness-window-20261003T205314Z/FORMAL_REDUCTION_LEMMA.md) supplies the bulk variation, junction signs, propagated first integral, and event sensitivity identities.

## Computer assisted theorem at the fixed parameter point

Within \(0\le a\le v_0\), restricted to \(k(a)>0\) and the first-event definition above, exactly one simultaneous-wall solution exists. It satisfies

\[
a_*\in[0.09901086489880687,0.09901086689880687],\qquad
D_*\in[1.99749755859375,1.99761962890625].
\]

An independent interval implementation encloses its curvature by \([0.000326841301145298,0.0003268413757636101]\), proves positive warp and finite conformal length, and encloses the first integral throughout the domain and the identities at both walls. The solution is locally isolated as a zero of \(F(a,D)\): the primary and independent determinant enclosures are respectively \([2221.879246216278,2224.53955879436]\) and \([2220.8647309726075,2225.5545418744878]\), both separated from zero. The displayed width in \(D_*\) represents enclosure uncertainty around an isolated separation.

At \(D_0=\mathtt{0.9996389747145851}\), interpreted as its exact binary64 value, no launch in \([0,v_0]\) with positive curvature satisfies both wall equations. On every cover box not already excluded by negative curvature, \(\max(|G(D_0,a)|,|h(D_0,a)|)>0.0077\). Consequently the mismatch between \(D_0\) and \(D_*\) cannot be attributed to a missed launch or root-locator tolerance within this declared static class. The [upgraded theorem](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-static-theorem-publication-upgrade-20261005T050426Z/UPGRADED_THEOREM.md) is the current combined statement.

## Proof dependencies and software assurance

The reduction gives the proof its subject: the certified residuals are the action-derived wall conditions with the specified factors and orientations. Differentiating the propagated constraint gives zero along the reduced flow. At a transverse event, \(D'=-G_a/G_s\) and \(q'=h_a+h_sD'\), so a strict interval-Newton self-map with \(0\notin q'(I)\) establishes one root in the narrow interval \(I\).

The high-resolution D1 producer supplies that self-map. Its exact Newton image is

\[
\left[\frac{456607025194779413}{4611686018427387904},
\frac{114151756532473697}{1152921504606846976}\right]\subset\operatorname{int}I.
\]

The independently implemented Taylor–Picard interval flow reproduces existence and the geometric enclosures. The global first-event certificate then extends uniqueness from \(I\) to the entire declared launch interval through a gap-free, dual-producer cover with 726 terminal boxes: one certified root box, 19 negative-curvature exclusions, and 706 scalar-residual exclusions. No unresolved box remains. Finally, the nonzero two-variable Jacobian gives local isolation in \((a,D)\); it does not exclude solutions on later Israel events or outside the ansatz.

The D2A proof uses a separate exact 693-box cover of \([0,v_0]\). Twenty boxes have negative curvature; 670 exclude zero in both wall residuals, one in the Israel residual alone, and two in the scalar residual alone. This is one proof-bearing full-cover producer with an independent audit of the stored exact cover and enclosures, not an independently reproduced D2A integration. Its uniform residual-vector floor is stronger than a finite collection of unsuccessful root searches. Primary producer results, audit records, and their roles are mapped in [CLAIM_EVIDENCE.json](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/20261012T192834Z_PAPER_A_STATIC_CONTRIBUTION/CLAIM_EVIDENCE.json).

## Existing extensions that change the discussion

Parameter persistence is no longer merely a suggested future calculation. With all other inputs fixed and \(\lambda_b=\lambda_{b,0}+\delta\), \(\delta\in[-10^{-6},10^{-6}]\) as exact rational endpoints, the [later uniform enclosure](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/RESULT.json) establishes a locally unique isolated first-event solution in the frozen narrow launch box for each fixed tension. It also preserves the full-launch exclusion at \(D_0\) and the residual floor above 0.0077. Its event bracket is \([16363/8192,16365/8192]\). This extends local persistence and fixed-distance exclusion, not full-launch first-event uniqueness across the tension interval. The associated integrity record reconstructs exact endpoints and bindings; it expressly does not claim a separate independent neighborhood producer.

The central solution also has a separately accepted physical scalar/radion mode with \(-33/25000<\mu_*<-131/100000\), positive kinetic norm, and nonzero wall-separation component. The [central mode result and report](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/RESULT_REPORT.md) support linear instability in a physical scalar direction at the central background. Two independent equation implementations establish the endpoint signs while sharing the pinned Arb arithmetic library and checkpoint runner. They do not establish eigenvalue uniqueness, a complete spectrum, instability throughout the tension neighborhood, or a nonlinear endpoint. The arbitrary perturbation sign does not choose contraction over expansion.

These results should replace the October 5 manuscript suggestions to perform an initial parameter-neighborhood calculation and an initial central spectral calculation. The static theorem remains the main result; the local extension can be a corollary or supplement, and the central negative mode should inform the physical discussion. Short generalized-harmonic responses are neither a stability premise nor part of this static proof.

## Significance and paper boundary

The plausible contribution is the conjunction of independently enclosed existence and geometry, complete-launch first-event uniqueness, isolated separation, and exhaustive exclusion at a second prescribed separation for the same specified action. Together these turn a numerical compatibility question into a model-specific certificate. Local tension persistence shows that the compatibility distinction survives one small, explicitly bounded input variation; the central negative mode prevents interpreting the selected static configuration as a stable endpoint.

This significance does not depend on a priority claim. The saved [literature assessment](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-static-theorem-publication-upgrade-20261005T050426Z/NOVELTY_REFRESH.md) already identifies scalar-selected spacing, curved branes, shooting, and computer-assisted Einstein existence as established ingredients. A conventional citation review remains necessary before submission.

The theorem is restricted to this action, its exact inputs and wall conventions, the reduced static ansatz, the launch interval, and the positive-curvature first-event class. It does not establish general static uniqueness, exclude zero or negative curvature at \(D_0\), prove dynamical selection, supply collapse initial data, or imply a horizon or child universe. The central mode adds a linear instability statement, not a nonlinear fate. The remaining immediate paper task is a portable, dependency-complete proof archive and integrated manuscript, as specified in [ARCHIVE_READINESS.md](/Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/20261012T192834Z_PAPER_A_STATIC_CONTRIBUTION/ARCHIVE_READINESS.md).
