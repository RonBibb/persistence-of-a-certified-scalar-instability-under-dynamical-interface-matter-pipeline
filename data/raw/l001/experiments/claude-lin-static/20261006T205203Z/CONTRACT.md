# Which enclosure width dominates the accepted D1 initial-data bounds (line 02, run 20261006T205203Z)

## Question and scope in this time window

The identity packet `lin-c4-evolution-identity-r1-20261006T051000Z` accepted three validated
spatial flows: mode, positive and negative. Each has 16,365 cells at step 1/8192 with 768-bit
outward Arb arithmetic. They give conservative whole-domain bounds between the exact certified
initial data and the saved numerical polynomials, at a common normalized coordinate u = s/D:

| Field | Bound |
|---|---|
| A | about 1.99e-4 |
| ell | 2.30e-7 |
| Phi | about 7.8e-5 |
| psi | 0.023 |
| f | 2.06 |
| g | 8.50 |

Run 20261006T185122Z admitted the six saved grids as deterministic representations.

**Question.** For each accepted bound, which enclosure width dominates it, before any interval
is narrowed or any expensive flow is added?

**Scope.** Ronald's time window allows no new job at or after 2026-10-06T21:51:21Z. This frozen
experiment therefore performs only the first stage the coordinator named: the width budget of
the accepted bounds.

- The propagation through the gauge-completion conformal lapse, the inverse coordinate map and
  the initial observables is not performed here.
- Its design is recorded under "Deferred" so that a later window can freeze it unchanged.

## Alternatives (frozen width classes)

Every per-cell comparison bound is E = maxabs(after - before), where:

- `after` is the Arb range of the validated cell over its whole width h;
- `before` is the hull of the native polynomial over [t Dn/Dhi, (t+h) Dn/Dlo].

E splits exactly (up to Arb rounding) into components, each assigned to one width class:

| Component | Definition | Width class |
|---|---|---|
| center | \|mid(after) - mid(before)\| | `CENTER_DISCREPANCY`: numerical approximation of the saved polynomials plus the offset of the enclosure centers |
| state | radius of the validated state at the cell start | `STATE_RADIUS`: background rectangle (a, k), mode bracket mu, correction root boxes (a, b0, b1), Taylor/Picard wrapping |
| source step + native step | rad(after) - state, and rad(before) - event | `COMPARISON_STEP`: comparing whole-cell ranges at step h = 1/8192 |
| event | radius of the native hull over [t Dn/Dhi, t Dn/Dlo] at the cell start | `EVENT_WIDTH`: the certified wall interval D* in [32727/16384, 32729/16384], width 1.22e-4, entering through u = s/D* |

The dominant width of an accepted bound is the largest of these four classes at the cell where
the bound attains its maximum.

**Diagnostic sub-attribution of the state radius (no gate):**

- Signed flows: the radii of W, |eps|psi, w, P and |eps|f at the cell start.
- Mode flow: the radii of the eight source fields, plus the first-order mu share |d/dmu|·rad(mu)
  for psi, f and g, taken from the flow's own mu-derivative states (u, v, w).

## Method

**Replay.**

- Each 256-cell block of each accepted flow is replayed from its own checkpoint. Block 0 starts
  from the reconstructed fresh state, using the inherited `identity_run.fresh_state` with its
  capacity probe replaced.
- The replay uses byte-identical copies of the inherited validated engine (identity packet
  sources; hashes bound) and repeats the inherited cell update exactly. The decomposition is
  computed alongside without changing the state.
- At every block end, the replayed state must equal the next checkpoint exactly in packed native
  form: y, max_errors, domain_maxima, event cover and derivative, max_picard, indices and p.
- The final running maxima must equal the inherited RESULT.json and SPATIAL_ENCLOSURES.json
  bounds exactly.

**Refined bound.** The same validated cell Taylor model is also evaluated on 16 equal subcells,
each against its matching native interval. This gives a rigorous refined bound E16 for the same
claim. It is a sharper evaluation of the same objects, not a new flow or a narrowed interval.

**Precision.**

- Arithmetic: Arb 768 bits, as the accepted flows require.
- Per-cell components are stored as binary64 values rounded upward from exact rationals.
- Maxima, argmax records and decisions use exact rationals.

## Gates (validity only; which width dominates is the outcome, not a gate)

| Gate | Requirement |
|---|---|
| R1 | Every replayed block equals its checkpoint bitwise (64 blocks per flow, 192 in total). |
| R2 | The replayed accepted bounds equal the inherited RESULT.json and SPATIAL_ENCLOSURES.json values exactly. |
| R3 | The argmax cell's E equals the inherited running maximum, for every field. |
| B1 | Closure in every cell and field: \|E - (center + rad(after) + rad(before))\| ≤ 2^-28·(rad(after) + rad(before)) + 2^-600·(1 + \|mid\| terms). Arb radii are 30-bit upward-rounded. |

## Classification (frozen)

- `ENCLOSURE_BUDGET_RESOLVED__A_DOMINATED_BY_<CLASS>`: all gates pass. CLASS is the dominant width
  of the accepted A bound, or `MIXED` if the positive and negative flows disagree. The full
  per-field table is reported.
- `ACCEPTED_FLOW_REPLAY_MISMATCH`: an R gate fails. The budget is then not interpretable.
- `BUDGET_NOT_CLOSED`: B1 fails.
- `UNRESOLVED_VERIFICATION`: the independent verifier disagrees or any of its checks fails.

## Independent verification

`code/verify2.py` does not import `budget.py`; it uses its own block driver over the shared
inherited engine. It replays blocks 0, 31 and 63 of every flow, plus the block containing each
field's argmax cell, and then:

- requires those blocks to equal the checkpoints bitwise;
- recomputes every component of every cell in those blocks exactly, and requires the producer's
  binary64 value to equal the upward rounding of the exact value;
- requires the exact argmax components to equal the producer's records and the inherited bound;
- requires the column maximum to equal the accepted bound;
- recomputes the dominant widths and the classification;
- performs a terminal process check.

## Resources and layout

- **Jobs.** Three independent producer jobs (mode, positive, negative), each a separate process
  with its own output directory. They run in parallel through `ClaudeCode/runtime/slot_run.sh`
  (LINE=02_lin_static, priority 5, line cap 3).
- **Order.** Assembly runs after all three have finished, then the verifier.
- **Per job.** One arithmetic thread, RLIMIT_AS 3 GiB, wall cap 3,600 s, and MemAvailable of at
  least 8 GiB at launch. The expected cost is minutes, so no checkpointing is required.
- **Failures.**
  - A job that fails writes a failed-closed receipt and is not restarted.
  - A launch refused before any outcome may be retried before the cutoff.
- **Cutoff.** After 2026-10-06T21:51:21Z only verification and finalization of this run start,
  declared with COMPLETION_OF.
- **Excluded.** No new flow, interval change, grid regeneration, time evolution or threshold
  change.

## Deferred: designed, not performed in this window

**Gauge completion.** The exact gauge completion q* would come from:

- validated exact wall jets: `prepared_flow.coeff` at s = 0 and over the event cells;
- an Arb port of the inherited `times`, `wall_jets` and `qualify_gauge`;
- port fidelity: reproduce the saved q from native jets to within 1e-50;
- consistency: the exact completed rows must contain 0;
- independent check: the inherited symbolic `independent_gauge_bridge.py`, requiring D2, D4,
  RC2 and RC4 to contain 0 on the exact jets.

**Then:**

- the conformal lapse sup |B* - B_n| in common u (= A bound + |ΔQ|);
- the proper separation and coordinate length from integrals over subcells, split into event and
  interior parts;
- monotone interval inversion for the node positions;
- node-level bounds on A, B, Phi and ell;
- wall observables: A, Phi, ell, the radius perturbation A - W, the clock rate and log R.

## Claim limits

These are statements about the accepted enclosures, at finite resolution. The refined bound is a
rigorous bound on the same claim. Nothing here is an exact-map, lapse or evolution certificate.
The zero-case metric correction is still not separately validated.
