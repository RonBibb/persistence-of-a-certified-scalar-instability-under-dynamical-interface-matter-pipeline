# Independent terminal review — local sign recovery accepted

Computational auditing ran on academic-linux under a temporary CPU lease, without ODE replay. All 689 admitted bindings match. All twenty raw propagation records, ten G/W hulls, cross-level overlaps, fixed-scale derivative conversions and five summaries were independently reconstructed. The worker exited zero and was reaped; no failure artifact exists. Producer elapsed time was 627.875994 seconds and wrapper time 629.197237 seconds.

The frozen classification SIGN_RECOVERY_AT_TESTED_WIDTH is correct. The point control succeeds; halfwidths 1/3200 and 1/32000 remain inconclusive; halfwidths 1/320000 and 1/3200000 certify both expected signs. At the first successful nonzero width, the lower-beta C4 hull is approximately [31.354412,43.926637] and the upper-beta hull [-43.198835,-30.647362]. These are sufficient derivative signs on that local parameter interval, not a full-domain certificate or a measured critical width.

The C4 widths decrease approximately tenfold with each tenfold reduction of the nonzero input halfwidth: roughly 1259,126,12.6,1.26. The point width is about 5.4e-9. This directly supports parameter-box overestimation as a practically controllable source of the previous broad enclosure. It does not establish that the true derivative varies by those widths or exclude other sources of error.

## Planning-only full-cover cost

The first successful halfwidth 1/320000 corresponds to full width 1/160000. Uniformly tiling d in [0,.01] at that width would require 1600 bins and 6400 propagations for two endpoints and two representations. The observed mean propagation time, 31.35495 seconds, extrapolates to approximately 55.7 single-core hours. This is a forecast, not an upper bound or an approved computation; local sign success does not guarantee success elsewhere. The result supports considering a more dependency-preserving representation before funding that cover, rather than treating this local diagnostic as a global solution.

No full cover or successor was launched by this review. All prior inconclusive and failed records remain preserved.
