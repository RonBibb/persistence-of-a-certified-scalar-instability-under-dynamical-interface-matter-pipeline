"""E01: one frozen 64-to-128 comparison intervention, Linux-only, two signs."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
import traceback
from array import array
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUND = ROOT.parents[1]
CFG = json.loads((ROOT/'CONTRACT.json').read_text())
PARENT = Path('/media/psf/Home/Research')/CFG['parent_relative']
assert hashlib.sha256((PARENT/'run.py').read_bytes()).hexdigest() == CFG['parent_runner_sha256']
spec = importlib.util.spec_from_file_location('n01_bound_parent', PARENT/'run.py')
n01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n01)
rp, c4, rec = n01.rp, n01.c4, n01.rec
from flint import ctx

PRE, OUT = ROOT/'preflight', ROOT/'output'
STATUS = ROUND/'status/row_01.json'
FIELDS, COLS = n01.FIELDS, n01.COLS
need, put = n01.need, n01.put
TOTAL, CADENCE = CFG['total_cells'], CFG['checkpoint_cells']
GUARD = None
CHILDREN = {}
NUMERICAL_SECONDS = 0.0
ACTIVE_SERIAL = None
LINUX_STARTED = None


def identity(pid=None):
    pid = os.getpid() if pid is None else pid
    p = Path('/proc')/str(pid)
    return {'pid': pid, 'proc_start_ticks': (p/'stat').read_text().split()[21],
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'cpu_affinity': sorted(os.sched_getaffinity(pid))}


def rss(pid):
    try:
        return int((Path('/proc')/str(pid)/'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
    except (FileNotFoundError, ProcessLookupError):
        return 0


def comparison(st, sign, subcells):
    # Sole numerical change; the parent source and all other settings stay frozen.
    original = n01.CONTRACT
    n01.CONTRACT = dict(original, subcells=subcells)
    try:
        return n01.comparison_cell(st, sign)
    finally:
        n01.CONTRACT = original


def physical_equal(st, sign):
    p = n01.cp_path(PARENT/f'output/{sign}_material', st['cell_index'])
    expected = n01.loadcp(p)
    return n01.source_keys(st) == n01.source_keys(expected), p


def report(phase, **kw):
    active = [v['p'].pid for v in CHILDREN.values() if v['p'].poll() is None]
    obj = {'round_id': CFG['round_id'], 'row': 1, 'phase': phase, 'updated_utc': rec.now(),
           'experiment_running': bool(active) or phase in ('PREFLIGHT', 'INTEGRITY_CHECK'),
           'controller': identity(), 'owned_pids': active, 'guard': GUARD,
           'allocated_cores': 2, 'allocated_cpu_ids': [3, 4], 'peak_memory_gib_limit': 4,
           'run_path': str(ROOT), 'terminal_outcome': None,
           'cumulative_occupied_numerical_seconds': spent()}
    obj.update(kw)
    rec.atomic(STATUS, obj)


def spent():
    total = NUMERICAL_SECONDS
    if ACTIVE_SERIAL is not None:
        total += time.monotonic()-ACTIVE_SERIAL
    for item in CHILDREN.values():
        if not item.get('accounted'):
            total += (item.get('finished_at') or time.monotonic())-item['started']
    return total


def cap_check():
    need(spent() < CFG['cumulative_occupied_numerical_core_seconds_max'], 'Cumulative 90 core-minute cap')
    need(time.time()-LINUX_STARTED < CFG['linux_wall_seconds_max'], '90-minute Linux wall cap')
    need(time.time()-CFG['release_epoch'] < CFG['total_work_seconds_max'], '120-minute total work cap')
    current_rss = rss(os.getpid()) + sum(rss(v['p'].pid) for v in CHILDREN.values() if v['p'].poll() is None)
    need(current_rss <= CFG['aggregate_rss_bytes'], 'Aggregate 4 GiB RSS cap')
    return current_rss


def usage(active):
    rec.atomic(ROOT/'COMPUTE_USAGE.json', {'occupied_seconds': spent(), 'active': active,
        'updated_epoch': time.time(), 'linux_started_epoch': LINUX_STARTED,
        'unclosed_numeric_slots': 2 if CHILDREN else 1,
        'controller': identity()})


def authenticate():
    proposal = rec.read(ROUND/'authorized/row_01_proposal.json')
    approval = rec.read(ROUND/'authorized/row_01_gate_review.json')
    need(proposal['proposal_id'] == CFG['proposal_id'], 'Wrong proposal')
    need(approval['decision'] == 'APPROVED_SINGLE_TEST' and approval['gates_unchanged']
         and approval['physical_scope_unchanged'], 'Approval mismatch')
    need(approval['allocation'] == {'cpu_ids': [3, 4], 'cores': 2, 'peak_memory_gib': 4}, 'Allocation mismatch')
    need(rec.sha(PARENT/'RESULT.json') == CFG['parent_result_sha256'], 'Parent result changed')
    need(rec.sha(PARENT/'HANDOFF.json') == CFG['parent_handoff_sha256'], 'Parent handoff changed')
    parent_guard = n01.guardcheck()
    terminal = rec.read(PARENT/'TERMINAL.json')
    need(terminal['guard'] == parent_guard and terminal['integrity_passed'], 'Parent not certified')
    need(terminal['result_sha256'] == rec.sha(PARENT/'RESULT.json') and
         terminal['integrity_sha256'] == rec.sha(PARENT/'RESULT_INTEGRITY.json'), 'Parent terminal binding')
    inherited = rec.read(PARENT/'BINDINGS.json')
    paths = set(inherited['sources']) | set(inherited['inputs'])
    paths.update(str(PARENT/n) for n in ('RESULT.json','RESULT_INTEGRITY.json','TERMINAL.json',
        'HANDOFF.json','HANDOFF_SEAL.json','BINDINGS.json','FREEZE.json','CONTRACT.json','run.py',
        'preflight/RESULT.json','preflight/JACOBIAN_DOMAIN.json'))
    for sign in CFG['cases']:
        paths.add(str(PARENT/f'output/ROOT_{sign}.json'))
        paths.update(str(p) for p in (PARENT/f'output/{sign}_material').rglob('*') if p.is_file())
    paths.update(str(ROUND/'authorized'/n) for n in ('row_01_proposal.json','row_01_gate_review.json'))
    paths.add('/media/psf/Home/Research/ClaudeCode/config/linux.json')
    capacity = c4.capacity()
    need(capacity['available_bytes'] >= 4*1024**3, 'Insufficient available RAM for allocation')
    need(n01.CONTRACT['subcells'] == 64 and n01.CONTRACT['bits'] == CFG['bits'] and
         n01.CONTRACT['step'] == CFG['step'] and n01.TOTAL == TOTAL, 'Inherited numerical contract mismatch')
    data = {'utc': rec.now(), 'contract': CFG, 'parent_guard': parent_guard,
        'runtime': c4.runtime_fingerprint(), 'capacity': capacity,
        'sources': {str(ROOT/n): rec.sha(ROOT/n) for n in ('run.py','CONTRACT.json')},
        'inputs': {p: rec.sha(p) for p in sorted(paths)}}
    put(ROOT/'BINDINGS.json', data)
    return rec.sha(ROOT/'BINDINGS.json')


def guard_check(full=True):
    b = rec.read(ROOT/'BINDINGS.json')
    f = rec.read(ROOT/'FREEZE.json')
    need(b['contract'] == CFG and f['bindings_sha256'] == rec.sha(ROOT/'BINDINGS.json'), 'Binding drift')
    need(f['preflight_sha256'] == rec.sha(PRE/'RESULT.json') and rec.read(PRE/'RESULT.json')['passed'], 'Preflight drift')
    files = b['sources'] | (b['inputs'] if full else {})
    for p, digest in files.items():
        need(rec.sha(p) == digest, 'Changed bound bytes '+p)
    need(b['runtime'] == c4.runtime_fingerprint(), 'Runtime drift')
    return rec.sha(ROOT/'FREEZE.json')


def preflight(binding):
    report('PREFLIGHT', stage='one accepted old block and fresh-process restart')
    st = n01.new_stats(n01.loadcp(n01.cp_path(PARENT/'output/positive_material', 16128)))
    rows = []
    while st['cell_index'] < TOTAL:
        cap_check()
        rows.extend(comparison(st, 'positive', 64))
    a = array('d', rows)
    if sys.byteorder != 'little': a.byteswap()
    same, _ = physical_equal(st, 'positive')
    controls = {'accepted_physical_endpoint_bitwise': same,
        'all_18_columns_bitwise': a.tobytes() == (PARENT/'output/positive_material/blocks/016128-016365.f64').read_bytes(),
        'coverage_and_closure': st['covered'] == str(n01.D2) and st['coverage_gaps'] == st['closure_failures'] == 0}
    trial = n01.new_stats(n01.loadcp(n01.cp_path(PARENT/'output/positive_material', 16128)))
    comparison(trial, 'positive', 64)
    rec.save(PRE/'restart', trial, binding)
    pointer = rec.read(PRE/'restart/LATEST.json')
    put(PRE/'restart/checkpoints/incomplete.uncommitted.json', {'incomplete': True})
    controls['partial_cannot_replace_pointer'] = rec.read(PRE/'restart/LATEST.json') == pointer
    try:
        rec.load(PRE/'restart', binding+'-invalid')
        controls['changed_guard_rejected'] = False
    except AssertionError:
        controls['changed_guard_rejected'] = True
    subprocess.run([sys.executable, '-B', str(ROOT/'run.py'), 'restart-control', '--guard', binding],
                   check=True, timeout=120)
    direct = rec.load(PRE/'restart', binding)
    row = comparison(direct, 'positive', 64)
    controls['fresh_process_full_state_exact'] = rec.pack({'state': direct, 'row': row}) == rec.read(PRE/'restart_child.json')
    result = {'utc': rec.now(), 'controls': controls, 'passed': all(controls.values()),
              'baseline': str(PARENT), 'subcells': 64, 'replayed_cells': [16128, TOTAL],
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    put(PRE/'RESULT.json', result)
    need(result['passed'], 'Preflight controls failed')
    put(ROOT/'FREEZE.json', {'utc': rec.now(), 'bindings_sha256': binding,
                            'preflight_sha256': rec.sha(PRE/'RESULT.json')})
    for name in ('CONTRACT.json','run.py'): (ROOT/name).chmod(0o444)


def initial(sign):
    # Pure parent constructor; its ROOT hash points to the bound inherited root.
    return n01.start_material(sign, n01.new_context(),
        rec.unpack(rec.read(PARENT/f'output/ROOT_{sign}.json')))


def worker(sign):
    global GUARD
    os.sched_setaffinity(0, {CFG['cpu_ids'][sign]})
    resource.setrlimit(resource.RLIMIT_AS, (CFG['worker_address_space_bytes'], CFG['worker_address_space_bytes']))
    GUARD = guard_check(False)
    folder = OUT/sign
    folder.mkdir(parents=True, exist_ok=True)
    lock = open(folder/'WORKER.lock', 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    need(not (folder/'FAILURE.json').exists(), 'Failed-closed sign cannot restart')
    if (folder/'RESULT.json').exists(): return
    began = time.monotonic()
    old_usage = rec.read(folder/'USAGE.json') if (folder/'USAGE.json').exists() else {'elapsed': 0, 'active': False}
    carry = old_usage['elapsed']
    if old_usage['active']: carry += max(0, time.time()-old_usage['updated_epoch'])
    st = rec.load(folder, GUARD) if (folder/'LATEST.json').exists() else initial(sign)
    need(st['root_sha256'] == rec.sha(PARENT/f'output/ROOT_{sign}.json'), 'Root drift')
    who = identity()
    try:
        while st['cell_index'] < TOTAL:
            start = st['cell_index']; end = min(TOTAL, ((start//CADENCE)+1)*CADENCE)
            rows = []
            while st['cell_index'] < end:
                need(carry+time.monotonic()-began < CFG['worker_active_seconds_max'], '45-minute signed-worker cap')
                rows.extend(comparison(st, sign, CFG['subcells']))
            same, parent_checkpoint = physical_equal(st, sign)
            need(same, 'Physical checkpoint changed at '+str(end))
            need(st['coverage_gaps'] == st['closure_failures'] == 0 and
                 st['max_picard'] <= CFG['strict_picard_iterations_max'], 'Coverage/Picard/budget failure')
            blocks = folder/'blocks'; blocks.mkdir(exist_ok=True)
            arr = blocks/f'{start:06d}-{end:06d}.f64'
            n01.block_bytes(arr, rows)
            block = {'guard': GUARD, 'sign': sign, 'subcells_per_cell': CFG['subcells'],
                'start_cell': start, 'end_cell': end, 'previous': st['last_block'],
                'covered': st['covered'], 'coverage_gaps': 0, 'closure_failures': 0,
                'max_picard': st['max_picard'], 'best': st['best'], 'component_max': st['component_max'],
                'array': arr.name, 'array_sha256': rec.sha(arr), 'count_values': len(rows),
                'physical_checkpoint_identical': same, 'parent_checkpoint': str(parent_checkpoint),
                'parent_checkpoint_sha256': rec.sha(parent_checkpoint)}
            bp = blocks/f'{start:06d}-{end:06d}.json'; put(bp, block)
            st['completed_blocks'] += 1
            st['last_block'] = {'path': str(bp.relative_to(folder)), 'sha256': rec.sha(bp)}
            st['elapsed_seconds'] = carry+time.monotonic()-began
            rec.save(folder, st, GUARD)
            # The canonical saved state, not just an in-memory comparison, must match.
            need(physical_equal(st, sign)[0], 'Canonical physical checkpoint changed')
            rec.atomic(folder/'USAGE.json', {'elapsed': st['elapsed_seconds'], 'active': True, 'updated_epoch': time.time()})
            rec.atomic(folder/'PROGRESS.json', {'phase': 'RUNNING', 'utc': rec.now(), 'guard': GUARD,
                'sign': sign, 'cells': end, 'total': TOTAL, 'identity': who,
                'elapsed_seconds': st['elapsed_seconds'], 'checkpoint': rec.read(folder/'LATEST.json'),
                'rss_bytes': rss(os.getpid()), 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'physical_checkpoints_bitwise': st['completed_blocks']})
            if end % 2048 == 0 or end == TOTAL:
                print(json.dumps({'sign': sign, 'cells': end, 'seconds': st['elapsed_seconds']}), flush=True)
        baseline = rec.read(PARENT/f'output/{sign}_material/RESULT.json')
        fields = {}
        for field in FIELDS:
            best = st['best'][field]; row = best['row']; E = rp.fq(row['E'])
            old = baseline['fields'][field]
            oldE = Q(old['bound_exact']); ratio = E/oldE
            shares = {'CENTER_DISCREPANCY': row['center'], 'STATE_RADIUS': row['state'],
                'COMPARISON_STEP': row['source_step']+row['native_step'], 'EVENT_WIDTH': row['event']}
            fields[field] = {'bound_exact': str(E), 'bound_approximate': float(E),
                'baseline_exact': str(oldE), 'ratio_exact': str(ratio), 'ratio_approximate': float(ratio),
                'primary_usefulness_pass': ratio <= Q(CFG['usefulness_ratio_max']) if field in CFG['primary_fields'] else None,
                'argmax': best, 'baseline_argmax': old['argmax'], 'component_max': st['component_max'][field],
                'shares': {k: float(rp.fq(v)/E) for k,v in shares.items()}}
        put(folder/'RESULT.json', {'guard': GUARD, 'sign': sign, 'fields': fields, 'cells': TOTAL,
            'subcells': TOTAL*CFG['subcells'], 'covered': st['covered'], 'coverage_start': st['coverage_start'],
            'coverage_gaps': st['coverage_gaps'], 'closure_failures': st['closure_failures'],
            'max_picard': st['max_picard'], 'checkpoint': rec.read(folder/'LATEST.json'),
            'last_block': st['last_block'], 'completed_blocks': st['completed_blocks'],
            'worker_identity': who, 'active_seconds': carry+time.monotonic()-began,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        rec.atomic(folder/'PROGRESS.json', {'phase': 'COMPLETE_PENDING_FINAL_INTEGRITY', 'utc': rec.now(),
            'cells': TOTAL, 'total': TOTAL, 'guard': GUARD, 'sign': sign, 'identity': who})
    except KeyboardInterrupt:
        rec.atomic(folder/'PROGRESS.json', {'phase': 'STOPPED_RECOVERABLE', 'utc': rec.now(),
            'guard': GUARD, 'sign': sign, 'identity': who, 'last_checkpoint': rec.read(folder/'LATEST.json') if (folder/'LATEST.json').exists() else None})
        raise
    except Exception as err:
        put(folder/'FAILURE.json', {'utc': rec.now(), 'guard': GUARD, 'error': str(err), 'traceback': traceback.format_exc()})
        raise
    finally:
        rec.atomic(folder/'USAGE.json', {'elapsed': carry+time.monotonic()-began, 'active': False, 'updated_epoch': time.time()})


def integrity():
    checks = {'bound_sources_inputs_runtime': guard_check(True) == GUARD}
    material = {}
    for sign in CFG['cases']:
        folder = OUT/sign
        final = rec.unpack(rec.read(folder/'RESULT.json')); material[sign] = final
        previous = None; end = 0; count = 0; maxima = [-math.inf]*18; chain = True
        physical = True
        for path in sorted((folder/'blocks').glob('*.json')):
            b = rec.unpack(rec.read(path)); n = b['end_cell']-b['start_cell']
            arr = path.parent/b['array']; vals = array('d'); vals.frombytes(arr.read_bytes())
            if sys.byteorder != 'little': vals.byteswap()
            chain = chain and b['guard'] == GUARD and b['start_cell'] == end and b['previous'] == previous
            chain = chain and n > 0 and b['end_cell'] == min(TOTAL, b['start_cell']+CADENCE)
            chain = chain and b['subcells_per_cell'] == 128 and len(vals) == n*18 == b['count_values']
            chain = chain and rec.sha(arr) == b['array_sha256'] and all(math.isfinite(v) for v in vals)
            chain = chain and b['covered'] == str(min(b['end_cell']*n01.H, n01.D2))
            chain = chain and b['coverage_gaps'] == b['closure_failures'] == 0 and b['max_picard'] <= 32
            for j in range(18): maxima[j] = max(maxima[j], max(vals[j::18]))
            chain = chain and all(n01.exact_peak_check(b['best'][f]) for f in FIELDS)
            cp = n01.cp_path(folder, b['end_cell']); saved = n01.loadcp(cp)
            physical = physical and physical_equal(saved, sign)[0] and b['physical_checkpoint_identical']
            physical = physical and rec.sha(b['parent_checkpoint']) == b['parent_checkpoint_sha256']
            physical = physical and rec.read(cp)['guard'] == GUARD
            previous = {'path': str(path.relative_to(folder)), 'sha256': rec.sha(path)}
            end = b['end_cell']; count += 1
        checks[sign+'_physical_checkpoints_bitwise'] = physical and count == math.ceil(TOTAL/CADENCE)
        checks[sign+'_full_block_chain_coverage'] = chain and end == TOTAL and count == final['completed_blocks'] and previous == final['last_block']
        checks[sign+'_full_domain'] = (final['covered'] == str(n01.D2) and final['coverage_start'] == '0' and
            final['subcells'] == 2094720 and final['coverage_gaps'] == final['closure_failures'] == 0)
        ptr = final['checkpoint']; cp = rec.read(folder/ptr['path'])
        checks[sign+'_terminal_checkpoint'] = rec.fingerprint(cp) == ptr['digest'] and cp['guard'] == GUARD
        baseline = rec.read(PARENT/f'output/{sign}_material/RESULT.json')
        for j, field in enumerate(FIELDS):
            f = final['fields'][field]; E = Q(f['bound_exact']); old = Q(baseline['fields'][field]['bound_exact'])
            checks[sign+'_'+field+'_exact_bound_ratio_budget'] = (n01.exact_peak_check(f['argmax']) and
                E == n01.exactq(f['argmax']['row']['E']) and c4.up_float(E) == maxima[j*6] and
                Q(f['baseline_exact']) == old and Q(f['ratio_exact']) == E/old)
            checks[sign+'_'+field+'_component_maxima'] = all(c4.up_float(n01.exactq(f['component_max'][col])) == maxima[j*6+k] for k,col in enumerate(COLS))
    useful = all(material[s]['fields'][f]['primary_usefulness_pass'] for s in CFG['cases'] for f in CFG['primary_fields'])
    valid = all(checks.values())
    classification = ('COMPARISON_ONLY_REFINEMENT_USEFUL_BOTH_SIGNS' if useful else
        'VALID_COMPARISON_REFINEMENT__20_PERCENT_PAYOFF_NOT_MET') if valid else 'TECHNICAL_INCOMPLETE__RESULT_INTEGRITY_FAILED'
    result = {'utc': rec.now(), 'round_id': CFG['round_id'], 'row': 1, 'guard': GUARD,
        'classification': classification, 'material': material, 'gates': {
            'E01-G1': 'PASS' if valid else 'INCOMPLETE', 'E01-G2': 'PASS_BOTH_SIGNS' if valid else 'INCOMPLETE',
            'E01-G3': ('PASS' if useful else 'FAIL_OPERATIONAL_PAYOFF') if valid else 'INCONCLUSIVE'},
        'claim': 'A controlled change in numerical comparison enclosures with the accepted physical trajectory unchanged; not a physical error fraction, time evolution or horizon result.',
        'new_source_root_eigenvalue_jacobian_solves': 0, 'successor_launched': False,
        'historical_raw_gate_retained_failed': True, 'absolute_accuracy_ceiling': None}
    put(ROOT/'RESULT.json', result)
    put(ROOT/'RESULT_INTEGRITY.json', {'utc': rec.now(), 'guard': GUARD, 'checks': checks,
        'passed': valid, 'result_sha256': rec.sha(ROOT/'RESULT.json')})
    return result, valid


def stop_children():
    # Exact owned Popen handles only; never scan or signal other research jobs.
    for item in CHILDREN.values():
        if item['p'].poll() is None: item['p'].send_signal(signal.SIGINT)
    for item in CHILDREN.values():
        try: item['p'].wait(timeout=20)
        except subprocess.TimeoutExpired:
            item['p'].terminate()
            try: item['p'].wait(timeout=10)
            except subprocess.TimeoutExpired: item['p'].kill(); item['p'].wait()
        if 'finished_at' not in item: item['finished_at'] = time.monotonic()


def run(resume=False):
    global GUARD, NUMERICAL_SECONDS, ACTIVE_SERIAL, LINUX_STARTED
    os.sched_setaffinity(0, {CFG['controller_cpu']})
    lock = open(ROOT/'RUN.lock', 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    need(not (ROOT/'TERMINAL.json').exists() and not (ROOT/'FAILURE.json').exists(), 'Terminal/failed-closed job cannot restart')
    LINUX_STARTED = time.time()
    if (ROOT/'COMPUTE_USAGE.json').exists():
        need(resume, 'Existing usage requires explicit resume')
        old = rec.read(ROOT/'COMPUTE_USAGE.json')
        NUMERICAL_SECONDS = old['occupied_seconds']; LINUX_STARTED = old['linux_started_epoch']
        if old['active']: NUMERICAL_SECONDS += max(0, time.time()-old['updated_epoch'])*old['unclosed_numeric_slots']
    try:
        ACTIVE_SERIAL = time.monotonic(); usage(True)
        if not resume:
            binding = authenticate(); preflight(binding)
        GUARD = guard_check(full=resume)
        NUMERICAL_SECONDS += time.monotonic()-ACTIVE_SERIAL; ACTIVE_SERIAL = None
        cap_check()
        for sign in CFG['cases']:
            folder = OUT/sign
            if (folder/'RESULT.json').exists(): continue
            folder.mkdir(parents=True, exist_ok=True)
            log = open(folder/'run.log', 'a')
            began = time.monotonic()
            process = subprocess.Popen([sys.executable, '-B', str(ROOT/'run.py'), 'worker', '--sign', sign],
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            CHILDREN[sign] = {'p': process, 'started': began, 'log': log}
        while any(v['p'].poll() is None for v in CHILDREN.values()):
            for sign, item in CHILDREN.items():
                rc = item['p'].poll()
                if rc is not None:
                    item.setdefault('finished_at', time.monotonic())
                    need(rc == 0, 'Signed worker failed: '+sign)
            memory = cap_check(); usage(True)
            progress = {s: rec.read(OUT/s/'PROGRESS.json') for s in CFG['cases'] if (OUT/s/'PROGRESS.json').exists()}
            report('RUNNING', signed_progress=progress, aggregate_rss_bytes=memory)
            time.sleep(5)
        for sign, item in CHILDREN.items():
            need(item['p'].wait() == 0, 'Signed worker failed: '+sign)
            item.setdefault('finished_at', time.monotonic())
            NUMERICAL_SECONDS += item['finished_at']-item['started']; item['accounted'] = True
            item['log'].close()
        need(all(v['p'].poll() is not None for v in CHILDREN.values()), 'Owned workers remain live')
        ACTIVE_SERIAL = time.monotonic(); report('INTEGRITY_CHECK'); cap_check()
        result, valid = integrity()
        NUMERICAL_SECONDS += time.monotonic()-ACTIVE_SERIAL; ACTIVE_SERIAL = None
        cap_check(); usage(False)
        put(ROOT/'TERMINAL.json', {'utc': rec.now(), 'classification': result['classification'], 'guard': GUARD,
            'result_sha256': rec.sha(ROOT/'RESULT.json'), 'integrity_sha256': rec.sha(ROOT/'RESULT_INTEGRITY.json'),
            'integrity_passed': valid, 'owned_numerical_processes_exited': True,
            'occupied_numerical_seconds': spent(), 'linux_wall_seconds': time.time()-LINUX_STARTED,
            'successor_launched': False})
        report('TERMINAL', terminal_outcome=result['classification'], gates=result['gates'],
               experiment_running=False, owned_pids=[], result_path=str(ROOT/'RESULT.json'))
        print(json.dumps({'terminal': result['classification'], 'integrity': valid, 'occupied_seconds': spent()}), flush=True)
    except KeyboardInterrupt:
        stop_children(); report('STOPPED_RECOVERABLE', experiment_running=False, owned_pids=[])
        raise
    except Exception as err:
        stop_children()
        put(ROOT/'FAILURE.json', {'utc': rec.now(), 'guard': GUARD, 'classification': 'TECHNICAL_INCOMPLETE',
            'error': str(err), 'traceback': traceback.format_exc(), 'physical_exclusion': False})
        report('FAILED_CLOSED', experiment_running=False, owned_pids=[], terminal_outcome='TECHNICAL_INCOMPLETE', error=str(err))
        raise
    finally:
        usage(False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run','resume','worker','restart-control'])
    parser.add_argument('--sign', choices=CFG['cases']); parser.add_argument('--guard')
    args = parser.parse_args()
    need(sys.platform == 'linux', 'Numerical work is Linux-only')
    c4.check_environment(); ctx.prec = CFG['bits']; ctx.threads = 1
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt('SIGTERM')))
    if args.command == 'restart-control':
        st = rec.load(PRE/'restart', args.guard); row = comparison(st, 'positive', 64)
        put(PRE/'restart_child.json', {'state': st, 'row': row})
    elif args.command == 'worker': worker(args.sign)
    else: run(args.command == 'resume')


if __name__ == '__main__': main()
