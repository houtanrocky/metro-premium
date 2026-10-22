"""Cached, bounded historical OSM acquisition; never downloads tiles.

Attic data are the map as recorded at the date, not proof of physical operation.
Downloads are sequential to avoid loading public Overpass instances concurrently.
"""
import argparse
import json
import hashlib
import time
import sys
import urllib.parse
from pathlib import Path

from acquire import fetch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline/src'))
from metropremium.provenance import run_record, write_json, digest

DATE = '2024-12-01T00:00:00Z'
BBOX = '35.42,51.02,35.93,51.68'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=['metro', 'line5', 'walk', 'all'], default='all')
    p.add_argument('--offline', action='store_true')
    p.add_argument('--base', default='https://overpass-api.de/api/interpreter')
    args = p.parse_args()
    dest = ROOT / 'data/raw/osm/historical-20241201'
    prefix = f'[out:json][timeout:180][maxsize:536870912][date:"{DATE}"];'
    queries = {
        'metro': prefix + f'(node[railway=station]({BBOX});node[railway=subway_entrance]({BBOX});relation[route=subway]({BBOX});relation[public_transport=stop_area]({BBOX}););(._;>>;);out body;',
        'line5': prefix + 'relation(443301);(._;>>;);out body;',
    }
    # Four immutable tiles keep historical scans bounded and permit resumption.
    for i,(south,north) in enumerate([(35.42,35.675),(35.675,35.93)]):
        for j,(west,east) in enumerate([(51.02,51.35),(51.35,51.68)]):
            queries[f'walk-{i}-{j}']=prefix+f'way[highway][highway!~"^(motorway|motorway_link|trunk|trunk_link|construction|proposed|raceway)$"]({south},{west},{north},{east});(._;>;);out body;'
    with run_record('acquire-historical', {'date': DATE, 'bbox': BBOX, 'kind': args.kind, 'base':args.base}, []) as (folder, state):
        selected = list(queries) if args.kind=='all' else [k for k in queries if k.startswith('walk-')] if args.kind=='walk' else [args.kind]
        for kind in selected:
            target = dest / f'{kind}.json'
            if args.offline and not target.exists():
                raise FileNotFoundError(target)
            # GET allows the immutable request to be fully recorded in the sidecar.
            url = args.base + '?' + urllib.parse.urlencode({'data': queries[kind]})
            write_json(folder / f'{kind}-request.json', {'query':queries[kind],'url':url,'output':str(target.relative_to(ROOT))})
            fetch(url, target, timeout=240)
            raw = json.loads(target.read_text(encoding='utf-8'))
            if raw.get('remark') or not raw.get('elements'):
                raise ValueError(f'Incomplete Overpass response: {raw.get("remark", "empty elements")}')
            write_json(folder / f'{kind}-acquisition.json', {'file': str(target.relative_to(ROOT)), 'query': queries[kind], 'elements': len(raw['elements']), 'osm3s': raw.get('osm3s'), 'requested_snapshot': DATE})
            state['validation'].append(f'{kind}: nonempty JSON response without runtime remark')
            state['inputs'].extend({'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in [target,Path(str(target)+'.source.json')])
        if args.kind in {'walk','all'}:
            merged={}
            inputs=[]
            for name in [k for k in queries if k.startswith('walk-')]:
                path=dest/f'{name}.json'
                raw=json.loads(path.read_text(encoding='utf-8'))
                for e in raw['elements']:
                    key=(e['type'],e['id'])
                    if key in merged and merged[key]!=e:raise ValueError('Tile overlap has inconsistent historical object versions')
                    merged[key]=e
                inputs.append({'file':path.name,'sha256':json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))['sha256']})
            target=dest/'walk.json'
            if not target.exists():
                write_json(target,{'elements':list(merged.values()),'requested_snapshot':DATE,'derived_from':inputs})
                write_json(Path(str(target)+'.source.json'),{'derivation':'union of four historical Overpass tiles, deduplicated by type and OSM ID','inputs':inputs,'requested_snapshot':DATE,'sha256':hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),'bytes':target.stat().st_size,'retrieved_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})


if __name__ == '__main__':
    main()
