# Prospective tightening of the absolute stiffness response

Status: design recommendation only, not frozen or authorized for execution by this packet.

The wall ranking is already resolved. The next distinct question is how tightly the two absolute local response coefficients can be enclosed on the same certified background. The current squared shifted-eigenvalue factor is much less precise than the norm: lambda=mu+4k ranges from about −1.2635e−5 to −2.6346e−6, whereas the norm lies between 292.43 and 359.26. Tightening the mass bracket should therefore precede a more expensive norm calculation.

## Smallest proposed calculation

Retain the exact central background, original action, lower normalization psi(0)=1, proper-coordinate determinant, certified first-event interval, and original negative-mass bracket. Before execution, independently review a fixed maximum number of interval bisection steps and the rule for handling a determinant enclosure containing zero. Each accepted step must preserve a certified opposite-sign pair. A zero-containing midpoint is an unresolved sign, not a sign inferred from its midpoint; preserve the last admitted bracket.

The later [independently reviewed strip-uniqueness lemma](ROOT_STRIP_UNIQUENESS_REVIEW.json) now proves that the original strip contains exactly one real eigenvalue in the retained sector. A nested opposite-sign bracket therefore retains that unique in-strip root. This conclusion relies on the separate analytic proof, not on bisection alone, and says nothing about eigenvalues outside the strip.

A prospective target is a mass-bracket width no greater than 5e−7, with at most six admitted subdivision attempts. The exact target and attempt budget belong in the next independently reviewed contract. This is an operational sizing choice, not a stability criterion. It does not guarantee any final coefficient width.

Endpoint integrations must use uniform exact-background enclosures, not a central best-fit background. The current saved wide-strip norm and endpoint enclosures remain valid for a narrowed mass subset. They may therefore be reused initially without integrating a new norm or new strip. Reevaluate the algebraic coefficients with the newly certified mass bracket and the same valid background, norm and wall-profile enclosures.

If the resulting absolute coefficient intervals are still too broad, diagnose their multiplicative width factors before choosing another calculation. Only then consider a narrow-strip replay with denser checkpoint norm bounds or direct validated norm accumulation. No parameter scan, new background, increased stiffness, or finite threshold search is part of this proposal.

## Required evidence and stop conditions

- Freeze source hashes, exact mass candidates or subdivision rule, original background/event bindings, and classification criteria before computing new signs.
- One numerical worker, BLAS1; acquire applicable resource admission without disturbing other owners.
- Preserve every endpoint enclosure, sign decision, unresolved attempt, runtime and source digest. Do not overwrite the current packet or parent certificate.
- Stop at the attempt/time budget, on inconsistent bindings, lost regularity, or an unresolved sign that the frozen rule cannot handle.
- Independently reconstruct the final sign bracket and response intervals. Report accepted narrow, retained wide, or technical incomplete outcomes without retuning.

The original central certification recorded roughly 51 seconds for its own full physical run. That is historical context, not a runtime promise for a different sequential bisection implementation. Qualify the proposed endpoint workload before scheduling it. There is no reason to launch a long evolution to answer this local spectral question.
