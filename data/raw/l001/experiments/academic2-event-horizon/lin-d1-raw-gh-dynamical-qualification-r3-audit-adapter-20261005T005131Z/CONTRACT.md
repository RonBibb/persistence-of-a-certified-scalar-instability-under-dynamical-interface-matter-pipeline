# R3 independent-audit serialization adapter

The frozen R2 independent verifier completed its checks in memory but its
unadapted JSON writer rejected NumPy scalar booleans before publishing the
audit.  R3 imports that exact verifier, replaces only its JSON writer with a
NumPy-scalar-aware equivalent, and preserves the resulting audit hash in a
receipt.  It changes no check, value, decision, or scientific classification.

This is a technical publication adapter, not a numerical calculation.

