# Readiness for the late-state P407 compatibility measurement

The three proposed states already exist as authenticated, complete endpoint
records.  No future evolution and no interpolation are needed to perform the
next discriminator.

| H-step | Time | Authoritative state source | Record SHA-256 | Payload SHA-256 | Complete fields |
|---:|---:|---|---|---|---|
| 512 | 0.008 | P400 `G10_future_step0512` | `3f017b297ec69f6e426331400dc1ba9d47ec8a885a33c5652f5027d19a59896d` | `c7e9389ee13e0214664b1a228443dacc720de13de6bbbbada37a5f28f5acaa8b` | q, v, source, memory |
| 1152 | 0.018 | P407 `evolution-block-0004` endpoint | `125c220a9014895c3fdd32172420966de819b3d01ae629b3a5f4460829e1cea2` | `20ab08265b2b27f535c107b47108c8c065328943ae84ca1f2e7a3ba7efe63091` | q, v, source, memory |
| 1792 | 0.028 | P407 `evolution-block-0008` endpoint | `022c9a10115c655f759b8cbf54694ca902525f9322d8049ab5d487e2ff50d7ec` | `8d6038631b0ab44e225e6cc686608cf9ad7e328899a0183bc85bde7487274b10` | q, v, source, memory |

Every field has shape `(129,241,9)` for q/v or `(129,241,3)` for
source/memory and dtype float64.  P407's frozen authority independently binds
the four H-step-512 array identities to the P400 terminal state.  The H-step
1152 and 1792 receipts bind their endpoint arrays and payloads directly to the
P407-R2 authority.

The P407 endpoint payloads also retain ten archived q/v knots per block, but
the three endpoint records are preferable for the first compatibility study
because source and driver memory are committed alongside q and v.  Using
interior q/v knots without matching source/memory would introduce an avoidable
reconstruction question.

## Required pre-execution binding

A future capsule should bind, before evaluation:

1. the P407-R2 authority SHA-256
   `a3074ad16fe9b7a35d5eddd06e786cc4319d7563e2e01e10dcc91aedfe7a7465`;
2. the three records and payloads above;
3. the P404 candidate nonlinear kernel SHA-256
   `48bb5f57e63e0b31bbb1d72e995a84b68fa8fd213942c0b407220dab5a02e945`;
4. the batched open-bulk kernel SHA-256
   `3cd8cedb50a629e0d8c78a94edafd900d6e2761beeba5b90e3a502d52f7aeefc`;
5. the reviewed branch-01 diagnostic sources and their saved-verifier
   versions; and
6. an explicit assertion that the four optional wall forcings are `None` and
   the owner mode is `legacy_wall_axis_outer`.

The output must be written to a new Academic2 branch.  It must not write into
P400, P407, O1/O2, or the branch-01 compatibility packet.

## What makes the test decisive

The purpose is not another generic constraint inventory.  The test must answer
whether the specific bulk-wall incompatibility found near formation is
present, absent, or changing along the actual causal parent.  It therefore
needs a time series across the three endpoints, the same physical row
definitions at every endpoint, and both absolute and normalized residuals.

The comparison should distinguish:

- a defect inherited at H-step 512 and transported roughly unchanged;
- a defect that decays before the late epoch;
- a defect generated or materially changed by the P404 batched continuation;
- and a diagnostic that cannot be made representation-consistent across the
  legacy-to-candidate transition.

No outcome from this three-state test by itself proves a continuum spacetime
or an event horizon.  Its value is narrower: it decides whether the existing
P407 archive is physically clean enough to justify the next expensive causal
extension.

