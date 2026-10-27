# Central background dependency and regeneration audit

Read-only source/record audit for the fixed allocation 2026-10-18T17:06:44Z–18:06:44Z. No background producer, replay, solver, control, checker, numerical import, or install was executed by this auditor. File reads and SHA-256 identity measurements only; this note and its identity list are new review artifacts. No manuscript or historical packet was changed.

## Finding

The source closure needed to regenerate the central reduced background is present. The original 32,768-step wrapper imports its separately frozen parent producer; the independent R1 wrapper imports a separate engine in its own packet. The six action labels agree between the two engines and use the same explicit binary64-to-dyadic conversion. Revision 6 Supplement A and the spectral binding print the same six exact fractions and the same original high-resolution Newton image. No conflicting declared input was found. This is a source/record comparison, not a newly executed conversion or numerical certificate.

The independent accepted record supplies positive endpoint `S` (manuscript `T`), positive curvature, and a positive whole-domain warp enclosure. It does **not** directly calculate or gate the sign of `T'`. The latter follows from the quadratic-potential argument in Supplement F.9 once `T_a<0<T_b`, `k>0`, smooth regular flow, and positive warp are supplied. The narrow manuscript launch interval still specifically depends on the original high-resolution Newton image: the independent R1 image is wider. A fresh unchanged independent R1 execution would independently regenerate existence/uniqueness and endpoint/geometry evidence on the common frozen input box, but would not by itself independently regenerate the narrower manuscript interval.

**Archival recovery update:** the initial packet-only inspection below found no original high-resolution raw stdout or summary adapter. Subsequent targeted historical-session inspection recovered the complete original command stdout, including the exact manuscript I_A strings and measured runtime70.2075723670423seconds. The recovery appendix preserves its narrow provenance and distinguishes this recovered record from a fresh producer execution. The initial missing-stdout observations are retained as first-pass findings and are superseded to that extent by the appendix.

## Path abbreviations

All paths below are relative to `/Users/ronbibb/Research`.

- `E = research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon`
- `P = E/lin-d1-validated-sensitivity-newton-20261002T012953Z`
- `H = E/lin-d1-high-resolution-confirmation-20261002T015100Z`
- `R = E/lin-d1-independent-ode-replay-20261002T225837Z`
- `C = E/lin-theorem-causal-readiness-window-20261003T205314Z`
- `S = papers/paper-A/manuscripts/20261018_revision_6/MATHEMATICAL_SUPPLEMENT.md`
- `B = papers/paper-A/experiments/20261013T202602Z_THREE_IDEAS/inputs/central_bindings.json`

## Exact inputs and their interpretation

| Meaning | Both source labels | Exact manuscript/binding value |
|---|---|---|
| `m²` | `0.41` | `7385903388887613/18014398509481984` |
| `gamma` | `20.0` | `20` |
| `v0` | `0.1` | `3602879701896397/36028797018963968` |
| `v1` | `0.09048374180359596` | `6520040733916207/72057594037927936` |
| `lambda_a` | `5.999990376773895` | `6755388606266369/1125899906842624` |
| `lambda_b` | `-6.052844277744164` | `-851862101055633/140737488355328` |

Pointers: `P/validated_sensitivity_newton.py:18-38,88-96`; `R/independent_d1_replay.py:21-40,95-103`; `S:7-26`; `B:79-85`. Both engines implement `float(text).as_integer_ratio()` followed by `fmpq`, so interpreting the labels as exact decimal fractions such as `41/100` would change the problem. The manuscript exact fractions and binding agree textually; no conversion checker was executed in this audit.

The common narrow **input** box is the exact binary64 promotion of `[0.09901086489880687,0.09901086689880687]`, with promoted center `0.09901086589880687`. Original `P:24-30,283-286`; independent `R:27-29,101-103,389-403`. The proper-distance integration endpoint is exactly `2`, distinct from the uncertain upper-wall event inside it.

The original high-resolution **output** image, used as manuscript/spectral `I_A`, is exactly

```
[456607025194779413/4611686018427387904,
 114151756532473697/1152921504606846976].
```

It agrees textually in `H/RESULT.json:20-23`, `S:20-26`, `B:3-6`, and `R/POSTRUN_AUDIT.json:25-28`. The event interval is `I_D=[32727/16384,32729/16384]` (`B:7-9`, `S:819`, `R/POSTRUN_AUDIT.json:21-24`); `H/RESULT.json` retains its exactly dyadic decimal display `[1.99749755859375,1.99761962890625]` rather than rational event strings.

## Original producer: wrapper, source closure, and predicates

`H/confirm_32768.py:3-27` imports `flint.arb` and **`validated_sensitivity_newton`**. That module is not in H's directory. A bare invocation from the archived H directory therefore requires either the sibling P directory in the import path or an isolated staging directory containing both frozen source files. The wrapper replaces the historical equality-based quotient control with interval containment, sets `STEP_COUNTS=(32768,)` and `PRECISION_BITS=768`, then invokes the parent `main()`. It does not import the intervening R1 correction wrapper. `H/CONTRACT.md:19-26` binds the parent and wrapper identities explicitly.

`P/validated_sensitivity_newton.py` is otherwise self-contained apart from Python stdlib and `python-flint`:

- `152-189`: 6 physical states plus 6 launch sensitivities, including varying `k(A)` and its initial derivative. Source `A` denotes log warp; the source's launch argument `a` is the manuscript scalar `A`. Source `S` is manuscript `T`.
- `192-208`: every cell must produce a strictly self-containing Picard box (at most 24 attempts), then the endpoint encloses the first Taylor term plus the second derivative over that whole box, computed through `TimeDual`. This is a second-derivative-remainder construction, different from the independent fifth-derivative method.
- `211-223`: `G=F1=H-tau_b/6`, `h=F2=T+gamma(Phi-v1)/2`, `D_A=-G_A/G_s`, and `q_A=h_A+h_s D_A`. This includes event movement and curvature dependence, rather than a fixed-terminal-distance derivative.
- `226-275`: integrates all `[0,2]`; zero-containing G cells must be nonempty and contiguous, all preceding cells positive, following cells negative, and `G_s<0` across their union. Source uses `all(...)` without explicitly demanding both sign regions be nonempty; the retained interior event bracket supplies that nonvacuity for the historical record. Fresh admission should explicitly verify it too.
- `283-318`: computes `N(I)=A0-q(A0)/q'(I)`, excludes zero from derivative, requires strict inclusion in input I and both center/box validated events.
- `333-388`: all declared boxes must pass corrected algebra controls, complete propagation, event gates, nonzero derivative and strict inclusion before a passing classification is printed.

The original H result records both wide/narrow self-maps, transverse event derivative, positive shooting derivative and the exact narrow Newton image (`H/RESULT.json:1-26`). It does not export the per-cell boxes, nor independently certify the endpoint `T>0` or complete geometry.

**Schema/provenance limitation:** the parent `main()` prints `schema=d1-validated-sensitivity-newton-result-v1`, runtime metadata and rich `all_results` (`P:358-388`); archived H `RESULT.json` is a compact `d1-high-resolution-confirmation-result-v1` summary with wide/narrow keys. No summary-construction adapter or full original H stdout is present in the inspected H packet. A fresh wrapper execution can regenerate proof-bearing raw fields, but cannot reproduce this compact file byte-for-byte through the wrapper alone. The historical command map already instructs comparison of exact mathematical fields rather than byte identity (`C/REPRODUCIBILITY_COMMAND_MAP.md:33-49`). No numerical invalidity is inferred merely from this documented serialization gap.

## Independent producer and accepted versus adverse records

`R/independent_d1_replay_r1.py:4-11` imports only local `independent_d1_replay`, changes the step pair from `(4096,8192)` to `(8192,16384)`, and invokes `main()`. The engine's imports (`11-18`) are Python stdlib plus `flint`; it reads no prior result/enclosure and imports no original producer. Source identities match its pre-run freezes and manifest; see `BACKGROUND_IDENTITIES.sha256`. Algorithmic independence is from the original implementation, while Arb and the reduced equations remain shared.

`R/independent_d1_replay.py`:

- `171-212`: same launch, background and sensitivity equations.
- `106-168,215-256`: independent truncated-series multiplication/exp recurrence and normalized Taylor coefficients; endpoint terms of degrees 0–4 at initial box plus the fifth coefficient over a whole-cell Picard box. Strict self-containment in `224-240`, at most 32 attempts.
- `259-290`: independent event residual and event derivative construction; exports raw `S`, curvature, warp, conformal position and algebraic wall residuals.
- `306-382`: every cell's first-integral containment, global warp bounds, strict negative H, event sign classification and exact event endpoints. Event union includes complete candidate cells, hence encloses the unknown actual wall.
- `389-410`: center/box event validation, nonzero q derivative and exact strict Newton self-map.
- `412-455`: positive k, D, Z, event warp, global H monotonicity and invariant/wall residual containment. Residual intervals containing zero are consistency gates, not independent proofs of exact identities; those follow from exact launch and the equations.
- `479-558`: both prospective R1 levels must pass and both geometry sets must pass; all output is JSON on stdout. Exceptions are recorded and can still result in process exit code zero. Therefore an exit code alone cannot establish success.

The first original invocation is retained as `P/FIRST_INVOCATION_RESULT.json`, `P/TERMINAL.json`: quotient control object equality falsely failed before **zero scientific ODE steps**; no nonexistence claim follows. Corrected containment is local to later wrapper execution.

The separately corrected original `E/lin-d1-validated-sensitivity-newton-r1-20261002T014500Z/RESULT.json:3-15` also retains an adverse aggregate: `VALIDATED_SENSITIVITY_NEWTON_NOT_ESTABLISHED`, because the narrow4096-step image was wider than its input box (five of six individual inclusions pass). Its contract retained all six cases; the later H32768 confirmation is a separately frozen packet and does not change that aggregate classification. This source lineage therefore has three distinct adverse records to preserve: original technical false-failure, corrected-original coarse/narrow inclusion failure, and independent r0 coarse inclusion failure.

Independent r0 is retained as `R/output/r0/RESULT.json`; its 4096 image fails strict inclusion while 8192 passes, so the two-level contract remains `INDEPENDENT_D1_REPLAY_NOT_ESTABLISHED`. R1 was separately frozen with step pair8192/16384 (`R/CONTRACT_R1.md:3-33`, `FREEZE_R1.json`). Its accepted result is `R/output/r1/RESULT.json`, terminal class `INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS`. The adverse curvature-width diagnostic, fine/coarse ratio `1.0000297219462309`, is preserved (`POSTRUN_AUDIT.json:74-85`); positivity passes, and monotone narrowing of every derived bound was not required. These records must not be overwritten or reclassified by future reproduction.

## What certifies endpoint T and T-prime

The load-bearing upper sign is in `R/output/r1/RESULT.json:1150-1160`, fine level → root_box → event_quantities → S. Both exact numerators/denominator are positive; the approximate interval is `[0.021551799860688146,0.02167604375206592]`. It encloses T throughout the full event-cell union for every scalar launch in the original narrow input box, so it includes the actual root/event without requiring exact root/event correlation. `S>0` is **not** a named automatic geometry gate (`R/independent_d1_replay.py:419-430`); a reproduction checker must explicitly read the exact lower bound and require it positive.

Lower `T_a=gamma(A-v0)/2<0` follows from the exact launch box being below v0 and gamma positive (`R:171-174`). Positive k is recorded in fine event curvature (`RESULT.json:1174-1184`) and is a constant state. Whole-domain warp positivity has an exported `global_warp_enclosure` (`RESULT.json:1285-1295`), generated by `R:330-335`; its exact lower bound should be checked directly, along with completed Picard propagation. The accepted geometry includes event warp positivity and strict negative H over all cells.

These supply the premises of `S:648-657` (Supplement F.9):

```
(a^4 T')' = a^4 Q T,
Q = m² + 4k/a² + 4T²/3 > 0.
```

Exact nonconstant regular flow excludes simultaneous `T=T'=0`; opposite endpoint signs imply at least one turn; the positive weighted integral excludes two; its sole upward turn has `T'>0`. To its left `a^4T'` is no smaller than its positive turn value, and to its right it increases. Thus `T'>0` throughout the closed physical interval, including endpoints. This analytical argument, rather than the shooting derivative `q_A>0`, establishes the endpoint derivatives. `q_A`, `G_s` and `T'` are different quantities.

## Same exact root and remaining narrow-interval premise

Both original and independent engines solve the identical reduced IVP and wall maps with identical promoted labels, center and narrow input box. A transverse event gives differentiable q; nonzero q' throughout the box and interval Newton strict self-inclusion prove a unique root in that box. Consequently their certified roots coincide. Overlapping numerical estimates alone would not identify a root.

The independent fine Newton image is

```
[456607024314529497/4611686018427387904,
 456607027779925737/4611686018427387904]
```

(`R/POSTRUN_AUDIT.json:29-36`; raw fine `interval_newton_image` in result). It is wider than the manuscript I_A. Therefore fresh R1 alone can independently recover the same root and geometric predicates, while use of the original narrower I_A by the phase solver still invokes original high-resolution containment. A changed or widened phase launch would be a new calculation, not an unchanged background replay, and is not proposed here.

## Runtime, commands, and feasible regeneration

Historical independent runtime is explicitly recorded (`R/output/r1/RESULT.json:1310-1325`): Linux6.8.0-139-generic aarch64, glibc2.39, CPython3.12.3, python-flint0.9.0, Arb768bits, total138.3287074828986seconds; level8192 took45.4743919800967seconds and level16384 took92.85020500188693seconds (`672,1307`). R0 took66.942seconds but is not the accepted step pair. These are historical observations, not a promised new ETA. The compact H record has no runtime field; its 15m46s activation-to-terminal span is an outer packet interval, not measured integration runtime.

`R/FREEZE.json:20-33` identifies historical Python-flint root `/home/parallels/research-runtimes/protocol406-python-flint-0.9.0` and one-thread/no-user-site/no-bytecode environment. This historical Linux directory was not present on the current Mac in the path inventory; no remote runtime was contacted by this auditor. A separate later spectral binding records a different cap-interval runtime with library hashes (`B:94-152`); those later binary identities must not silently be attributed to the historical background execution. Native python-flint requires compatible FLINT/GMP/MPFR libraries; its wheel/runtime supplies these. The inspected background packet has version/platform declarations, not a full binary lock/container/requirements file. Source syntax needs Python3.10+ (`zip(strict=True)`, union annotations); reproducing the recorded environment favors3.12.3 and flint0.9.0. No package import or compatibility test was executed here.

Historical command shapes are explicitly retained in `C/REPRODUCIBILITY_COMMAND_MAP.md:33-63`. Once two exact source files are copied into a fresh isolated staging directory, unchanged commands are:

```sh
# Original: staged confirm_32768.py and validated_sensitivity_newton.py together.
env PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTHONPATH=/home/parallels/research-runtimes/protocol406-python-flint-0.9.0 \
  /usr/bin/python3.12 -B /ABSOLUTE/NEW/STAGE/original/confirm_32768.py \
  > /ABSOLUTE/NEW/OUTPUT/original/RESULT.raw.json \
  2> /ABSOLUTE/NEW/OUTPUT/original/run.stderr

# Independent: staged independent_d1_replay_r1.py and independent_d1_replay.py together.
env PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  PYTHONPATH=/home/parallels/research-runtimes/protocol406-python-flint-0.9.0 \
  /usr/bin/python3.12 -B /ABSOLUTE/NEW/STAGE/independent/independent_d1_replay_r1.py \
  > /ABSOLUTE/NEW/OUTPUT/independent/RESULT.raw.json \
  2> /ABSOLUTE/NEW/OUTPUT/independent/run.stderr
```

These are **unexecuted templates**: replace fresh output/stage paths and use a separately identified available pinned runtime. Files must be hash-checked after copying; do not reconstruct them from this prose. Both programs only print stdout; they do not write source/data files or read inherited results. `-B` suppresses generated `__pycache__`. A launcher may write lease, runtime/source identities, stderr/stdout and exit receipt solely beneath its new output directory. No stage should use or overwrite historical `output/r0`, `output/r1` or H/RESULT.

The existing portable archive is a separate packaging limit: `papers/paper-A/manuscripts/20261017_revision_1/portable/static/archive/branches/02-event-horizon/` contains original H wrapper and parent producer, but its `lin-d1-independent-ode-replay-20261002T225837Z/` contains only `POSTRUN_AUDIT.json` and `TERMINAL.json`. Its union manifest lists those two (`portable/static/ARCHIVE_UNION_MANIFEST.json:183-202`) and does not include independent engine, R1 wrapper or accepted raw result. Consequently that portable package alone cannot perform unchanged independent background regeneration or independently inspect raw endpoint S. The full research tree supplies the missing files. No archive was changed in this audit.

### Narrow candidate for separate reviewer admission

One unchanged independent R1 invocation is feasible if its runtime is available and separately admitted: one numerical slot, hard timeout at most600seconds and never beyond18:06:44Z, no tuning, retry, repair, extra levels or successor. Stage exactly wrapper+engine, preserve the frozen8192/16384 pair,768bits, all launch labels, and predicates. Freeze source/runtime/launcher identities and new output path before launching. On timeout/exception/missing levels close incomplete; do not extend the fixed window. This paragraph proposes an action; it does not authorize or execute it.

Required terminal scrutiny of any fresh raw output (not performed here):

1. Source hashes match; reported runtime and768bits match the admitted environment; labels exactly match frozen sources; method pair is8192/16384; controls all true; no error; status COMPLETE and pass classification.
2. For both center and box at both levels: completed flow, nonempty contiguous event cells strictly interior to integration interval, explicit preceding/following sign regions, `G_s<0`, q' excludes zero, and exact Newton image strictly inside common input box. Re-derive strict inequalities from exact strings, not booleans/decimal endpoints.
3. All original geometry gates pass; explicitly add exact positive global warp, positive k, and positive event S (endpoint T) at both levels. Interpret first-integral/wall zero containment as consistency, not a substitute for exact launch/identity arguments.
4. Keep all three old adverse records; compare fresh exact proof-bearing intervals to archived accepted raw R1 output and identify any drift. Wallclock/platform metadata need not be byte-identical. Independent internal success still requires an independent terminal audit before promotion.
5. State the surviving original I_A premise. If full background regeneration means independently recovering the narrower phase launch enclosure as well, unchanged R1 alone is insufficient. Original wrapper regeneration, with its parent import explicitly closed, is a distinct prospective admission; estimated integration runtime is unavailable in H's compact record.

## Identity and scope receipt

Current SHA-256 measurements for the14 core source/record files are in `BACKGROUND_IDENTITIES.sha256`; every listed identity agrees with the inspected frozen manifests/terminal bindings. This establishes file identity only. The note reviewed the central local root and geometry path, not the726-box global first-event uniqueness certificate or693-box fixed-distance exclusion. It did not rerun any predicate and does not upgrade inherited numerical evidence to regenerated proof.

## Recovery appendix: original high-resolution stdout found outside the sealed packet

At approximately17:15Z, a targeted read of the original historical Codex transcript recovered the complete stdout from the accepted original high-resolution command. No producer, checker or numerical import was executed. The operation parsed the historical JSONL event and transcribed its `payload.item.stdout` string to `RECOVERED_HIGHRES_STDOUT.json`. No unrelated transcript content was copied.

Provenance is retained in `RECOVERED_HIGHRES_PROVENANCE.json`:

- Transcript `/Users/ronbibb/.codex/sessions/2026/09/01/rollout-2026-09-01T19-56-16-01a0543c-b99b-72e2-b0c2-ca518a4dd5d1_01a05f66-ee84-7991-998a-fa0acac11eed.jsonl`.
- Exact line56261; event timestamp `2026-10-02T01:57:14.792Z`; ordinal78553.
- Completed command item `exec-a99105d7-4f03-4d08-a669-612b74aabc10`, exit0.
- Command invokes the frozen `confirm_32768.py` through SSH using `/home/parallels/codex-precision-noble-py312-20260830/bin/python`, with `PYTHONPATH` containing `/home/parallels/research-runs/cap-interval-arb-2026-09-12` and the original parent producer directory. This historical primary runtime root differs from the later independent replay's freeze path; it resolves the primary command provenance without assuming one shared path.

Recovered raw stdout SHA-256 is `d4ea2078fc6537b940075bef5ecf959e606a651de1af75b0db2690c05b94ae86`; the provenance file has its own identity receipt. It is a **recovered historical record**, not an originally packet-sealed file and not a regenerated execution. Its identity is measured now; its contents are supported by the named saved command event.

The full stdout uses the parent's raw `d1-validated-sensitivity-newton-result-v1` schema and reports both32768-step cases passing. The narrow `interval_newton_image.exact_bounds` strings are exactly

```
["456607025194779413/4611686018427387904",
 "114151756532473697/1152921504606846976"]
```

These are the same strings as the compact H summary and manuscript I_A. The recorded root-box event strings are `["32727/16384","32729/16384"]`. Thus the compact summary's manuscript interval can be traced directly to the original raw exact-bound export; no intermediate float-to-fraction conversion is needed to explain those values. The reconstruction of the compact summary file itself remains a historical manual/serialization operation, but its load-bearing exact intervals now have an original raw source. A denominator smaller than768bits was not by itself evidence of inward rounding: the saved independent raw result also exports compact Newton bounds using the same `lower().fmpq()` / `upper().fmpq()` interface.

The recovered original narrow input box is `["3567242354111177/36028797018963968","3567242426168771/36028797018963968"]`. It is the exact promoted source-label box used for the same-root uniqueness comparison. The raw record preserves interior event-cell indices and preceding/following sign booleans, addressing information omitted by the compact summary; it still does not export every Picard box or exact event derivative ball.

Recovered `runtime` (`RECOVERED_HIGHRES_STDOUT.json:416-421`) reports the same Linuxaarch64/glibc2.39, CPython3.12.3 and python-flint0.9.0 at768bits, and **70.2075723670423seconds** measured wall time. Together with the independent138.3287074828986seconds, the historical producer computation total is approximately209seconds, excluding staging, witness and terminal audit. This informs feasibility only; it does not promise elapsed time on another host.

The independently reviewed fresh-run proposal owned by the parent may use a separate single900second sequence lease for unchanged original+independent regeneration, bounded by the fixed absolute cutoff. That later proposal supersedes this note's earlier independent-only candidate, and is not launched by this auditor. If a fresh original raw Newton image falls outside manuscript I_A, classify the narrow enclosure link as unestablished for that execution even if the difference is tiny; that is not a physical counterexample. Do not rescue-tune or silently widen a frozen spectral launch. Any completed fresh producer result must be separately audited before promoting it beyond producer output.
