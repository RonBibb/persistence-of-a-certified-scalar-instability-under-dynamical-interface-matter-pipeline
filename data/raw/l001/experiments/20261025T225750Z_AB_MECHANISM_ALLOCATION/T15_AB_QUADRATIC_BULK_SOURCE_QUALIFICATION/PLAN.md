# T15 — exact quadratic bulk-source qualification

Prospective candidate, no execution before independent review/admission. The existing Linux Python runtime has no SymPy; no dependency installation is proposed. Use a deliberately small bounded sparse rational polynomial ring plus degree-two z-series, not a general computer algebra framework.

## Authority and scope

Bind manuscript S6, Q1–Q4, current SECOND_ORDER_BULK_SCRATCH.md and SECOND_ORDER_MECHANISM_SCOPE.md. Production scope is the **fixed Eulerian s chart**, X=0, for bulk-source qualification only. The intended future full second-order solve remains in the manuscript pulled chart and requires its own source transformation and wall qualification. No new radial solution, boundary source, numerical amplitude, finite-charge radius or proper-distance coefficient is computed here.

Use e=E² and m2 for the scalar potential coefficient. Variables in exact lexicographic order are g,H,T,Phi,e,p,f,m2,h. Background and first-order ODEs define a polynomial radial derivation, with h,m2 constant, e'=-2He, mu1=-18h² and R=-6h. The input background constraint is 6H²-T²/2-6+m2 Phi²/2-6h²e=0. The first-order constraint is Tg-(m2 Phi-4HT)f+(2T²+42h²e)p=0. Verify preservation identities before source qualification.

## Independent source construction

Create truncated series p(z)=zp,b(z)=-2zp,f(z)=zf. Compute the exact four displayed S6 residual expressions using series convolution, polynomial radial differentiation, temporal differentiation nR, and exact exponential coefficients through z². Compare z0/z1 with their expected background/first-order constraint expressions without silently replacing them by zero. Compare extracted z² coefficients to the independently written simplified qT,qM,qK,qR formulas in the scratch document. The series construction must not call those simplified formulas.

Form c2,Sp2,Sc2,Sg2 from Q2/Q3 and construct the Q4 polynomial remainder Sc2'+4HSc2-T Sg2-Dn2 Sp2. Polynomial division by the first-order and background constraints emits explicit multipliers and remainder, and reconstructs the polynomial identity exactly. In the declared order the leading monomials are gT and H²; their coprimality verifies that the two generators form a Groebner basis by the product criterion. A zero remainder is an exact conditional identity, not a random sample. No inverse T occurs.

Report every original coefficient, reduced source, constraint, Q4 raw residual, multiplier and remainder in IDENTITIES.json with exact rational coefficients. Deliberate mutations flip the KG pf sign, halve the mixed source and omit scalar time-stress from the radial source; each must disagree with the independent direct S6 extraction. Ring, derivative and product-rule controls qualify the small arithmetic machinery. The separate chart control checks X b1'+X' b1=(Xb1)' for a nonconstant manufactured profile; integration establishes the transport boundary term. It is not full pulled-source qualification.

## Gates and runtime

All identities must pass or publish TECHNICAL_INCOMPLETE. Scientific initialization occurs only after source/runtime admission. Linux exact Python, standard one-core1GiB lease, producer cap900 seconds and wrapper910 seconds, product/term/reduction size caps. No new dependencies and no new ODE. Standard admitted/sources plus exact runtime hashes; bind manuscript equation authority in the source manifest. Atomic no-overwrite output and independent terminal reconstruction required. No scientific execution has been performed by the author.
