# Exact single-turn application to the inherited central background

Status: proposed analytic application for independent review. This reads existing certified artifacts and proves a new consequence; it runs no background or spectral solver and does not replace the predecessor's exact-background or interval-validity premises.

## A quadratic-potential lemma

Let an exact smooth background on [0,b] satisfy

    Phi'=T,       T'=m²Phi-4HT,
    m²>0,        T_a<0<T_b.

The continuous scalar attains its global minimum. The lower endpoint cannot be a global minimum because T_a<0 makes Phi decrease immediately into the interval. The upper endpoint cannot be a global minimum because T_b>0 makes Phi smaller immediately to its left. Thus a global minimum occurs at an interior point s*, where T=0 and

    Phi''(s*)=m²Phi(s*)>=0.

Hence Phi(s*)>=0. Equality would give Phi=T=0 at s*, and the background uniqueness argument would force Phi identically zero, contradicting the endpoint derivative signs. Therefore Phi(s*)>0 and Phi>0 everywhere on the interval.

At every zero of T, consequently `T'=m²Phi>0`. Every scalar turn is an upward crossing. There is at least one because the endpoint signs differ, and there cannot be two upward crossings without an intervening downward crossing. Hence there is exactly one scalar turn, a strict minimum. This proof needs no sampled plot, no numerical turn-location search, and no separate whole-profile positivity certificate.

## Exact hypothesis-to-source map

All paths below are relative to the common experiments directory. The central background continues to mean the exact background already accepted by the predecessor, not a newly reconstructed rounded solution.

| Hypothesis | Existing evidence and exact interpretation |
|---|---|
| Canonical Einstein–scalar, quadratic V, pure wall potentials, generic scalar sector | `academic2-event-horizon/lin-curved-stability-2026-09-29/analysis/INDEPENDENT_FORMULATION.md`, sections1–4, fixes action, half-Robin convention, regular constraint, and exceptional-sector boundary. |
| m²>0 | `20261013T140416Z_PAPER_A_FINITE_STIFFNESS_HOUR/inputs/central_bindings.json`, `model_exact.m2 = 7385903388887613/18014398509481984 >0`. |
| γ=κ_a0=κ_b0=20 | Same bindings, `model_exact.gamma="20"`. |
| T_a<0 | Same bindings give the exact lower launch interval A and v0. Its upper endpoint is `114151756532473697/1152921504606846976`; v0 at that denominator is `115292150460684704/1152921504606846976`, strictly larger. The wall identity `T_a=20(A-v0)/2` proves T_a<0. |
| T_b>0 | `20261013T001854Z_PAPER_A_STATIC_TESTS/inputs/independent_root.json`, `levels[1].root_box.event_quantities.S.exact_bounds`, has strictly positive lower numerator and denominator. Its displayed decimal enclosure is approximately `[0.021551799860688146,0.02167604375206592]`; only the exact rational sign is used. The producer's `rhs` directly identifies `Phi'=S`, so this S is the proper scalar derivative T. |
| Finite smooth interval, a>0, k>0, exact background existence | The same root record's `levels[1].geometry` gives positive proper separation, positive curvature and global positive warp enclosures, under its accepted exact root/flow premises. The predecessor's `TWO_WALL_REVIEW.json` explicitly inherits and accepts these premises for the exact background used here. No new reauthentication of every historical producer step is claimed. |
| B_a0<0 | `20261013T140416Z_PAPER_A_FINITE_STIFFNESS_HOUR/inputs/stiffness_result.json`, both `result.engines.*.B0.exact_bounds`, are strictly negative; displayed outward bounds are `[-0.099942517827263682,-0.099942489356185241]`. |
| β_b0<0 | Same stiffness record, `result.background.bb.exact_bounds`, is strictly negative; displayed outward bounds are `[-0.340445533730908376,-0.338689889412052510]`. The predecessor review identifies bb with the proper upper coefficient `-γT_b/2-T'_b`. |
| No inherited numerical seed required for existence/index | The new seed-free and turning-count theorems use the preceding background predicates directly. The old mass certificate remains useful for locating the unique branch, but is not a premise of its new existence or global negative-shifted count. |

The read-only source checks produced these SHA-256 values:

    predecessor TWO_WALL_REVIEW.json
      efa077c7b365c3607cae39504231883fcc256a41ffd61c30f9af6a9d22f2a4b9
    predecessor inputs/central_bindings.json
      e3061fbe20f11df19df9acc71d8869daaea78a99952dd4ef1baedd36a5c7c282
    predecessor inputs/stiffness_result.json
      fb12d70dd7c89933e03bfc04f256ecca86a590fc58ad485c8bb6847438fabc8d
    static-tests inputs/independent_root.json
      41077a7977079705dbd49379f2f9ecb3fe9c007c518b02277aba6aa4b8df7d16
    academic2-event-horizon/lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay.py
      d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044

The central bindings, stiffness record and independent root hashes match the immutable predecessor source bindings. Source inspection of the producer at lines194–203 identifies the state and equation only; the producer was not executed.

## New central conclusion

Conditional on the same exact-background validity premises as the accepted predecessor, the central quadratic background has exactly one interior scalar minimum. The reviewed turning-count theorem therefore supplies exactly one regular scalar eigenvalue in

    μ<-4k

for every pair of independent background-preserving wall Hessians κ_a,κ_b>=20, including either or both Dirichlet limits. It is simple, has positive regular kinetic norm, and is the compact strictly increasing stiffness-response branch already selected by the inherited negative mode. Its DD ceiling remains below -4k. Spectral reality follows from the separate Green-pairing corollary.

This is uniqueness in the entire negative-shifted sector, a stronger scope than uniqueness within the inherited narrow numerical mass strip. It does not exclude further tachyonic masses in `-4k<=μ<0`, count the full spectrum, supply new numerical DD data, or establish nonlinear dynamics.
