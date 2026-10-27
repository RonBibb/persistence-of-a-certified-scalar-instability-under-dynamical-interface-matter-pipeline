# A unique upper wall threshold removes the extra instability

For the same exact concave background, keep kappa_a=0 and vary only kappa_b>=0. There is a unique finite positive threshold

    kappa_b* = -2 L_b(0)/f_b(0),

where the argument denotes physical mu=0, not lambda=0, and the endpoint solution is the fixed lower-soft-wall IVP authenticated in the predecessor. Below this threshold there are two negative regular scalar modes. At the threshold there is one negative mode and one massless mode. Above it, including the upper Dirichlet limit, exactly one negative mode remains and there is no massless mode. These claims use the inherited regular scalar spectral premises and await terminal review here.

## Unique massless condition and exact bracket

The lower condition and normalization at physical mu=0 are independent of kappa_b. The exact upper residual is

    R_0(kappa_b)=L_b+kappa_b f_b/2.

The inherited endpoint signs f_b<0 and L_b>0 make R_0 affine with a strictly negative slope, so precisely one nonnegative value makes it zero. The unique lower-admissible solution spans the constrained solution space obeying the lower wall. Therefore there are no other massless thresholds on this path.

From -56<f_b<-23 and the accepted bounds on L_b,

    14569591/1050000000 < kappa_b* < 21183503/143750000.  (1)

The lower fraction is 2*(14569591/37500000)/56; the upper is 2*(21183503/12500000)/23. Strictness follows from the strict f bounds. Comparing exact integers,

    14569591 > 10500000,
    21183503 < 21562500,

gives the two predeclared witness regions:

    kappa_b in [0,1/100] lies strictly below kappa_b*,
    kappa_b in [3/20,infinity] lies strictly above kappa_b*.

These are certified analytical regions, not a floating-point estimate of the exact threshold. The interval between them is not reclassified by interpolation. The implicit threshold itself is exact because the endpoint values come from the uniquely specified exact IVP.

## Counting through the crossing

At every finite-wall root with lambda nonzero the inherited norm and Green identity give

    dmu/dkappa_b = a_b^4 f_b^2/Z > 0.

In particular the massless root at kappa_b* has lambda=4k>0, nonzero f_b, positive Z and a simple mass root. It is therefore a transverse crossing from negative to positive mass squared as upper stiffness increases. The local branch is in the remaining band immediately below the threshold and is positive immediately above it.

The initial remaining-band count is exactly one. On a compact portion of the path not meeting the massless threshold, simple roots continue and cannot collide. They cannot disappear through mu=-4k because the inherited auxiliary strip is uniformly root-free on the compactified nonnegative-wall family. Nor can a remaining-band root escape to unbounded mass within (-4k,0). Thus its count changes only at a massless crossing. There is exactly one such crossing, just proved to remove a negative mode, so the remaining-band count is one below kappa_b* and zero above it. At threshold the crossing mode is massless, not negative.

The one root below -4k persists at every wall pair by the restricted theorem. Hence the full negative regular scalar count is two before crossing and one at and after crossing. This is not a claim of total stability: the below-threshold instability survives.

## Upper Dirichlet endpoint

Use compact upper coordinate c_b=1/(1+kappa_b). The upper residual is c_b L_b+(1-c_b)f_b/2; at c_b=0 it requires f_b=0. At physical mu=0 the authenticated f_b is strictly negative, so there is no massless mode at upper Dirichlet. If a negative remaining-band root existed at that face, the inherited simple-root continuation would yield one for nearby finite kappa_b, contradicting the zero count there. The uniform auxiliary exclusion prevents a threshold exception. Thus the upper Dirichlet face has exactly the persistent below-threshold tachyon and no additional negative or massless regular mode on this path.

## Scope and next justified question

The witnesses [0,1/100] and [3/20,infinity] both pass without changing any frozen bound. This is a conditional analytical classification, not a numerical mass spectrum or a new solution. The original central background's complete one-mode result is unchanged.

The result resolves the entire admitted one-wall path. The remaining natural question is the transition set when both Hessians vary in the same nonnegative family. A separately admitted constrained two-component transfer at physical zero mass could test whether that set is a single decreasing curve, with regions containing one or two modes. This is a proposed next test, not a conclusion or an automatic launch under T1.
