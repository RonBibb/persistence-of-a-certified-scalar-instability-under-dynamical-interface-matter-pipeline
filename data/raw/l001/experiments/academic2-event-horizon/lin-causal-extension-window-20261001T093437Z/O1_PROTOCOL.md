# O1 — P407-R3 stable-band terminal-seed interface

## Question

Can the post-diagnostic N=(157,165,173) lineages be reproduced exactly from
the authenticated H-step-512 parent through all 80 sealed Protocol 407-R2
future knots and published as a new terminal-seed interface for causal
tracing?

## Inputs and preservation

The experiment reads the frozen Protocol 407-R2 authority and evolution
payloads, the bound Protocol 401 MOTS implementation, and the September 30
full-lineage confirmation. Protocol 407-R2 remains failed at its original
N=145 terminal certificate and is not modified, resumed, or reclassified.

All source, contract, checkpoints, and results are written under this Academic2
window namespace. Numerical-library threads are fixed to one. Surface solves
and SciPy linear algebra are binary64. The Linux NumPy runtime also supplies a
112-fraction-bit `longdouble`, but that dtype is not used to relabel the
binary64 surface calculation.

## Fixed test

For each of N=157,165,173:

1. solve the H-step-512 parent from two independently interpolated,
   authenticated P401 parent profiles;
2. use the unchanged secant predictor and two-seed tracked solve at every one
   of the 80 sealed future knots;
3. retain the fixed terminals H=(1744,1760,1776,1792);
4. apply the unchanged dense-root and complete leaf certificate at each
   terminal; and
5. require the terminal profile SHA-256 to equal the corresponding bound
   September 30 profile SHA exactly.

Each resolution is an atomic recoverable unit. The final interface contains
the 12 profiles and their primary stability modes. No resolution fallback,
gate relaxation, or post-result seed change is permitted.

## Decision

`P407-R3-STABLE-BAND-TERMINAL-SEED-INTERFACE-PASS` requires:

- three admitted parent anchors;
- 240/240 tracked knot and dense-root checks;
- 12/12 full leaf certificates;
- 12/12 exact expected profile hashes;
- source, authority, core, and September 30 result hashes unchanged; and
- an atomically published interface archive and record.

Any mismatch or failed check is technical incompleteness. A pass supplies
terminal seeds on the inherited represented spacetime. It does not establish
continuum convergence, global outermostness, a physical causal exterior,
capture, escape, or an event horizon. The separate wall-acceleration
compatibility result has not been established on these late states, so all
downstream causal geometry remains conditional on the inherited spacetime.

