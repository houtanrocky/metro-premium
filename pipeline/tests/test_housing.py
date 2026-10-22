from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import yaml
from metropremium.provenance import ROOT, REVISION
from metropremium.price_contract import load_price_contract
from metropremium.housing import price_descriptives
from metropremium.cleaning import prepare
from metropremium.aggregation import summaries
from metropremium.synthetic import demo

def test_owner_price_evidence_is_scoped_and_not_publisher_verification(tmp_path):
    source=ROOT/'configs/price-contract.yaml'
    c=load_price_contract(source)
    assert c['denomination']=='toman' and c['price_basis']=='total_apartment_asking_price'
    assert c['verification_source']=='owner_confirmation'
    for key,value in [('revision','another-revision'),('publisher_documentation_verified',True),('scope',{}),('evidence','')]:
        changed=dict(c);changed[key]=value
        path=tmp_path/'contract.yaml';path.write_text(yaml.safe_dump(changed),encoding='utf-8')
        with pytest.raises(ValueError):load_price_contract(path)

def test_total_price_divides_by_area_without_currency_rescaling():
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    raw=df.iloc[:2].copy()
    raw['price_value']=[8_500_000_000,7_400_000_000]
    raw['building_size']=[60,90]
    cleaned,_=prepare(raw,config,load_price_contract(ROOT/'configs/price-contract.yaml'))
    assert cleaned.per_m2.iloc[0]==pytest.approx(141_666_666.6667)
    assert cleaned.per_m2.iloc[1]==pytest.approx(82_222_222.2222)
    assert cleaned.price_value.iloc[0]==8_500_000_000

def test_observed_price_distribution_and_tail_sensitivity_preserve_baseline():
    values=np.arange(1,102,dtype=float)
    values[-1]=1e9
    df=pd.DataFrame({'per_m2':values,'price_value':values*80,'building_size':80,'month':'2024-12','duplicate_candidate':[False]*100+[True]})
    result=price_descriptives(df,minimum=30)
    assert result['n']==101
    assert result['median_per_m2']==51
    assert result['q25_per_m2']==26 and result['q75_per_m2']==76
    assert result['tail_rule']['flagged_n']==2
    assert result['tail_rule']['default_excludes_tails'] is False
    assert result['variants'][1]['n']==99
    assert result['variants'][2]['n']==100
    assert len(df)==101

def test_insufficient_samples_and_cross_period_pooling_are_not_published():
    df=pd.DataFrame({'per_m2':[1.,2.],'price_value':[100.,200.],'building_size':[100,100],'month':['2024-12','2025-01'],'duplicate_candidate':[False,False]})
    assert price_descriptives(df)['status']=='insufficient_sample'
    with pytest.raises(ValueError,match='single common month'):price_descriptives(df,minimum=2)

def test_neighborhood_measured_price_denominator_cannot_borrow_group_count():
    df=pd.DataFrame({'per_m2':[100.]*29+[np.nan]*11,'neighborhood_slug':'SYNTHETIC','month':'2024-12','coordinate_valid':True,'radius_valid':False,'route_status':'network_not_validated'})
    row=summaries(df)[0]
    assert row['n']==40 and row['price_n']==0 and row['median_per_m2'] is None
    assert row['median_network_m'] is None and row['comparison_eligible'] is False
