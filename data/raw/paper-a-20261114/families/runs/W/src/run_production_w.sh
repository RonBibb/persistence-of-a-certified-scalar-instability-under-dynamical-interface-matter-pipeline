#!/bin/bash
# Frozen family W sequence.  The W stage must match its freeze manifest; the V/L
# production controls must have passed; W controls run next; W cells start only
# if every W control passes.
set -u
S=/home/parallels/claude-second-bg-20261114T055250Z/W
VL="$S/VL_CONTROLS_VERDICT.json"
VL_LOG=/home/parallels/claude-second-bg-20261114T055250Z/production.log
PY=/usr/bin/python3.14
cd "$S" || exit 2
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$S/production_w.log"; }
log "W PRODUCTION BEGIN"
if ! grep -q "PRODUCTION END" "$VL_LOG"; then
  log "VL_PRODUCTION_NOT_ENDED; nothing launched"
  exit 7
fi
log "VL_PRODUCTION_ENDED"
if ! sha256sum -c --strict --quiet FROZEN_STAGE_W.sha256 >> "$S/production_w.log" 2>&1; then
  log "W_STAGE_DOES_NOT_MATCH_FREEZE; nothing launched"
  exit 5
fi
log "W_STAGE_MATCHES_FREEZE"
$PY -I -B src/build_jobs_w.py "$S" "$S/FAMILY_BOXES_W.json" || { log "BUILD_FAILED"; exit 3; }
$PY -I -B src/run_jobs.py "$S/jobs_controls_w.json" "$S/runner_controls_w.log" || { log "CONTROL_RUNNER_FAILED"; exit 6; }
$PY -I -B src/check_family_w.py controls "$S" "$S/archived_refs" "$VL" "$S/CONTROLS_VERDICT_W.json" > "$S/controls_check_w.stdout" 2>&1
code=$?
log "W_CONTROLS_CHECK exit=$code"
if [ $code -ne 0 ]; then
  log "CONTROL_FAILURE_NO_FAMILY_VERDICT; W cells not launched"
  exit 4
fi
$PY -I -B src/run_jobs.py "$S/jobs_family_w.json" "$S/runner_family_w.log" || log "FAMILY_RUNNER_FAILED"
mkdir -p "$S/check_w"
$PY -I -B src/check_family_w.py family "$S" "$S/archived_refs" "$S/FAMILY_BOXES_W.json" "$S/check_w" > "$S/check_w/stdout.json" 2> "$S/check_w/stderr.txt"
log "W_FAMILY_CHECK exit=$?"
log "W PRODUCTION END"
