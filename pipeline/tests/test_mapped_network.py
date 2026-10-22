import json
import numpy as np
import pandas as pd
import pytest
from metropremium.mapped_network import entrance_inventory, boundary_clearance, checked_json, SNAPSHOT
from metropremium.statistics import spatial_wild_bootstrap
from metropremium.accessibility import Router, project
from metropremium.geographic import walking_from_elements
from metropremium.provenance import digest


def inventory_fixture():
    guide={'routes':[{'parent_line':'1','stations':[{'normalized_name':'تجریش'}]}]}
    elements=[
        {'type':'node','id':1,'lon':51.4,'lat':35.7,'tags':{'railway':'station','name':'تجریش'}},
        {'type':'node','id':2,'lon':51.401,'lat':35.7,'tags':{'railway':'subway_entrance'}},
        {'type':'node','id':3,'lon':51.402,'lat':35.7,'tags':{'railway':'subway_entrance'}},
        {'type':'relation','id':10,'tags':{'route':'subway','ref':'1','network:wikidata':'Q714823'},'members':[{'type':'node','ref':1,'role':'stop'}]},
        {'type':'relation','id':20,'tags':{'public_transport':'stop_area','name':'تجریش'},'members':[{'type':'node','ref':1,'role':'stop'},{'type':'node','ref':2,'role':''}]},
    ]
    return elements,guide


def test_membership_is_explicit_and_not_nearest_station_guess():
    elements,guide=inventory_fixture()
    entrances,report=entrance_inventory(elements,guide)
    assert [e['id'] for e in entrances]==['2']
    assert report['excluded_entrance_nodes']==[3]
    assert entrances[0]['stop_areas']==[20] and entrances[0]['lines']==['1']
    assert report['opening_dates_verified'] is False


@pytest.mark.parametrize('change',['different_name','wrong_network','proposed_stop','private_entrance'])
def test_unverified_identity_or_restricted_entrance_stays_excluded(change):
    elements,guide=inventory_fixture()
    if change=='different_name':
        guide['routes'][0]['stations'][0]['normalized_name']='کهریزک'
    if change=='wrong_network': elements[3]['tags']['network:wikidata']='other'
    if change=='proposed_stop': elements[0]['tags']['railway']='proposed'
    if change=='private_entrance': elements[1]['tags']['access']='private'
    assert entrance_inventory(elements,guide)[0]==[]


def test_historical_json_rejects_truncation_and_wrong_snapshot(tmp_path):
    p=tmp_path/'source.json'
    p.write_text(json.dumps({'elements':[{'id':1}]}))
    side=tmp_path/'source.json.source.json'
    metadata={'sha256':digest(p),'bytes':p.stat().st_size,'url':f'https://example.org/?data=[date:"{SNAPSHOT}"]'}
    side.write_text(json.dumps(metadata))
    assert checked_json(p)['elements']
    metadata['url']='https://example.org/?data=[date:"2026-01-01T00:00:00Z"]'
    side.write_text(json.dumps(metadata))
    with pytest.raises(ValueError,match='snapshot'):checked_json(p)
    metadata['url']=f'https://example.org/?data=[date:"{SNAPSHOT}"]'
    side.write_text(json.dumps(metadata))
    p.write_text('{}')
    with pytest.raises(ValueError,match='checksum'):checked_json(p)


def test_boundary_certificate_uses_metric_crs_and_outside_fails():
    x,y=project(51.4,35.7)
    outside=project(52.,35.7)
    distances=boundary_clearance([x,outside[0]],[y,outside[1]])
    assert 20000<distances[0]<30000
    assert distances[1]==0


def test_json_importer_respects_foot_direction_and_real_lengths():
    elements=[{'type':'node','id':1,'lon':51.4,'lat':35.7}, {'type':'node','id':2,'lon':51.401,'lat':35.7}, {'type':'way','id':3,'nodes':[1,2],'tags':{'highway':'footway','oneway:foot':'-1'}}]
    g,_,_=walking_from_elements(elements)
    assert g.has_edge(2,1) and not g.has_edge(1,2)
    assert 85<g[2][1]['length']<95


def test_large_chain_router_retains_labels_not_quadratic_paths():
    import networkx as nx
    g=nx.DiGraph(crs='EPSG:32639')
    for i in range(1000):g.add_node(i,x=i,y=0)
    for i in range(999):g.add_edge(i,i+1,length=1.)
    r=Router(g,[{'id':'destination','x':999,'y':0,'verified':True,'eligible':True}])
    assert r.route(0,0)['network_m']==999
    assert len(r.destinations)==1000 and not hasattr(r,'paths')


def test_spatial_wild_bootstrap_checks_draws_and_insufficient_cells():
    from metropremium.synthetic import demo
    import yaml
    from metropremium.provenance import ROOT
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    with pytest.raises(ValueError):spatial_wild_bootstrap(df,draws=0)
    df['x']=0;df['y']=0
    result=spatial_wild_bootstrap(df,draws=10)
    assert result['status']=='insufficient_spatial_cells_or_model_sample'


def test_spatial_wild_bootstrap_is_seeded_and_preserves_design():
    from metropremium.synthetic import demo
    import yaml
    from metropremium.provenance import ROOT
    config=yaml.safe_load((ROOT/'configs/smoke.yaml').read_text())
    df,_,_=demo(config)
    df['x']=np.arange(len(df))%40*2100.
    df['y']=0.
    result=spatial_wild_bootstrap(df,draws=20,seed=7)
    assert result==spatial_wild_bootstrap(df,draws=20,seed=7)
    assert result['spatial_cells']==40 and len(result['models'])==3
    assert all(m['failed_draws']==0 for m in result['models'])
