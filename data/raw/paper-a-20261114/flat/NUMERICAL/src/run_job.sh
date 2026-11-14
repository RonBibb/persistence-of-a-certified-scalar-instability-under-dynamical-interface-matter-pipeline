#!/bin/bash
# Usage: run_job.sh JOB_NAME CASE_ID [--dry]
# Runs flatcount.py in this stage directory and writes an exec record.
set -u
NAME="$1"; CASE="$2"; shift 2
STAGE="$(cd "$(dirname "$0")" && pwd)"
cd "$STAGE" || exit 90
mkdir -p jobs
SRC=flatcount.py
SHA=$(sha256sum "$SRC" | cut -d' ' -f1)
echo "$SHA  $SRC" > "jobs/$NAME.source_sha256.txt"
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
S0=$(date +%s.%N)
/usr/bin/python3.14 -I "$SRC" "$CASE" "jobs/$NAME.json" "$@" > "jobs/$NAME.stdout.txt" 2> "jobs/$NAME.stderr.txt"
EC=$?
S1=$(date +%s.%N)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EL=$(awk -v a="$S0" -v b="$S1" 'BEGIN{printf "%.3f", b-a}')
cat > "jobs/$NAME.exec.json" <<EOF
{"job": "$NAME", "case": "$CASE", "extra_args": "$*", "source": "$SRC", "source_sha256": "$SHA",
 "interpreter": "/usr/bin/python3.14 -I", "host": "$(hostname)", "stage": "$STAGE",
 "start_utc": "$START", "end_utc": "$END", "exit_code": $EC, "elapsed_s": $EL,
 "label": "FLOAT EXPLORATORY"}
EOF
exit $EC
