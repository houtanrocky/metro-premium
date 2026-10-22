import argparse
import json
from pathlib import Path
import shutil
import pandas as pd
import yaml
from .provenance import ROOT, REVISION, run_record, write_json, digest
from .audit import audit_source
from .cleaning import prepare
from .geographic import build_networks
from .synthetic import demo
from .statistics import fit_models, sensitivity_models
from .aggregation import summaries, band_summaries, assert_public_safe

def latest_audit():
    pointer = ROOT/'artifacts/audits/latest.json'
    if not pointer.exists():
        raise FileNotFoundError('Run audit-data first; no cached full audit')
    folder = ROOT/json.loads(pointer.read_text(encoding='utf-8'))['run']
    return folder,json.loads((folder/'audit.json').read_text(encoding='utf-8'))

def public_payload(audit, flow, df, network, state):
    selected = audit['tehran_apartment_sale_rows']
    return {'schema_version':1,'kind':'empirical_preview','generated_utc':state['started_utc'],'run_id':state['run_id'],'source':{'repository':'divarofficial/real_estate_ads','revision':REVISION,'url':'https://huggingface.co/datasets/divarofficial/real_estate_ads','license':'ODbL-1.0'},'scope':{'source_rows':audit['total_observed_rows'],'source_columns':audit['column_count'],'tehran_apartment_sale_rows':selected,'analysis_rows':len(df),'period':flow['period'],'coordinate_valid_rows':flow['coordinate_valid_rows'],'routable_candidate_rows':flow['routable_candidate_rows']},'gates':[{'id':1,'status':'partial','label':'داده‌های آگهی','reason':'ممیزی کامل انجام شد؛ تعریف قیمت کل و واحد پول هنوز تأیید نشده است.'},{'id':2,'status':'blocked','label':'شبکه و جغرافیا','reason':'شبکه کوچک آزمایشی دریافت شده؛ اعتبارسنجی پوشش مترو و ورودی‌ها کامل نیست.'},{'id':3,'status':'blocked','label':'اعتبار آماری','reason':'تا تأیید تعریف قیمت و شبکه، برآورد تجربی منتشر نمی‌شود.'},{'id':4,'status':'preview','label':'انتشار عمومی','reason':'فقط شمارش‌ها و کیفیت داده؛ بدون موقعیت آگهی و نقشه قیمت.'}],'price_contract':audit['price_contract'],'sample_flow':flow['flow'],'months':audit['selected_months'],'radii':[{'radius':r['radius'],'n':r['n']} for r in audit['radius_selected']],'neighborhoods':summaries(df),'bands':[],'models':[],'network':{'public_routes_enabled':False,'public_stations_enabled':False,'walking_nodes':network.get('walking',{}).get('nodes',0),'walking_edges':network.get('walking',{}).get('directed_edges',0),'reference_date':network.get('metro',{}).get('timestamp_osm_base'),'status':'unverified'},'limitations':['آگهی فروش، معامله قطعی نیست؛ رابطه احتمالی به معنای اثر علّی نیست.','این داده تاریخی است و وضعیت امروز بازار را نشان نمی‌دهد.','شعاع مکان، توزیع احتمال خطای موقعیت را مشخص نمی‌کند.','مقایسه دسترسی تاریخی بدون بازسازی تاریخ افتتاح ایستگاه‌ها معتبر نیست.'],'attribution':['Divar official dataset · ODbL','© OpenStreetMap contributors · ODbL'],'findings_available':False}

def empirical(config, folder, state):
    audit_folder,audit = latest_audit()
    source = audit_folder/'tehran-source.parquet'
    df = pd.read_parquet(source)
    if config.get('sample_limit'):
        df = df.sample(min(len(df),config['sample_limit']),random_state=config['seed']).sort_index()
    cleaned,flow = prepare(df,config,audit['price_contract'])
    cleaned['route_status'] = 'network_not_validated'
    cleaned.to_parquet(folder/'cleaned.parquet',index=False)
    write_json(folder/'sample-flow.json',flow)
    network = build_networks(folder)
    write_json(folder/'analysis.json',{'status':'blocked','models':[],'reason':'Price semantics and complete verified network are required','descriptives':{'n':len(cleaned),'area_median_m2':float(cleaned.building_size.median()),'area_iqr_m2':cleaned.building_size.quantile([.25,.75]).tolist()}})
    payload = public_payload(audit,flow,cleaned,network,state)
    assert_public_safe(payload)
    write_json(folder/'public.json',payload)
    state['validation'] += ['No listing coordinates in public export','Price-per-m2 and metro claims blocked pending source contracts','Full-source audit referenced']
    state['audit_run'] = str(audit_folder.relative_to(ROOT))
    state['inputs'] += [{'path':str(source.relative_to(ROOT)),'sha256':digest(source)}]
    return payload

def smoke(config, folder, state):
    df,flow,uncertainty = demo(config)
    analysis = fit_models(df)
    write_json(folder/'sample-flow.json',flow)
    write_json(folder/'analysis.json',analysis)
    write_json(folder/'sensitivity.json',sensitivity_models(df))
    write_json(folder/'uncertainty.json',uncertainty)
    payload = {'schema_version':1,'kind':'synthetic_demo','warning':'SYNTHETIC ONLY — not observations from Tehran','seed':config['seed'],'n':len(df),'neighborhoods':summaries(df),'bands':band_summaries(df),'models':analysis['models'],'uncertainty':uncertainty}
    assert_public_safe(payload)
    write_json(folder/'public.json',payload)
    if not all(r['status']=='estimated' for r in analysis['models']) or len(analysis['models'])!=3:
        raise ValueError('Synthetic model validation did not estimate all planned models')
    state['validation'] += ['Synthetic fixture cleaned, routed, modeled and aggregated','Synthetic outputs never become default public empirical data']
    return payload

def figures(payload, folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7f5ef','axes.facecolor':'#f7f5ef','svg.hashsalt':'metropremium-v0.1'})
    if payload['kind']=='synthetic_demo':
        rows = payload['bands']
        title = 'SYNTHETIC DEMO — not Tehran findings'
        labels = [str(r['band']) for r in rows]
        values = [r['median_per_m2'] for r in rows]
        ylabel = 'Arbitrary synthetic source units / m²'
    else:
        rows = payload['months']
        title = 'Official Divar source audit: Tehran apartment-sale listing months'
        labels = [r['month'] for r in rows]
        values = [r['n'] for r in rows]
        ylabel = 'Listing count (before analytical exclusions)'
    fig,ax=plt.subplots(figsize=(12,6))
    fig.subplots_adjust(left=.1,right=.98,top=.87,bottom=.27)
    ax.bar(labels,values,color='#167875')
    ax.set_ylabel(ylabel)
    ax.set_title(title,loc='left',pad=22)
    ax.tick_params(axis='x',rotation=65,labelsize=8)
    footer = 'SYNTHETIC ONLY | not Tehran observations' if payload['kind']=='synthetic_demo' else f"Source: divarofficial/real_estate_ads | N={payload['scope']['tehran_apartment_sale_rows']:,} before filters | Audit {payload['generated_utc'][:10]}"
    fig.text(.02,.055,footer,fontsize=8)
    fig.text(.02,.025,'Historical asking listings, not transactions | No empirical metro-price finding | MetroPremium',fontsize=8)
    fig.savefig(folder/'figure.png',dpi=240)
    fig.savefig(folder/'figure.svg',metadata={'Date':None})
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(description='MetroPremium reproducible workflows')
    p.add_argument('command',choices=['audit-data','prepare-data','build-networks','compute-accessibility','analyze','export-public-data','report','reproduce','smoke'])
    p.add_argument('--config',default='configs/full.yaml')
    p.add_argument('--offline',action='store_true',help='Use cached inputs only (pipeline never downloads implicitly)')
    args=p.parse_args()
    config=yaml.safe_load((ROOT/args.config).read_text(encoding='utf-8'))
    if args.command=='smoke': config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text(encoding='utf-8'))
    source=ROOT/'data/raw/divar'/REVISION/'real_estate_ads.csv'
    inputs = [ROOT/args.config]
    inputs += [p for p in (ROOT/'data/raw/osm').glob('*') if p.is_file()]
    if args.command=='audit-data': inputs.append(source)
    with run_record(args.command,config,inputs) as (folder,state):
        (ROOT/'artifacts/reports').mkdir(parents=True,exist_ok=True)
        (ROOT/'artifacts/figures').mkdir(parents=True,exist_ok=True)
        if args.command=='audit-data':
            if not source.exists(): raise FileNotFoundError('Download with python scripts/acquire.py first')
            audit,_=audit_source(source,folder)
            write_json(ROOT/'artifacts/audits/latest.json',{'run':str(folder.relative_to(ROOT))})
            # Only aggregate audit statistics enter tracked reports.
            shutil.copyfile(folder/'audit.json',ROOT/'artifacts/audits/source-audit.json')
            state['validation'].append('Strict CSV full-source audit completed')
            print(json.dumps({'rows':audit['total_observed_rows'],'columns':audit['column_count'],'tehran_apartment_sales':audit['tehran_apartment_sale_rows']}))
        elif args.command=='build-networks':
            report=build_networks(folder)
            write_json(ROOT/'artifacts/reports/network-validation.json',report)
        else:
            payload=smoke(config,folder,state) if config['mode']=='synthetic' else empirical(config,folder,state)
            figures(payload,folder)
            if args.command in {'reproduce','export-public-data','report','smoke'}:
                target=ROOT/'data/public'/('synthetic-demo.json' if config['mode']=='synthetic' else 'research.json')
                write_json(target,payload)
                if config['mode']!='synthetic':
                    dest=ROOT/'apps/web/public/data'
                    dest.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(target,dest/'research.json')
                    for filename in ['sample-flow.json','network-validation.json','analysis.json']:
                        shutil.copyfile(folder/filename,ROOT/'artifacts/reports'/filename)
                    shutil.copyfile(folder/'figure.png',ROOT/'artifacts/figures/source-months.png')
                    shutil.copyfile(folder/'figure.svg',ROOT/'artifacts/figures/source-months.svg')
                    if (folder/'walking-preview.geojson').exists():
                        shutil.copyfile(folder/'walking-preview.geojson',ROOT/'data/public/walking-preview.geojson')
                        shutil.copyfile(folder/'walking-preview.geojson',dest/'walking-preview.geojson')
            state['outputs']=[str(p.relative_to(ROOT)) for p in folder.iterdir() if p.is_file()]
        print('Run:',folder.relative_to(ROOT))

if __name__=='__main__': main()
