import numpy as np
import pytest
import yaml
from metropremium.cleaning import number, parse_month, prepare
from metropremium.synthetic import demo
from metropremium.provenance import ROOT
from metropremium.aggregation import assert_public_safe,summaries

@pytest.fixture
def config():return yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())

def test_numerals_dates_and_censored_values():
    assert number('۱۲۳٬۴۵۶')==123456
    assert np.isnan(number('ثلاث'))
    assert number('دو')==2
    assert np.isnan(number('۳۰ سال به بالا'))
    assert parse_month('۲۰۲۴-۰۵-01 00:00:00')=='2024-05'
    assert parse_month('2024-13') is None
    assert parse_month('2024-02-09') is None

def test_population_filters_missing_coordinates_and_price_contract(config):
    df,_,_=demo(config)
    df=df.iloc[:8].copy().reset_index(drop=True)
    df.loc[0,'cat3_slug']='apartment-rent'
    df.loc[1,'price_value']=0
    df.loc[2,'building_size']=0
    df.loc[3,'location_latitude']=91
    df.loc[4,'price_mode']='توافقی'
    df.loc[5,'created_at_month']='invalid'
    df.loc[6,'location_radius']=None
    cleaned,flow=prepare(df,config,{'total_price_verified':False})
    assert len(cleaned)==3
    assert flow['final_rows']==3
    assert cleaned.per_m2.isna().all()
    assert not bool(cleaned.loc[3,'coordinate_valid'])
    assert not bool(cleaned.loc[6,'radius_valid'])
    assert sum(row['excluded'] for row in flow['flow'])==5

def test_price_per_m2_and_duplicates_are_flags_not_silent_removal(config):
    df,_,_=demo(config)
    import pandas as pd
    raw=pd.concat([df.iloc[:1],df.iloc[:1]],ignore_index=True)
    cleaned,flow=prepare(raw,config,{'total_price_verified':True})
    assert cleaned.per_m2.iloc[0]==pytest.approx(cleaned.price_value.iloc[0]/cleaned.building_size.iloc[0])
    assert len(cleaned)==2 and flow['duplicate_candidates']==1

def test_public_boundary_and_small_group_suppression(config):
    df,_,_=demo(config)
    assert summaries(df.iloc[:2],minimum=30)==[]
    for payload in [{'location_latitude':1},{'nested':[{'description':'private'}]},{'n':float('nan')}]:
        with pytest.raises(ValueError):assert_public_safe(payload)
    assert_public_safe({'n':30,'median_per_m2':None})
