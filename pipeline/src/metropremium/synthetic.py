"""Nongeographic generated fixtures. Never interpreted as Tehran observations."""
import networkx as nx
import numpy as np
import pandas as pd
from .cleaning import prepare
from .accessibility import Router

def demo(config):
    rng = np.random.default_rng(config['seed'])
    graph = nx.DiGraph(crs='EPSG:32639',synthetic=True)
    for i in range(25):
        graph.add_node(i,x=500000+i*100.,y=3950000.)
        if i:
            graph.add_edge(i-1,i,length=100.)
            graph.add_edge(i,i-1,length=100.)
    entrances = [{'id':'SYNTHETIC-A','x':500000.,'y':3950000.,'verified':True,'eligible':True}, {'id':'SYNTHETIC-B','x':502400.,'y':3950000.,'verified':True,'eligible':True}]
    n=1200
    origins = rng.integers(0,25,n)
    area = rng.integers(40,180,n)
    rooms = rng.integers(1,5,n)
    build_year = rng.integers(1360,1404,n)
    neighborhoods = rng.integers(0,40,n)
    network = np.minimum(origins,24-origins)*100.
    # Arbitrary generative coefficient for recovery tests; not a research estimate.
    per_m2 = np.exp(17.-.12*network/1000+.08*np.log(area)+.03*rooms+.004*(build_year-1380)+neighborhoods*.002+rng.normal(0,.18,n))
    df = pd.DataFrame({'cat2_slug':'residential-sell','cat3_slug':'apartment-sell','city_slug':'tehran','neighborhood_slug':['SYNTHETIC-'+str(i) for i in neighborhoods],'created_at_month':np.where(rng.random(n)>.5,'2024-06-01 00:00:00','2024-07-01 00:00:00'),'price_mode':'مقطوع','price_value':per_m2*area,'building_size':area,'construction_year':build_year,'rooms_count':rooms,'floor':rng.integers(0,5,n),'total_floors_count':5,'has_parking':rng.choice(['true','false'],n),'has_elevator':rng.choice(['true','false'],n),'has_warehouse':rng.choice(['true','false'],n),'location_latitude':35.7,'location_longitude':51.4,'location_radius':rng.choice([0,100,500],n)})
    cleaned, flow = prepare(df,config,{'total_price_verified':True,'denomination':'SYNTHETIC source units','per_m2_enabled':True})
    router = Router(graph,entrances)
    routes = [router.route(500000+o*100,3950000) for o in origins]
    route_frame = pd.DataFrame(routes).rename(columns={'status':'route_status'})
    cleaned = pd.concat([cleaned.reset_index(drop=True),route_frame],axis=1)
    cleaned['x'] = 500000+origins*100
    cleaned['y'] = 3950000
    uncertainty = router.perturb(500500,3950000,100,config['seed'],200)
    return cleaned,flow,uncertainty
