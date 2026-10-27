# Independent post-run scientific review

The precision successor qualifies the central background and reproduces the
physical growing scalar/radion mode at all nine prescribed parameter points.
All 18 coarse/fine solutions and all nine pairs pass the unchanged frozen
gates. The numerical campaign completed at 2026-10-05 16:48:41 UTC with no
uncomputed cases. This is a successful bounded numerical qualification.

## Decisive numerical evidence

The independently authored `independent_review.py` was executed serially by
the runner after the central pair and again on all 18 completed cases. It
imports none of the primary background, mode or differentiation routines.
`output/CENTRAL_INDEPENDENT.json` admits the center before the neighbors;
`output/FINAL_INDEPENDENT.json` reports every completed case passing, agreement
with producer acceptance, exact parameter membership, and unchanged inputs.

Across both verification resolutions, including both endpoints, the largest
independent normalized background residual is 2.1949491665e-16 against 1e-8.
The largest direct W_ss metric residual is 5.9237565584e-17. On 2001 nodes the
corresponding maxima are 1.7491690071e-18 and 4.7702377886e-19. The central fine
2001-node direct metric residual is 4.6557455080e-19; its predecessor value was
2.4163588399e-8. No endpoint, equation or wall was removed.

The largest independent mode residual is 5.8380693945e-9 against 1e-6; among
fine solves it is 1.1509577105e-9. Every scalar turn remains present, with the
largest normalized finite-turn relation 1.5559739646e-14. Independent kinetic
norms range from 320.6550953 to 321.9127145 and are positive. The normalized
proper-separation response ranges from -2.990183112 to -2.984335741; its sign
depends on mode normalization, while its nonzero magnitude is well resolved.
Independent norm and displacement integrals agree with their receipts within
1.44e-12 relative, below the 1e-7 gate.

The central physical mass is mu=-0.0013122306827991104 and the shifted quantity
mu+4k is approximately -4.8653289812e-6. Across all nine points, mu ranges from
-0.0013122956834787777 to -0.0013121659336991461, and the growing exponent in
units of the de Sitter Hubble rate ranges from 1.0029362721 to 1.0030146985.
The largest paired mass difference is 8.6736173799e-19; both physical-mass sign
and separation from the exceptional shifted sector pass their frozen tests.
That small paired difference is a numerical comparison, not an eigenvalue
error bound or a claim of multiprecision mode accuracy.

Independent conformal mode replays from the 1001/2001-node stored backgrounds
agree with proper-coordinate masses within 3.4520997172e-16 and with full
profiles within scaled 1.1858686873e-11. Central exact a,D,k membership in the
D1 enclosures and the archived profile/mass link pass. A separate conformal
MP RK4 background integration gives maximum field disagreements of
1.0790377432e-14 and 6.7445843132e-16 for the fixed 4/8-substep controls. Its
largest wall residuals are 1.5900247644e-13 and 9.9385364725e-15 against 1e-8.

## Precision interpretation

The primary source performs 50/70-digit MP integration and stores authoritative
MP decimal fields, coordinates and metadata. Independent storage checks pass
for every case. They parse directly into Linux extended precision, detect the
retained information beyond binary64, and independently confirm E exp(W)=1.
The roughly 125-fold reduction in central background residual from 1001 to
2001 verification nodes is consistent with endpoint differentiation truncation
dominating after the precision repair.

The new calculation therefore resolves the prior frozen residual failure by
reconstructing and storing the same branch at higher precision. It supports
an arithmetic/sampling limitation in the earlier computation. Because both
integration and storage precision changed, it does not isolate final-storage
rounding from binary64 trajectory or dense-sampling error. The predecessor
remains classified UNRESOLVED with its failed gate intact.

## Integrity and scope

A separate read-only post-run verification checked 240 identities and
consistency conditions: frozen
source and inputs, runtime/control links, terminal/result and final-audit
hashes, checkpoint guards and completed queue, all three artifacts and receipt
links for every case, and all 42 files in the predecessor's sealed manifest.
This includes rechecking all 87 file identities recorded by the final independent
audit against the current files, plus its runtime and control links. All 240
checks passed. No duplicate shooting or new numerical scan was performed.

Controlling hashes:

- BINDINGS.json: `fcf67907cf57828cd4a7b16732b80213935ec0e101a4bb7c99d6ec03adc8fa72`
- output/RESULT.json: `8a85d9edac50f309c4b6c484b9ffd6ea34d085446521b70dc946cabb5b66362c`
- output/TERMINAL.json: `b5934cb0ed30998730d1681d7cfd4e0444279a99a0eba708f66b7c934d9075e2`
- output/FINAL_INDEPENDENT.json: `dcabae45adb3d0632cc23f902aca057ba8f4844fd641dd3c7a832fd1de57eb04`

No unresolved numerical-admission or integrity issue was identified. The
supported conclusion is persistence of this resolved growing mode at the nine
frozen points on the certified static branch. It is not a uniform continuous-box
spectral theorem, a rigorous exact-background eigenvalue enclosure, a lowest-mode
or complete-spectrum result, nonlinear evolution, global initial data, an event
horizon, or a merger with the separate P16 construction. The R2 static theorem
retains its distinct rigorous scope.
