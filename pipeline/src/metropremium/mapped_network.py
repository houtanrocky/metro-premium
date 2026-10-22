"""Executable empirical extension: historical *mapped subset*, not certified service.

No geographic proximity is used to invent station membership or transfers.
"""
from collections import Counter, defaultdict
import json
import math
import pickle
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon

from .accessibility import Router, project, band
from .geographic import walking_from_elements
from .metro_reference import extract_guide, normalize_name, DIGITS
from .provenance import ROOT, digest, write_json
from .statistics import fit_models, sensitivity_models, spatial_wild_bootstrap
from .aggregation import band_summaries

SNAPSHOT = '2024-12-01T00:00:00Z'
BBOX = (51.02, 35.42, 51.68, 35.93)
WARNING = 'Exploratory distances to an incomplete retained subset of OSM-mapped entrances at 2024-12-01; operational eligibility, entrance completeness and physical walking routes are not independently certified. Not nearest operational metro access or a causal effect.'


def checked_json(path):
    sidecar = Path(str(path) + '.source.json')
    meta = json.loads(sidecar.read_text(encoding='utf-8'))
    if digest(path) != meta['sha256'] or path.stat().st_size != meta['bytes']:
        raise ValueError(f'OSM cached source failed checksum: {path.name}')
    if 'inputs' in meta:
        if meta.get('requested_snapshot')!=SNAPSHOT:raise ValueError('Derived source snapshot mismatch')
        for entry in meta['inputs']:
            child=path.parent/entry['file']
            checked_json(child)
            if digest(child)!=entry['sha256']:raise ValueError('Derived source input mismatch')
    elif f'date%3A%22{SNAPSHOT.replace(":", "%3A")}' not in meta['url']:
        # Compare decoded query rather than trusting a descriptive file name.
        from urllib.parse import unquote_plus
        if f'[date:"{SNAPSHOT}"]' not in unquote_plus(meta['url']):
            raise ValueError('OSM source does not request the declared historical snapshot')
    raw = json.loads(path.read_text(encoding='utf-8'))
    if raw.get('remark') or not raw.get('elements'):
        raise ValueError('Incomplete/empty Overpass result')
    return raw


def entrance_inventory(elements, guide):
    """Strict historical route -> stop area -> entrance join + guide identity.

    Names are exact after orthographic normalization. Branches are matched only
    to routes with a corresponding exact name and parent line, never proximity.
    """
    objects = {(e['type'], e['id']): e for e in elements}
    guide_names = defaultdict(set)
    for route in guide['routes']:
        guide_names[route['parent_line']].update(s['normalized_name'] for s in route['stations'])
    stops = defaultdict(set)
    line_stats = defaultdict(lambda: {'route_relations':[], 'stop_nodes':set(), 'identity_matched_nodes':set(), 'retained_entrances':set()})
    for e in objects.values():
        tags = e.get('tags', {})
        line = tags.get('ref', '').translate(DIGITS)
        if e['type'] != 'relation' or tags.get('route') not in {'subway','train'} or line not in guide_names or tags.get('network:wikidata') != 'Q714823':
            continue
        line_stats[line]['route_relations'].append(e['id'])
        for member in e.get('members', []):
            if member['type'] != 'node' or member.get('role') not in {'stop','stop_entry_only','stop_exit_only','platform'}:
                continue
            obj = objects.get(('node', member['ref']), {})
            ot = obj.get('tags', {})
            if ot.get('railway') in {'proposed','construction','disused','abandoned'}:
                continue
            line_stats[line]['stop_nodes'].add(member['ref'])
            stops[member['ref']].add(line)
    candidates = {e['id']: e for e in objects.values() if e['type']=='node' and e.get('tags',{}).get('railway')=='subway_entrance'}
    retained = {}
    area_review = []
    def names(obj):
        tags = obj.get('tags', {})
        return {normalize_name(n.strip()) for key in ['name','name:fa','official_name','alt_name','old_name','short_name'] for n in tags.get(key,'').split(';') if n.strip()}
    for area in objects.values():
        if area['type']!='relation' or area.get('tags',{}).get('public_transport')!='stop_area':
            continue
        members = [objects.get((m['type'],m['ref']),{}) for m in area.get('members',[])]
        member_stops = [m for m in area.get('members',[]) if m['type']=='node' and m['ref'] in stops]
        if not member_stops: continue
        identities = names(area)
        for obj in members:
            if obj.get('tags',{}).get('railway') in {'station','stop'}:
                identities.update(names(obj))
        lines = sorted({line for m in member_stops for line in stops[m['ref']] if identities & guide_names[line]})
        entrances = [candidates[m['ref']] for m in area.get('members',[]) if m['type']=='node' and m['ref'] in candidates]
        area_review.append({'stop_area':area['id'],'name':area.get('tags',{}).get('name'), 'route_lines':sorted({line for m in member_stops for line in stops[m['ref']]}),'guide_identity_lines':lines,'entrances_in_relation':len(entrances)})
        if not lines: continue
        for member in member_stops:
            for line in stops[member['ref']] & set(lines):
                line_stats[line]['identity_matched_nodes'].add(member['ref'])
        for e in entrances:
            tags = e.get('tags',{})
            if tags.get('access') in {'no','private'} or tags.get('foot') in {'no','private'} or tags.get('disused')=='yes': continue
            x,y = project(e['lon'],e['lat'])
            record = retained.setdefault(e['id'], {'id':str(e['id']), 'x':x, 'y':y, 'longitude':e['lon'], 'latitude':e['lat'], 'lines':set(), 'stop_areas':set(), 'station_names':set(), 'verified':True, 'eligible':True, 'verification_scope':'OSM historical tag + explicit membership + guide identity only; operation not certified'})
            record['lines'].update(lines)
            record['stop_areas'].add(area['id'])
            record['station_names'].add(area.get('tags',{}).get('name',''))
            for line in lines: line_stats[line]['retained_entrances'].add(e['id'])
    output = []
    for record in retained.values():
        output.append({k:sorted(v) if isinstance(v,set) else v for k,v in record.items()})
    reports = [{ 'line':line, **{k:sorted(v) if isinstance(v,set) else v for k,v in data.items()}} for line,data in sorted(line_stats.items())]
    return output, {'mapped_entrance_nodes':len(candidates),'retained_entrance_nodes':len(output),'excluded_entrance_nodes':sorted(set(candidates)-set(retained)), 'lines':reports,'stop_area_checks':area_review, 'opening_dates_verified':False, 'physical_routes_verified':False, 'rule': 'historical explicit membership + active mapped route tag + exact guide identity; no spatial station assignment', 'warning':WARNING}


def load_mapped_graph(raw_dir):
    source = raw_dir/'walk.json'
    raw = checked_json(source)
    fingerprint = digest(source)
    cache = ROOT/'data/intermediate/networks'/f'walk-v2-{fingerprint}.pickle'
    metadata = cache.with_suffix('.json')
    if cache.exists() and metadata.exists():
        meta = json.loads(metadata.read_text(encoding='utf-8'))
        if meta['sha256'] != digest(cache): raise ValueError('Derived graph checksum mismatch')
        with cache.open('rb') as stream: graph = pickle.load(stream) # local, hash-checked cache only
        report = meta['report']
    else:
        graph,_,report = walking_from_elements(raw['elements'])
        graph.graph.update(source='Historical OSM Overpass', snapshot=SNAPSHOT, historical=True)
        report.update(scope='Buffered Tehran study rectangle; historically mapped walking ways, not certified physical access', snapshot=SNAPSHOT, acquisition_bbox=BBOX)
        cache.parent.mkdir(parents=True,exist_ok=True)
        with cache.open('wb') as stream: pickle.dump(graph,stream,protocol=5)
        write_json(metadata,{'sha256':digest(cache),'report':report})
    return graph,report


def boundary_clearance(x, y):
    # Densify WGS84 rectangle sides before projection so its curved projected
    # boundary is represented to sub-metre accuracy at this scale.
    west,south,east,north = BBOX
    corners = [(west,south),(east,south),(east,north),(west,north),(west,south)]
    ring=[]
    for a,b in zip(corners,corners[1:]):
        ring.extend(project(a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])) for t in np.linspace(0,1,101,endpoint=False))
    boundary = Polygon(ring)
    return np.array([Point(px,py).distance(boundary.boundary) if boundary.covers(Point(px,py)) else 0 for px,py in zip(x,y)])


def route_frame(frame, router, candidates_only=True):
    df=frame.copy()
    df['route_status']='missing_or_invalid_coordinate'
    for col in ['x','y','network_m','euclidean_m','walking_minutes','ratio','band','origin_snap_m','boundary_clearance_m']:
        df[col]=np.nan
    valid=df.coordinate_valid & (df.radius_valid if candidates_only else True)
    df.loc[df.coordinate_valid & ~valid,'route_status']='unknown_or_excessive_radius'
    indices=df.index[valid]
    xy=np.array([project(lon,lat) for lon,lat in zip(df.loc[indices,'location_longitude'],df.loc[indices,'location_latitude'])])
    if len(xy)==0:return df
    df.loc[indices,['x','y']]=xy
    df.loc[indices,'boundary_clearance_m']=boundary_clearance(xy[:,0],xy[:,1])
    for idx,(x,y) in zip(indices,xy):
        result=router.route(x,y)
        df.loc[idx,'route_status']=result['status']
        for col in ['network_m','euclidean_m','walking_minutes','ratio','band','origin_snap_m']:
            if col in result:df.loc[idx,col]=result[col]
        if result['status']=='ok' and result['network_m'] >= df.loc[idx,'boundary_clearance_m'] - 1:
            df.loc[idx,'route_status']='boundary_sensitive'
    return df


def numeric_summary(values):
    values=pd.Series(values).replace([np.inf,-np.inf],np.nan).dropna()
    return {'n':len(values),'q05':float(values.quantile(.05)),'q25':float(values.quantile(.25)), 'median':float(values.median()),'q75':float(values.quantile(.75)), 'q95':float(values.quantile(.95))} if len(values) else {'n':0}


def mapped_analysis(cleaned, config, folder):
    if config.get('snapshot')!=SNAPSHOT:
        raise ValueError('Mapped analysis configuration snapshot mismatch')
    raw_dir=ROOT/'data/raw/osm/historical-20241201'
    raw=checked_json(raw_dir/'metro.json')
    if (raw_dir/'line5.json').exists():raw['elements'].extend(checked_json(raw_dir/'line5.json')['elements'])
    guide=extract_guide((ROOT/'data/raw/references/alibaba/tehran-subway-guide.html').read_text(encoding='utf-8'))
    entrances,inventory=entrance_inventory(raw['elements'],guide)
    write_json(folder/'mapped-entrance-inventory.json',inventory)
    write_json(folder/'mapped-entrances-private.json',entrances)
    retained_by_id={e['id']:e for e in entrances}
    pd.DataFrame([{'osm_entrance_node':e['id'],'longitude':e['lon'],'latitude':e['lat'],'snapshot':SNAPSHOT,'station_names':' | '.join(retained_by_id.get(str(e['id']),{}).get('station_names',[])),'lines':';'.join(retained_by_id.get(str(e['id']),{}).get('lines',[])),'stop_area_relations':';'.join(map(str,retained_by_id.get(str(e['id']),{}).get('stop_areas',[]))),'retained_as_mapped':str(e['id']) in retained_by_id,'operation_verified':False} for e in raw['elements'] if e['type']=='node' and e.get('tags',{}).get('railway')=='subway_entrance']).drop_duplicates('osm_entrance_node').to_csv(folder/'station-entrance-review.csv',index=False,encoding='utf-8-sig')
    graph,graph_report=load_mapped_graph(raw_dir)
    router=Router(graph,entrances,max_snap_m=config['max_snap_m'],speed=config['walking_speed_m_per_min'])
    routed=route_frame(cleaned,router)
    routed.to_parquet(folder/'mapped-accessibility.parquet',index=False)
    good=routed.loc[routed.route_status.eq('ok')].copy()
    n=len(good)
    if n==0: raise ValueError('No supported empirical routes; investigate network and joins')
    if (good.network_m+1e-5<good.euclidean_m).any():raise ValueError('Triangle inequality violation')
    models=fit_models(good)
    sensitivity=sensitivity_models(good)
    for snap in [50,150]:
        alternative=route_frame(cleaned,Router(graph,entrances,max_snap_m=snap))
        sensitivity[f'snap_{snap}m']={'coverage':alternative.route_status.value_counts().to_dict(), 'analysis':fit_models(alternative.loc[alternative.route_status.eq('ok')])}
    spatial=spatial_wild_bootstrap(good, draws=config.get('spatial_bootstrap_draws',199), block_m=config.get('spatial_block_m',2000), seed=config['seed'])
    # Batched whole-sample draws retain aligned source rows for model refits.
    rng=np.random.default_rng(config['seed'])
    indices=routed.index[routed.coordinate_valid & routed.radius_valid]
    samples=routed.loc[indices].copy()
    instability=[]
    refits=[]
    nominal=routed.loc[indices,'band'].to_numpy()
    all_bands=[]
    successes=np.zeros(len(indices),dtype=int)
    for draw in range(config.get('location_draws',30)):
        angle=rng.uniform(0,2*np.pi,len(indices))
        radius=samples.location_radius.to_numpy()*np.sqrt(rng.uniform(0,1,len(indices)))
        sx=samples.x.to_numpy()+radius*np.cos(angle)
        sy=samples.y.to_numpy()+radius*np.sin(angle)
        clearance=boundary_clearance(sx,sy)
        results=[router.route(x,y) for x,y in zip(sx,sy)]
        bands=np.array([s.get('band',np.nan) if s['status']=='ok' and s['network_m']<c-1 else np.nan for s,c in zip(results,clearance)])
        all_bands.append(bands)
        successes+=np.isfinite(bands)
        if draw<config.get('model_perturbation_draws',10):
            perturbed=samples.copy()
            perturbed['network_m']=[s.get('network_m',np.nan) if np.isfinite(b) else np.nan for s,b in zip(results,bands)]
            perturbed['x']=sx;perturbed['y']=sy
            refits.append({'draw':draw,'analysis':fit_models(perturbed)})
    sampled=np.array(all_bands)
    nominal_ok=np.isfinite(nominal)
    changed=(sampled != nominal) & np.isfinite(sampled) & nominal_ok
    denom=np.sum(np.isfinite(sampled[:,nominal_ok]))
    uncertainty={'assumption':'Uniform area within each stated-radius disk; scenario, not the empirical error law. Failed draws remain failed, not straight-line replacements.', 'seed':config['seed'], 'draws_per_origin':len(sampled), 'origins':len(indices), 'nominal_supported_origins':int(nominal_ok.sum()), 'successful_draws':int(successes.sum()), 'total_draws':int(sampled.size), 'failure_fraction':float(1-successes.sum()/sampled.size), 'classification_change_fraction_among_successful_nominal_supported':float(changed.sum()/denom) if denom else None, 'fraction_nominal_supported_origins_ever_changing_band':float(np.mean(changed[:,nominal_ok].any(axis=0))) if nominal_ok.any() else None, 'model_refits':refits}
    write_json(folder/'mapped-location-sensitivity.json',uncertainty)
    result={'schema_version':1,'status':'exploratory_mapped_reference','warning':WARNING,'snapshot':SNAPSHOT,'period':str(cleaned.month.iloc[0]),'unit':'toman_per_m2','scope':{'price_valid_rows':len(cleaned),'coordinate_known_radius_candidates':len(indices),'supported_route_rows':n,'mapped_entrances':inventory['mapped_entrance_nodes'],'retained_entrances_before_snapping':len(entrances),'retained_entrances_after_snapping':len(router.entrances),'distinct_stop_areas':len({s for e in router.entrances for s in e['stop_areas']})}, 'coverage':{str(k):int(v) for k,v in routed.route_status.value_counts().items()},'walking':graph_report,'entrance_rejections':router.rejected_entrances,'network_m':numeric_summary(good.network_m),'euclidean_m':numeric_summary(good.euclidean_m),'ratio':numeric_summary(good.ratio),'walking_minutes':numeric_summary(good.walking_minutes),'bands':band_summaries(good,config['min_public_group']), 'models':models,'sensitivity':sensitivity,'spatial_sensitivity':spatial,'location_uncertainty':{k:v for k,v in uncertainty.items() if k!='model_refits'}, 'primary_quality_gate_passed':False,'public_routes_enabled':False,'public_stations_enabled':False}
    write_json(folder/'mapped-analysis.json',result)
    mapped_figure(result,folder)
    # Public OSM entrance features carry no listing coordinates. Quarantined
    # asset is an audit artifact; app must not imply verified operating service.
    write_json(folder/'mapped-entrance-source.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[e['longitude'],e['latitude']]},'properties':{k:e[k] for k in ['id','lines','stop_areas','station_names','verification_scope']}} for e in router.entrances]})
    return result


def mapped_figure(result,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt']='metropremium-mapped-v1'
    rows=result['bands']
    if not rows:return
    fig,axes=plt.subplots(1,2,figsize=(12,6),facecolor='#f7f5ef')
    labels=['0–500','500–1,000','1,000–1,500','>1,500']
    x=np.arange(len(rows))
    axes[0].bar(x,[r['n'] for r in rows],color='#167875')
    axes[0].set_ylabel('Supported listings (count)')
    median=np.array([r['median_per_m2']/1e6 for r in rows])
    axes[1].errorbar(x,median,yerr=[median-np.array([r['q25']/1e6 for r in rows]),np.array([r['q75']/1e6 for r in rows])-median],fmt='o',color='#167875',capsize=4)
    axes[1].set_ylabel('Million toman / m²; median and IQR (not CI)')
    for ax in axes:
        ax.set_xticks(x,[labels[r['band']] for r in rows]);ax.set_xlabel('Distance to retained mapped entrance subset (m)');ax.spines[['top','right']].set_visible(False)
    fig.suptitle('EXPLORATORY | Historical mapped entrance subset, not certified metro access',fontsize=12)
    fig.subplots_adjust(left=.08,right=.98,top=.85,bottom=.25,wspace=.28)
    fig.text(.03,.12,f"Divar {result['period']} | supported n={result['scope']['supported_route_rows']:,} | OSM snapshot {result['snapshot'][:10]}",fontsize=9)
    fig.text(.03,.075,'Asking prices; total-price/toman interpretation confirmed by owner. Not causal or current-market evidence.',fontsize=8)
    fig.text(.03,.035,'Incomplete entrances, uncertain locations, approximate connectors; primary quality gate remains closed. © OSM contributors / Divar, ODbL.',fontsize=8)
    fig.savefig(folder/'mapped-accessibility.png',dpi=240)
    fig.savefig(folder/'mapped-accessibility.svg',metadata={'Date':None})
    p=folder/'mapped-accessibility.svg'
    p.write_text('\n'.join(s.rstrip() for s in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)
