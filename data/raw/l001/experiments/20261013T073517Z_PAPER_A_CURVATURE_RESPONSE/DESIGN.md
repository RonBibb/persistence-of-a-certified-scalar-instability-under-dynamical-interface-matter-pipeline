# Lower wall curvature response along the certified static family

This test derives a new susceptibility consequence of the saved uniform upper-tension family. It does not replay previous arithmetic tests or execute a flow producer. All scientific arithmetic uses exact rational endpoints. Floating point output is descriptive only.

## Mathematical consequence

Keep every model input except lambda_b fixed, with the original exact interval delta in [-1/1000000,1/1000000]. Use the saved uniform Newton image as an enclosure of a(lambda_b), the saved uniform da/dlambda_b and dD/dlambda_b intervals, and the original dyadic model constants. The narrow launch box is checked to contain the image.

For x=a-v0 and A0=0, the action reduction gives H0=-(lambda_a+gamma*x^2/2)/6, S0=gamma*x/2, k=H0^2-1-S0^2/12+m2*a^2/12. Thus

    k_a = -gamma*H0*x/3 - gamma^2*x/24 + m2*a/6
        = gamma*x*(lambda_a+gamma*x^2/2)/18 - gamma^2*x/24 + m2*a/6.

The code constructs the polynomial k(a) from the launch definitions, differentiates its exact coefficients, and requires exact coefficient equality with the displayed derivative. It evaluates both derivative forms over the uniform Newton image and intersects their valid interval enclosures. The intersection must be nonempty and strictly positive. No finite-difference approximation is used.

With k_lambda=k_a*a_lambda, strict positivity proves increasing curvature with increasing additive upper tension on this connected local family. The induced lower-wall metric has scalar curvature R_lower=12*k*exp(-2*A0)=12*k; this is an intrinsic scalar, while D is proper separation. Therefore dR_lower/dlambda=12*k_lambda and dR_lower/dD=12*k_lambda/D_lambda are well-defined and negative in the latter case. The implicit function theorem and local uniqueness glue the inherited local solutions into a smooth branch over the interval; this uses the inherited transverse-event and nonzero-Jacobian premises. It does not extend global first-event uniqueness.

For any ordered tensions lambda1<lambda2 in this same interval, integrate the uniform derivative bounds to enclose their curvature difference. The full endpoint difference uses width 1/500000. Likewise the slope dR_lower/dD bounds any secant between two distinct branch points, by the mean value theorem in D. These are static comparisons between distinct parameterized models.

## Frozen pass criteria and controls

Baseline requires exact source hashes; the exact original model and tension range; all four inherited P01 gates; the same nonempty Newton image inside the original launch box; positive a response and negative D response; symbolic coefficient equality; positive k and k_a; positive k_lambda and R_lower response; negative dR_lower/dD. It records rational enclosures and outward-rounded decimal bounds (12 places) for these and the full endpoint curvature changes. No bound is tuned after execution.

Six controls alter deep in-memory copies after hash authentication: negative a response (A_RESPONSE_POSITIVE), zero-reaching D response (D_RESPONSE_NEGATIVE), nonzero lower normalization (LOWER_NORMALIZATION), altered gamma (MODEL_EXACT), Newton image outside the certified launch box (IMAGE_INSIDE_ROOT_BOX), and altered analytic derivative coefficient (DERIVATIVE_IDENTITY). Each must reject at its named predicate. No original source or prior failure is changed.

Execution is one standard-library Python process, BLAS thread variables set to one, after an independent gate binding script, design and source manifest hashes. Script emits JSON to stdout only; no automatic successors, IVP integrations, Linux work, upper-wall calculation, spectral extension, dynamics or stability claims. Terminal independent audit is required before scientific classification. The saved-interval validity and model provenance remain explicit premises even if the arithmetic passes. Earlier migration hashes are documentary evidence, not proof of interval validity.
