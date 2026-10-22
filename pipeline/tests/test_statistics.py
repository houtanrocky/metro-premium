import yaml
import numpy as np
from metropremium.provenance import ROOT
from metropremium.synthetic import demo
from metropremium.statistics import fit_models

def test_synthetic_coefficient_recovery_and_shared_complete_case_sample():
    c=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(c)
    result=fit_models(df)
    assert result['status']=='estimated'
    assert len(result['models'])==3
    adjusted=result['models'][-1]
    assert adjusted['confidence_interval_95'][0]<-.12<adjusted['confidence_interval_95'][1]
    assert abs(adjusted['distance_coefficient_per_km']+.12)<.05
    assert len(set(m['n'] for m in result['models']))==1
    assert 'exploratory_knn_moran_i' in adjusted
    assert adjusted['association_percent_per_km']==100*np.expm1(adjusted['distance_coefficient_per_km'])

def test_no_invented_rows_on_insufficient_or_constant_sample():
    c=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(c)
    assert fit_models(df.iloc[:20])['models']==[]
    df['network_m']=5
    assert fit_models(df)['models']==[]

def test_missingness_does_not_turn_into_zero_covariates():
    c=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(c)
    df.loc[:99,'construction_year']=np.nan
    r=fit_models(df)
    assert r['diagnostics']['complete_case_n']==1100
