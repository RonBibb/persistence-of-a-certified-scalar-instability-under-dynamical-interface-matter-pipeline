# Nonlinear source domain check

The conditional analytic-domain check passed on Linux, and a separately authored exact-rational replay verified every recorded gate for both authenticated background enclosures. The analytic review identified and corrected a shifted-domain gap before execution: the sufficient envelope condition is now `Y(16|z|) <= 1/100000`, not `Y(4|z|)`.

Under that condition, interface displacements remain inside the verified complex background collar, while the graph Jacobian, physical-wall speed denominator, and selected wall coupling remain away from zero. The calculation establishes a usable domain for nonlinear source estimates, not a numerical charge-amplitude range.

## Quantitative bounds

Both enclosures give a maximum graph shift of about `1.00001252e-5`, leaving `2.49987484e-6` of the allocated shift reserve. The background composition ratio is at most `0.40000501`, below the chosen ceiling of one half. The Jacobian deviation is at most `5.00626394e-6`, and the physical-wall speed bound is `1.92024e-5`. The selected coupling deviates from one by at most `1.02265024e-8` across the two enclosures.

These are sufficient analytic bounds under the envelope assumption, not measured displacements or velocities of a new solution.

## Evidence and next step

`RESULT.json` and `TERMINAL.json` bind the producer calculation. `AUDIT_RESULT.json` and `AUDIT_TERMINAL.json` record the independent replay, classified `CONDITIONAL_NONLINEAR_DOMAIN_ARITHMETIC_VERIFIED`. The audit also fingerprints `DERIVATION.md`, which contains the domain argument and its scope. All calculations used the inherited Linux lease; no new evolution was run and no parent record was changed.

The next step is to bound the actual compatible bulk, Israel, scalar-normal, and oscillator sources term by term, incorporating the domain dilation and derivative weights. This must produce explicit nonlinear majorant constants and prove closure before converting the conditional envelope into an allowed charge amplitude or a remainder bound for the distance expansion.
