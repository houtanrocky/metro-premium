import json
import pandas as pd
from metropremium.audit import audit_source
from metropremium.provenance import ROOT
from metropremium.cleaning import prepare
from metropremium.synthetic import demo
import yaml

def test_actual_csv_schema_categories_nulls_and_duplicate_counts(tmp_path):
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    # Construct an explicitly synthetic raw CSV using only expected source fields.
    columns=['cat2_slug','cat3_slug','city_slug','neighborhood_slug','created_at_month','price_mode','price_value','building_size','construction_year','rooms_count','floor','total_floors_count','has_parking','has_elevator','has_warehouse','location_latitude','location_longitude','location_radius']
    raw=df[columns].iloc[:3].copy()
    raw['property_type']=None
    raw=pd.concat([raw,raw.iloc[[0]]],ignore_index=True)
    raw.loc[1,'cat3_slug']='apartment-rent'
    raw.loc[2,'location_radius']=None
    source=tmp_path/'source.csv';raw.to_csv(source,index=False)
    source.with_suffix('.csv.source.json').write_text(json.dumps({'repository':'SYNTHETIC','revision':'test'}))
    report,parquet=audit_source(source,tmp_path)
    assert report['total_observed_rows']==4
    assert report['column_count']==19
    assert report['tehran_apartment_sale_rows']==3
    assert report['exact_duplicates_selected']['excess_rows']==1
    assert report['missing_all']['property_type']==4
    assert len(pd.read_parquet(parquet))==3
    assert report['price_contract']['per_m2_enabled'] is False
