# Methods citation chain for the computer-assisted theorem

## Purpose

This note identifies the standard validated-numerics results that support the
manuscript-level explanation of the certificate. It does not outsource any
model-specific proof obligation. The actual theorem still depends on the
stored interval enclosures, exact cover, source audit, and local verifiers
listed in `CLAIM_TO_EVIDENCE_MATRIX.md`.

## Canonical references

1. **Moore, Kearfott, and Cloud, _Introduction to Interval Analysis_,** SIAM,
   2009, especially Chapter 8, pp. 105--128,
   [doi:10.1137/1.9780898717716.ch8](https://doi.org/10.1137/1.9780898717716.ch8).
   This is the appropriate standard reference for interval Newton methods and
   the existence-and-uniqueness implication of a strict interval-Newton
   inclusion. In the present theorem, that general implication is applied only
   after the validated first-event map and its total derivative have been
   enclosed on the frozen launch interval.

2. **Warwick Tucker, _Validated Numerics: A Short Introduction to Rigorous
   Computations_,** Princeton University Press, 2011, ISBN
   978-0-691-14781-9. Chapter 6 treats ordinary differential equations. This is
   a broad reference for directed rounding, interval enclosures, and the
   distinction between an ordinary numerical approximation and a rigorous
   computation. It is context, not evidence that this particular implementation
   is correct.

3. **Nedialkov, Jackson, and Corliss, “Validated solutions of initial value
   problems for ordinary differential equations,”** _Applied Mathematics and
   Computation_ **105** (1999), 21--68,
   [doi:10.1016/S0096-3003(98)10083-8](https://doi.org/10.1016/S0096-3003(98)10083-8).
   This surveys validated Taylor-series methods for ODE initial-value problems
   and the two required outputs: a uniqueness guarantee and an enclosure of the
   true solution. It is the closest general methodological reference for the
   Taylor--Picard flow enclosures used by the independent D1 replay.

4. **Kapela, Mrozek, Wilczak, and Zgliczyński, “CAPD::DynSys: a flexible C++
   toolbox for rigorous numerical analysis of dynamical systems,”**
   _Communications in Nonlinear Science and Numerical Simulation_ **101**
   (2021), 105578,
   [doi:10.1016/j.cnsns.2020.105578](https://doi.org/10.1016/j.cnsns.2020.105578)
   and [arXiv:2010.07097](https://arxiv.org/abs/2010.07097). This is a modern
   comparator for rigorous ODE integration and computer-assisted dynamical
   analysis. The present certificate does **not** use CAPD; citing it must not
   imply software or producer identity.

## Exact role in the manuscript

The methods section should make the logical chain explicit:

1. interval arithmetic with outward rounding encloses the IVP flow and its
   sensitivity on each accepted cell;
2. Picard self-containment certifies the represented solution segment;
3. a transverse interval enclosure of `G_s` defines the local first-event map;
4. the implicit-event formula encloses the total derivative of the scalar
   shooting function;
5. a strict interval-Newton inclusion establishes one and only one root in the
   frozen root interval;
6. the fixed-distance result uses a different implication: an exact contiguous
   interval cover whose every terminal box excludes negative curvature or
   separates at least one wall residual from zero.

Only step 5 is the standard interval-Newton theorem cited to Moore--Kearfott--
Cloud. Steps 1--2 are situated by Nedialkov--Jackson--Corliss and Tucker, but
their satisfaction here is established by the local source and certificates.
Step 6 is a finite exhaustive-cover argument and should be proved directly in
the article rather than presented as an appeal to software.

## Citation boundary

- A methods citation does not validate a local implementation.
- A passing hash or replay does not prove an interval theorem by itself.
- The independent D1 producer reduces common-code risk but does not make the
  D2A cover producer-independent.
- CAPD is a comparison point only; it was not used to produce either sealed
  certificate.
- The article should state the rounding model, inclusion guards, failure
  routes, and interval-Newton hypothesis explicitly enough that a reader can
  map each standard theorem to the stored evidence.

## Recommended placement

Cite Moore--Kearfott--Cloud at the interval-Newton proposition; cite
Nedialkov--Jackson--Corliss when introducing validated Taylor flow enclosures;
cite Tucker once in the general methods paragraph. CAPD is optional and useful
only if the article includes a short paragraph situating the custom replay
against established rigorous-ODE tooling.
