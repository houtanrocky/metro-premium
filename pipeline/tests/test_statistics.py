import yaml
import numpy as np
import json
import pytest
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


def test_singleton_fixed_effect_keeps_undefined_influence_explicit():
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    df.loc[df.index[0],'neighborhood_slug']='SYNTHETIC_SINGLETON'
    result=fit_models(df)
    adjusted=next(m for m in result['models'] if m['name']=='M3')
    assert adjusted['status']=='estimated'
    assert adjusted['cooks_distance_undefined_n']>=1
    assert adjusted['cooks_distance_defined_n']+adjusted['cooks_distance_undefined_n']==adjusted['n']
    assert adjusted['max_cooks_distance'] is None or np.isfinite(adjusted['max_cooks_distance'])
    json.dumps(result,allow_nan=False)


@pytest.mark.parametrize('near_count',[29,30])
def test_threshold_exports_enforce_privacy_for_both_comparison_groups(monkeypatch,near_count):
    from metropremium import statistics
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    df=df.iloc[:near_count+40].copy()
    df['network_m']=np.r_[np.full(near_count,100.),np.full(40,2000.)]
    monkeypatch.setattr(statistics,'fit_models',lambda frame:{'status':'synthetic_privacy_test_no_model_fit'})
    result=statistics.sensitivity_models(df)
    if near_count<30:
        assert result['threshold_summaries']==[]
        assert len(result['suppressed_thresholds_m'])==5
    else:
        assert len(result['threshold_summaries'])==5
        assert all(min(row['near_n'],row['far_n'])>=30 for row in result['threshold_summaries'])
