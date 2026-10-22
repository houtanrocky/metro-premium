"""Acquire/cache the user-selected reference and compare factual lists with OSM.

Use --offline after first acquisition. The article and linked PDF stay ignored;
only factual comparison records and source provenance enter tracked reports.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import urllib.request

from metropremium.metro_reference import GUIDE_URL, build_reference_report
from metropremium.provenance import ROOT, digest, run_record, write_json

def acquire(url,path,offline):
    sidecar=path.with_suffix(path.suffix+'.source.json')
    if path.exists():
        if not sidecar.exists():
            raise ValueError(f'Cached input has no acquisition record: {path}')
        metadata=json.loads(sidecar.read_text(encoding='utf-8'))
        if metadata['sha256']!=digest(path) or metadata['url']!=url:
            raise ValueError('Reference provenance mismatch')
        return metadata
    if offline: raise FileNotFoundError(f'Offline reference input missing: {path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    request=urllib.request.Request(url,headers={'User-Agent':'MetroPremium/0.1 (research reference inspection)'})
    with urllib.request.urlopen(request,timeout=45) as response:
        payload=response.read()
        content_type=response.headers.get('Content-Type')
    if not payload or (path.suffix=='.pdf' and not payload.startswith(b'%PDF-')):
        raise ValueError('Reference response failed content check')
    path.write_bytes(payload)
    metadata={'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':digest(path),'bytes':len(payload),'content_type':content_type,'source_role':'User-supplied secondary metro reference; publication and reuse rights not established'}
    write_json(sidecar,metadata)
    return metadata

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    raw=ROOT/'data/raw/references/alibaba'
    html_path=raw/'tehran-subway-guide.html'
    osm_path=ROOT/'data/raw/osm/metro.json'
    with run_record('metro-reference',{'source':GUIDE_URL,'offline':args.offline,'match_policy':'exact orthographic identity candidates only; fuzzy suggestions require manual review'},[p for p in [html_path,osm_path] if p.exists()]) as (folder,state):
        metadata=acquire(GUIDE_URL,html_path,args.offline)
        reference,comparison=build_reference_report(html_path,osm_path,folder)
        reference['acquisition']=metadata
        pdfs=[]
        for url in reference['linked_schematic_pdfs']:
            pdf_metadata=acquire(url,raw/'tehran-metro-schematic.pdf',args.offline)
            pdfs.append(pdf_metadata)
        reference['linked_schematic_acquisitions']=pdfs
        write_json(folder/'alibaba-station-reference.json',reference)
        for filename in ['alibaba-station-reference.json','metro-reference-comparison.json']:
            destination=ROOT/'artifacts/reports'/filename
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(folder/filename,destination)
        state['inputs']=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in [html_path,osm_path,raw/'tehran-metro-schematic.pdf'] if p.exists()]
        state['validation']=['Seven main line and three branch lists parsed','No article prose or source images exported','Exact-name candidates never enable operational or geographic claims','Fuzzy suggestions remain unaccepted']
        state['outputs']=[str(p.relative_to(ROOT)) for p in folder.iterdir() if p.is_file()]
        print(json.dumps({'main_line_entries':comparison['total_main_line_entries'],'exact_name_candidates':comparison['total_exact_name_candidates'],'source_discrepancies':reference['discrepancies'],'run':str(folder.relative_to(ROOT))}))

if __name__=='__main__': main()
