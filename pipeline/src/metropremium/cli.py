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
from .price_contract import load_price_contract
from .housing import price_descriptives, housing_figure

def latest_audit():
    pointer = ROOT/'artifacts/audits/latest.json'
    if not pointer.exists():
        raise FileNotFoundError('Run audit-data first; no cached full audit')
    folder = ROOT/json.loads(pointer.read_text(encoding='utf-8'))['run']
    return folder,json.loads((folder/'audit.json').read_text(encoding='utf-8'))

def public_payload(audit, flow, df, network, state, housing):
    return {
        'schema_version':2, 'kind':'empirical_preview', 'generated_utc':state['started_utc'], 'run_id':state['run_id'],
        'source':{'repository':'divarofficial/real_estate_ads','revision':REVISION,'url':'https://huggingface.co/datasets/divarofficial/real_estate_ads','license':'ODbL-1.0'},
        'scope':{'source_rows':audit['total_observed_rows'],'source_columns':audit['column_count'],'tehran_apartment_sale_rows':audit['tehran_apartment_sale_rows'],'analysis_rows':len(df),'period':flow['period'],'coordinate_valid_rows':flow['coordinate_valid_rows'],'routable_candidate_rows':flow['routable_candidate_rows']},
        'gates':[
            {'id':1,'status':'owner_confirmed','label':'داده‌های آگهی','reason':'تعریف قیمت کل آپارتمان به تومان با تأیید مالک پروژه ثبت شد؛ قیمت هر مترمربع محاسبه شده است.'},
            {'id':2,'status':'blocked','label':'شبکه و جغرافیا','reason':'شبکه کوچک آزمایشی دریافت شده؛ اعتبارسنجی پوشش مترو و ورودی‌ها کامل نیست.'},
            {'id':3,'status':'blocked','label':'اعتبار آماری','reason':'تا تأیید شبکه، رابطه قیمت و دسترسی به مترو برآورد نمی‌شود.'},
            {'id':4,'status':'preview','label':'انتشار عمومی','reason':'خلاصه توصیفی قیمت و کیفیت داده؛ بدون موقعیت آگهی یا ادعای رابطه با مترو.'}
        ],
        'price_contract':flow['price_contract'], 'housing_descriptives_available':True, 'housing_prices':housing,
        'sample_flow':flow['flow'],'months':audit['selected_months'],'radii':[{'radius':r['radius'],'n':r['n']} for r in audit['radius_selected']],
        'neighborhoods':summaries(df,minimum=state['config']['min_public_group']),'bands':[],'models':[],
        'network':{'public_routes_enabled':False,'public_stations_enabled':False,'walking_nodes':network.get('walking',{}).get('nodes',0),'walking_edges':network.get('walking',{}).get('directed_edges',0),'reference_date':network.get('metro',{}).get('timestamp_osm_base'),'status':'unverified'},
        'limitations':['واحد تومان و تعریف قیمت کل با تأیید مالک پروژه ثبت شده؛ تأیید رسمی ناشر ادعا نمی‌شود.','آگهی فروش، معامله قطعی نیست؛ رابطه احتمالی به معنای اثر علّی نیست.','این داده تاریخی است و وضعیت امروز بازار را نشان نمی‌دهد.','مقادیر بسیار غیرعادی در خلاصه اصلی حفظ شده‌اند؛ حساسیت به کنارگذاری دُم‌های قیمت گزارش می‌شود.','شعاع مکان، توزیع احتمال خطای موقعیت را مشخص نمی‌کند.','مقایسه دسترسی تاریخی بدون بازسازی تاریخ افتتاح ایستگاه‌ها معتبر نیست.'],
        'attribution':['Divar official dataset · ODbL','© OpenStreetMap contributors · ODbL'],'findings_available':False
    }

def empirical(config, folder, state):
    audit_folder,audit = latest_audit()
    source = audit_folder/'tehran-source.parquet'
    df = pd.read_parquet(source)
    if config.get('sample_limit'):
        df = df.sample(min(len(df),config['sample_limit']),random_state=config['seed']).sort_index()
    contract=load_price_contract(ROOT/config['price_contract'])
    cleaned,flow = prepare(df,config,contract)
    cleaned['route_status'] = 'network_not_validated'
    cleaned.to_parquet(folder/'cleaned.parquet',index=False)
    write_json(folder/'sample-flow.json',flow)
    network = build_networks(folder)
    housing=price_descriptives(cleaned,minimum=config['min_public_group'])
    write_json(folder/'housing-descriptives.json',housing)
    pd.DataFrame(housing['variants']).to_csv(folder/'housing-descriptives.csv',index=False)
    housing_figure(housing,folder,contract)
    analysis={'status':'descriptive_only_network_blocked','models':[],'reason':'Housing price descriptions computed using owner-confirmed total asking prices in toman; primary metro associations require an operationally verified network','price_contract':contract,'descriptives':housing}
    payload = public_payload(audit,flow,cleaned,network,state,housing)
    if config.get('network_scope')=='historical-mapped-reference':
        from .mapped_network import mapped_analysis
        mapped=mapped_analysis(cleaned,config,folder)
        analysis['mapped_reference_extension']=mapped
        payload['mapped_reference']=mapped
        payload['gates'][1].update(status='partial',reason='شبکه معابر تاریخی و زیرمجموعه ورودی‌های ثبت‌شده بررسی و مسیریابی شدند؛ کامل بودن ورودی‌ها و بهره‌برداری تاریخی هنوز تأیید نشده است.')
        payload['gates'][2].update(status='partial',reason='مدل‌های اکتشافی برای فاصله تا زیرمجموعه ورودی‌های ثبت‌شده اجرا شدند؛ نتیجه اصلی درباره دسترسی عملیاتی مترو همچنان تأیید نشده است.')
        state['validation'].append('Exploratory historical mapped-subset routes, models and uncertainty executed; primary operational-access gate remains closed')
    write_json(folder/'analysis.json',analysis)
    assert_public_safe(payload)
    write_json(folder/'public.json',payload)
    state['validation'] += ['No listing coordinates in public export','Price-per-m2 uses owner-confirmed total price in toman, without currency conversion','Metro association estimates remain blocked pending network validation','Full-source audit preserved as published-documentation evidence']
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
    svg_path=folder/'figure.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
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
    if config.get('price_contract'): inputs.append(ROOT/config['price_contract'])
    inputs += [p for p in (ROOT/'data/raw/osm').rglob('*') if p.is_file() and not p.name.endswith('.part')]
    inputs += [p for p in (ROOT/'data/raw/references/alibaba').glob('*.html*') if p.is_file()]
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
                    for filename in ['housing-descriptives.json','housing-descriptives.csv']:
                        shutil.copyfile(folder/filename,ROOT/'artifacts/reports'/filename)
                    # Individual entrance review coordinates stay in the private run.
                    for filename in ['mapped-analysis.json','mapped-entrance-inventory.json','mapped-location-sensitivity.json']:
                        if (folder/filename).exists():
                            shutil.copyfile(folder/filename,ROOT/'artifacts/reports'/filename)
                    for filename in ['mapped-accessibility.png','mapped-accessibility.svg']:
                        if (folder/filename).exists():
                            shutil.copyfile(folder/filename,ROOT/'artifacts/figures'/filename)
                    for filename in ['housing-price-summary.png','housing-price-summary.svg']:
                        if (folder/filename).exists():
                            shutil.copyfile(folder/filename,ROOT/'artifacts/figures'/filename)
                    shutil.copyfile(folder/'figure.png',ROOT/'artifacts/figures/source-months.png')
                    shutil.copyfile(folder/'figure.svg',ROOT/'artifacts/figures/source-months.svg')
                    if (folder/'walking-preview.geojson').exists():
                        shutil.copyfile(folder/'walking-preview.geojson',ROOT/'data/public/walking-preview.geojson')
                        shutil.copyfile(folder/'walking-preview.geojson',dest/'walking-preview.geojson')
            state['outputs']=[str(p.relative_to(ROOT)) for p in folder.iterdir() if p.is_file()]
        print('Run:',folder.relative_to(ROOT))

if __name__=='__main__': main()
