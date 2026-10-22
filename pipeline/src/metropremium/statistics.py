"""Staged associations with explicit identifiability and covariance checks."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy.spatial import cKDTree

def fit_models(frame, minimum_n=100, minimum_clusters=30):
    required = ['per_m2','network_m','building_size','rooms_count','construction_year','floor','neighborhood_slug','month','has_parking','has_elevator','has_warehouse']
    df = frame.dropna(subset=required).copy()
    df = df.loc[(df.per_m2>0) & (df.network_m>=0)]
    df['log_price'] = np.log(df.per_m2)
    df['distance_km'] = df.network_m/1000
    df['log_area'] = np.log(df.building_size)
    clusters = df.neighborhood_slug.nunique()
    diagnostics = {'input_n':len(frame),'complete_case_n':len(df),'clusters':int(clusters),'covariance':'neighborhood-clustered CR1, t inference; no causal identification','limitations':['Clustered errors do not remove spatial confounding or account for all cross-neighborhood dependence.','Complete-case analysis may change sample composition.']}
    if len(df)<minimum_n or clusters<minimum_clusters:
        return {'status':'insufficient_sample','diagnostics':diagnostics,'models':[]}
    if df.distance_km.std()<1e-8:
        return {'status':'no_accessibility_variation','diagnostics':diagnostics,'models':[]}
    property_terms = 'log_area + rooms_count + construction_year + floor + C(has_parking) + C(has_elevator) + C(has_warehouse)'
    equations = [('M1','log_price ~ distance_km'),('M2',f'log_price ~ distance_km + {property_terms}'),('M3',f'log_price ~ distance_km + {property_terms} + C(neighborhood_slug) + C(month)')]
    within = df.distance_km-df.groupby('neighborhood_slug').distance_km.transform('mean')
    diagnostics['within_neighborhood_sd_km'] = float(within.std())
    output = []
    for name, formula in equations:
        if name=='M3' and within.std()<.01:
            output.append({'name':name,'status':'insufficient_within_neighborhood_variation'})
            continue
        model = smf.ols(formula,df)
        x = model.exog
        rank = np.linalg.matrix_rank(x)
        if rank<x.shape[1] or len(df)<5*x.shape[1]:
            output.append({'name':name,'status':'rank_deficient_or_sample_too_small','rank':int(rank),'parameters':x.shape[1]})
            continue
        result = model.fit(cov_type='cluster',cov_kwds={'groups':df.neighborhood_slug,'use_correction':True},use_t=True)
        ci = result.conf_int().loc['distance_km'].tolist()
        beta = float(result.params['distance_km'])
        influence = result.get_influence()
        resid = np.asarray(result.resid)
        item = {'name':name,'status':'estimated','formula':formula,'n':int(result.nobs),'clusters':int(clusters),'distance_coefficient_per_km':beta,'confidence_interval_95':ci,'association_percent_per_km':float(100*np.expm1(beta)),'association_percent_ci_95':(100*np.expm1(ci)).tolist(),'r_squared':float(result.rsquared),'condition_number':float(result.condition_number),'breusch_pagan_pvalue':float(het_breuschpagan(resid,x)[1]),'max_cooks_distance':float(influence.cooks_distance[0].max()),'residual_quantiles':np.quantile(resid,[.01,.25,.5,.75,.99]).tolist()}
        # Exploratory residual spatial structure, kNN at approximate origins; not a significance test.
        if {'x','y'}.issubset(df.columns) and df[['x','y']].notna().all().all():
            _, nn = cKDTree(df[['x','y']]).query(df[['x','y']],k=min(9,len(df)))
            z = resid-resid.mean()
            # Coincident coordinates mean the first returned neighbor is not always self.
            neighbors=np.array([row[row!=i][:nn.shape[1]-1] for i,row in enumerate(nn)])
            item['exploratory_knn_moran_i'] = float(np.sum(z[:,None]*z[neighbors])/((nn.shape[1]-1)*np.sum(z*z))) if np.sum(z*z)>0 else None
            item['spatial_diagnostic_caveat'] = 'Directed row-standardized 8NN residual Moran I; approximate coordinates, duplicated origins and no permutation inference.'
        output.append(item)
    return {'status':'estimated','diagnostics':diagnostics,'models':output}

def sensitivity_models(df):
    variants = {'baseline':df, 'candidate_deduplicated':df.loc[~df.duplicate_candidate], 'without_flagged_price_tails':df.loc[~df.tail_flag], 'radius_at_most_100m':df.loc[df.location_radius.le(100)], 'radius_at_most_250m':df.loc[df.location_radius.le(250)]}
    if 'euclidean_m' in df:
        variants['euclidean_distance'] = df.assign(network_m=df.euclidean_m)
    results = {key:fit_models(value) for key,value in variants.items()}
    # Threshold comparisons are summaries, not regressions at arbitrarily selected cutoffs.
    results['threshold_summaries'] = [{'threshold_m':t,'near_n':int(df.network_m.le(t).sum()),'far_n':int(df.network_m.gt(t).sum()),'near_median':float(df.loc[df.network_m.le(t),'per_m2'].median()) if df.network_m.le(t).any() else None,'far_median':float(df.loc[df.network_m.gt(t),'per_m2'].median()) if df.network_m.gt(t).any() else None} for t in [400,500,800,1000,1500]]
    return results
