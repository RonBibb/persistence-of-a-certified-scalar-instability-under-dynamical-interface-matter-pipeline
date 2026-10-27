# R1: exact integer metadata serialization only

The frozen predecessor `lin-central-validated-mode-20261005T165817Z` stopped at
its first checkpoint publication after 256 accepted primary lower-endpoint cells.
Its `output/FAILURE.json` records `TypeError: Object of type fmpz is not JSON
serializable`. No physical checkpoint or terminal determinant was published.
Its binding guard is
`acf1206756cdcda072cf818c3ad65806328d78eb904971d098b6983f21d7b63d`.
All frozen predecessor files and the failure remain unchanged.

Cause: in this exact-arithmetic runtime, `math.ceil(fmpq)` returns `flint.fmpz`,
not a built-in Python integer. The synthetic recovery checkpoint did not include
the production `total_cells` field and therefore missed this metadata defect.

Repair: explicitly convert that exact integer count with `int(...)`; retain the
same exact ceil operation, and add the production `total_cells` field to both
analytic fresh-process recovery controls. There is no truncation of a noninteger:
conversion happens after the exact ceiling. Bind the failed predecessor sources,
freeze and failure report as provenance of this separately frozen repair.

Both interval engines, all model parameters, mass/root/event intervals, Picard and
Taylor settings, gates, task ordering and claim boundaries are unchanged. The
prospective proof and preflight scientific reviews carry over only in that scope;
an additional independent technical repair review and a new final-source
preflight are mandatory. No new physical evaluation is permitted before R1 freeze.
