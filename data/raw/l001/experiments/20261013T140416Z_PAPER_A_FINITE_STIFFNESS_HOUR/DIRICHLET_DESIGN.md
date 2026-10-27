# Quantitative upper Dirichlet saturation limit

The accepted finite response test identifies a strictly increasing branch mu(eta) whose limit mu_D satisfies upper Dirichlet condition f_b=0. This separate prospective test brackets that limit and quantifies the maximum available mass increase, rather than repeating the finite response test or refining the old infinitesimal coefficients.

## Identification and uniqueness

Retained first-test event records certify f_b>0 at mu=−164/125000 and f_b<0 at mu=−131/100000, for each engine. Both masses lie within the original full-strip IVP enclosure. The unchanged lower launch, regular flow and exact background therefore give a Dirichlet root between them.

The accepted positive-overlap proof also applies to upper Dirichlet profiles. If two different real masses in the original strip both have f_b=0, their upper Green concomitant vanishes: every term in a³(f_i p_j−p_i f_j−2S(psi_i f_j−f_i psi_j)) contains f_i or f_j. The common lower Robin condition also gives zero lower concomitant. The original full-strip bounds psi>=99/100 and −1<=f<=3 make f_i f_j+6psi_i psi_j>=14403/5000>0 everywhere. Orthogonality is impossible. Thus there is at most one real Dirichlet eigenvalue in this strip.

The first-test original-low R_0>0,f_b>0 and original-high R_0<0,f_b<0 imply opposite Robin endpoint signs for every eta>=0. Exactly one Robin root lies in the original strip by the unchanged positive-overlap argument. The tracked branch remains there for all finite eta. Its Dirichlet limit cannot be either boundary because f_b is nonzero at both. Therefore this unique Dirichlet root is precisely the tracked limit, not an unidentified spectral root.

## Frozen computation

Start from the retained strict f_b bracket [−164/125000,−131/100000], width2e−6. Execute at most six sequential dual-engine exact midpoints using the same original engines, bits, A/D, model and lower normalization. Require both strict signs to agree before replacing an endpoint. Stop immediately at a zero-containing enclosure or disagreement; retain the last admitted bracket. Stop when width<=1/20000000=5e−8. No endpoint replacement, retry, precision change, or threshold change is permitted.

`dirichlet_test.py` uses the frozen first-test `flow` function, which records f_b over the entire event cover and preserves every cell enclosure check. It does not modify the producers or the first test. All new products are under `output_dirichlet`. The new gate, first terminal receipt, first execution and the exact source endpoint records are hash-bound. The original runtime authentication remains required in addition to this test's gate.

## Predeclared outputs and classifications

Report the strict mu_D bracket [d_lo,d_hi]. With the accepted original mode bracket [m_lo,m_hi] and eta100 lower bound q=−164/125000, report

- total available gain: d_lo−m_hi < mu_D−mu(0) < d_hi−m_lo;
- remaining gain after the sixfold change: 0 < mu_D−mu(100) < d_hi−q;
- conservative achieved fraction: (mu(100)−mu(0))/(mu_D−mu(0)) > (3/16000000)/(d_hi−m_lo).

The last expression is only a certified lower bound on the achieved fraction, not an estimated or exact fraction. All statements use the accepted monotone branch theorem and strict finite displacement; no quotient of uncertain correlated central values is used. If a coarse bracket makes a displayed lower bound uninformative, preserve it without claiming positivity beyond the theorem.

`QUANTIFIED_SATURATION` requires target width and total gain upper bound <1e−6. Otherwise report `RETAINED_WIDE` with the last strict bracket and stop reason. A technical failure is `TECHNICAL_INCOMPLETE`. Controls retain zero-sign, denominator, event-cover and both engine algebra checks. Production cap300 seconds,90 seconds/flow, at most12flows, single CPU/BLAS1; reserve600 seconds before the hour deadline. Expected runtime under two minutes. Independent sequential audit cap180 seconds reconstructs midpoint transitions, exact f event hulls, source/gate/runtime/exit records, and all gain/fraction bounds, and checks the uniqueness corollary above. It does not launch another flow.
