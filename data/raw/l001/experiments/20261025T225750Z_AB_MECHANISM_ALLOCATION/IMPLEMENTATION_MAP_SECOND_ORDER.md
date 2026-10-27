# Full second-order proper separation: concrete implementation map

Preparation only. No production code, computation, launch or modification of bound sources. This maps the next implementation onto the actual inspected engine interfaces. Read with `FULL_SECOND_ORDER_PROPER_SEPARATION_SUCCESSOR.md`, the qualified T15/T17/T18/T19 records, and `NONRESONANCE_DEPENDENCY_NOTE.md`.

## 1. Exact source entry points

All paths below are relative to this allocation directory.

- `T20_AB_SECOND_HARMONIC_HOMOGENEOUS_INVERSE/engine/primary_interval.py`: `initial` line39; `rhs`56; `product`64; `coeff`68; `padded`83; `picard`89; `range_on_cell`101; `step`114; old `determinant`122; old `constraint`127; `first_integral`132; `geometry`137.
- Its `engine/independent_interval.py`: `initial`70; `rhs`86; `convolution`99; `triple_convolution`106; `exponential_coefficients`114; `taylor_coefficients`124; `picard_box`150; `range_on_cell`163; `step`177; old `determinant`188; old `constraint`193; `first_integral`199; `geometry`204.
- `T10_AB_CURRENT_RADAR_RESPONSE/basis.py`: `initial` constructs the homogeneous and lower-current particular first-order launches; `combine` gives the accepted multiplier and both physical wall traces. Its `load_wall` fixes the current and orientation conventions. This is a copy of the first-current producer, not a new second-order engine.
- `T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py`: qualified Eulerian source identities and exact polynomial controls.
- `T17_AB_COMPLETE_QUADRATIC_GRAPH_SUBSYSTEM/producer.py`: qualified graph coefficient xi2.
- `T18_AB_COMPLETE_QUADRATIC_WALL_SOURCE_QUALIFICATION/producer.py`: Q5 source extraction, undivided Q6 loading and explicit chart bridge.

The historical engine functions are **not already generic second-order integrators**. Their state unpacking, coefficient recurrences and diagnostics are hard-coded for one three-component homogeneous mode. Preserve them as parent bytes; implement new modules in a new successor packet.

## 2. Recommended coupled state and first-order initialization

For a first lower-current unit direction, use one shared background and three perturbation blocks:

```
primary:     (W,H,Phi,T,E, p1,f1,g1, p2P,f2P,g2P, p2H,f2H,g2H)
independent:(W,H,Phi,T,   p1,f1,g1, p2P,f2P,g2P, p2H,f2H,g2H)
```

Here P/H suffixes mean **particular/homogeneous shooting blocks**, not pulled/Eulerian charts. All perturbations in this implementation are Eulerian. Prefer explicit names such as `second_particular` in code to prevent that collision.

Recover, separately for each engine, the accepted first-order homogeneous multiplier `A1` from T10's bound `output/current_radar_<engine>.json` under `full_forced_assembly.channels.lower.homogeneous_multiplier`. The physical first-order initial perturbation is

`(p1,f1,g1)_a = A1 * (pH,fH,gH)_a + (pP,fP,gP)_a`.

The two lower launch states are saved in `homogeneous_<engine>.json` and `particular_lower_<engine>.json` under `lower_state`. Equivalently reconstruct them using the unchanged `basis.initial` equations with the bound inputs. **Do not add their background entries:** retain one background launch from the exact original A interval. The upper-current direction would instead omit the particular block, but is not part of the first proposed run.

Retain the complete interval A1, not its midpoint or a rounded published number. It encloses the exact multiplier as a function of the same uncertain background. Treating its enclosure independently can lose correlation but is an outward over-enclosure. If this causes excessive wrapping, that is a feasibility limitation requiring a separately reviewed representation change, not permission to narrow A1.

Set `mu1=-18*k`, `mu2=-108*k` from the same full background parameter enclosure. Reintegrate the now-assembled first-order solution inside the coupled flow. Saved integral budgets alone cannot supply its derivative jets. Require fresh first-order endpoints to overlap the accepted assembled wall traces and fresh first-order separation to overlap the accepted coefficient, without intersecting away uncertainty.

## 3. What changes in each engine

| Function | Required treatment |
|---|---|
| Exact interval construction, bounds, hull | Reuse unchanged; retain outward arithmetic/runtime premises. |
| `initial` | New initializer: one background, physical first-order launch above, constrained second-order particular/homogeneous launches below. |
| `rhs` | New augmented RHS: background, first-order homogeneous bulk at mu1, second-order forced block at mu2, second-order homogeneous block at mu2. |
| `product` / independent convolutions and exponential recurrence | Reuse arithmetic helpers unchanged. |
| `coeff` / `taylor_coefficients` | Extend explicitly to every augmented component and every source product. Independent engine must retain its separately written direct exponential recurrence; do not call the primary recurrence. Remove/replace the independent seven-entry assertion. |
| `padded` / `enlarge`, strict inclusion predicates | Reuse unchanged. |
| `picard` / `picard_box` | Their dimension-generic iteration is reusable in the new module, but it must call the new augmented RHS. Strict whole-vector inclusion is required, including source-carrying first-order fields. |
| `range_on_cell` | Dimension-generic Horner evaluation reusable unchanged with the enlarged coefficient/remainder arrays. |
| `step` | Same Taylor/Picard remainder construction reusable, wired to the new recurrences. Its old proof applies only after those new normalized derivatives are qualified. |
| `constraint`, `geometry` | Replace hard-coded unpacking and homogeneous-only checks with separate first-order, forced second-order and homogeneous second-order constraints. |
| `first_integral` | Same background expression, new unpacking/view; check on every whole-cell box. |
| `determinant` | Do not use inherited gamma=20 function. Evaluate selected Gamma2=21-1/(2-mu2 E²), with Q6 forcing and orientation explicitly. |

Never monkey-patch a bound parent module. A copied generic function still resolves its own module globals; importing its old `step` without rebinding the RHS/recurrence is not an augmented integrator.

## 4. RHS and normalized derivative construction

Use background derivatives and the first-order regular system directly. At each state or formal Taylor series, form

```
u = -2 H p1 - T f1/3
v = -4 H g1 + (m2-mu1 E²+2 T²) f1 + (12 H T-4 m2 Phi) p1
c2 = -(3/13)*(6 p1²+f1²)
c2prime = -(3/13)*(12 p1*u+2 f1*g1)
Sp = H*c2 - p1*u - f1*g1/6
qK = (4 m2-6 mu1 E²)*p1*f1 + 6*u*g1 - 8*m2*Phi*p1²
Sg = T*c2prime + 2*m2*Phi*c2 - 6*T*Sp - qK
```

Then the forced second-order block obeys

```
p2P' = -2H p2P - T f2P/3 + Sp
f2P' = g2P
g2P' = -4H g2P +(m2-mu2 E²+2T²)f2P +(12HT-4m2Phi)p2P + Sg.
```

The homogeneous second-order block is identical with Sp=Sg=0. No numerical differentiation, no division by T, and no need to add c2 as an independent ODE state. Primary recurrences evaluate polynomial products with E retained; independent recurrences use coefficients of exp(-2W), not a copied primary E recurrence. Source coefficients at order n use known state coefficients through n; then each state coefficient at n+1 is RHS coefficient/(n+1), as in the original engines. Audit that c2prime is formed from the analytic first-order RHS rather than differentiating an interval profile.

Compute `Sc=12H*Sp-(12H²-T²)c2+qR` using the exact T15 qR expression. The forced constraint is

`T*g2P - Tprime*f2P + (2T²-3(mu2+4k)E²)*p2P - Sc = 0`.

The homogeneous block has the same constraint with Sc=0. Check the qualified Q4 source identity at the symbolic recurrence level and retain all three constraints as whole-cell numerical diagnostics. Merely seeing zero inside a broad constraint box is not a replacement for source qualification.

## 5. Loading and shooting assembly

Bind T17 xi2 and T18 Eulerian Q6 loads at both walls for the lower-current direction. These sources are functions of the first-order fields, not unknown second-order profiles. Reconstruct them from fresh first-order wall jets and require overlap with accepted parent values. For a first probe, using the full accepted source enclosures as frozen interval inputs is valid but may be wide; declare that choice before execution.

Let `B=Gamma2*T/2-Tprime`. At the lower wall choose p2P(a)=0 and p2H(a)=1. For either launch,

`f2a=(Sca+3(mu2+4k)E_a²*p2a-T_a*R2a/2)/B_a`,

`g2a=Gamma2_a*f2a/2+R2a/2-2T_a*p2a`.

For the homogeneous launch set Sca=R2a=0. Require the launch divisor to exclude zero. Evaluate the entire uncertain upper-wall strip and form F_P/H=g2P/H+2T*p2P/H+Gamma2*f2P/H/2. The final multiplier is `A2=(-R2b/2-F_P)/F_H`. Only divide if the numerical F_H enclosure excludes zero. T20 can supply a checked reference for this homogeneous flow, not a silently substituted denominator from a different normalization/domain.

Assemble p2=A2*p2H+p2P, f2=A2*f2H+f2P, g2=A2*g2H+g2P. Reconstruct both undivided scalar and oscillator wall rows, including xi2 and Q5 sources, on these full interval fields. Q6 loads cannot be inserted unchanged into a scalar-reduced Q7 Robin row, nor into pulled-chart variables.

## 6. Proper-distance output and uncertain-wall handling

Accumulate/export outward whole-cell integrals separately for p2P, p2H, c2 and p1². A useful optional improvement is integrating them as extra ODE states, but that requires new recurrence qualification; the first implementation can use the accepted mandatory-prefix plus signed optional-tail interval budget pattern.

After assembly, use the Eulerian coefficient

`D2 = xi2_b-xi2_a -2*(A2*Integral(p2H)+Integral(p2P)) + Integral(c2)+2*Integral(p1²) + [(-2p1)*xi1]_a^b`.

Integrate over the full uncertain neutral domain exactly as previous packets: mandatory length to Dlo, optional signed interval length to Dhi. Endpoint products must use full uncertain physical-wall traces. Save each contribution and their sum; no interpretation of an isolated chart piece as an independent observable. A separately evaluated pulled-chart identity may check transport, but cannot replace an unresolved Eulerian enclosure by a narrower convenient expression unless prospectively chosen and reviewed.

## 7. Required qualification before a full production run

1. Independently derive augmented RHS/recurrences and compare their exact coefficients through the engine's remainder order, including source terms. Use qualified T15 identities as an oracle without treating a shared source evaluator as two independent implementations.
2. Verify source-off reduction against the original neutral engines at both masses; manufacture a nonzero forced solution with known source, constraints and boundary loads. Mutate qK, Sc, c2prime and boundary-transport signs to demonstrate sensitivity.
3. Validate recurrence-to-RHS agreement and full-vector Picard inclusion, not only endpoint agreement. Retain separate primary polynomial-E and independent exponential-W routes.
4. Probe a predeclared short domain and then the full homogeneous/forced domain with complete uncertainty. Record memory, time, wrapping, all inverse margins and checkpoint costs. Source magnitudes do not establish an admissible finite charge.
5. Run full production only under new authorization, frozen bounds/settings and independent admission. If projected runtime exceeds an hour, exact atomic resumable state must include all coupled states, integral budgets, source/multiplier bindings and predecessor hashes before launch.

This map closes implementation ambiguity, not the remaining field equation. No second-order proper-separation sign or value is inferred from T15–T20 alone.
