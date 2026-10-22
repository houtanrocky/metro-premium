"""Explicit sample flow; conservative exclusions and reversible sensitivity flags."""
import re
import numpy as np
import pandas as pd

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
WORDS = {'بدون اتاق': 0, 'بدون': 0, 'یک': 1, 'دو': 2, 'سه': 3, 'چهار': 4, 'پنج': 5, 'همکف': 0, 'زیرزمین': -1}

def number(value):
    if pd.isna(value):
        return np.nan
    s = str(value).strip().translate(DIGITS).replace(',', '').replace('٬', '')
    if s in WORDS:
        return float(WORDS[s])
    if not re.fullmatch(r'-?\d+(\.\d+)?', s):
        return np.nan
    result = float(s)
    return result if np.isfinite(result) else np.nan

def parse_month(value):
    if pd.isna(value):
        return None
    s = str(value).translate(DIGITS)
    if not re.fullmatch(r'\d{4}-\d{2}(-01( 00:00:00)?)?', s):
        return None
    try:
        return pd.Timestamp(s).strftime('%Y-%m')
    except ValueError:
        return None

def prepare(frame, config, price_contract):
    df = frame.copy()
    flow = []
    def retain(stage, mask):
        nonlocal df
        before = len(df)
        df = df.loc[mask].copy()
        flow.append({'stage': stage, 'before': before, 'after': len(df), 'excluded': before-len(df)})
    retain('tehran_apartment_sale', (df.city_slug == 'tehran') & (df.cat2_slug == 'residential-sell') & (df.cat3_slug == 'apartment-sell'))
    df['month'] = df.created_at_month.map(parse_month)
    retain('parseable_month', df.month.notna())
    period = config['period']
    if period == 'auto-largest-2024-month':
        counts = df.loc[df.month.str.startswith('2024'), 'month'].value_counts()
        if counts.empty:
            raise ValueError('No 2024 observations: explicitly revise period after audit')
        period = sorted(counts.index, key=lambda x: (-counts[x], x))[0]
    if period != 'synthetic':
        retain('single_month:' + period, df.month == period)
    for col in ['price_value','building_size','location_latitude','location_longitude','location_radius','construction_year','rooms_count','floor','total_floors_count']:
        df[col + '_raw'] = df[col]
        df[col] = df[col].map(number)
    retain('fixed_positive_finite_price', (df.price_mode == 'مقطوع') & df.price_value.gt(0) & np.isfinite(df.price_value))
    lo, hi = config['size_range_m2']
    retain('area_range', df.building_size.between(lo, hi))
    df['coordinate_valid'] = df.location_latitude.between(35.45,35.9) & df.location_longitude.between(51.05,51.65)
    df['radius_valid'] = df.location_radius.between(0, config['location_radius_max_m'])
    # No fabricated age: source years use Solar Hijri; recode implausible and censored labels to missing.
    df['construction_year'] = df.construction_year.where(df.construction_year.between(1300,1403))
    df['rooms_count'] = df.rooms_count.where(df.rooms_count.between(0,5))
    for col in ['has_parking','has_elevator','has_warehouse']:
        df[col] = df[col].map(lambda x: str(x).lower() if pd.notna(x) else 'missing')
        df.loc[~df[col].isin(['true','false','missing']), col] = 'missing'
    # Potential duplicates are NOT removed by default. They are flagged for sensitivity.
    key = ['neighborhood_slug','month','price_value','building_size','rooms_count','construction_year','floor','has_parking','has_elevator','has_warehouse','location_latitude','location_longitude']
    df['duplicate_candidate'] = df.duplicated(key, keep='first')
    df['per_m2'] = df.price_value / df.building_size if price_contract.get('total_price_verified') else np.nan
    if df.per_m2.notna().any():
        lower, upper = df.per_m2.quantile([.005,.995])
        df['tail_flag'] = ~df.per_m2.between(lower,upper)
    else:
        df['tail_flag'] = False
    # Retain price-valid rows for reporting missing-coordinate selection bias; route only valid subset.
    return df, {'flow': flow, 'period': period, 'final_rows': len(df), 'coordinate_valid_rows': int(df.coordinate_valid.sum()), 'known_radius_rows': int(df.radius_valid.sum()), 'routable_candidate_rows': int((df.coordinate_valid & df.radius_valid).sum()), 'duplicate_candidates': int(df.duplicate_candidate.sum()), 'tail_flagged': int(df.tail_flag.sum()), 'price_contract': price_contract}
