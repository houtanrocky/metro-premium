"""Clearly synthetic topology and source-contract fixtures; no live downloads."""
import json
import math

import networkx as nx
import pytest

from metropremium import network_audit
from metropremium.network_audit import object_index, ordered_chain_breaks, route_audit, connector_audit, endpoint_gap_candidates
from metropremium.provenance import digest


def synthetic_objects():
    return object_index([
        {'type':'node','id':1,'lon':51.4,'lat':35.7},
        {'type':'node','id':2,'lon':51.401,'lat':35.7},
        {'type':'node','id':3,'lon':51.402,'lat':35.7},
        {'type':'node','id':4,'lon':51.45,'lat':35.7},
        {'type':'way','id':10,'nodes':[1,2],'tags':{'railway':'subway'}},
        {'type':'way','id':11,'nodes':[2,3],'tags':{'railway':'subway'}},
        {'type':'way','id':12,'nodes':[3,4],'tags':{'railway':'subway'}},
    ])


def synthetic_route(members):
    return {'type':'relation','id':999,'tags':{'ref':'6','route':'subway','network:wikidata':'Q714823'},'members':members}


def test_actual_way_geometry_connects_without_inventing_station_edges():
    objects=synthetic_objects()
    route=synthetic_route([{'type':'way','ref':10},{'type':'way','ref':11},
                           {'type':'node','ref':2,'role':'stop'}])
    result=route_audit(route,objects)
    assert result['track_edges']==2 and result['track_components']==1
    assert 170<result['summed_unique_track_edge_length_m']<190
    assert result['software_geometry_screen_passed'] is True
    assert result['independent_topology_verified'] is False
    assert result['public_geometry_approved'] is False


def test_missing_way_nodes_are_not_connected_across_gaps():
    objects=synthetic_objects()
    objects[('way',10)]['nodes']=[1,9999,2]
    result=route_audit(synthetic_route([{'type':'way','ref':10}]),objects)
    assert result['missing_track_nodes']==1
    assert result['track_edges']==0
    assert result['software_geometry_screen_passed'] is False


def test_disconnected_track_and_off_track_stop_fail_screen():
    result=route_audit(synthetic_route([{'type':'way','ref':10},{'type':'way','ref':12},
                                       {'type':'node','ref':9999,'role':'stop'}]),synthetic_objects())
    assert result['track_components']==2 and result['ordered_chain_breaks']==1
    assert result['missing_stop_nodes']==1
    assert not result['software_geometry_screen_passed']
    gaps=endpoint_gap_candidates(synthetic_route([{'type':'way','ref':10},{'type':'way','ref':12}]),synthetic_objects())
    assert len(gaps)==1 and gaps[0]['endpoint_separation_m']>80
    assert gaps[0]['edge_created'] is False


def test_ordered_chain_checks_global_orientation_and_explicit_roles():
    assert ordered_chain_breaks([([1,2],''),([3,2],''),([3,4],'')])==0
    assert ordered_chain_breaks([([1,2],''),([2,3],''),([2,4],'')])==1
    assert ordered_chain_breaks([([1,2],'forward'),([2,3],'backward')])==1
    assert ordered_chain_breaks([([],''),([1,2],'')])==1


@pytest.mark.parametrize('sequence,expected',[
    ([0,1,2],'forward_compatible'),([2,1,0],'reverse_compatible'),([0,2,1],'non_monotone_matched_subsequence'),
])
def test_matched_station_order_is_checked_without_claiming_historical_service(sequence,expected):
    names=['syntheticalpha','syntheticbeta','syntheticgamma']
    guide={'routes':[{'id':'6','parent_line':'6','stations':[{'normalized_name':name} for name in names]}]}
    objects=object_index([{'type':'node','id':i,'tags':{'name':names[i]}} for i in range(3)])
    route=synthetic_route([{'type':'node','ref':i,'role':'stop'} for i in sequence])
    result=network_audit.station_order_checks(route,objects,guide)['reference_checks'][0]
    assert result['order_compatibility']==expected
    assert result['historical_service_verified'] is False


def test_conflicting_raw_versions_fail_closed():
    with pytest.raises(ValueError,match='Conflicting'):
        object_index([{'type':'node','id':1,'lon':1},{'type':'node','id':1,'lon':2}])


def test_connector_ties_preserve_component_ambiguity_without_physical_approval():
    graph=nx.DiGraph(crs='EPSG:32639')
    for node,x in [(1,0),(2,10),(99,0),(100,-10)]:graph.add_node(node,x=x,y=0)
    graph.add_edge(1,2,length=10)
    graph.add_edge(99,100,length=10)
    entrances=[{'id':'1','x':0,'y':0,'longitude':0,'latitude':0,'station_names':['SYNTHETIC ALPHA'],'lines':['6']},
               {'id':'500','x':40,'y':0,'longitude':0,'latitude':0,'station_names':['SYNTHETIC BETA'],'lines':['6']}]
    summary,private_rows=connector_audit(graph,entrances)
    assert summary['entrance_nodes_present_on_walking_graph']==1
    assert summary['ties_spanning_components']==1
    assert summary['connectors_over_25m']==1
    assert summary['physical_connections_verified']==0
    assert len(private_rows)==2
    assert all(row['physical_connection_verified'] is False for row in private_rows)


def synthetic_official_contract(tmp_path,monkeypatch):
    monkeypatch.setattr(network_audit,'ROOT',tmp_path)
    path=tmp_path/'synthetic-official-fixture.html'
    path.write_text('<html><p>SYNTHETIC ARTICLE 999999999 DATE 18 TEST 1402</p>'
                    '<article>SYNTHETIC STATION ALPHA inauguration report</article></html>',encoding='utf-8')
    url='https://president.ir/fa/SYNTHETIC-TEST-NOT-A-REAL-ARTICLE'
    source={'id':'synthetic-999999999','authority':'official_presidential_event_report','url':url,
            'file':path.name,'sha256':digest(path),'bytes':path.stat().st_size,
            'article_date_marker':'18 TEST 1402','event_date_gregorian':'2023-10-10','event_date_persian':'1402-07-18',
            'claims':[{'station':'SYNTHETIC STATION ALPHA','line':'6'}],
            'verifies_specific_entrance':False,'verifies_continuous_service':False,'verifies_physical_walking':False}
    path.with_suffix('.html.source.json').write_text(json.dumps({'url':url,'sha256':digest(path)}))
    objects=object_index([
        {'type':'node','id':1},
        {'type':'relation','id':2,'tags':{'public_transport':'stop_area','name':'SYNTHETIC STATION ALPHA'},'members':[{'type':'node','ref':1}]},
        {'type':'relation','id':3,'tags':{'route':'subway','ref':'6'},'members':[{'type':'node','ref':1,'role':'stop'}]},
    ])
    config={'snapshot':network_audit.SNAPSHOT,'source_scope':'station_inauguration_only','sources':[source]}
    return config,objects,[{'stop_areas':[2]}],path


def test_pinned_station_claim_does_not_verify_an_entrance_or_continuous_service(tmp_path,monkeypatch):
    config,objects,entrances,_=synthetic_official_contract(tmp_path,monkeypatch)
    evidence=network_audit.official_evidence(config,objects,entrances)
    assert evidence['retained_stop_areas_with_inauguration_evidence']==1
    assert evidence['specific_entrances_with_operation_evidence']==0
    assert evidence['operational_eligibility_approved'] is False
    assert evidence['station_claims'][0]['continuous_study_period_service_verified'] is False


@pytest.mark.parametrize('failure',['changed_bytes','wrong_line','overbroad_claim'])
def test_official_evidence_is_integrity_checked_and_scoped(tmp_path,monkeypatch,failure):
    config,objects,entrances,path=synthetic_official_contract(tmp_path,monkeypatch)
    if failure=='changed_bytes':path.write_text('SYNTHETIC CHANGED CONTENT')
    if failure=='overbroad_claim':config['sources'][0]['verifies_specific_entrance']=True
    if failure=='wrong_line':
        config['sources'][0]['claims'][0]['line']='7'
        result=network_audit.official_evidence(config,objects,entrances)
        assert result['station_claims'][0]['exact_name_stop_area_matches']==0
    else:
        with pytest.raises(ValueError):network_audit.official_evidence(config,objects,entrances)
