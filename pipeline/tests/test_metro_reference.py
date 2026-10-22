import pytest
from metropremium.metro_reference import extract_guide, compare_reference, normalize_name

def synthetic_guide():
    # Generated HTML fixture, not a copied article or factual station inventory.
    lines=''.join(f'<h3>خط {i} آزمایشی</h3><p>2 ایستگاه</p><p>نمونه {i} الف &gt; <a href="/">نمونه {i} ب</a></p>' for i in range(1,8))
    branches=''.join(f'<h4>{heading}</h4><ol><li>نمونه شاخه الف</li><li>نمونه شاخه ب</li></ol>' for heading in ['خط انشعابی فرودگاه امام خمینی','خط انشعابی فرودگاه مهرآباد','خط انشعابی هشتگرد'])
    alias='<table><tr><th>خط</th><th>ایستگاه</th><th>نام‌های دیگر</th></tr><tr><td>خط ۱</td><td>نمونه 1 الف</td><td>نام نمونه یا نام جایگزین</td></tr></table>'
    return f'<html><head><meta property="og:title" content="۱۴۰۴"/></head><body><h1>۱۴۰۵</h1><div class="entry-content">{lines}{branches}{alias}</div><p>نظر کاربر الف &gt; متن بیرونی ب</p></body></html>'

def test_extracts_ordered_lists_inline_links_branches_and_aliases():
    ref=extract_guide(synthetic_guide())
    assert len(ref['routes'])==10
    assert ref['routes'][0]['stations'][1]['name']=='نمونه 1 ب'
    assert ref['routes'][-1]['branch'] is True
    assert len(ref['alias_claims'])==1
    assert len(ref['alias_claims'][0]['alternative_names'])==2
    assert all(s['opening_date'] is None for r in ref['routes'] for s in r['stations'])
    assert any(d['kind']=='page_title_year_conflict' for d in ref['discrepancies'])

def test_reports_source_conflicts_without_changing_station_lists():
    html=synthetic_guide().replace('<p>2 ایستگاه</p>','<p>3 ایستگاه</p>',1)
    ref=extract_guide(html)
    conflict=next(d for d in ref['discrepancies'] if d['kind']=='guide_internal_count_conflict')
    assert (conflict['declared'],conflict['listed'])==(3,2)
    assert len(ref['routes'][0]['stations'])==2

def test_schema_changes_fail_closed():
    with pytest.raises(ValueError,match='entry-content'):
        extract_guide('<p>No article</p>')
    with pytest.raises(ValueError,match='seven'):
        extract_guide(synthetic_guide().replace('<h3>خط 7 آزمایشی</h3>','<h3>عنوان ناشناخته</h3>'))

def test_orthography_normalization_does_not_guess_semantic_aliases():
    assert normalize_name('علي\u200cآباد')==normalize_name('علی آباد')
    assert normalize_name('كیان‌شهر')==normalize_name('کیان شهر')
    assert normalize_name('میدان هفت تیر')!=normalize_name('شهدای هفتم تیر')

def test_comparison_handles_reverse_order_and_never_promotes_fuzzy_match():
    ref=extract_guide(synthetic_guide())
    osm={'elements':[{'type':'node','id':1,'lon':51.4,'lat':35.7,'tags':{'name':'نمونه 1 الف'}},{'type':'node','id':2,'lon':51.41,'lat':35.71,'tags':{'name':'نمونه 1 ب'}},{'type':'relation','id':10,'tags':{'ref':'1','route':'subway'},'members':[{'type':'node','ref':2,'role':'stop'},{'type':'node','ref':1,'role':'stop'}]}]}
    result=compare_reference(ref,osm)
    assert result['routes'][0]['order_among_exact_matches']=='reverse'
    assert result['total_exact_name_candidates']==2
    assert result['public_stations_enabled'] is False
    assert not result['routes'][0]['all_adjacencies_verified']
    osm['elements'][0]['tags']['name']='نمونه 1 الف نام متفاوت'
    changed=compare_reference(ref,osm)['routes'][0]
    assert changed['exact_name_candidates']==1
    assert changed['matches'][0]['status']=='unmatched'
    assert changed['matches'][0]['suggestions_for_manual_review']
