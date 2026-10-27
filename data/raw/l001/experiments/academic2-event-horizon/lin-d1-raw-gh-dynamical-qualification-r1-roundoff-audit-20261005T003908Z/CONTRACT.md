# R1 roundoff audit of the D1 scalar-response amplitude gate

## Purpose

The frozen producer completed every numerical step and passed every physical
response gate, but recorded its declared `1e-6` scalar perturbation as
`1.000000000001e-6` after adding it to and subtracting it from a nonzero
binary64 background.  Its strict upper comparison therefore returned false.

This is a post-outcome technical audit, not an outcome-blind scientific rerun.
It does not alter the producer, its terminal classification, any checkpoint,
or any physical threshold.  It asks only whether the amplitude discrepancy is
bounded by ordinary floating-point representation error in the declared
construction.

## Frozen audit rule

Authenticate the producer source, freeze, result, terminal, evidence,
independent audit, and all eight checkpoint/record pairs.

Let `epsilon=1e-6`, let `Phi_bg` and the declared unit-bounded shape be read
from the sealed evidence, and reconstruct in binary64

`Phi_stored = fl(Phi_bg + epsilon shape)`.

Define the representation allowance prospectively as

`8 u max(1, ||Phi_bg||_inf)`,

where `u` is NumPy binary64 machine epsilon.  The amplitude false failure is
confirmed only if:

1. the shape is finite, nonnegative, no larger than one, and zero on both
   compact-wall rows;
2. the exact declared increment `epsilon shape` has maximum no larger than
   `epsilon`;
3. the measured stored increment is no larger than `epsilon` plus the stated
   representation allowance;
4. the excess above `epsilon`, if any, is no larger than that allowance;
5. the original independent audit is `VERIFIED`; and
6. every other producer perturbation gate and all eight per-step gates pass.

If all conditions hold, the scientific response discriminator is classified
as passing with a technical amplitude-comparison false failure.  The original
producer label remains unchanged.

No new numerical evolution, stability, continuum, collapse, P16, horizon, or
parent-child inference is authorized.

