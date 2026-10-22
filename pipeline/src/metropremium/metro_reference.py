"""Extract factual station lists from the user-selected guide; never infer geometry.

No article prose or guide illustrations are redistributed. Guide matches remain
identity evidence only: they do not certify entrances, service dates or transfers.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from html.parser import HTMLParser
import json
import re
import unicodedata

from .provenance import digest, write_json

GUIDE_URL = 'https://www.alibaba.ir/mag/tehran/tehran-ci/tehran-subway-guide/'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')

@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def text(self):
        if self.tag in {'script','style','noscript','img'}:
            return ''
        value = ''.join(c if isinstance(c,str) else c.text() for c in self.children)
        return re.sub(r'\s+', ' ', value).strip()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child,Element):
                yield from child.walk()

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element('root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Element(tag,dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag==tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

def normalize_name(value):
    """Orthographic normalization only; no fuzzy identity or semantic title removal."""
    text = unicodedata.normalize('NFKC',value).translate(str.maketrans({'ي':'ی','ى':'ی','ك':'ک'})).translate(DIGITS)
    text = re.sub(r'[\u064b-\u065f\u0670\u0640\u200b-\u200f\u202a-\u202e\ufeff]', '', text)
    return ''.join(c for c in text.casefold() if c.isalnum())

def section_id(text):
    if text.startswith('خط انشعابی'):
        if 'امام خمینی' in text: return '1-airport'
        if 'مهرآباد' in text: return '4-airport'
        if 'هشتگرد' in text: return '5-hashtgerd'
        raise ValueError('Unrecognized branch heading; review guide schema')
    match = re.match(r'^خط\s*([1-7])(?:\s|$)',text.translate(DIGITS))
    return match[1] if match else None

def extract_guide(html):
    document = Document()
    document.feed(html)
    elements = list(document.root.walk())
    contents = [n for n in elements if 'entry-content' in n.attrs.get('class','').split()]
    if len(contents)!=1:
        raise ValueError('Expected exactly one article entry-content; review extraction')
    meta = {n.attrs.get('property',n.attrs.get('name')):n.attrs.get('content') for n in elements if n.tag=='meta'}
    routes = {}
    aliases = []
    active = None
    for node in contents[0].walk():
        text=node.text()
        if node.tag in {'h2','h3'} or (node.tag=='h4' and section_id(text)):
            active=section_id(text)
            if active:
                if active in routes: raise ValueError('Duplicate route heading')
                routes[active]={'id':active,'parent_line':active.split('-')[0],'branch':'-' in active,'heading':text,'stations':[],'declared_station_count':None}
        if active and node.tag=='p':
            # A number followed by station, not the line identifier or journey minutes.
            claim=re.search(r'(\d+)\s*ایستگاه',text.translate(DIGITS))
            if claim and routes[active]['declared_station_count'] is None:
                routes[active]['declared_station_count']=int(claim[1])
            if text.count('>')>=1:
                names=[re.sub(r'\s+',' ',s).strip() for s in text.split('>')]
                if any(not name or len(name)>110 for name in names):
                    raise ValueError('Suspicious station-list format; manual review required')
                if routes[active]['stations']:
                    raise ValueError('Multiple station sequences in route section')
                routes[active]['stations']=[{'position':i+1,'name':name,'normalized_name':normalize_name(name),'operational_status':'not_established','opening_date':None} for i,name in enumerate(names)]
        if active and routes[active]['branch'] and node.tag=='ol' and not routes[active]['stations']:
            names=[c.text() for c in node.children if isinstance(c,Element) and c.tag=='li']
            if len(names)<2 or any(not name or len(name)>110 for name in names):
                raise ValueError('Suspicious branch station list')
            routes[active]['stations']=[{'position':i+1,'name':name,'normalized_name':normalize_name(name),'operational_status':'not_established','opening_date':None} for i,name in enumerate(names)]
        if node.tag=='table':
            rows=[row for row in node.walk() if row.tag=='tr']
            if not rows or 'نام‌های دیگر' not in rows[0].text(): continue
            line=None
            for row in rows[1:]:
                cells=[c.text() for c in row.children if isinstance(c,Element) and c.tag in {'td','th'}]
                if len(cells)!=3: raise ValueError('Alias table format changed')
                if cells[0]:
                    match=re.search('[1-7]',cells[0].translate(DIGITS))
                    line=match[0] if match else None
                aliases.append({'line':line,'station':cells[1],'alternative_names':[s.strip() for s in re.split(r'،| یا ',cells[2]) if s.strip()],'identity_status':'source_claim_unreviewed'})
    if set(routes)!={'1','2','3','4','5','6','7','1-airport','4-airport','5-hashtgerd'} or any(not r['stations'] for r in routes.values()):
        raise ValueError(f'Expected seven complete main-line lists and three branch lists; found {[(k,len(v["stations"])) for k,v in routes.items()]}')
    discrepancies=[]
    for route in routes.values():
        route['extracted_station_count']=len(route['stations'])
        if route['declared_station_count'] is not None and route['declared_station_count']!=len(route['stations']):
            discrepancies.append({'route':route['id'],'kind':'guide_internal_count_conflict','declared':route['declared_station_count'],'listed':len(route['stations'])})
    memberships=defaultdict(set)
    for route in routes.values():
        for station in route['stations']: memberships[station['normalized_name']].add(route['id'])
    shared=[{'normalized_name':name,'guide_routes':sorted(ids),'transfer_verified':False} for name,ids in memberships.items() if len(ids)>1]
    # Preserve heading/list endpoint ambiguities rather than choosing a terminus.
    for route_id,name in [('5','گلشهر'),('7','بسیج')]:
        route=routes[route_id]
        interior=[s for s in route['stations'][1:-1] if s['normalized_name']==normalize_name(name)]
        if name in route['heading'] and interior:
            discrepancies.append({'route':route_id,'kind':'heading_endpoint_ambiguity','heading_mentions':name,'listed_first':route['stations'][0]['name'],'listed_last':route['stations'][-1]['name'],'resolution':'No operating terminus inferred'})
    visible_title=next((n.text() for n in elements if n.tag=='h1'),None)
    title_years=re.findall(r'14\d{2}',(meta.get('og:title') or '').translate(DIGITS))
    heading_years=re.findall(r'14\d{2}',(visible_title or '').translate(DIGITS))
    if title_years and heading_years and title_years!=heading_years:
        discrepancies.append({'kind':'page_title_year_conflict','metadata_years':title_years,'visible_heading_years':heading_years,'resolution':'Neither year proves network validity date'})
    return {'source_url':GUIDE_URL,'source_role':'User-selected secondary station identity and order reference','copyright_policy':'Factual station identifiers extracted for comparison; no article prose or illustrations redistributed; not covered by OSM ODbL or project MIT automatically','page_metadata':{'title':meta.get('og:title'),'visible_heading':visible_title,'published_time_raw':meta.get('article:published_time'),'modified_time_raw':meta.get('article:modified_time'),'date_handling':'Retained as source strings; Persian-calendar values are not silently parsed as Gregorian.'},'routes':list(routes.values()),'alias_claims':aliases,'shared_name_candidates':shared,'discrepancies':discrepancies,'linked_schematic_pdfs':sorted({n.attrs['href'] for n in contents[0].walk() if n.tag=='a' and '.pdf' in n.attrs.get('href','').lower() and 'subway-map' in n.attrs['href']}),'coordinate_policy':'Guide names and schematic do not create geographic coordinates. No geocoding or geometry inference performed.','historical_eligibility_verified':False}

def osm_route_stations(osm):
    nodes={e['id']:e for e in osm['elements'] if e['type']=='node'}
    output={}
    for relation in osm['elements']:
        tags=relation.get('tags',{})
        ref=tags.get('ref','').translate(DIGITS)
        if relation['type']!='relation' or tags.get('route') not in {'subway','train','light_rail'} or ref not in set('1234567'):
            continue
        if ref in output: raise ValueError('Multiple relations for a line; disambiguate source direction')
        stops=[]
        for member in relation.get('members',[]):
            if member['type']!='node' or not any(role in member.get('role','') for role in ['stop','platform']): continue
            node=nodes.get(member['ref'])
            if not node: continue
            names=[]
            for key in ['name:fa','name','official_name','alt_name','old_name','short_name']:
                names.extend(s.strip() for s in node.get('tags',{}).get(key,'').split(';') if s.strip())
            stops.append({'osm_node':node['id'],'names':list(dict.fromkeys(names)),'longitude':node['lon'],'latitude':node['lat']})
        output[ref]={'relation':relation['id'],'stations':stops}
    return output

def compare_reference(reference, osm):
    routes=osm_route_stations(osm)
    reports=[]
    for guide in reference['routes']:
        if guide['branch']: continue # OSM main relations may include branches; flag unmatched members below.
        source=routes.get(guide['id'],{'relation':None,'stations':[]})
        matches=[]
        for station in guide['stations']:
            exact=[s for s in source['stations'] if any(normalize_name(n)==station['normalized_name'] for n in s['names'])]
            record={'guide_position':station['position'],'guide_name':station['name'],'status':'exact_name_candidate' if len(exact)==1 else 'ambiguous' if exact else 'unmatched','osm_node':exact[0]['osm_node'] if len(exact)==1 else None,'independently_verified':False}
            if len(exact)!=1:
                suggestions=sorted([{'osm_node':s['osm_node'],'name':s['names'][0] if s['names'] else None,'similarity':round(max((SequenceMatcher(None,station['normalized_name'],normalize_name(n)).ratio() for n in s['names']),default=0),3)} for s in source['stations']],key=lambda x:(-x['similarity'],x['osm_node']))[:3]
                record['suggestions_for_manual_review']=suggestions
            matches.append(record)
        positions={s['osm_node']:i for i,s in enumerate(source['stations'])}
        indices=[positions[m['osm_node']] for m in matches if m['status']=='exact_name_candidate']
        order='forward' if len(indices)>=2 and all(a<b for a,b in zip(indices,indices[1:])) else 'reverse' if len(indices)>=2 and all(a>b for a,b in zip(indices,indices[1:])) else 'insufficient_or_conflicting'
        matched={m['osm_node'] for m in matches if m['status']=='exact_name_candidate'}
        reports.append({'line':guide['id'],'osm_relation':source['relation'],'guide_listed':len(guide['stations']),'osm_members':len(source['stations']),'exact_name_candidates':sum(m['status']=='exact_name_candidate' for m in matches),'unmatched_or_ambiguous':sum(m['status']!='exact_name_candidate' for m in matches),'order_among_exact_matches':order,'matched_subsequence_only':True,'all_adjacencies_verified':False,'matches':matches,'osm_members_without_exact_guide_match':[{'osm_node':s['osm_node'],'names':s['names']} for s in source['stations'] if s['osm_node'] not in matched]})
    return {'guide_source':reference['source_url'],'status':'comparison_only','routes':reports,'total_main_line_entries':sum(r['guide_listed'] for r in reports),'total_exact_name_candidates':sum(r['exact_name_candidates'] for r in reports),'public_routes_enabled':False,'public_stations_enabled':False,'limitations':['Exact normalized names establish correspondence candidates, not operational status or historical eligibility.','Fuzzy suggestions and guide alias claims are never automatically accepted.','Subsequence order agreement cannot verify omitted stations, transfers, route geometry or adjacent service.','Branch segmentation and changed endpoints require manual review.']}

def build_reference_report(html_path, osm_path, output):
    reference=extract_guide(html_path.read_text(encoding='utf-8'))
    reference['source_sha256']=digest(html_path)
    metadata=json.loads(html_path.with_suffix('.html.source.json').read_text(encoding='utf-8'))
    if metadata['sha256']!=reference['source_sha256'] or metadata['url']!=GUIDE_URL:
        raise ValueError('Guide source differs from its acquisition provenance')
    reference['acquisition']=metadata
    comparison=compare_reference(reference,json.loads(osm_path.read_text(encoding='utf-8')))
    comparison['guide_sha256']=reference['source_sha256']
    comparison['osm_sha256']=digest(osm_path)
    write_json(output/'alibaba-station-reference.json',reference)
    write_json(output/'metro-reference-comparison.json',comparison)
    return reference,comparison
