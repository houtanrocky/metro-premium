"""Audit real cached topology and scoped official claims without approving service.

Track edges use only consecutive nodes of actual rail ways. No station-dot
connections, geographic transfer guesses or listing coordinates enter this audit.
"""
from collections import Counter, defaultdict
from datetime import date
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

import networkx as nx
import numpy as np
from scipy.spatial import cKDTree

from .accessibility import project
from .aggregation import assert_public_safe
from .mapped_network import checked_json, entrance_inventory, load_mapped_graph, SNAPSHOT
from .metro_reference import Document, extract_guide, normalize_name, DIGITS
from .provenance import ROOT, digest, write_json


def object_index(elements):
    objects = {}
    for element in elements:
        key = (element['type'], element['id'])
        if key in objects and objects[key] != element:
            raise ValueError(f'Conflicting cached OSM object versions: {key}')
        objects[key] = element
    return objects


def object_names(element):
    tags = element.get('tags', {})
    return {normalize_name(value.strip()) for key in ['name','name:fa','official_name','alt_name','old_name']
            for value in tags.get(key, '').split(';') if value.strip()}


def ordered_chain_breaks(ways):
    """Dynamic orientation check of actual way endpoints, honoring explicit roles.

    Pairwise endpoint intersections alone cannot validate a whole ordered chain.
    An empty way represents a missing member and breaks the chain explicitly.
    """
    ends = None
    breaks = 0
    for nodes, role in ways:
        if len(nodes) < 2:
            breaks += 1
            ends = None
            continue
        orientations = [(nodes[0], nodes[-1])]
        if role == 'backward':
            orientations = [(nodes[-1], nodes[0])]
        elif role != 'forward':
            orientations.append((nodes[-1], nodes[0]))
        next_ends = {end for start, end in orientations if ends is None or start in ends}
        if not next_ends:
            breaks += 1
            next_ends = {end for _, end in orientations}
        ends = next_ends
    return breaks


def endpoint_gap_candidates(route, objects):
    """Private diagnostic candidates only; measured separation never creates an edge."""
    previous = None
    previous_way = None
    gaps = []
    for member in route.get('members', []):
        way = objects.get((member['type'],member['ref']),{})
        if member['type']!='way' or way.get('tags',{}).get('railway') not in {'rail','subway','light_rail','narrow_gauge'}:
            continue
        nodes = way.get('nodes',[])
        if len(nodes)<2:
            previous = None
            continue
        current = {nodes[0],nodes[-1]}
        if previous and not previous & current:
            candidates = []
            for a in previous:
                for b in current:
                    first,second = objects.get(('node',a)),objects.get(('node',b))
                    if first is None or second is None:continue
                    try:
                        separation = math.dist(project(first['lon'],first['lat']),project(second['lon'],second['lat']))
                    except (KeyError,ValueError,TypeError):continue
                    if math.isfinite(separation):candidates.append((separation,a,b))
            if candidates:
                distance,a,b = min(candidates)
                gaps.append({'relation_id':route['id'],'line':route.get('tags',{}).get('ref','').translate(DIGITS),
                             'previous_way_id':previous_way,'next_way_id':member['ref'],
                             'previous_endpoint_node':a,'next_endpoint_node':b,
                             'endpoint_separation_m':distance,'edge_created':False})
        previous,previous_way = current,member['ref']
    return gaps


def route_audit(route, objects):
    graph = nx.Graph()
    missing_ways, missing_nodes = set(), set()
    invalid_nodes = set()
    chain = []
    tracks = []
    stops = []
    for member in route.get('members', []):
        key = (member['type'], member['ref'])
        element = objects.get(key)
        if member['type'] == 'node' and member.get('role') in {'stop','stop_entry_only','stop_exit_only','platform'}:
            stops.append(member['ref'])
        if member['type'] != 'way':
            continue
        if element is None:
            missing_ways.add(member['ref'])
            chain.append(([], member.get('role', '')))
            continue
        if element.get('tags', {}).get('railway') not in {'rail','subway','light_rail','narrow_gauge'}:
            continue
        nodes = element.get('nodes', [])
        chain.append((nodes, member.get('role', '')))
        tracks.append(member['ref'])
        for a, b in zip(nodes, nodes[1:]):
            points = []
            for node in [a, b]:
                source = objects.get(('node', node))
                if source is None:
                    missing_nodes.add(node)
                    break
                try:
                    point = project(source['lon'], source['lat'])
                    if not all(math.isfinite(value) for value in point):
                        raise ValueError('Invalid projected node')
                except (ValueError, KeyError, TypeError):
                    invalid_nodes.add(node)
                    break
                points.append(point)
            if len(points) != 2:
                continue
            length = math.dist(*points)
            if length > 0:
                graph.add_edge(a, b, length=length)
    tags = route.get('tags', {})
    components = nx.number_connected_components(graph) if graph else 0
    missing_stop_nodes = sum(('node', node) not in objects for node in stops)
    off_track_stops = sum(node not in graph for node in stops if ('node', node) in objects)
    reasons = []
    if not tracks: reasons.append('no_actual_track_way_members')
    if missing_ways or missing_nodes or invalid_nodes or missing_stop_nodes: reasons.append('incomplete_or_invalid_member_geometry')
    if components != 1: reasons.append('track_geometry_not_one_connected_component')
    breaks = ordered_chain_breaks(chain)
    if breaks: reasons.append('ordered_track_way_chain_breaks')
    if off_track_stops: reasons.append('stop_nodes_not_on_member_track_graph')
    return {'relation_id': route['id'], 'line': tags.get('ref','').translate(DIGITS),
            'route_tag': tags.get('route'), 'has_required_network_identifier': tags.get('network:wikidata') == 'Q714823',
            'actual_track_way_members': len(tracks), 'track_nodes': len(graph), 'track_edges': graph.number_of_edges(),
            'track_components': components, 'ordered_chain_breaks': breaks, 'stop_members': len(stops),
            'missing_way_members': len(missing_ways), 'missing_track_nodes': len(missing_nodes),
            'invalid_track_nodes': len(invalid_nodes), 'missing_stop_nodes': missing_stop_nodes,
            'stop_nodes_off_track': off_track_stops,
            'summed_unique_track_edge_length_m': sum(e['length'] for _,_,e in graph.edges(data=True)),
            'software_geometry_screen_passed': not reasons, 'screen_failures': reasons,
            'independent_topology_verified': False, 'public_geometry_approved': False}


def line_coverage(objects, entrances, inventory):
    by_line = {line['line']: line for line in inventory['lines']}
    routes = [e for e in objects.values() if e['type'] == 'relation' and e.get('tags',{}).get('route') in {'subway','train'}]
    rows = []
    for line in map(str, range(1,8)):
        candidates = [e for e in routes if e.get('tags',{}).get('ref','').translate(DIGITS) == line]
        accepted = by_line.get(line, {})
        cached_stops = {member['ref'] for route in candidates for member in route.get('members',[])
                        if member['type']=='node' and member.get('role') in {'stop','stop_entry_only','stop_exit_only','platform'}}
        rejected = Counter('missing_required_network_wikidata' for e in candidates if e.get('tags',{}).get('network:wikidata') != 'Q714823')
        rows.append({'line':line, 'cached_route_relations':len(candidates),
                     'cached_stop_nodes':len(cached_stops),
                     'retained_route_relations':len(accepted.get('route_relations',[])),
                     'mapped_stop_nodes':len(accepted.get('stop_nodes',[])),
                     'identity_matched_stop_nodes':len(accepted.get('identity_matched_nodes',[])),
                     'retained_unique_entrances':len({e['id'] for e in entrances if line in e['lines']}),
                     'route_rejection_reasons':dict(rejected)})
    return rows


def station_order_checks(route, objects, guide):
    """Exact-name matched-subsequence compatibility; never a service-date approval."""
    line = route.get('tags',{}).get('ref','').translate(DIGITS)
    stop_nodes = [objects.get(('node',m['ref']),{}) for m in route.get('members',[])
                  if m['type']=='node' and m.get('role') in {'stop','stop_entry_only','stop_exit_only','platform'}]
    checks = []
    for reference in guide['routes']:
        if reference['parent_line'] != line:continue
        positions = defaultdict(set)
        for index, station in enumerate(reference['stations']):
            positions[station['normalized_name']].add(index)
        matched, ambiguous, unmatched = [], 0, 0
        for stop in stop_nodes:
            candidates = {position for name in object_names(stop) for position in positions.get(name,set())}
            if len(candidates)==1:matched.append(next(iter(candidates)))
            elif candidates:ambiguous += 1
            else:unmatched += 1
        unique = len(set(matched))
        if unique<2:status='insufficient_exact_matches'
        elif all(a<=b for a,b in zip(matched,matched[1:])):status='forward_compatible'
        elif all(a>=b for a,b in zip(matched,matched[1:])):status='reverse_compatible'
        else:status='non_monotone_matched_subsequence'
        checks.append({'reference_list':reference['id'], 'reference_station_entries':len(reference['stations']),
                       'exact_matched_stop_nodes':len(matched),'unique_matched_reference_positions':unique,
                       'unmatched_stop_nodes':unmatched,'ambiguous_stop_nodes':ambiguous,
                       'order_compatibility':status,'historical_service_verified':False})
    return {'relation_id':route['id'],'line':line,'reference_checks':checks}


def official_evidence(config, objects, entrances):
    """Validate pinned official content, never turn station claims into entrance approval."""
    if config['snapshot'] != SNAPSHOT or config['source_scope'] != 'station_inauguration_only':
        raise ValueError('Historical evidence scope/snapshot mismatch')
    cutoff = date.fromisoformat(SNAPSHOT[:10])
    stop_areas = [e for e in objects.values() if e['type']=='relation' and e.get('tags',{}).get('public_transport')=='stop_area']
    retained_areas = {area for entrance in entrances for area in entrance['stop_areas']}
    lines_by_stop = defaultdict(set)
    for element in objects.values():
        if element['type']=='relation' and element.get('tags',{}).get('route') in {'subway','train'}:
            line = element.get('tags',{}).get('ref','').translate(DIGITS)
            for member in element.get('members',[]):
                if member['type']=='node' and member.get('role') in {'stop','stop_entry_only','stop_exit_only','platform'}:
                    lines_by_stop[member['ref']].add(line)
    dated_retained_areas = set()
    claims = []
    sources = []
    for source in config['sources']:
        if source['authority'] != 'official_presidential_event_report' or urlsplit(source['url']).hostname != 'president.ir':
            raise ValueError('Unreviewed historical evidence authority')
        if any(source[field] is not False for field in ['verifies_specific_entrance','verifies_continuous_service','verifies_physical_walking']):
            raise ValueError('Station-only evidence cannot approve entrances, continuity or physical routes')
        path = ROOT/source['file']
        metadata = json.loads(Path(str(path)+'.source.json').read_text(encoding='utf-8'))
        if digest(path) != source['sha256'] or path.stat().st_size != source['bytes'] or metadata['sha256'] != source['sha256'] or metadata['url'] != source['url']:
            raise ValueError('Official evidence checksum, length or source URL mismatch')
        document = Document()
        document.feed(path.read_text(encoding='utf-8'))
        articles = [element for element in document.root.walk() if element.tag == 'article']
        if len(articles) != 1:
            raise ValueError('Expected one official article body')
        article = normalize_name(articles[0].text())
        page_text = document.root.text()
        if source['article_date_marker'] not in page_text or str(source['id'].split('-')[-1]) not in page_text:
            raise ValueError('Official article identity/date marker mismatch')
        event_date = date.fromisoformat(source['event_date_gregorian'])
        sources.append({'id':source['id'], 'authority':source['authority'], 'url':source['url'],
                        'sha256':source['sha256'], 'bytes':source['bytes'],
                        'event_date':source['event_date_gregorian'], 'event_date_persian':source['event_date_persian'],
                        'scope':'station inauguration only; no entrance identity, continuity or physical route verification'})
        for claim in source['claims']:
            name = normalize_name(claim['station'])
            if name not in article:
                raise ValueError('Claimed station not in pinned official article body')
            matched = [area for area in stop_areas if name in object_names(area) and any(
                member['type']=='node' and claim['line'] in lines_by_stop[member['ref']]
                for member in area.get('members',[]))]
            retained = [area for area in matched if area['id'] in retained_areas]
            if event_date < cutoff:
                dated_retained_areas.update(area['id'] for area in retained)
            claims.append({'station':claim['station'], 'line':claim['line'], 'source_id':source['id'],
                           'event_date':source['event_date_gregorian'], 'inauguration_before_snapshot':event_date < cutoff,
                           'exact_name_stop_area_matches':len(matched), 'retained_stop_area_matches':len(retained),
                           'specific_entrance_operation_verified':False, 'continuous_study_period_service_verified':False})
    return {'sources':sources, 'station_claims':claims, 'accepted_station_inauguration_claims':len(claims),
            'retained_stop_areas_with_inauguration_evidence':len(dated_retained_areas),
            'specific_entrances_with_operation_evidence':0,
            'rejected_source_candidates':config.get('rejected_sources',[]),
            'operational_eligibility_approved':False}


def connector_audit(graph, entrances):
    nodes = list(graph)
    xy = np.array([(graph.nodes[n]['x'],graph.nodes[n]['y']) for n in nodes])
    tree = cKDTree(xy)
    components = {}
    for component_id, component in enumerate(nx.weakly_connected_components(graph)):
        components.update((node,component_id) for node in component)
    private_rows = []
    for entrance in entrances:
        point = np.array([entrance['x'],entrance['y']])
        distance, index = tree.query(point)
        node = nodes[index]
        ties = tree.query_ball_point(point,float(distance)+1e-6)
        tied_nodes = [nodes[i] for i in ties if abs(float(np.linalg.norm(xy[i]-point))-distance)<=1e-6]
        direct_node = int(entrance['id']) in graph
        private_rows.append({'entrance_id':entrance['id'], 'station_names':' | '.join(entrance['station_names']),
                             'lines':';'.join(entrance['lines']), 'entrance_longitude':entrance['longitude'],
                             'entrance_latitude':entrance['latitude'], 'snapped_node_id':node,
                             'connector_m':float(distance), 'entrance_node_on_walking_graph':direct_node,
                             'snapped_to_same_osm_node':int(entrance['id'])==node,
                             'nearest_node_tie_count':len(tied_nodes),
                             'nearest_tie_spans_components':len({components[n] for n in tied_nodes})>1,
                             'component':components[node], 'physical_connection_verified':False})
    distances = [row['connector_m'] for row in private_rows]
    summary = {'retained_entrances':len(entrances),
               'entrance_nodes_present_on_walking_graph':sum(row['entrance_node_on_walking_graph'] for row in private_rows),
               'snapped_to_same_osm_node':sum(row['snapped_to_same_osm_node'] for row in private_rows),
               'nonzero_straight_connectors':sum(row['connector_m']>1e-6 for row in private_rows),
               'connectors_over_25m':sum(row['connector_m']>25 for row in private_rows),
               'connectors_over_100m':sum(row['connector_m']>100 for row in private_rows),
               'nearest_node_ties':sum(row['nearest_node_tie_count']>1 for row in private_rows),
               'ties_spanning_components':sum(row['nearest_tie_spans_components'] for row in private_rows),
               'components_with_snapped_entrances':len({row['component'] for row in private_rows}),
               'connector_quantiles_m':dict(zip(['min','median','q95','max'],map(float,np.quantile(distances,[0,.5,.95,1])))) if distances else {},
               'physical_connections_verified':0,
               'triage_note':'25 m flags review priority only; every physical connector remains unverified. Nearest-node tie tolerance is 1e-6 m.'}
    return summary, private_rows


def audit_network(evidence_config, folder):
    raw_dir = ROOT/'data/raw/osm/historical-20241201'
    elements = checked_json(raw_dir/'metro.json')['elements'] + checked_json(raw_dir/'line5.json')['elements']
    objects = object_index(elements)
    guide = extract_guide((ROOT/'data/raw/references/alibaba/tehran-subway-guide.html').read_text(encoding='utf-8'))
    entrances, inventory = entrance_inventory(list(objects.values()),guide)
    routes = [e for e in objects.values() if e['type']=='relation' and e.get('tags',{}).get('route') in {'subway','train'} and e.get('tags',{}).get('ref','').translate(DIGITS) in set('1234567')]
    route_checks = [route_audit(route,objects) for route in sorted(routes,key=lambda r:r['id'])]
    order_checks = [station_order_checks(route,objects,guide) for route in sorted(routes,key=lambda r:r['id'])]
    gap_candidates = [gap for route in routes for gap in endpoint_gap_candidates(route,objects)]
    graph, graph_report = load_mapped_graph(raw_dir)
    connectors, private_rows = connector_audit(graph,entrances)
    import pandas as pd
    pd.DataFrame(private_rows).to_csv(folder/'entrance-connector-review-private.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(gap_candidates).to_csv(folder/'track-endpoint-review-private.csv',index=False,encoding='utf-8-sig')
    memberships = {e['id']:{normalize_name(n) for n in e['station_names'] if n} for e in entrances}
    report = {'schema_version':1, 'status':'audit_complete_operational_validation_incomplete', 'snapshot':SNAPSHOT,
              'line_coverage':line_coverage(objects,entrances,inventory), 'route_geometry_checks':route_checks,
              'station_order_checks':order_checks,
              'station_order_note':'Only exact orthographic matches in the later owner-selected guide are compared. Missing/unmatched/ambiguous entries remain unresolved; compatible subsequences do not verify every adjacency, transfers or historical service.',
              'line_coverage_note':'Parent-line groups include directions/branches. Stops are OSM node identities, not certified unique stations. Shared entrances occur on multiple lines; per-line entrance counts must not be summed.',
              'route_geometry_summary':{'cached_routes':len(route_checks), 'software_screens_passed':sum(r['software_geometry_screen_passed'] for r in route_checks),
                                        'ordered_endpoint_review_cases':len(gap_candidates),
                                        'closest_endpoint_separations_m':[gap['endpoint_separation_m'] for gap in gap_candidates],
                                        'independent_topology_verified':0, 'note':'Checks inspect actual OSM track ways, endpoint order and stop membership. A software pass is not independent topology or service approval.'},
              'entrance_membership':{'retained_unique_entrances':len(entrances), 'retained_stop_areas':len({area for e in entrances for area in e['stop_areas']}),
                                     'stop_areas_examined':len(inventory['stop_area_checks']),
                                     'areas_without_member_entrances':sum(not area['entrances_in_relation'] for area in inventory['stop_area_checks']),
                                     'entrances_with_multiple_orthographic_station_names':sum(len(names)>1 for names in memberships.values())},
              'walking':{'nodes':graph_report['nodes'], 'directed_edges':graph_report['directed_edges'], 'weak_components':graph_report['weak_components']},
              'entrance_connectors':connectors, 'historical_station_evidence':official_evidence(evidence_config,objects,entrances),
              'primary_operational_gate_passed':False, 'public_routes_enabled':False, 'public_stations_enabled':False,
              'limitations':['Official station inaugurations do not identify individual entrances or uninterrupted service during the listing month.',
                             'Track geometry and walking connectors lack independent physical verification; no missing link or station adjacency was invented.',
                             'Line 5 remains outside the retained entrance rule when its required network identifier is missing.',
                             'No housing observations were read and no earlier model result was replaced by this audit.']}
    assert_public_safe(report)
    write_json(folder/'historical-network-audit.json',report)
    return report
