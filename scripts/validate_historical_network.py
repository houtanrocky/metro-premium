"""Offline audit of pinned real geometry and scoped official station evidence."""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline/src'))
import yaml
from metropremium.provenance import run_record
from metropremium.network_audit import audit_network


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',default='configs/historical-evidence.yaml')
    args = parser.parse_args()
    config_path = ROOT/args.config
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    inputs = [config_path]
    for name in ['metro.json','line5.json','walk.json']:
        path = ROOT/'data/raw/osm/historical-20241201'/name
        inputs.extend([path,Path(str(path)+'.source.json')])
    for source in config['sources']:
        path = ROOT/source['file']
        inputs.extend([path,Path(str(path)+'.source.json')])
    for source in config.get('rejected_sources',[]):
        path = ROOT/source['cached_file']
        inputs.extend([path,Path(str(path)+'.source.json')])
    guide = ROOT/'data/raw/references/alibaba/tehran-subway-guide.html'
    inputs.extend([guide,Path(str(guide)+'.source.json')])
    with run_record('validate-historical-network',config,inputs) as (folder,state):
        report = audit_network(config,folder)
        destination = ROOT/'artifacts/reports/historical-network-audit.json'
        shutil.copyfile(folder/'historical-network-audit.json',destination)
        state['validation'].extend(['Real OSM track-way geometry audited; no station-dot geometry generated',
                                    'Pinned official article checked; claims restricted to station inauguration',
                                    'Entrance coordinates confined to ignored private review CSV',
                                    'Existing empirical results preserved; primary operational and public metro geometry gates remain closed'])
        print(json.dumps({'run':str(folder.relative_to(ROOT)), 'status':report['status'],
                          'routes_screened':report['route_geometry_summary']['cached_routes'],
                          'official_station_claims':report['historical_station_evidence']['accepted_station_inauguration_claims']}))


if __name__ == '__main__':
    main()
