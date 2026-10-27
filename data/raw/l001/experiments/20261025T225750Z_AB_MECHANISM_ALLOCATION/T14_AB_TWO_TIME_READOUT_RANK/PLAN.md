# T14 — time-resolved local readout rank

Prospective saved-record protocol, not a rescore of T12 or T13. No execution until independent admission. Predeclare LOCAL_TIME_RESOLVED_LINEAR_READOUT_INJECTIVITY iff both the authoritative raw current minor and neutral radar coefficient exclude zero after independent-engine hulls; otherwise UNRESOLVED. No tuned numerical delay.

## Physical measurement and exact factorization

Readouts are D(0), lower-observer elapsed radar time for a pulse emitted at0, and the same elapsed radar readout for a pulse emitted after a strictly positive delay. The radar coefficients already incorporate time evolution throughout each round trip; multiplying by the later-emission factor therefore does not double count transport. Columns are neutral growing mode and separately conserved lower/upper first-current amplitudes at the initial emission event.

The neutral column has rate gamma>0. Both current columns have **the exact same rate r=-6h by their shared source law** on the same background. This equality is not inferred from overlapping numerical rate intervals. Thus the matrix columns are (Dn,Rn,Rn exp(gamma Delta_t)), (Da,Ra,Ra exp(r Delta_t)), (Db,Rb,Rb exp(r Delta_t)). Subtract exp(r Delta_t) times row2 from row3. Expanding the remaining row3,col1 entry has positive cofactor sign:

    determinant = Rn [exp(gamma Delta_t)-exp(r Delta_t)] (Da Rb-Db Ra).

The exponential factor is strictly positive for every positive Delta_t because gamma>0>r. The statement is conditional on both experiments remaining in the common perturbative patch. No value of Delta_t is selected, scanned or evaluated numerically.

Prescribe a positive background lower-observer proper delay Delta_tau=a_a Delta_t (a_a=1 in this normalization). Scheduling by the perturbed observer clock changes the emission coordinate time only at first order; multiplying this shift into an already first-order response changes it at second order. The background radial radar duration is time independent. Thus the linear protocol has a physical clock interpretation rather than arbitrary coordinate synchronization. This order argument is an analytical premise; the executable control only verifies its simple formal coefficient bookkeeping.

## Authoritative arithmetic

Use full raw per-engine T12 columns D,F,R, never rounded ratios or normalized determinant data. Bind accepted T12, T8, T10 reviews/results and T8 radar, T10 current assembly and both basis records. Check direct linkage to accepted radar/distance fields, positive gamma, negative current rates and rate/mass source-law interval consistency. The exact equality of current rates is inherited from the analytical action/source construction, not proved by these consistency checks.

The authoritative current minor is **Da*Rb-Db*Ra**. Report each engine's raw interval and their hull. The factorized expression Da*Db*(Rb/Db-Ra/Da), when denominators exclude zero, is consistency only; require overlap without intersecting or switching authority. Report Rn and the determinant prefactor Rn*minor separately. If either authoritative factor contains zero, the result is unresolved regardless of a narrower diagnostic expression.

Controls: independent full3x3 determinant versus row operation and factorization; common current rate cancellation; dependent current columns; raw/factorized minor identity; formal positive exponential gap and emission-clock scheduling order. All science is exact Fraction arithmetic on Linux under the normal one-core1GiB lease; producer900 seconds and wrapper910 seconds. No new ODE, amplitude or charge-radius test. Atomic no-overwrite terminal artifacts and independent terminal review are required.

## Interpretation boundary

Zero exclusion certifies a local formal linear distinction among these three response directions using this time-resolved protocol. Current-square amplitudes occupy a nonnegative cone. It does not establish mode excitation, actual measured amplitudes, favorable conditioning, noise robustness, finite-charge inverse uniqueness or nonlinear evolution. As delay tends to zero the determinant tends to zero; at long delays current signals decay. Neither limitation is solved by exact rank. Earlier T12 and T13 outcomes remain unchanged.
