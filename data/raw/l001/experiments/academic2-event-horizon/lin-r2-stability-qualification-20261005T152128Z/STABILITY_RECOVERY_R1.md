# Serialization-only recovery, prospectively frozen before spectrum evaluation

The original attempt stopped while publishing its control receipt because a
NumPy Boolean was not JSON serializable. No scientific background or mode case
was evaluated. The failed output and original source/bindings are retained.

R1 converts NumPy scalar objects to their corresponding native scalar only
when writing JSON. It also changes the output and binding filenames to a new
namespace. The scientific equations, parameter points, controls, precision,
brackets, sample counts, acceptance gates and recovery policy are identical.

The corrected writer is exercised with NumPy Boolean and float payloads in a
disposable serialization check before production. This check contains no
physical solution. The new binding includes the original failure and binding.
