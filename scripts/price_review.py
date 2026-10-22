"""Create a private, coordinate-free source-value workbook for owner review.

This exports source fields, not a public research database or validated price/m².
All generated files live in an ignored per-run folder and never enter the website.
"""
import json
from pathlib import Path
import pandas as pd

from metropremium.provenance import ROOT, REVISION, digest, run_record, write_json
from metropremium.price_contract import load_price_contract

def main():
    pointer=json.loads((ROOT/'artifacts/audits/latest.json').read_text(encoding='utf-8'))
    audit_folder=ROOT/pointer['run']
    source=audit_folder/'tehran-source.parquet'
    contract_path=ROOT/'configs/price-contract.yaml'
    contract=load_price_contract(contract_path)
    config={'period':'2024-12','city':'tehran','cat2':'residential-sell','cat3':'apartment-sell','price_mode':'مقطوع','price_rule':'positive finite source number','area_m2':[20,500],'seed':20261022,'publication':'private owner inspection only','price_interpretation':'Owner-confirmed total apartment asking price in toman; original values retained, no per-m² calculation in this raw-field review export'}
    with run_record('price-review',config,[source,contract_path]) as (folder,state):
        raw=pd.read_parquet(source)
        price=pd.to_numeric(raw.price_value,errors='coerce')
        area=pd.to_numeric(raw.building_size,errors='coerce')
        selected=raw.loc[raw.city_slug.eq('tehran') & raw.cat2_slug.eq('residential-sell') & raw.cat3_slug.eq('apartment-sell') & raw.created_at_month.str.startswith(config['period']) & raw.price_mode.eq(config['price_mode']) & price.gt(0) & price.lt(float('inf')) & area.between(*config['area_m2'])].copy()
        columns=['city_slug','neighborhood_slug','created_at_month','cat2_slug','cat3_slug','price_mode','price_value','building_size','rooms_count','construction_year','floor','has_parking','has_elevator','has_warehouse']
        # A private review ID links these files to each other, not to a seller/property identity.
        selected=selected[columns].reset_index(drop=True)
        selected.insert(0,'review_id',range(1,len(selected)+1))
        assert len(selected)==11767, 'Candidate population changed; inspect source/config before exporting'
        assert not {'description','title','location_latitude','location_longitude','source_row'}.intersection(selected.columns)
        counts=selected.neighborhood_slug.dropna().value_counts()
        top=sorted(counts.index,key=lambda n:(-int(counts[n]),n))[:12]
        examples=pd.concat([selected.loc[selected.neighborhood_slug.eq(n)].sample(1,random_state=config['seed']) for n in top],ignore_index=True)
        random_sample=selected.sample(min(500,len(selected)),random_state=config['seed']).sort_values('review_id')
        for name,data in [('tehran-december-2024-source-values.csv',selected),('random-500-source-values.csv',random_sample),('12-neighborhood-examples.csv',examples)]:
            data.to_csv(folder/name,index=False,encoding='utf-8-sig')
        provenance={'source_repository':'divarofficial/real_estate_ads','revision':REVISION,'official_url':'https://huggingface.co/datasets/divarofficial/real_estate_ads','license':'ODbL-1.0','audit_run':pointer['run'],'selected_parquet_sha256':digest(source),'rows':len(selected),'columns':list(selected.columns),'config':config,'examples_selection':'One seeded randomly selected actual record from each of the 12 neighborhoods with most eligible records; not representative price estimates','missing_cells':'Empty CSV cells represent source nulls','source_values':'Original Parquet source fields retained as strings; no currency scaling, price conversion or price/m² calculation','privacy':'No descriptions, titles, seller data or property coordinates; ignored private run folder; no public website changes'}
        provenance['price_contract']=contract
        write_json(folder/'review-provenance.json',provenance)
        lines=['# Housing asking-price source values for owner inspection','',f'Actual official-source records, revision `{REVISION}`. Period: December 2024. Full selected file: {len(selected):,} records. Source money unit and total-versus-unit-price meaning remain unverified. This is private source inspection, not an empirical price finding.','', 'Files:','', '- `tehran-december-2024-source-values.csv`: all 11,767 selected records.', '- `random-500-source-values.csv`: seeded simple random sample of 500.', '- `12-neighborhood-examples.csv`: one seeded example in each of 12 high-count neighborhoods.', '- `review-provenance.json`: exact selection, source hash and rights notices.','', 'All CSV files use UTF-8 with BOM for spreadsheet compatibility. Original source fields are preserved. Empty cells are missing, not zero. No price per square metre is calculated.','', '| Review ID | Neighborhood source slug | Month | Original price_value | Original building_size (m²) | Rooms (source) | Construction year (source) |','|---|---|---|---:|---:|---|---|']
        for row in examples.itertuples(index=False):
            lines.append(f'| {row.review_id} | {row.neighborhood_slug} | {row.created_at_month[:7]} | {int(float(row.price_value)):,} | {row.building_size} | {row.rooms_count or "missing"} | {row.construction_year or "missing"} |')
        lines[2]=f'Actual official-source records, revision `{REVISION}`. Period: December 2024. Full selected file: {len(selected):,} records. Price meaning is owner-confirmed as total apartment asking price in toman. This export preserves original values and does not compute price/m². It is private source inspection, not a metro finding.'
        lines += ['', 'The owner has confirmed the field meaning and unit. Individual erroneous, placeholder or installment-like values may still need review. Record such issues separately from the interpretation evidence; do not rescale suspicious values without source support.']
        (folder/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        state['validation']=['Exact candidate count 11767 reproduced','Original source strings retained','No per-m2 calculation or currency conversion','No property coordinates, descriptions, seller fields or titles exported','All output stays in ignored private run folder']
        state['outputs']=[str(p.relative_to(ROOT)) for p in folder.iterdir() if p.is_file()]
        print(json.dumps({'folder':str(folder.relative_to(ROOT)),'rows':len(selected),'examples':examples[['review_id','neighborhood_slug','price_value','building_size','rooms_count','construction_year']].to_dict(orient='records')},ensure_ascii=True))

if __name__=='__main__': main()
