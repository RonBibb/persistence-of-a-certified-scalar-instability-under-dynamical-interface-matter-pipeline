#!/usr/bin/env bash
# Campaign driver for run 20261007T030034Z (line 02_lin_static), run on Linux from the Research root after the freeze.
# Every job goes through ClaudeCode/runtime/slot_run.sh with LINE=02_lin_static. The driver waits only with
# `wait <pid>` on the recorded PIDs of its own children; it never matches process names or command lines.
# Production jobs (phases, materials) carry no COMPLETION_OF; assembly and verification declare COMPLETION_OF.
# The material jobs start only after all four phase jobs exit 0; a nonzero exit (4 = CONTROL_FAILED, anything
# else = failure) means no material job is launched.
set -u
cd /media/psf/Home/Research || exit 2
R=ClaudeCode/lines/02_lin_static/runs/20261007T030034Z
PY=/home/parallels/codex-precision-noble-py312-20260830/bin/python
FLINT=/home/parallels/research-runs/cap-interval-arb-2026-09-12
LAST=0

note() {
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$R/logs/campaign.log"
}

launch() {
    local name=$1 completion=$2
    shift 2
    if [ "$completion" = yes ]; then
        COMPLETION_OF="$R" LINE=02_lin_static nohup ClaudeCode/runtime/slot_run.sh env PYTHONPATH="$FLINT" PYTHONDONTWRITEBYTECODE=1 \
            PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
            "$PY" -B "$@" > "$R/logs/$name.log" 2>&1 &
    else
        LINE=02_lin_static nohup ClaudeCode/runtime/slot_run.sh env PYTHONPATH="$FLINT" PYTHONDONTWRITEBYTECODE=1 \
            PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
            "$PY" -B "$@" > "$R/logs/$name.log" 2>&1 &
    fi
    LAST=$!
    echo "$LAST" > "$R/logs/$name.pid"
    note "launched $name pid $LAST"
}

finish() {
    local name=$1 pid=$2 code
    wait "$pid"
    code=$?
    echo "$code" > "$R/logs/$name.exit"
    note "finished $name pid $pid exit $code"
    return "$code"
}

LATEST=1791354000   # 2026-10-07T06:20:00Z: latest campaign start; later, the run is FROZEN_NOT_LAUNCHED
if [ "$(date -u +%s)" -ge "$LATEST" ]; then
    echo "{\"status\": \"FROZEN_NOT_LAUNCHED\", \"utc\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"latest_campaign_start_utc\": \"2026-10-07T06:20:00Z\"}" > "$R/FROZEN_NOT_LAUNCHED.json"
    note "not launched: past the latest campaign start 2026-10-07T06:20:00Z"
    exit 3
fi
note "campaign start pid $$"
launch phase-positive-center no "$R/code/reprep.py" phase positive center; PC=$LAST
launch phase-positive-box no "$R/code/reprep.py" phase positive box; PB=$LAST
launch phase-negative-center no "$R/code/reprep.py" phase negative center; NC=$LAST
launch phase-negative-box no "$R/code/reprep.py" phase negative box; NB=$LAST
ok=1
finish phase-positive-center "$PC" || ok=0
finish phase-positive-box "$PB" || ok=0
finish phase-negative-center "$NC" || ok=0
finish phase-negative-box "$NB" || ok=0
if [ "$ok" = 1 ]; then
    launch material-positive no "$R/code/reprep.py" material positive; MP=$LAST
    launch material-negative no "$R/code/reprep.py" material negative; MN=$LAST
    finish material-positive "$MP"
    finish material-negative "$MN"
else
    note "material stage not launched: a phase job did not complete (exit codes in logs/phase-*.exit)"
fi
launch assemble yes "$R/code/assemble4.py" run; AS=$LAST
finish assemble "$AS"
launch verify-positive yes "$R/code/verify4.py" case positive; VP=$LAST
launch verify-negative yes "$R/code/verify4.py" case negative; VN=$LAST
finish verify-positive "$VP"
finish verify-negative "$VN"
launch verify-final yes "$R/code/verify4.py" final; VF=$LAST
finish verify-final "$VF"
note "campaign end"
