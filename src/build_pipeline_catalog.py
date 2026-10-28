#!/usr/bin/env python3
"""Inventory frozen packets without importing or executing their producers.

Paths in outputs are relative to the public repository. Binding comparisons use
the frozen archive manifest; use verify_l001_archive.py to check actual bytes.
Static gate excerpts are navigation aids, not a complete semantic analysis.
"""
import argparse
import ast
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

sys.set_int_max_str_digits(0)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
root = args.repo.resolve()
out = args.output_dir.resolve()
archive = root / 'data/raw/l001/experiments'
manifest_path = root / 'data/processed/l001/ARCHIVE_MANIFEST.json'
manifest = json.loads(manifest_path.read_text())
identities = {'data/raw/l001/' + r['path']: r['sha256'] for r in manifest['files']}
by_digest = collections.defaultdict(list)
for path, digest in identities.items():
    by_digest[digest].append(path)

def rel(p):
    return p.relative_to(root).as_posix()

def load(p):
    return json.loads(p.read_text())

def small_value(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        s = str(v)
        return v if len(s) < 700 else s[:697] + '...'
    return None

def bools(d, prefix=''):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from bools(v, prefix + ('.' if prefix else '') + str(k))
    elif isinstance(d, list):
        # Array booleans in large cell records are not the terminal gate list.
        return
    elif isinstance(d, bool):
        yield prefix, d

def references(d, context=''):
    if isinstance(d, dict):
        path = next((d[k] for k in ['path', 'source', 'original', 'donor'] if isinstance(d.get(k), str)), None)
        digest = d.get('sha256')
        if path and isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest):
            yield context, path, digest
        for k, v in d.items():
            # Metadata fields such as executable_sha256 are not path locators.
            if isinstance(v, str) and re.fullmatch('[0-9a-f]{64}', v) and ('/' in str(k) or re.search(r'\.(py|json|txt|md|so|sh|gz)$', str(k), re.I)):
                yield context, str(k), v
            elif isinstance(v, (dict, list)):
                yield from references(v, context + '/' + str(k))
    elif isinstance(d, list):
        for v in d:
            if isinstance(v, dict):
                path = next((v[k] for k in ['path', 'source', 'original', 'donor'] if isinstance(v.get(k), str)), None)
                digest = v.get('sha256')
                if path and isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest):
                    yield context, path, digest
                else:
                    yield from references(v, context)

def resolve_path(path, digest):
    marker = '/experiments/'
    if marker in path:
        candidate = 'data/raw/l001/experiments/' + path.split(marker, 1)[1]
        if candidate in identities:
            return candidate, 'manifest_match' if identities[candidate] == digest else 'manifest_mismatch'
    if path.startswith('experiments/'):
        candidate = 'data/raw/l001/' + path
        if candidate in identities:
            return candidate, 'manifest_match' if identities[candidate] == digest else 'manifest_mismatch'
    candidates = by_digest.get(digest, [])
    if candidates:
        return candidates[0], 'identical_digest_copy'  # All alternatives retained below.
    return None, 'external_or_unmapped'

def purpose(p):
    for name in ['DERIVATION.txt', 'CONTRACT.md', 'RESULTS.md', 'README.md', 'RESULT_REPORT.md', 'FINDINGS.txt']:
        f = p / name
        if f.is_file():
            text = f.read_text(errors='replace')
            text = re.sub(r'(?m)^#+\s*', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:1000], rel(f)
    return 'No top-level purpose document found; inspect the listed source and child packets.', None

def gate_sources(p):
    rows, packets = [], set()
    for f in sorted(p.glob('*.py')):
        try:
            src = f.read_text(); tree = ast.parse(src)
        except (SyntaxError, UnicodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                rows.append({'file': rel(f), 'line': node.lineno, 'kind': 'assert', 'expression': (ast.get_source_segment(src, node) or '')[:1200]})
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', '')
                if name in ['need', 'check', 'require', 'ensure', 'gate']:
                    rows.append({'file': rel(f), 'line': node.lineno, 'kind': name, 'expression': (ast.get_source_segment(src, node) or '')[:1200]})
                if name in ['packet', 'parent', 'authenticate'] and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    if (archive / node.args[0].value).is_dir():
                        packets.add(node.args[0].value)
    return rows, sorted(packets)

dirs = sorted(p for p in archive.iterdir() if p.is_dir())
# Selected nested experiment contracts are separate tests, not independent reruns
# of copied inputs/review snapshots. Record this selection rule explicitly.
children = []
for top in dirs:
    for p in sorted(top.iterdir()):
        if not p.is_dir() or not (p.name.startswith('T') or top.name == 'academic2-event-horizon'):
            continue
        if any((p / n).is_file() for n in ['CONTRACT.md', 'TERMINAL.json', 'RESULT.json', 'RESULTS.json']):
            children.append(p)
rows = []
for p in dirs + children:
    desc, desc_file = purpose(p)
    gates, calls = gate_sources(p)
    bindings = []
    for name in ['BINDING.json', 'BINDINGS.json', 'INPUTS.json', 'SOURCE_BINDINGS.json']:
        f = p / name
        if not f.is_file():
            continue
        try:
            for context, historical, digest in references(load(f)):
                local, status = resolve_path(historical, digest)
                # Do not export historical personal paths a second time. Frozen
                # originals remain available in the bound packet itself.
                display = historical.split('/experiments/', 1)[-1] if '/experiments/' in historical else Path(historical).name
                bindings.append({'binding_file': rel(f), 'group': context, 'historical_locator_suffix': display,
                                 'sha256': digest, 'repo_path': local, 'resolution': status,
                                 'same_digest_locations': None})
        except (ValueError, TypeError):
            pass
    records = []
    for name in ['TERMINAL.json', 'RESULT.json', 'RESULTS.json', 'production_RESULT.json', 'FAILURE.json', 'STATUS.json', 'TRANSPORT_QUALIFICATION.json']:
        f = p / name
        if not f.is_file():
            continue
        try:
            d = load(f)
            if not isinstance(d, dict):
                continue
            records.append({'file': rel(f), 'sha256': identities.get(rel(f)),
                            'classification': {k: small_value(v) for k, v in d.items() if k in ['status', 'classification', 'scope', 'pass', 'pass_status', 'scientific_certificate', 'complete', 'seconds', 'iterations', 'new_ode_solves', 'ode_solves', 'new_radial_integrations']},
                            'saved_booleans': dict(bools(d))})
        except (ValueError, TypeError):
            pass
    dependency_packets = sorted({b['repo_path'].split('data/raw/l001/experiments/', 1)[1].split('/')[0]
                                 for b in bindings if b['repo_path'] and b['repo_path'].startswith('data/raw/l001/experiments/')}
                                - {p.relative_to(archive).parts[0]})
    rows.append({'id': p.relative_to(archive).as_posix(), 'folder': rel(p), 'purpose_excerpt': desc,
                 'purpose_source': desc_file, 'entry_sources': [rel(f) for f in sorted(p.glob('*.py'))],
                 'contract_documents': [rel(p/n) for n in ['CONTRACT.md', 'DERIVATION.txt', 'CHECK_PLAN.md', 'PINS.json', 'AUTHORITY.txt'] if (p/n).is_file()],
                 'saved_records': records, 'static_gate_excerpts': gates,
                 'bindings': bindings, 'bound_predecessor_packets': dependency_packets,
                 'literal_packet_calls': calls,
                 'output_files': [rel(f) for f in sorted(p.iterdir()) if f.is_file() and (f.suffix in ['.json', '.gz'] or f.name.endswith('.json.gz'))],
                 'scope': 'Documented packet; recorded status is not independent scientific acceptance. Static extraction is not a source-term audit.'})

lookup = {r['id']: r for r in rows}
seeds = ['20261027_ACTUAL_NINTH_FULL_BUDGET', '20261027_FINAL_FIXED_GRID_CERTIFICATE',
         '20261026_NEUTRAL_SOURCE_MAJORANT', '20261026_NEUTRAL_ANALYTIC_INVERSE',
         '20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE', '20261026_NEUTRAL_WALL_IDENTITY',
         '20261026_NEUTRAL_TWO_SIDED_DEPARTURE', '20261027_COMPONENT_SEED_CERTIFICATE']
closure = set()
def visit(name):
    if name in closure or name not in lookup:
        return
    closure.add(name)
    for parent in lookup[name]['bound_predecessor_packets']:
        visit(parent)
for seed in seeds:
    visit(seed)
for r in rows:
    r['bound_to_selected_route'] = r['id'] in closure
totals = collections.Counter(b['resolution'] for r in rows for b in r['bindings'])
# Flattened historical bindings repeat a large ancestor closure in every child.
# Normalize them once, rather than publishing hundreds of megabytes of copies.
artifacts = []
artifact_ids = {}
for r in rows:
    groups = collections.defaultdict(set)
    for b in r.pop('bindings'):
        artifact = {k: v for k, v in b.items() if k not in ['binding_file', 'group', 'same_digest_locations']}
        key = json.dumps(artifact, sort_keys=True)
        if key not in artifact_ids:
            artifact_ids[key] = len(artifacts)
            artifacts.append(artifact)
        groups[(b['binding_file'], b['group'])].add(artifact_ids[key])
    r['binding_groups'] = [{'file': f, 'group': g, 'artifact_ids': sorted(ids)} for (f, g), ids in sorted(groups.items())]
report = {'schema': 'paper-pipeline-catalog/v1', 'snapshot_date': '2026-10-27',
          'repository_base_commit': 'f135faa390af8cf7f497e96407a03cae052662e7',
          'archive_manifest': rel(manifest_path), 'archive_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'scope': 'All 210 top-level L001 experiment folders and eligible immediate child tests; selected analytical seeds plus their bound predecessor closure. Historical copies are not additional executions. Binding resolution compares frozen manifest identities, not actual file bytes.',
          'counts': {'top_level_packets': len(dirs), 'child_test_packets': len(children), 'catalog_entries': len(rows),
                     'selected_bound_top_level_closure': len(closure), 'static_gate_excerpts': sum(len(r['static_gate_excerpts']) for r in rows),
                     'binding_resolution': dict(totals)},
          'artifact_table': artifacts,
          'same_digest_locations': dict(by_digest),
          'selected_route_seeds': seeds, 'packets': rows}
out.mkdir(parents=True, exist_ok=True)
(out/'TEST_CATALOG.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
md = ['# Frozen test catalog', '', 'All paths are relative to the public pipeline repository. This generated catalog inventories records and source locations; it does not execute or certify their mathematics. The companion PDF supplies the interpreted claim-to-test route.', '',
      'The `bound_to_selected_route` marker is a transitive **binding-reference** closure, including provenance and controls. It is not a minimal execution schedule or a claim that every referenced record supplies a mathematical premise. Failed and superseded records are retained.', '',
      'The JSON companion includes every resolved input/hash, static gate expression and line number, saved boolean, entry source, output and dependency. Gate extraction is syntactic; data-dependent labels and unrecognized helper calls require reading the source.', '']
for r in rows:
    md += ['## '+r['id'], '', r['purpose_excerpt'], '', '**Folder:** `'+r['folder']+'`', '',
           '**Contracts:** '+(', '.join('`'+x+'`' for x in r['contract_documents']) or 'No top-level contract document found.'), '',
           '**Entry sources:** '+(', '.join('`'+x.rsplit('/',1)[1]+'`' for x in r['entry_sources']) or 'No top-level Python source; inspect child tests.'), '',
           '**Inputs / predecessors:** '+(', '.join('`'+x+'`' for x in r['bound_predecessor_packets']) or 'No automatically resolved bound predecessor packet; inspect input/contract files.'), '',
           '**Gates:** '+str(len(r['static_gate_excerpts']))+' static source excerpts; saved booleans and exact expressions are in `TEST_CATALOG.json`.', '']
    for rec in r['saved_records']:
        md += ['- `'+rec['file'].rsplit('/',1)[1]+'`: '+json.dumps(rec['classification'], ensure_ascii=True)]
    md += ['', '**Outputs:** '+(', '.join('`'+x.rsplit('/',1)[1]+'`' for x in r['output_files']) or 'No top-level output JSON; inspect children.'), '',
           '**Selected binding closure:** '+str(r['bound_to_selected_route'])+'.', '']
(out/'TEST_CATALOG.md').write_text('\n'.join(md)+'\n')
print(json.dumps(report['counts'], indent=2))
