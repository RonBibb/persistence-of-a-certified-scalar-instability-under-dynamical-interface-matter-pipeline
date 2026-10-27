# Exact sixth order width coefficient

Derive the nextlocalanalyticcoefficient from the same regular ODE, independently of numerical fitting. This derivation is retrospective relative to T5's coarseD6diagnostics. A held-out thirdwidth may bepredicted onlyafter thispacket isaccepted anditsseparatewindowpublished before thatrun.

Normalizecentralpsi1,f0=-3lambda,g0=B. Use nested exactrational polynomials: radialdegree7, halfwidthddegree6, withlambda(d),B(d) even. Generate fullradialTaylorrecurrence retaining parameterdependence. Evaluate E=(f(d)+f(-d))/2 and O=(f(d)-f(-d))/(2d). Termsr>=8 cannotcontribute toEthroughd6orOthroughd6 becausepowersarednonnegative; r7isretainedforO'sd6term. At eachorder d2,d4,d6, withlowercoefficientsfixed, solveusingJacobiandiag(-3,1): lambda_j=E_j/3,B_j=-O_j, then regenerate andverify allE/Ocoefficientsthroughthatorder vanish. This retains lower-derivative dependenceonlambda/B, unlikea frozenzero-parameterjet.

Controls exacttruncatedreciprocalproduct; oldcentraljetf''-4,f'''-72,f''''-1256; reproduceacceptedlambda2=-2/3,lambda4=20/9,B2=12. BindT22analyticIFTjustification andprimaryequations. ReportfullwidthgapD6=-lambda6/64. No fixedfiniteDremainderconstantorconvergenceradiusclaimed. Nopassgateonthe sign/valueofnewcoefficient beyond arithmeticconsistency.

Onecore1GiB590s/600scaps, expectedunder1min, originalcutoff20:07:08Z, leases/noqueue/nooverwrite, independentprospectiveandterminalreviews. NoODEevolutionoreigenvalue solve.
