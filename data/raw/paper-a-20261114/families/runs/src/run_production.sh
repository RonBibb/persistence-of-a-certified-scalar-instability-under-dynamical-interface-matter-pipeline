#!/bin/bash
# Frozen production sequence.  The stage must match the freeze manifest; the
# controls run first; family jobs start only if every control passes.
set -u
S=/home/parallels/claude-second-bg-20261114T055250Z
PY=/usr/bin/python3.14
cd "$S" || exit 2
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$S/production.log"; }
log "PRODUCTION BEGIN"
if ! sha256sum -c --strict --quiet FROZEN_STAGE.sha256 >> "$S/production.log" 2>&1; then
  log "STAGE_DOES_NOT_MATCH_FREEZE; nothing launched"
  exit 5
fi
log "STAGE_MATCHES_FREEZE"
$PY -I -B src/build_jobs.py "$S" "$S/FAMILY_BOXES.json" || { log "BUILD_FAILED"; exit 3; }
$PY -I -B src/run_jobs.py "$S/jobs_controls.json" "$S/runner_controls.log" || { log "CONTROL_RUNNER_FAILED"; exit 6; }
$PY -I -B src/check_family.py controls "$S" "$S/archived_refs" "$S/CONTROLS_VERDICT.json" > "$S/controls_check.stdout" 2>&1
code=$?
log "CONTROLS_CHECK exit=$code"
if [ $code -ne 0 ]; then
  log "CONTROL_FAILURE_NO_FAMILY_VERDICT; family jobs not launched"
  exit 4
fi
$PY -I -B src/run_jobs.py "$S/jobs_family.json" "$S/runner_family.log" || log "FAMILY_RUNNER_FAILED"
mkdir -p "$S/check"
$PY -I -B src/check_family.py family "$S" "$S/archived_refs" "$S/FAMILY_BOXES.json" "$S/check" > "$S/check/stdout.json" 2> "$S/check/stderr.txt"
log "FAMILY_CHECK exit=$?"
log "PRODUCTION END"
