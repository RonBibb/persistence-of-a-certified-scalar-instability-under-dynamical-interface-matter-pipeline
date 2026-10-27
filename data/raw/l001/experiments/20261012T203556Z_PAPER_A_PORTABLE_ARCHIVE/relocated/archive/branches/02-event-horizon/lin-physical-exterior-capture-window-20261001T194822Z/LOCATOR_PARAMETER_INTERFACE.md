# Optional locator parameter interface

The existing O1/O2 numerical mechanics can be exercised on the warped-Kottler
control without loading P407 or inheriting any of its physical claims.

## Required parameters

- `geometry_id`: `WARPED_KOTTLER_CONTROL_V1`
- exact metric provider:
  \(g_5=\psi(z)^2[-f dv^2+2dvdr+r^2d\Omega^2+dz^2]\)
- \(f=1-2M/r-kr^2\), with explicit \(M,k,\psi\) IDs;
- exterior ID: future static region \(E_{\rm stat}\);
- exact terminal surface: \(r=r_b\);
- exact outgoing null equation: \(dr/dv=f/2\);
- exact horizon rate:
  \[
  \kappa_b=\frac12f'(r_b)=\frac{M}{r_b^2}-kr_b>0;
  \]
- physical width on \(\tau=v-r\) sections, not coordinate width; and
- independent captured/visible authorities from the construction note.

For the retained numerical parameter instance, \(\kappa_b\) is approximately
0.2486904891542565.  Infinitesimal terminal offsets contract backward as
\(\exp[-\kappa_b\Delta v]\).

## Reusable mechanics

The coordinate, Hamiltonian and induced-endpoint null formulations,
atomic/checkpoint machinery, terminal-quartet comparisons and physical-width
reporting may be reused after replacing every hardcoded source, path,
terminal label and expected digest.

## Scope

This would be a curved-background positive control for the locator.  It cannot
turn the numerical curved BVP into an exact solution, transfer the control to
the collapse lineage, or substitute for the physical exterior/capture
authorities.  No locator run was needed in this window because the exact null
equation and central horizon are already known.

