# Neutral-mode operational radial radar clock

Prospective candidate, no execution until independent admission. Governing question and physical idealization are in `../RADAR_TIME_SCOPE.md`. Select **only the neutral growing mode** here: generic longitudinal walls have zero bending, modeP=ψ, b=−2p, γ>0. No current-driven history is substituted or mixed with its free amplitude.

## Independent derivation

Background opticalcoordinate τ(s)=∫a^s E and L=τ(b). Outbound reflection-time variation is `−Ea xia+Eb exp(rL)xib+∫E(B−P)exp(rτ)`. Return-leg duration variation is `−Ea exp(2rL)xia+Eb exp(rL)xib+∫E(B−P)exp(r(2L−τ))`. Reflection-time perturbations multiplying a first-order metric/velocity are second-order, so the displayed sum accounts for both legs. WithB=−2P the integral factor is−3. Lower-clock rate is `aa[1+epsilon exp(rt)(Pa+Ha xia)]`; radial observer velocity enters quadratically. Integration along the background roundtrip plus the shifted finalendpoint gives the statedproperclockformula. Here xia=xib=0,aa=1,ψa=1, but retain the boundnormalization in arithmetic.

The pulse is an ideal negligible-energy probe reflectinginstantaneously at theupperinterface and returning to the samecomovinglowerobserver. Reflection is an explicitkinematic idealization, not a wallmaterialprediction. Perturbationsareinfinitesimal and bothwalls timelike, within thecommonpatch. Radial travel hasfixed3Dcomovingcoordinates. No eventhorizon statement follows.

### Gauge control in the correctly enlarged metric

For a general radial metric perturbation include `δg_ts=epsilon exp(rt) C(s)`. The null integral adds `∫C E²[exp(rτ)−exp(r(2L−τ))]ds`. An arbitrary radial relabeling has `P=−Halpha,B=−alpha',C=−r alpha,xi_i=alpha_i`, notgenerallyB=−2P. The completeintegrand becomes `−d{Ealpha[exp(rτ)+exp(r(2L−τ))]}/ds`. Itsboundaryterms cancelthemovingendpointterms, whilePa+Ha xia=0 cancelsclockchange. A temporalrelabeling'scoordinate-durationterm similarlycancelsitsclockterm. Exactformal-rational controlschecktheseidentities withindependentexponentialendpointvariables; nofalsegaugeclaimis madeusinga metricwithoutitsinducedshift.

## Validated computation

Two unchangedregularengines, exactcentralbackground andentireacceptedT2R1massstrip, original768-bitArb andsteps2/8192,2/16384. γ=(-3sqrt(k)+sqrt(9k−4μ))/2 withpositiveγ andgrowth-massconsistency. AllcellPicard/Taylor, constraints,firstintegral,positivewarp, fulluncertainwalldomaincover androotstripdeterminantchecksremain.

Firstpass saveswholecell E,ψ outward-coarsenedto2^-80, opticalprefixτbox, andopticalintegralL contributions. Prefixat acellincludesallprecedingfullcells; τwithin cellusespositiveE times[0,clippedextent]. Ltotrueuncertainwall usesmandatoryprefixtoDlo andoptionaltailtoDhi, notfixedDhi. Sumexportedcontributions. Secondpass usesfullLinterval andτbox toboundboth exponentials alongoutbound/returnlegs. Saveoutwardkernel andweightedcontributionenclosures; signedoptionalweightedtailincludes0. No midpointmode, interpolatedclock, or frozenemission-timeapproximation.

`Ccoord=−3Iweighted`; `Cproper=aa[Ccoord+ψa(exp(2γL)−1)/γ]`; reporthalfroundtripcoefficient, acceptedmatchedδD, theirratio andratiooffractionalresponses. Do notassumehalfclockresponseequalsproper-distance response. Savepointwise E/ψboxes,prefixdata,kernelsandbudgetssufficientforarithmeticandtranscendental audit. Rationalresummationalonecannotcertifyexp/sqrt; identifiedoutwardArbexecutionremainsa numericalpremise unlessreviewerindependentlyboundsit.

Controls: flatstaticconstantP givesCproper=−4PL=2δD; time-dependentflatconstantP uses∫bothlegs=(exp(2rL)−1)/r andCproper=−2PJ; moving-boundarystaticlimit; generalizedshiftgaugeendpointandclockcancellation; inheritedcorrectedintervalcontrols. Allcontrolsandscienceonacademic-linuxonly.

Oneleasedcore, aggregateallocationmaximum2; hard900s producer,360sperflow,910swrapper. No retry orautomatic successor. Atomicnooverwritepublication. AcceptedT2R1terminalreviewandexplicitboundrecordsrequired. Independentprospectiveandterminalreviewmustconfirmoperationalinterpretation, nulltransport, intervalkernelsandtwoenginehulls. Unresolvedsigns remain validunresolvedresults.
