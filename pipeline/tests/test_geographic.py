from metropremium.geographic import walking_from_xml

def test_access_and_foot_direction_restrictions(tmp_path):
    fixture='''<osm><node id="1" lat="35.7" lon="51.4"/><node id="2" lat="35.7" lon="51.401"/><node id="3" lat="35.7" lon="51.402"/><node id="4" lat="35.7" lon="51.403"><tag k="barrier" v="wall"/></node><way id="1"><nd ref="1"/><nd ref="2"/><tag k="highway" v="footway"/><tag k="oneway:foot" v="yes"/></way><way id="2"><nd ref="2"/><nd ref="3"/><tag k="highway" v="residential"/><tag k="access" v="private"/></way><way id="3"><nd ref="2"/><nd ref="4"/><tag k="highway" v="footway"/></way></osm>'''
    p=tmp_path/'walk.osm';p.write_text(fixture)
    graph,entrances,report=walking_from_xml(p)
    assert graph.has_edge(1,2) and not graph.has_edge(2,1)
    assert 3 not in graph and 4 not in graph
    assert 85<graph[1][2]['length']<95
    assert report['omitted']['ways_access']==1
