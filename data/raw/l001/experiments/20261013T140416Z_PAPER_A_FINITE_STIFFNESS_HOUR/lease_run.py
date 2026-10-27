"""One worker, existing shared leases, no permission bypass, fixed hour cutoff."""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
assert sys.platform=='linux'
label,script,*args=sys.argv[1:]
assert label.replace('_','').isalnum()
script=(ROOT/script).resolve()
assert script.is_relative_to(ROOT) and script.is_file()
assert not (ROOT/f'EXECUTION_{label}.json').exists()
deadline=dt.datetime.fromisoformat(json.loads((ROOT/'AUTHORITY.json').read_text())['hard_deadline_utc'].replace('Z','+00:00'))
remaining=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()-300
assert remaining>30,'Insufficient time before audit/report reserve'
lockdir=Path('/tmp/research-20261012-astra-medium')
admission=(lockdir/'admission.lock').open('r+')
try: fcntl.flock(admission,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
    with (ROOT/f'RESOURCE_HOLD_{label}.json').open('x') as f: json.dump({'reason':'Admission lock busy'},f)
    raise SystemExit(75)
snapshot=subprocess.check_output(['ps','-eo','pid,pcpu,psr,comm,args'],text=True)
excluded,active,held,available=set(),[],[],[]
for line in snapshot.splitlines()[1:]:
    fields=line.split(None,4)
    if len(fields)!=5: continue
    pid,pct,cpu,comm,command=fields
    if int(pid)==os.getpid(): continue
    science=any(x in comm.lower() for x in ('python','julia','wolfram','math','solver','mpirun')) and not any(x in command for x in ('unattended-upgrade','update-manager','check-new-release'))
    if science or (float(pct)>20 and not command.startswith('[')):
        try: affinity=set(os.sched_getaffinity(int(pid)))
        except ProcessLookupError: continue
        excluded.update(affinity)
        active.append({'pid':int(pid),'affinity':sorted(affinity),'command':command})
for cpu in range(10):
    try: handle=(lockdir/f'cpu-{cpu}.lock').open('r+')
    except PermissionError: held.append(cpu); continue
    try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: held.append(cpu); handle.close(); continue
    if cpu in excluded: handle.close()
    else: available.append((cpu,handle))
mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
occupied=set(held)|excluded
ready=bool(available) and len(occupied|{available[0][0]})<=10 and mem>4*1024**2
record={'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'excluded':sorted(excluded),'held':held,'active':active,'memory_available_kib':mem,'process_snapshot':snapshot,'admitted':ready,'eligible_campaign_cpus':list(range(10))}
if not ready:
    for _,handle in available: handle.close()
    admission.close()
    with (ROOT/f'RESOURCE_HOLD_{label}.json').open('x') as f: json.dump(record,f,indent=2)
    print(json.dumps(record)); raise SystemExit(75)
cpu,lease=available[0]
for _,handle in available[1:]: handle.close()
admission.close()
os.sched_setaffinity(0,{cpu})
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
os.environ.update(PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONNOUSERSITE='1')
record.update(cpu=cpu,timeout_seconds=remaining)
with (ROOT/f'RESOURCE_{label}.json').open('x') as f: json.dump(record,f,indent=2)
started=time.monotonic()
with (ROOT/f'{label}.log').open('x') as log:
    child=subprocess.Popen([sys.executable,'-I','-B',str(script),*args],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    timed_out=False
    try: code=child.wait(timeout=remaining)
    except subprocess.TimeoutExpired:
        timed_out=True; os.killpg(child.pid,signal.SIGTERM)
        try: code=child.wait(timeout=3)
        except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); code=child.wait()
record.update(exit_code=code,timed_out=timed_out,wall_seconds=time.monotonic()-started)
lease.close()
with (ROOT/f'EXECUTION_{label}.json').open('x') as f: json.dump(record,f,indent=2)
print(json.dumps({k:record[k] for k in ('exit_code','timed_out','wall_seconds','cpu')}))
raise SystemExit(code)
