# Failure recorder qualification

Question: does a conversion-safe recorder retain raw identity and interval metadata before any fragile exact-endpoint conversion, and return explicit conversion errors without losing evidence? This is implementation qualification, not physical integration.

Freeze Python 3.12.3, python-flint 0.9.0, Arb 256-bit, one thread and predecessor Python/Arb binary hashes. Import the original coordinate producer only after hashing it. No numerical stepping or changed model occurs. Inventory both failed predecessor packets before and after. Current test sources are hash-bound by ADMISSION.json.

Controls are finite: exact one, radius-one ball, NaN ball, positive infinity ball, and a fake object whose endpoint conversion deliberately raises. Publish raw records (case identity, repr/str, finite/exact flags, midpoint and radius where available) with flush/fsync before endpoint conversion. Then publish safe detailed records whose endpoint errors are strings, not raised exceptions. Require finite controls to produce ordered rational endpoints, invalid/fake controls to retain explicit errors, raw files to remain readable, and exclusive publication to reject overwrite. No deletion or overwriting of evidence. Three optional constructor observations at h=-1/128,-1/100,-1/102400 record the original interval constructor's output; they are diagnostic observations, not qualification pass conditions for physics.

PASS_RECORDER_QUALIFIED requires all recorder controls, immutable source/parent/runtime bindings, and successful publication. Any unmet condition is TECHNICAL_INCOMPLETE; no repair in this packet. Source, controls and output require independent prospective and terminal review.

One normal resource attempt using shared admission/HOLD/CPU/L001 locks, one core including the controller and library thread through inherited affinity, 1 GiB memory ceiling, 600-second wrapper and 590-second child cap. No queue/retry. Must start before allocation cutoff 2026-10-25T16:12:07Z; qualified output may support a separately admitted replay within this allocation.
