"""Metric graph routing: exact over the modeled snapped-node graph, not the physical city."""
import math
import heapq
from itertools import count
import networkx as nx
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree

PROJECT = Transformer.from_crs('EPSG:4326', 'EPSG:32639', always_xy=True)
UNPROJECT = Transformer.from_crs('EPSG:32639', 'EPSG:4326', always_xy=True)

def project(lon, lat):
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError('Invalid WGS84 coordinate')
    return PROJECT.transform(lon,lat)

def band(distance, thresholds=(500,1000,1500)):
    if distance is None or not math.isfinite(distance):
        return None
    return int(np.searchsorted(thresholds, distance, side='left'))

def euclidean_bounds(distance, radius):
    """Triangle inequality bounds; radius treated as hard bound only as a sensitivity assumption."""
    if radius is None or not math.isfinite(radius) or radius < 0:
        return None
    return max(0.,distance-radius), distance+radius

class Router:
    def __init__(self, graph, entrances, max_snap_m=100, speed=80):
        if graph.graph.get('crs') != 'EPSG:32639':
            raise ValueError('Routing requires EPSG:32639 in metres')
        if speed <= 0:
            raise ValueError('Walking speed must be positive')
        for _,_,attrs in graph.edges(data=True):
            if not math.isfinite(attrs.get('length',-1)) or attrs['length'] < 0:
                raise ValueError('Invalid edge weight')
        self.graph = graph
        self.nodes = list(graph)
        if not self.nodes:
            raise ValueError('Empty walking graph')
        self.xy = np.array([(graph.nodes[n]['x'],graph.nodes[n]['y']) for n in self.nodes])
        self.tree = cKDTree(self.xy)
        self.entrances = []
        self.rejected_entrances = []
        self.max_snap = max_snap_m
        self.speed = speed
        # Super-source on the REVERSED graph. Each source has its own connector weight.
        reverse = nx.DiGraph()
        reverse.add_nodes_from(graph.nodes(data=True))
        for a,b,attrs in graph.edges(data=True):
            pairs = [(b,a)] if graph.is_directed() else [(a,b),(b,a)]
            for u,v in pairs:
                if not reverse.has_edge(u,v) or attrs['length'] < reverse[u][v]['length']:
                    reverse.add_edge(u,v,length=attrs['length'])
        source = '__metro_super_source__'
        if source in reverse:
            raise ValueError('Reserved source node collision')
        reverse.add_node(source)
        for e in entrances:
            if not e.get('verified') or not e.get('eligible'):
                self.rejected_entrances.append({'id':e.get('id'),'reason':'unverified_or_ineligible'})
                continue
            if not (isinstance(e.get('x'),(int,float)) and isinstance(e.get('y'),(int,float)) and math.isfinite(e['x']) and math.isfinite(e['y'])):
                self.rejected_entrances.append({'id':e.get('id'),'reason':'invalid_coordinate'})
                continue
            snap, idx = self.tree.query([e['x'],e['y']])
            if snap > max_snap_m:
                self.rejected_entrances.append({'id':e.get('id'),'reason':'snap_too_far'})
                continue
            node = self.nodes[idx]
            candidate = dict(e, node=node, snap_m=float(snap))
            self.entrances.append(candidate)
            if not reverse.has_edge(source,node) or reverse[source][node]['length'] > snap:
                reverse.add_edge(source,node,length=float(snap),entrance_id=e['id'])
        # Store one distance and destination label per node, not a complete path
        # per node (which can grow quadratically on city-scale chains).
        self.distances, self.destinations = {}, {}
        pending = []
        serial = count()
        for node, attrs in reverse[source].items():
            heapq.heappush(pending, (attrs['length'], next(serial), node, attrs['entrance_id']))
        while pending:
            distance, _, node, destination = heapq.heappop(pending)
            if node in self.distances:
                continue
            self.distances[node] = distance
            self.destinations[node] = destination
            for neighbor, attrs in reverse[node].items():
                if neighbor not in self.distances:
                    heapq.heappush(pending, (distance + attrs['length'], next(serial), neighbor, destination))
        self.reverse = reverse
        self.source = source
        self.entrance_tree = cKDTree([(e['x'],e['y']) for e in self.entrances]) if self.entrances else None

    def route(self, x, y):
        if not (math.isfinite(x) and math.isfinite(y)):
            return {'status':'invalid_coordinate'}
        if not self.entrances:
            return {'status':'no_eligible_entrance'}
        euclidean, _ = self.entrance_tree.query([x,y])
        snap, idx = self.tree.query([x,y])
        node = self.nodes[idx]
        result = {'euclidean_m':float(euclidean),'origin_snap_m':float(snap)}
        if snap > self.max_snap:
            return dict(result,status='snap_too_far')
        if node not in self.distances:
            return dict(result,status='unreachable')
        walking = float(snap + self.distances[node])
        chosen = self.destinations[node]
        return dict(result,status='ok',entrance_id=chosen,network_m=walking,walking_minutes=walking/self.speed,ratio=walking/euclidean if euclidean>0 else None,band=band(walking),connector_assumption='Straight connectors to nearest graph node; physical access not certified')

    def perturb(self, x, y, radius, seed=0, draws=100):
        if not math.isfinite(radius) or radius < 0:
            return {'status':'unknown_radius'}
        rng = np.random.default_rng(seed)
        angles = rng.uniform(0,2*np.pi,draws)
        radii = radius*np.sqrt(rng.uniform(0,1,draws))
        samples = [self.route(x+r*np.cos(a),y+r*np.sin(a)) for a,r in zip(angles,radii)]
        valid = [s for s in samples if s['status']=='ok']
        nominal = self.route(x,y)
        return {'assumption':'Uniform area within disk; scenario, not an estimated error distribution', 'draws':draws,'successful_draws':len(valid),'failure_fraction':1-len(valid)/draws, 'classification_change_fraction_among_successful':sum(s['band']!=nominal.get('band') for s in valid)/len(valid) if valid else None,'network_m_quantiles':np.quantile([s['network_m'] for s in valid],[.025,.5,.975]).tolist() if valid else None}
