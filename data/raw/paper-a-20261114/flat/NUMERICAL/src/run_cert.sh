#!/bin/bash
# Usage: run_cert.sh JOB_NAME
# Runs certify_flat_background.py with the python-flint 0.9.0 runtime via PYTHONPATH
# (python -I would drop PYTHONPATH) and writes an exec record.
set -u
NAME="$1"
STAGE="$(cd "$(dirname "$0")" && pwd)"
cd "$STAGE" || exit 90
mkdir -p jobs
SRC=certify_flat_background.py
SHA=$(sha256sum "$SRC" | cut -d' ' -f1)
echo "$SHA  $SRC" > "jobs/$NAME.source_sha256.txt"
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
S0=$(date +%s.%N)
PYTHONPATH="$HOME/research-runtimes/protocol406-python-flint-0.9.0" /usr/bin/python3.14 -s "$SRC" > "jobs/$NAME.stdout.txt" 2> "jobs/$NAME.stderr.txt"
EC=$?
S1=$(date +%s.%N)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EL=$(awk -v a="$S0" -v b="$S1" 'BEGIN{printf "%.3f", b-a}')
cat > "jobs/$NAME.exec.json" <<EOF
{"job": "$NAME", "source": "$SRC", "source_sha256": "$SHA",
 "interpreter": "PYTHONPATH=~/research-runtimes/protocol406-python-flint-0.9.0 /usr/bin/python3.14 -s",
 "host": "$(hostname)", "stage": "$STAGE", "start_utc": "$START", "end_utc": "$END",
 "exit_code": $EC, "elapsed_s": $EL, "label": "OUTWARD ARB ARITHMETIC (python-flint 0.9.0); background predicates only"}
EOF
exit $EC
