"""Staged associations with explicit identifiability and covariance checks."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from scipy.spatial import cKDTree

def model_frame(frame):
    required = ['per_m2','network_m','building_size','rooms_count','construction_year','floor','neighborhood_slug','month','has_parking','has_elevator','has_warehouse']
    df = frame.dropna(subset=required).copy()
    df = df.loc[(df.per_m2>0) & (df.network_m>=0) & (df.building_size>0)]
    df['log_price'] = np.log(df.per_m2)
    df['distance_km'] = df.network_m/1000
    df['log_area'] = np.log(df.building_size)
    return df

def fit_models(frame, minimum_n=100, minimum_clusters=30):
    df = model_frame(frame)
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
        # A singleton fixed-effect group has unit leverage: Cook's distance is
        # undefined there. Preserve that limitation rather than exporting NaN
        # or replacing it with zero. Coefficients retain their existing gates.
        leverage = np.asarray(influence.hat_matrix_diag)
        with np.errstate(divide='ignore', invalid='ignore'):
            cooks = np.asarray(influence.cooks_distance[0])
        defined = np.isfinite(cooks) & np.isfinite(leverage) & (leverage >= 0) & (leverage < 1 - 1e-10)
        item = {'name':name,'status':'estimated','formula':formula,'n':int(result.nobs),'clusters':int(clusters),'distance_coefficient_per_km':beta,'confidence_interval_95':ci,'association_percent_per_km':float(100*np.expm1(beta)),'association_percent_ci_95':(100*np.expm1(ci)).tolist(),'r_squared':float(result.rsquared),'condition_number':float(result.condition_number),'breusch_pagan_pvalue':float(het_breuschpagan(resid,x)[1]),'max_cooks_distance':float(cooks[defined].max()) if defined.any() else None,'cooks_distance_defined_n':int(defined.sum()),'cooks_distance_undefined_n':int((~defined).sum()),'influence_diagnostic_caveat':'Maximum over defined Cook distances only; nonfinite values or leverage within 1e-10 of one are excluded and counted, not replaced with zero.','residual_quantiles':np.quantile(resid,[.01,.25,.5,.75,.99]).tolist()}
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


def spatial_wild_bootstrap(frame, draws=199, block_m=2000, seed=0):
    """Fixed-design spatial-cell wild bootstrap, a covariance sensitivity check.

    One Rademacher residual multiplier per projected grid cell. Adjacent cells
    need not be independent, so the percentile range is not a calibrated spatial
    confidence interval. Do not use it to assert robustness or causality.
    """
    if draws<1 or block_m<=0: raise ValueError('Positive draw count and block size required')
    df=model_frame(frame)
    if not {'x','y'}.issubset(df) or df[['x','y']].isna().any().any():
        return {'status':'missing_projected_origins','models':[]}
    baseline=fit_models(frame)
    labels=pd.MultiIndex.from_arrays([np.floor(df.x/block_m),np.floor(df.y/block_m)])
    codes,unique=pd.factorize(labels,sort=True)
    out={'method':'Fixed-design residual wild bootstrap, Rademacher sign per projected spatial cell; percentile sensitivity range, not calibrated spatial CI', 'seed':seed,'draws':draws,'block_m':block_m,'spatial_cells':len(unique),'n':len(df),'status':'computed','models':[]}
    if len(unique)<20 or baseline['status']!='estimated':
        return dict(out,status='insufficient_spatial_cells_or_model_sample')
    rng=np.random.default_rng(seed)
    signs=rng.choice([-1.,1.],size=(draws,len(unique)))[:,codes]
    for entry in baseline['models']:
        if entry['status']!='estimated':continue
        fitted=smf.ols(entry['formula'],df).fit()
        row=np.linalg.pinv(fitted.model.exog)[fitted.model.exog_names.index('distance_km')]
        residual=np.asarray(fitted.resid)
        # HC2 leverage correction within the fixed design.
        leverage=fitted.get_influence().hat_matrix_diag
        adjusted=residual/np.sqrt(np.maximum(1-leverage,1e-6))
        coefficients=float(fitted.params['distance_km'])+signs@(row*adjusted)
        out['models'].append({'name':entry['name'],'coefficient_quantiles_025_50_975':np.quantile(coefficients,[.025,.5,.975]).tolist(),'failed_draws':0})
    return out

def sensitivity_models(df, minimum_group=30):
    variants = {'baseline':df, 'candidate_deduplicated':df.loc[~df.duplicate_candidate], 'without_flagged_price_tails':df.loc[~df.tail_flag], 'radius_at_most_100m':df.loc[df.location_radius.le(100)], 'radius_at_most_250m':df.loc[df.location_radius.le(250)]}
    if 'euclidean_m' in df:
        variants['euclidean_distance'] = df.assign(network_m=df.euclidean_m)
    results = {key:fit_models(value) for key,value in variants.items()}
    # Threshold comparisons are summaries, not regressions at arbitrarily selected cutoffs.
    results['threshold_summaries'] = []
    results['suppressed_thresholds_m'] = []
    for t in [400,500,800,1000,1500]:
        near = df.loc[df.network_m.le(t) & df.per_m2.notna(), 'per_m2']
        far = df.loc[df.network_m.gt(t) & df.per_m2.notna(), 'per_m2']
        if min(len(near), len(far)) < minimum_group:
            results['suppressed_thresholds_m'].append(t)
            continue
        results['threshold_summaries'].append({'threshold_m':t,'near_n':len(near),'far_n':len(far),'near_median':float(near.median()),'far_median':float(far.median())})
    results['threshold_minimum_group'] = minimum_group
    return results
