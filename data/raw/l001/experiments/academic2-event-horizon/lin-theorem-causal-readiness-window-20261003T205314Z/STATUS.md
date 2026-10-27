# Lin theorem and causal-readiness window status

Final state: **COMPLETE**.

The authorized research window activated at `2026-10-03T20:53:14Z`, paused at
`2026-10-03T21:07:33Z`, resumed at `2026-10-03T21:34:59Z`, and reached its
adjusted no-new-experiment boundary at `2026-10-03T23:19:59Z`. No new
experiment was started after that boundary.

Final classification:

```text
NARROW_STATIC_THEOREM_DRAFT_READY__CAUSAL_EXPERIMENT_NOT_ADMITTED
```

The static paired theorem is ready to organize as a narrow manuscript draft,
but the work is not submission-ready. The incompatible P407/O4 causal lineage
was not extended, unsealed concurrent initial-data output was not consumed,
and no sealed parent or external record was changed.

`RESULT.json` contains the machine-readable conclusion. `MANIFEST.json` and
`TERMINAL.json` bind the completed packet. A valid terminal state requires
`verify_window.py` to report both `local_manifest=PASS` and
`LIN_THEOREM_READINESS_WINDOW=PASS` on macOS and Linux.
