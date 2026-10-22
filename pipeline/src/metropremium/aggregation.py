"""Only explicit aggregate allowlists can cross the public boundary."""
import numpy as np

def summaries(df, minimum=30):
    out = []
    for (neighborhood,month), group in df.groupby(['neighborhood_slug','month']):
        measured = group.loc[group.per_m2.notna()]
        if len(group)<minimum:
            continue
        routed = group.loc[group.route_status.eq('ok')] if 'route_status' in group else group.iloc[:0]
        out.append({'neighborhood':str(neighborhood),'month':str(month),'n':len(group),'price_n':len(measured) if len(measured)>=minimum else 0,'median_per_m2':float(measured.per_m2.median()) if len(measured)>=minimum else None,'q25_per_m2':float(measured.per_m2.quantile(.25)) if len(measured)>=minimum else None,'q75_per_m2':float(measured.per_m2.quantile(.75)) if len(measured)>=minimum else None,'routed_n':len(routed) if len(routed)>=minimum else 0,'median_network_m':float(routed.network_m.median()) if len(routed)>=minimum else None,'coordinate_coverage':round(float(group.coordinate_valid.mean()),3),'known_radius_coverage':round(float(group.radius_valid.mean()),3),'comparison_eligible':False})
    return out

def band_summaries(df, minimum=30):
    out = []
    if 'band' not in df:
        return out
    for (month,band), group in df.loc[df.route_status.eq('ok')].groupby(['month','band']):
        if len(group)<minimum or group.per_m2.notna().sum()<minimum:
            continue
        out.append({'month':str(month),'band':int(band),'n':len(group),'median_per_m2':float(group.per_m2.median()),'q25':float(group.per_m2.quantile(.25)),'q75':float(group.per_m2.quantile(.75))})
    return out

def assert_public_safe(payload):
    forbidden = {'location_latitude','location_longitude','description','title','source_row','x','y','coordinates','price_value_raw'}
    def check(value):
        if isinstance(value,dict):
            if forbidden & set(value):
                raise ValueError('Listing-level data at public boundary')
            for child in value.values(): check(child)
        elif isinstance(value,list):
            for child in value: check(child)
        elif isinstance(value,float) and not np.isfinite(value):
            raise ValueError('Nonfinite public value')
    check(payload)
