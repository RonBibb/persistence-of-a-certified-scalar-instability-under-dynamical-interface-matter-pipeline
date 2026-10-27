# R1 technical correction to the D1-to-Cauchy boundary-jet assessment

The original frozen evaluator stopped before producing a scientific result
because python-flint 0.9.0 does not accept exponent-form decimal strings as
`fmpq` constructor input.  R1 parses every saved decimal string through
Python's exact base-10 `Fraction` constructor and then creates the same exact
rational value in `fmpq`.

R1 imports the frozen original evaluator.  It changes no chart, formula,
parent binding, physical parameter, comparison gate, classification rule, or
claim boundary.  The original `FAILURE.json` remains immutable.  The governing
contract is the original `CONTRACT.md`, SHA-256
`8c037c44b9c5176e377589859882eb17444009ea469f71933fa468b51cbb7238`.

