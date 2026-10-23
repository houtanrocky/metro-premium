"""Cached, bounded historical OSM acquisition; never downloads tiles.

Attic data are the map as recorded at the date, not proof of physical operation.
Downloads are sequential to avoid loading public Overpass instances concurrently.
"""
import argparse
import json
import hashlib
import http.client
import html
import shutil
import time
import sys
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

from acquire import fetch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline/src'))
from metropremium.provenance import run_record, write_json, digest
from metropremium.mapped_network import checked_json

DATE = '2024-12-01T00:00:00Z'
BBOX = '35.42,51.02,35.93,51.68'


class IncompleteResponse(ValueError):
    """An Overpass response must not become an accepted source."""


def historical_queries():
    prefix = f'[out:json][timeout:180][maxsize:536870912][date:"{DATE}"];'
    queries = {
        'metro': prefix + f'(node[railway=station]({BBOX});node[railway=subway_entrance]({BBOX});relation[route=subway]({BBOX});relation[public_transport=stop_area]({BBOX}););(._;>>;);out body;',
        'line5': prefix + 'relation(443301);(._;>>;);out body;',
    }
    for i, (south, north) in enumerate([(35.42,35.675),(35.675,35.93)]):
        for j, (west, east) in enumerate([(51.02,51.35),(51.35,51.68)]):
            queries[f'walk-{i}-{j}'] = prefix + f'way[highway][highway!~"^(motorway|motorway_link|trunk|trunk_link|construction|proposed|raceway)$"]({south},{west},{north},{east});(._;>;);out body;'
    return queries


def browser_plan(queries, selected, dest, base, folder):
    entries = []
    for name in selected:
        if (dest / f'{name}.json').exists():
            checked_json(dest / f'{name}.json')
            continue
        server = base.removesuffix('interpreter')
        query = '{{data:overpass,server=' + server + '}}\n' + queries[name]
        url = 'https://overpass-turbo.eu/?' + urllib.parse.urlencode({'Q': query})
        command = (f'node scripts/task.mjs acquire-historical --input {name} '
                   f'--import-file "$env:USERPROFILE\\Downloads\\{name}.json" --base {base}')
        entries.append({'input': name, 'query': queries[name], 'browser_url': url,
                        'source_url': base + '?' + urllib.parse.urlencode({'data': queries[name]}),
                        'filename': f'{name}.json', 'import_command': command})
    write_json(folder / 'browser-plan.json', {'snapshot': DATE, 'inputs': entries})
    cards = ''.join(
        f'<article><h2>{html.escape(e["filename"])}</h2>'
        f'<p><a target="_blank" rel="noopener" href="{html.escape(e["browser_url"], quote=True)}">Open prepared query in Overpass Turbo</a></p>'
        f'<p>Click Run. After a successful response, choose Export → raw data → download. '
        f'Save the raw OSM JSON in Downloads as <strong>{e["filename"]}</strong>.</p>'
        f'<p>Then run this in PowerShell from the project directory:</p><pre>{html.escape(e["import_command"])}</pre></article>'
        for e in entries)
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' + \
        '<title>MetroPremium historical downloads</title><style>body{font:17px/1.6 system-ui;max-width:900px;margin:40px auto;padding:0 24px;color:#18312e;background:#f6f5ef}article{padding:16px 24px;margin:24px 0;background:white;border:1px solid #cad7d1;border-radius:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#edf3ef;padding:16px}a{color:#086c60}</style>' + \
        '<body><h1>MetroPremium historical downloads</h1><p>Only missing inputs are listed. The queries request the OSM database at <strong>' + DATE + \
        '</strong>. Run one query at a time. Keep each query unchanged and export raw OSM JSON. GeoJSON loses the node/member structure needed here.</p>' + \
        '<p>Importing a file records your statement that it came from its prepared query. The importer checks file integrity and object structure; it cannot independently prove which query generated a saved file. Historical operating eligibility remains unverified.</p>' + \
        (cards or '<p>All selected inputs are already cached.</p>') + \
        '<p>After all four walking tiles are imported, merge them offline:</p><pre>node scripts/task.mjs acquire-historical --kind walk --offline</pre></body></html>'
    path = folder / 'browser-downloads.html'
    path.write_text(page, encoding='utf-8')
    print(f'{len(entries)} missing inputs. Open this file in your browser:\n{path.resolve()}', flush=True)
    return entries


def import_browser_file(source, name, query, dest, base, folder, state):
    """Preserve owner-supplied bytes and explicitly record attested request provenance."""
    target = dest / f'{name}.json'
    if target.exists() or Path(str(target) + '.source.json').exists():
        raise ValueError(f'Existing source or sidecar will not be overwritten: {target}')
    candidate = folder / f'{name}-browser-response.json'
    shutil.copyfile(source, candidate)
    url = base + '?' + urllib.parse.urlencode({'data': query})
    metadata = {'url': url, 'sha256': digest(candidate), 'bytes': candidate.stat().st_size,
                'imported_at_utc': datetime.now(timezone.utc).isoformat(),
                'retrieval_method': 'operator_supplied_browser_download',
                'request_evidence': 'Operator attests this file came from the unchanged prepared query at the recorded endpoint.',
                'snapshot_request_independently_verified': False}
    write_json(Path(str(candidate) + '.source.json'), metadata)
    raw = checked_json(candidate)
    elements = raw['elements']
    if raw.get('version') != 0.6 or not str(raw.get('generator', '')).startswith('Overpass API'):
        raise ValueError('Expected raw Overpass OSM JSON, not GeoJSON or a converted export')
    objects = {}
    for element in elements:
        key = (element.get('type'), element.get('id'))
        if key[0] not in {'node', 'way', 'relation'} or not isinstance(key[1], int) or key in objects:
            raise ValueError('Invalid or duplicate OSM object identity')
        objects[key] = element
    if name == 'line5' and ('relation', 443301) not in objects:
        raise ValueError('Line 5 response must contain relation 443301')
    if name == 'line5' and not objects[('relation', 443301)].get('members'):
        raise ValueError('Line 5 response must include full relation members, not tags only')
    if name.startswith('walk-') and not any(e.get('tags', {}).get('highway') for e in elements if e['type'] == 'way'):
        raise ValueError('Walking response contains no highway ways')
    for element in elements:
        if element['type'] == 'way' and not isinstance(element.get('nodes'), list):
            raise ValueError('Raw ways must include node references')
        if element['type'] == 'relation' and not isinstance(element.get('members'), list):
            raise ValueError('Raw relations must include member references')
        if element['type'] == 'node':
            if not (-180 <= element.get('lon', float('nan')) <= 180 and -90 <= element.get('lat', float('nan')) <= 90):
                raise ValueError('Invalid or missing node coordinates')
        references = [('node', n) for n in element.get('nodes', [])]
        references += [(m['type'], m['ref']) for m in element.get('members', [])]
        if any(ref not in objects for ref in references):
            raise ValueError('Incomplete raw response: referenced OSM objects are missing')
    dest.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as output, candidate.open('rb') as saved:
        shutil.copyfileobj(saved, output)
    write_json(Path(str(target) + '.source.json'), metadata)
    write_json(folder / 'browser-import.json', {'input': name, 'query': query, 'metadata': metadata})
    state['inputs'].extend({'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}
                          for p in [target, Path(str(target) + '.source.json')])
    state['validation'].append('Manually supplied raw JSON checked for integrity, expected object identity and reference closure; request provenance is operator-attested')
    print(f'Imported {target.name}: {len(elements):,} elements. Browser request provenance is operator-attested.', flush=True)


def acquire_query(query, target, base, folder, state, *, attempts=2, timeout=240, offline=False):
    url = base + '?' + urllib.parse.urlencode({'data': query})
    write_json(folder / f'{target.stem}-request.json', {'query': query, 'url': url, 'output': str(target.relative_to(ROOT))})
    if target.exists():
        print(f'Validating cached {target.name}', flush=True)
        raw = checked_json(target)
    else:
        if offline:
            raise FileNotFoundError(f'Offline input missing: {target}')
        for attempt in range(1, attempts + 1):
            # Preserve all responses in the run, including rejected or partial bytes.
            candidate = folder / f'{target.stem}-attempt-{attempt}.json'
            print(f'Requesting {target.name} from {urllib.parse.urlsplit(base).netloc} '
                  f'(attempt {attempt}/{attempts}; socket timeout {timeout}s)', flush=True)
            started = time.monotonic()
            try:
                fetch(url, candidate, timeout=timeout)
                try:
                    raw = checked_json(candidate)
                except (ValueError, KeyError) as exc:
                    raise IncompleteResponse(str(exc)) from exc
            except (TimeoutError, ConnectionError, http.client.IncompleteRead,
                    urllib.error.URLError, IncompleteResponse) as exc:
                retryable = (not isinstance(exc, urllib.error.HTTPError)
                             or exc.code in {408, 429, 502, 503, 504})
                state.setdefault('request_attempts', []).append({
                    'target': target.name, 'attempt': attempt, 'url': url,
                    'elapsed_s': round(time.monotonic() - started, 2),
                    'error_type': type(exc).__name__, 'error': str(exc),
                })
                print(f'{target.name}: {type(exc).__name__}: {exc}', flush=True)
                if not retryable or attempt == attempts:
                    raise RuntimeError(
                        f'Acquisition stopped at {target.name}; no complete source was accepted. '
                        f'Completed downloads are retained. Retry later or use --base with another '
                        f'historical-data-capable endpoint. Request evidence: {folder}'
                    ) from exc
                delay = 30 * attempt
                print(f'Waiting {delay}s before retrying; Ctrl+C stops safely.', flush=True)
                time.sleep(delay)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Only promote complete, checksum-validated responses; never overwrite sources.
            with target.open('xb') as output, candidate.open('rb') as source:
                shutil.copyfileobj(source, output)
            metadata = json.loads(Path(str(candidate) + '.source.json').read_text(encoding='utf-8'))
            write_json(Path(str(target) + '.source.json'), metadata)
            state.setdefault('request_attempts', []).append({
                'target': target.name, 'attempt': attempt, 'url': url,
                'elapsed_s': round(time.monotonic() - started, 2), 'status': 'validated',
            })
            print(f'Accepted {target.name}: {len(raw["elements"]):,} OSM elements', flush=True)
            break
    write_json(folder / f'{target.stem}-acquisition.json', {
        'file': str(target.relative_to(ROOT)), 'query': query, 'elements': len(raw['elements']),
        'osm3s': raw.get('osm3s'), 'requested_snapshot': DATE,
    })
    state['validation'].append(f'{target.stem}: checksum-validated historical JSON without runtime remark')
    state['inputs'].extend({'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}
                          for p in [target, Path(str(target) + '.source.json')])
    return raw


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=['metro', 'line5', 'walk', 'all'], default='all')
    p.add_argument('--offline', action='store_true')
    p.add_argument('--base', default='https://overpass-api.de/api/interpreter')
    p.add_argument('--attempts', type=int, default=2, help='Maximum attempts per missing input (default: 2)')
    p.add_argument('--request-timeout', type=int, default=240, help='Socket timeout in seconds (default: 240)')
    p.add_argument('--browser-links', action='store_true', help='Prepare browser queries without downloading')
    p.add_argument('--import-file', type=Path, help='Raw OSM JSON saved from the unchanged prepared browser query')
    p.add_argument('--input', choices=list(historical_queries()), help='Exact input name for a manual browser import')
    args = p.parse_args()
    if not 1 <= args.attempts <= 3 or args.request_timeout < 1:
        p.error('--attempts must be 1-3 and --request-timeout must be positive')
    if bool(args.import_file) != bool(args.input) or (args.import_file and (args.browser_links or args.offline)):
        p.error('--import-file requires --input and cannot be combined with --browser-links or --offline')
    dest = ROOT / 'data/raw/osm/historical-20241201'
    queries = historical_queries()
    config = {'date': DATE, 'bbox': BBOX, 'kind': args.kind, 'base': args.base, 'attempts': args.attempts, 'request_timeout': args.request_timeout,
              'browser_links': args.browser_links, 'manual_import_input': args.input}
    with run_record('acquire-historical', config, []) as (folder, state):
        selected = list(queries) if args.kind=='all' else [k for k in queries if k.startswith('walk-')] if args.kind=='walk' else [args.kind]
        if args.browser_links:
            browser_plan(queries, selected, dest, args.base, folder)
            state['validation'].append('Browser query plan prepared; no download or empirical analysis performed')
            return
        if args.import_file:
            import_browser_file(args.import_file, args.input, queries[args.input], dest, args.base, folder, state)
            return
        for kind in selected:
            target = dest / f'{kind}.json'
            acquire_query(queries[kind], target, args.base, folder, state,
                          attempts=args.attempts, timeout=args.request_timeout, offline=args.offline)
        if args.kind in {'walk','all'}:
            merged={}
            inputs=[]
            for name in [k for k in queries if k.startswith('walk-')]:
                path=dest/f'{name}.json'
                raw=checked_json(path)
                for e in raw['elements']:
                    key=(e['type'],e['id'])
                    if key in merged and merged[key]!=e:raise ValueError('Tile overlap has inconsistent historical object versions')
                    merged[key]=e
                inputs.append({'file':path.name,'sha256':json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))['sha256']})
            target=dest/'walk.json'
            if not target.exists():
                write_json(target,{'elements':list(merged.values()),'requested_snapshot':DATE,'derived_from':inputs})
                write_json(Path(str(target)+'.source.json'),{'derivation':'union of four historical Overpass tiles, deduplicated by type and OSM ID','inputs':inputs,'requested_snapshot':DATE,'sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),'bytes':target.stat().st_size,'retrieved_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            checked_json(target)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
