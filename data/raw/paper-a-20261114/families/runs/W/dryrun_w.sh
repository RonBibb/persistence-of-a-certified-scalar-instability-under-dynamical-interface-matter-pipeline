#!/bin/bash
# PLAN_W section 5b pre-freeze dry run (never part of production).  Runs only
# after V/L production has ended.  Real jobs: C2w and C3w (5 jobs).  Zero
# compute: the full W job-list build (expect 360 jobs, W_02 first), a 2x2
# synthetic family checked in 2-D family mode (cells (0,0), (1,0), (0,1)
# symlinked to the C2w jobs, cell (1,1) skipped at the cutoff; expect
# FAMILY_CERTIFIED_CELL_COMPONENT with 3 cells, all edge and diagonal contacts
# passing, (1,1) NOT_RUN), and bash -n of the W production script.
set -u
S=/home/parallels/claude-second-bg-20261114T055250Z
W=$S/W
D=$W/W_dryrun
PY=/usr/bin/python3.14
grep -q "PRODUCTION END" "$S/production.log" || { echo "V/L production has not ended"; exit 9; }
test -e "$D" && { echo "W_dryrun exists"; exit 1; }
mkdir -p "$D" && cp -r "$W/archived_src" "$W/archived_refs" "$W/src" "$D/" || exit 2
cd "$D" || exit 2
$PY -I -B -c "
import json, hashlib, os
src = {n: hashlib.sha256(open(os.path.join('src', n), 'rb').read()).hexdigest() for n in os.listdir('src') if n.endswith('.py')}
json.dump(src, open('FROZEN_SOURCES.json', 'w'), indent=2, sort_keys=True)
"
$PY -I -B src/build_jobs_w.py "$D" "$W/FAMILY_BOXES_W.json" || exit 3
$PY -I -B -c "
import json
f = json.load(open('jobs_family_w.json')); c = json.load(open('jobs_controls_w.json'))
print('W family jobs', len(f), 'unique', len({j['name'] for j in f}), 'first', [j['name'] for j in f[:3]], 'W control jobs', len(c))
"
rm -rf "$D/jobs"/bgp_W_* "$D/jobs"/bgi_W_* "$D/jobs"/ph_W_* "$D/jobs_family_w.json"
$PY -I -B src/run_jobs.py "$D/jobs_controls_w.json" "$D/runner.log" || exit 4
$PY -I -B src/check_family_w.py controls "$D" "$D/archived_refs" "$W/VL_CONTROLS_VERDICT.json" "$D/CONTROLS_VERDICT_W_dryrun.json"
echo "W controls exit=$?"
for cell in 00 01 02; do
  for k in bgp bgi; do ln -sfn "$D/jobs/c2w_$k" "$D/jobs/${k}_W_$cell"; done
  ln -sfn "$D/jobs/c2w_phase" "$D/jobs/ph_W_$cell"
done
$PY -I -B -c "
import json, os, sys
sys.path.insert(0, 'src')
import build_jobs as bj
job = json.load(open('jobs/c2w_bgp/job.json'))
for made in (bj.background_primary('.', 'bgp_W_03', job), bj.background_independent('.', 'bgi_W_03', job),
             bj.phase('.', 'ph_W_03', 'bgp_W_03')):
    json.dump({'job': made['name'], 'status': 'SKIPPED', 'reason': 'LAUNCH_CUTOFF_REACHED'}, open(os.path.join(made['dir'], 'exec.json'), 'w'))
cells = [dict(job, j=2 * k + i, i=i, k=k) for k in (0, 1) for i in (0, 1)]
boxes = {'families': {'W': {'params': ['v1', 'lambda_b'], 'box': {}, 'shape': [2, 2], 'anchor_cell': [0, 0], 'subboxes': cells}}}
json.dump(boxes, open('BOXES_W_SYN.json', 'w'), indent=1)
"
mkdir -p check_syn
$PY -I -B src/check_family_w.py family "$D" "$D/archived_refs" "$D/BOXES_W_SYN.json" "$D/check_syn" > check_syn/stdout.json 2> check_syn/stderr.txt
echo "W synthetic family exit=$?"
$PY -I -B -c "
import json; f = json.load(open('check_syn/FAMILY_VERDICT_W.json'))['families']['W']
print(f['classification'], f['component_containing_anchor'], 'contacts checked', f['contacts_checked_inside_component'],
      'untied', f['untied_contacts_inside_component'], 'branch', f['branch_continuous_on_component'], f['verdict_counts'], f['not_certified_cells'])
"
bash -n "$W/src/run_production_w.sh" && echo "run_production_w.sh syntax ok"
