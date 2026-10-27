# Parameter-neighborhood failure diagnosis and local sensitivity contract

## Purpose

This successor has two bounded purposes:

1. independently reconstruct why the frozen two-parameter neighborhood run
   ended `INCOMPLETE`; and
2. derive, with both sealed interval producers, the local implicit
   sensitivities of the D1 shooting root to `v1` and `lambda_b` at the central
   solution.

It does not alter, repair, or reinterpret the failed frozen run.  It does not
claim persistence over any finite parameter box.

## Frozen diagnostic inputs

- the incomplete parameter-neighborhood `RESULT.json` and terminal record;
- the sealed primary D1 interval variational producer;
- the sealed independent fifth-order D1 interval producer.

## Structural failure audit

The audit must reconstruct the exact four-cell depth-2 parameter cover and
confirm the declared subdivision history.  It must state whether both
producers failed for the same recorded reason, whether the frozen center event
remained validated, and whether any global-launch or fixed-D0 calculation was
executed.  Failure of the interval certificate must not be described as proof
that a physical root is absent.

## Local sensitivity calculation

The calculation uses the original sealed narrow D1 root box

`[0.09901086489880687, 0.09901086689880687]`

with the exact central parameters, 8192 proper-distance cells, and 768-bit Arb
arithmetic.  At the validated first event, with

`G = H - [lambda_b + gamma (phi-v1)^2/2]/6 = 0`

and

`q = S + gamma (phi-v1)/2 = 0`,

the explicit parameter derivatives are

- `G_lambda = -1/6`,
- `G_v1 = gamma (phi-v1)/6`,
- `D_p = -G_p/G_s`,
- `q_lambda = q_s D_lambda`,
- `q_v1 = -gamma/2 + q_s D_v1`,
- `a_p = -q_p/q_a`.

The total event-position sensitivity is

`(dD/dp)_root = D_p + D_a a_p`.

Both producers must validate the first event, enclose `G_s<0`, and exclude
zero from `q_a`.  The two producer intervals for every reported sensitivity
must overlap and have the same sign.  Otherwise the sensitivity result is
incomplete.

The finite-box displacement estimate obtained by multiplying central local
sensitivities by the declared parameter half-widths is explicitly a
linearized design diagnostic, not a rigorous finite-neighborhood bound.

## Claim boundary

This calculation may identify an interval-dependency mechanism and size a
future root tube.  It does not prove finite-parameter persistence, global
uniqueness, fixed-D0 exclusion, spectral stability, dynamical selection,
collapse, a horizon, or a cosmological interpretation.
