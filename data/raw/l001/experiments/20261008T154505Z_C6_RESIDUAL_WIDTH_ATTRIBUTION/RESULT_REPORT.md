# Lin C6 residual enclosure width attribution

The completed attribution localizes the problematic upper-H5 correction width to the upper scalar C4 residual and demonstrates that 85.616% of that correction enclosure can be removed by equivalent, rigorous interval evaluations. No physical source value, root center, box, preconditioner or scientific gate changed.

The producer classification is `C6_RESIDUAL_WIDTH_MULTISOURCE_UNRESOLVED`. The removable fraction is substantial but below the prospectively frozen 90% dominance criterion. Source uncertainty, accumulated integration error and earlier interval wrapping remain mixed in the residual width that survives. The preceding C6 existence certificate remains incomplete.

## The target and the channel ledger

The primary quantity is the halfwidth of coordinate 2 of the existing center-correction enclosure `-C F(c)`: the **upper H5 physical coefficient**, not a new residual or a measured displacement of the physical solution. The five residual channels feeding it are upper spatial Israel, lower and upper scalar C4, and lower and upper scalar C6.

The fixed-preconditioner ledger closes exactly in rational arithmetic at both precisions, including a separately recorded signed rounding and representation excess. At 1024 bits:

| Residual channel | Contribution to the upper-H5 linear radius budget |
| --- | ---: |
| Upper spatial Israel | 8.12798e-10 |
| Lower scalar C4 | 2.10723e-18 |
| Upper scalar C4 | 0.1148792492833 |
| Lower scalar C6 | 2.04545e-19 |
| Upper scalar C6 | 4.40035e-16 |
| Separately recorded rounding and representation excess | 1.01240e-9 |

The upper scalar C4 channel supplies **99.999999292% of the ideal linear radius budget** at both precisions. Its own residual halfwidth is approximately 0.115194341. Thus the large upper-H5 correction enclosure is not primarily caused by mixing other residual channels through the preconditioner. This localizes a channel; it does not yet identify the physical or numerical origin of uncertainty within that channel.

## Equivalent evaluations remove most of the enclosure width

All three diagnostics evaluate the same residual with its dependent lapse controls rebuilt consistently. They use analytic derivatives over the complete retained input rectangles. Midpoints serve only as algebraic expansion pivots in a mean-value enclosure; no midpoint is substituted into the physical source, IVP or root center. The final intersections and reduction fractions use the predecessor's literal rational endpoints.

| Representation in the frozen order | 768 bit upper-H5 halfwidth | 1024 bit upper-H5 halfwidth | Removable fraction at 1024 bits |
| --- | ---: | ---: | ---: |
| Original sealed enclosure | 0.1148792515742 | 0.1148792511085 | Reference |
| Mean-value enclosure using independent saved endpoint jets | 0.0194390628603 | 0.0194390628603 | 83.07869988% |
| Higher metric jets linked by the same Hamiltonian identity | 0.0194357951696 | 0.0194357951405 | 83.08154436% |
| Canonical scalar spatial targets and Hamiltonian identities retained | 0.0165241739305 | 0.0165241739014 | **85.61605012%** |

These are ordered reductions of an enclosing description, not additive physical error sources. Most of the measured improvement comes from the mean-value representation. The canonical spatial identities supply a further reduction. The agreement between precision levels corroborates this implemented range calculation; it does not identify the remaining physical error or certify a root.

The rigorous statement is that an equivalent enclosing interval is narrower while still containing the same exact residual value. It is not that the physical residual itself fell by 85.6%, or that 85.6% of an actual physical error has been identified.

## The unsolved upper wall condition was retained

The upper metric slope remains the Hamiltonian-integrated slope. It was not replaced by its Israel target. The canonical scalar first and third spatial derivatives are used as the actual C7 profile definition, not as permission to set the upper C2 time-row to zero away from a root.

The independent Initial derivation gives the retained identity

`exp(-2B) h_tt = (p - p_wall) [6u + 4(p + p_wall - c)t - 2 m2 Phi]`.

The endpoint diagnostic explicitly records this remainder. Its algebraic pivot has an upper spatial Israel residual near `1.36451e-12`, rather than an imposed zero. The pivot is not a claimed physical solution. The identity control passed at both precisions.

## What remains in the upper bound

In the final 1024-bit mean-value radius budget, **99.995998% of the input-radius sum** belongs to the upper-wall scalar-jet group. The largest individual terms are:

| Stored upper-wall Taylor coefficient | Contribution upper bound | Share of this mean-value input budget |
| --- | ---: | ---: |
| `Phi[0]` | 0.01076891505 | 65.1707% |
| `Phi[2]` | 0.00372175038 | 22.5231% |
| `Phi[4]` | 0.00120347707 | 7.2831% |
| `Phi[5]` | 0.00082937005 | 5.0191% |

Indices here denote Taylor coefficients, including their factorial convention; they are not unscaled ordinary derivatives. These are sensitivity upper bounds evaluated over the full primitive rectangle, including nonlinear interactions. The percentages describe that upper budget, not independent physical causes or measured error shares. In particular, the source, IVP and wrapping contributions already merged into a scalar-jet enclosure cannot be separated by relabelling this table.

## Contribution ledger by requested origin

| Requested origin or stage | Evidence and rigorous bound available | Unresolved part and accounting boundary |
| --- | --- | --- |
| Source and root uncertainty | The original source, event and endpoint-jet intervals remain in all derivative evaluations. Upper scalar enclosures dominate the final sensitivity budget. | No disjoint source-only share can be recovered from endpoint balls already containing integration error and wrapping. |
| Validated spatial integration and Taylor remainder | The archive supplies genuine local fifth-order remainder bounds for 128 stored last cells out of 16,365 integration cells per precision. | Those samples do not bound the missing cells or total accumulated truncation. No missing steps were recomputed; no cumulative share is claimed. |
| Endpoint event localization | The event interval is approximately `[1.99756652117, 1.99756786227]`. The saved event tube provides rigorous raw-state evaluation-shift bounds from `sup(abs(rhs)) * halfwidth(D)`. | These overlap source and integration uncertainty and are not directly residual shares. Explicit D-dependence in an endpoint formula is distinct from D uncertainty already carried in endpoint fields. |
| Canonical epsilon-series remainder | All eight coefficient remainder bounds are retained; the largest is approximately `4.37345e-28` in C7 coefficient units. | This is not a spatial-IVP error bound or a propagated residual fraction. |
| High-jet and algebraic propagation | Full-box analytic derivative budgets and three equivalent interval evaluations give the quantitative reductions above. | The remaining rectangular input budget still discards some source and cross-jet correlations. |
| Interval dependency and wrapping | At least 85.616% of the original primary enclosure width is removable by the declared equivalent endpoint evaluations. | Earlier IVP wrapping is inseparable from source and integration uncertainty here; the frozen 90% dominance gate is not met. |

For perspective at the **raw-state level only**, event-localization upper bounds divided by the corresponding stored halfwidth are about 1.606% for the background scalar, 2.210% for its slope, 0.360% for the scalar mode and 0.767% for its slope. They are about 99% for several metric or lapse-source variables. These comparisons show why event uncertainty must be tracked by variable rather than assigned a universal fraction. They do not supply an additive residual budget or establish that the event shift attains its upper bound.

## Enabling value for the Initial construction

This result supplies a targeted numerical-proof lead rather than a standalone novelty claim: the current bottleneck is a broad **upper scalar C4 enclosure**, and much of its width is avoidable endpoint algebra overestimation. The strongest remaining budget is attached to upper-wall scalar value, second, fourth and fifth Taylor coefficients.

The exact next certificate premise is a sufficiently tight, validated enclosure of the **same center residual**, with all source, event, accumulated IVP and correlation uncertainty retained. That premise is needed before a separately authorized attempt can revisit the unchanged five-variable root-inclusion test. Passing that future test would establish the physical C6 preparation needed by the Initial construction; validated lapse and inverse-coordinate-map bounds would still be required before the broader collapse/horizon effort could consume the continuum-certified datum.

This attribution closes none of those existence, map, evolution or horizon gates by itself. No next calculation was launched. Standalone literature priority was not assessed.

## Integrity and stopping status

Both saved-residual reproductions, analytic-dual controls, all equivalent-evaluation checks and the retained upper off-shell C2 controls passed. The local readback passed 144 exact accounting and hash checks. The single worker used CPU 0 under both exclusive lock namespaces, consumed 133.38 core-seconds, and released its slot after 134.08 seconds of execution. Peak RSS was 46,552 KiB. All 12 finite diagnostic cases are sealed.

A pre-execution reference-handling correction preserved the initial unexecuted source and freeze, then introduced the `*_exact.py` variant so the original interval denominators and final intersections use literal sealed endpoints. No attribution outcome preceded that correction. The active binding is `BINDINGS_EXACT_ENDPOINTS.json`.

| Artifact | SHA-256 |
| --- | --- |
| Active source and input binding | `433db07408462b1a1cebc3f0763316901c5c198811d43a157166d79816967637` |
| Result | `3794399d998d29795fce19d0b4acd6480049c20eb831e6d0617a7b619d9ce7d5` |
| Terminal | `d91ba5a348758461511e3c41121b2a081c9b49333dc6ec62d4db231ee0dd6f6d` |
| Local audit | `1fa542933f103b4bc81efe4a038e7647c9eac8507a916ca42a6bb238bf6525a8` |
| Resource release | `82b94ec7d59700b143dda516410bcd22b13d203776321ced0004d3a51f635bb3` |
| Static submission | `1014d1538c997a498ae54e4bb58989ffe754bfd5f7ff3fd097426e27c91f4988` |

The exact source, gradients, interval endpoints and contribution terms remain in the line-owned ignored `raw/` directory, bound by the submission manifest. No C6 integration, root decision, map stage, evolution, box change, threshold change or automatic successor was run. Independent Initial audit and the joint receipt are the remaining closure steps.
