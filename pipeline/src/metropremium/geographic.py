"""Conservative OSM interpretation and public-layer quarantine."""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import networkx as nx
from shapely.geometry import LineString
from .accessibility import project, Router
from .provenance import write_json, digest

def walking_from_xml(path):
    tree = ET.parse(path)
    elements = []
    for node in tree.findall('node'):
        elements.append({'type':'node','id':int(node.attrib['id']),'lon':float(node.attrib['lon']),'lat':float(node.attrib['lat']),'tags':{t.attrib['k']:t.attrib['v'] for t in node.findall('tag')}})
    for way in tree.findall('way'):
        elements.append({'type':'way','id':int(way.attrib['id']),'nodes':[int(n.attrib['ref']) for n in way.findall('nd')],'tags':{t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}})
    return walking_from_elements(elements)


def walking_from_elements(elements):
    """Same conservative importer for historical Overpass JSON and smoke XML."""
    nodes = {}
    for node in elements:
        if node['type'] != 'node': continue
        x,y = project(node['lon'],node['lat'])
        nodes[node['id']] = dict(x=x,y=y,tags=node.get('tags',{}),lon=node['lon'],lat=node['lat'])
    graph = nx.DiGraph(crs='EPSG:32639',source='OSM map API',historical=False)
    allowed = {'footway','path','pedestrian','steps','living_street','residential','service','tertiary','secondary','primary','unclassified','tertiary_link','secondary_link','primary_link','track','cycleway'}
    omitted = {'ways_access':0,'ways_not_walkable':0,'barrier_edges':0}
    blocked = {n for n,v in nodes.items() if v['tags'].get('foot')=='no' or v['tags'].get('access') in {'no','private'} or v['tags'].get('barrier') in {'wall','fence','retaining_wall'}}
    for way in elements:
        if way['type'] != 'way': continue
        tags = way.get('tags',{})
        if tags.get('highway') not in allowed or (tags.get('highway')=='cycleway' and tags.get('foot') not in {'yes','designated','permissive'}):
            omitted['ways_not_walkable']+=1
            continue
        if tags.get('foot') in {'no','private'} or (tags.get('access') in {'no','private'} and tags.get('foot') not in {'yes','designated','permissive'}):
            omitted['ways_access']+=1
            continue
        refs = way.get('nodes',[])
        oneway = tags.get('oneway:foot','no')
        for a,b in zip(refs,refs[1:]):
            if a not in nodes or b not in nodes or a in blocked or b in blocked:
                omitted['barrier_edges']+=1
                continue
            for n in [a,b]: graph.add_node(n,**nodes[n])
            length = math.hypot(nodes[a]['x']-nodes[b]['x'],nodes[a]['y']-nodes[b]['y'])
            attrs = {'length':length,'osmid':way['id'],'highway':tags['highway']}
            pairs = [(b,a)] if oneway=='-1' else [(a,b)] if oneway in {'yes','1','true'} else [(a,b),(b,a)]
            for u,v in pairs:
                if not graph.has_edge(u,v) or graph[u][v]['length']>length:
                    graph.add_edge(u,v,**attrs)
    entrances = [{'id':str(n),'x':v['x'],'y':v['y'],'eligible':False,'verified':False,'osm_tagged':True,'tags':v['tags']} for n,v in nodes.items() if v['tags'].get('railway')=='subway_entrance']
    report = {'nodes':len(graph),'directed_edges':graph.number_of_edges(),'weak_components':nx.number_weakly_connected_components(graph) if graph else 0,'entrance_candidates':len(entrances),'omitted':omitted,'crs':'EPSG:32639','scope':'tiny central-Tehran API bounding box only; not metropolitan coverage','entrance_eligibility':'Quarantined: mapped entrances need station membership and historical eligibility evidence','connector_limit_m':100,'barrier_limitations':'Incomplete access mapping, unmodeled crossing legality, conditional restrictions and node snapping remain limitations.'}
    return graph,entrances,report

def inspect_metro(path):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    elems = raw.get('elements',[])
    nodes = {e['id']:e for e in elems if e['type']=='node'}
    ways = {e['id']:e for e in elems if e['type']=='way'}
    relations = [e for e in elems if e['type']=='relation']
    stations = [e for e in nodes.values() if e.get('tags',{}).get('railway') in {'station','stop'} or e.get('tags',{}).get('public_transport')=='station']
    routes = []
    for rel in relations:
        tags = rel.get('tags',{})
        if tags.get('route') not in {'subway','train','light_rail'}:
            continue
        refs = [m['ref'] for m in rel.get('members',[]) if m['type']=='way']
        missing = [w for w in refs if w not in ways or any(n not in nodes for n in ways[w].get('nodes',[]))]
        station_members = [m for m in rel.get('members',[]) if m['type']=='node' and m['ref'] in nodes and ('stop' in m.get('role','') or 'platform' in m.get('role',''))]
        invalid_geometries = 0
        for ref in refs:
            coords = [(nodes[n]['lon'],nodes[n]['lat']) for n in ways.get(ref,{}).get('nodes',[]) if n in nodes]
            if len(coords)<2 or not LineString(coords).is_valid:
                invalid_geometries+=1
        routes.append({'osm_relation':rel['id'],'name':tags.get('name'),'ref':tags.get('ref'),'from':tags.get('from'),'to':tags.get('to'),'colour':tags.get('colour'),'station_member_count':len(station_members),'way_member_count':len(refs),'missing_ways':missing,'invalid_way_geometries':invalid_geometries,'public_approved':False})
    return {'status':'acquired_unverified','elements':len(elems),'station_candidates':len(stations),'relations':routes,'timestamp_osm_base':raw.get('osm3s',{}).get('timestamp_osm_base'),'public_routes_enabled':False,'reasons':['OSM tagging is evidence of mapping, not independent verification of operational lines.','Termini, route sequence, station membership and transfer identity require source comparison.','Opening dates not reconstructed; no claim of historical accessibility.'],'sha256':digest(path)}

def build_networks(folder):
    from .provenance import ROOT
    raw = ROOT/'data/raw/osm'
    report = {'public_routes_enabled':False,'public_stations_enabled':False,'reference_image':'Not supplied in initial workspace','historical_eligibility_verified':False}
    if (raw/'metro.json').exists():
        report['metro'] = inspect_metro(raw/'metro.json')
    else:
        report['metro'] = {'status':'unavailable','reason':'No successful cached Overpass extract'}
    guide=ROOT/'data/raw/references/alibaba/tehran-subway-guide.html'
    if guide.exists() and (raw/'metro.json').exists():
        from .metro_reference import build_reference_report
        reference,comparison=build_reference_report(guide,raw/'metro.json',folder)
        report['secondary_reference']={'source':reference['source_url'],'sha256':reference['source_sha256'],'main_line_entries':comparison['total_main_line_entries'],'exact_name_candidates':comparison['total_exact_name_candidates'],'source_discrepancies':reference['discrepancies'],'status':'comparison_only','public_approval_changed':False}
    if (raw/'walk-smoke.osm').exists():
        graph,entrances,walk = walking_from_xml(raw/'walk-smoke.osm')
        # Actual OSM street segments, not listing points or interpolated price surfaces.
        features=[]
        seen=set()
        for a,b,attrs in graph.edges(data=True):
            key=tuple(sorted([a,b]))
            if key in seen: continue
            seen.add(key)
            features.append({'type':'Feature','properties':{'highway':attrs['highway'],'osm_way':attrs['osmid']},'geometry':{'type':'LineString','coordinates':[[graph.nodes[a]['lon'],graph.nodes[a]['lat']],[graph.nodes[b]['lon'],graph.nodes[b]['lat']]]}})
        write_json(folder/'walking-preview.geojson',{'type':'FeatureCollection','features':features})
        # NetworkX node-link JSON preserves directions and metric attributes.
        write_json(folder/'walk-smoke-graph.json',nx.node_link_data(graph))
        write_json(folder/'entrance-candidates.json',entrances)
        report['walking'] = walk
        # Validate mapped routes only when connected actual nodes exist; no listing coordinates published.
        components = sorted(nx.weakly_connected_components(graph),key=len,reverse=True)
        route_examples = []
        if components:
            component = graph.subgraph(components[0])
            ordered = sorted(component.nodes)
            for a,b in zip(ordered[:5],ordered[-5:]):
                try:
                    d = nx.shortest_path_length(component,a,b,weight='length')
                    direct = math.hypot(graph.nodes[a]['x']-graph.nodes[b]['x'],graph.nodes[a]['y']-graph.nodes[b]['y'])
                    route_examples.append({'from_osm_node':a,'to_osm_node':b,'network_m':d,'euclidean_m':direct,'triangle_check':d+1e-6>=direct})
                except nx.NetworkXNoPath:
                    route_examples.append({'from_osm_node':a,'to_osm_node':b,'status':'unreachable'})
        report['route_checks'] = route_examples
    else:
        report['walking'] = {'status':'unavailable'}
    report['sources'] = [json.loads(p.read_text(encoding='utf-8')) for p in raw.glob('*.source.json')]
    write_json(folder/'network-validation.json',report)
    return report
