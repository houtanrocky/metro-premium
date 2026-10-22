import networkx as nx
import pytest
from metropremium.accessibility import Router, band, euclidean_bounds, project

def graph():
    g=nx.DiGraph(crs='EPSG:32639')
    for n,(x,y) in {'o':(0,0),'near':(10,0),'far':(0,20),'detour':(0,100),'island':(500,500)}.items():
        g.add_node(n,x=x,y=y)
    g.add_edge('o','detour',length=100)
    g.add_edge('detour','near',length=101)
    g.add_edge('o','far',length=20)
    return g

def entrance(id,x,y,**kw):return dict(id=id,x=x,y=y,verified=True,eligible=True,**kw)

def test_actual_nearest_path_is_not_nearest_euclidean():
    r=Router(graph(),[entrance('near',10,0),entrance('far',0,20)])
    a=r.route(0,0)
    assert a['euclidean_m']==10
    assert a['entrance_id']=='far'
    assert a['network_m']==20
    assert a['walking_minutes']==.25
    assert a['ratio']==2

def test_directed_disconnected_and_snapping():
    r=Router(graph(),[entrance('target',10,0)])
    assert r.route(0,0)['network_m']==201
    assert r.route(0,20)['status']=='unreachable'
    assert r.route(500,500)['status']=='unreachable'
    assert r.route(3000,3000)['status']=='snap_too_far'
    assert r.route(float('nan'),1)['status']=='invalid_coordinate'

def test_weighted_entrance_connectors_choose_optimum():
    r=Router(graph(),[entrance('near-snap',11,0),entrance('far-snap',0,19)])
    assert r.route(0,0)['network_m']==21
    assert r.route(0,0)['entrance_id']=='far-snap'

def test_invalid_and_missing_entrances_fail_closed():
    e=entrance('unverified',0,0);e['verified']=False
    r=Router(graph(),[e,entrance('bad',float('nan'),1),entrance('distant',9000,9000)])
    assert len(r.rejected_entrances)==3
    assert r.route(0,0)=={'status':'no_eligible_entrance'}

def test_parallel_edges_choose_minimum():
    g=nx.MultiDiGraph(graph())
    g.add_edge('o','far',length=30)
    assert Router(g,[entrance('far',0,20)]).route(0,0)['network_m']==20

def test_crs_and_weight_safety():
    g=graph();g.graph['crs']='EPSG:4326'
    with pytest.raises(ValueError): Router(g,[])
    g=graph();g['o']['far']['length']=-1
    with pytest.raises(ValueError): Router(g,[])
    x,y=project(51.4,35.7)
    assert 500000<x<600000 and 3900000<y<4000000
    with pytest.raises(ValueError):project(200,35)

def test_uncertainty_bounds_and_reproducible_disk_scenario():
    assert euclidean_bounds(300,500)==(0,800)
    assert euclidean_bounds(300,None) is None
    assert band(500)==0 and band(500.1)==1 and band(None) is None
    r=Router(graph(),[entrance('far',0,20)])
    a=r.perturb(0,0,50,seed=3,draws=50)
    assert a==r.perturb(0,0,50,seed=3,draws=50)
    assert a['draws']==50 and 'scenario' in a['assumption']

def test_modeled_network_triangle_inequality():
    r=Router(graph(),[entrance('near',10,0),entrance('far',0,20)])
    for x,y in [(0,0),(1,1),(8,2)]:
        p=r.route(x,y)
        assert p['network_m']+1e-8>=p['euclidean_m']
