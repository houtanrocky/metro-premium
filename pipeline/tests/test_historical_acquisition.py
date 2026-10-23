"""Synthetic transport fixtures: no live downloads or empirical source rows."""
import importlib
import json
from pathlib import Path
import urllib.error
import urllib.parse

import pytest

from metropremium.provenance import ROOT, digest


@pytest.fixture
def acquisition(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))
    module = importlib.import_module('acquire_historical')
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    return module


def synthetic_download(url, path, payload):
    path.write_text(json.dumps(payload), encoding='utf-8')
    Path(str(path) + '.source.json').write_text(json.dumps({
        'url': url, 'sha256': digest(path), 'bytes': path.stat().st_size,
    }), encoding='utf-8')


def execute(module, tmp_path, **kwargs):
    folder = tmp_path / 'synthetic-run'
    folder.mkdir(exist_ok=True)
    target = tmp_path / 'synthetic-cache' / 'line5.json'
    state = {'validation': [], 'inputs': []}
    result = module.acquire_query(
        f'[date:"{module.DATE}"];relation(443301);out body;', target,
        'https://synthetic.example/api/interpreter', folder, state, **kwargs,
    )
    return target, state, result


def test_timeout_retries_then_accepts_validated_response(acquisition, monkeypatch, tmp_path):
    calls, waits = [], []
    payload = {'elements': [{'type': 'relation', 'id': 443301, 'tags': {'synthetic': 'yes'}}]}

    def fake_fetch(url, path, timeout):
        calls.append((path, timeout))
        if len(calls) == 1:
            raise TimeoutError('synthetic timeout')
        synthetic_download(url, path, payload)

    monkeypatch.setattr(acquisition, 'fetch', fake_fetch)
    monkeypatch.setattr(acquisition.time, 'sleep', waits.append)
    target, state, result = execute(acquisition, tmp_path, timeout=17)
    assert result == payload
    assert waits == [30] and [timeout for _, timeout in calls] == [17, 17]
    assert calls[0][0] != calls[1][0]
    assert state['request_attempts'][0]['error_type'] == 'TimeoutError'
    assert state['request_attempts'][1]['status'] == 'validated'
    assert acquisition.checked_json(target) == payload
    assert len(state['inputs']) == 2


@pytest.mark.parametrize('payload', [
    {'elements': []},
    {'elements': [{'id': 1}], 'remark': 'runtime error: synthetic timeout'},
])
def test_incomplete_response_is_preserved_but_never_cached(acquisition, monkeypatch, tmp_path, payload):
    monkeypatch.setattr(acquisition, 'fetch', lambda url, path, timeout: synthetic_download(url, path, payload))
    with pytest.raises(RuntimeError, match='no complete source was accepted'):
        execute(acquisition, tmp_path, attempts=1)
    assert not (tmp_path / 'synthetic-cache' / 'line5.json').exists()
    assert (tmp_path / 'synthetic-run' / 'line5-attempt-1.json').exists()


def test_permanent_http_error_does_not_retry(acquisition, monkeypatch, tmp_path):
    def forbidden(url, path, timeout):
        raise urllib.error.HTTPError(url, 403, 'synthetic forbidden', {}, None)

    monkeypatch.setattr(acquisition, 'fetch', forbidden)
    monkeypatch.setattr(acquisition.time, 'sleep', lambda _: pytest.fail('permanent errors must not retry'))
    with pytest.raises(RuntimeError, match='Acquisition stopped'):
        execute(acquisition, tmp_path)


def test_cached_input_is_validated_offline_without_network(acquisition, monkeypatch, tmp_path):
    monkeypatch.setattr(acquisition, 'fetch', lambda url, path, timeout: synthetic_download(url, path, {'elements': [{'id': 1}]}))
    target, _, _ = execute(acquisition, tmp_path)
    original = target.read_bytes()
    monkeypatch.setattr(acquisition, 'fetch', lambda *a, **k: pytest.fail('offline mode must not fetch'))
    execute(acquisition, tmp_path, offline=True)
    assert target.read_bytes() == original
    target.write_text('{}', encoding='utf-8')
    with pytest.raises(ValueError, match='checksum'):
        execute(acquisition, tmp_path, offline=True)


def test_missing_offline_input_never_fetches(acquisition, monkeypatch, tmp_path):
    monkeypatch.setattr(acquisition, 'fetch', lambda *a, **k: pytest.fail('offline mode must not fetch'))
    with pytest.raises(FileNotFoundError, match='Offline input missing'):
        execute(acquisition, tmp_path, offline=True)


def synthetic_browser_response():
    return {'version': 0.6, 'generator': 'Overpass API SYNTHETIC TEST FIXTURE', 'elements': [
        {'type': 'node', 'id': 1, 'lon': 51.4, 'lat': 35.7},
        {'type': 'node', 'id': 2, 'lon': 51.401, 'lat': 35.7},
        {'type': 'way', 'id': 3, 'nodes': [1, 2], 'tags': {'highway': 'footway'}},
        {'type': 'relation', 'id': 443301, 'members': [{'type': 'way', 'ref': 3, 'role': ''}]},
    ]}


def import_synthetic_browser(acquisition, tmp_path, payload):
    source = tmp_path / 'synthetic-browser-download.json'
    source.write_text(json.dumps(payload), encoding='utf-8')
    folder = tmp_path / 'synthetic-import-run'
    folder.mkdir(exist_ok=True)
    dest = tmp_path / 'synthetic-import-cache'
    state = {'validation': [], 'inputs': []}
    acquisition.import_browser_file(source, 'line5', acquisition.historical_queries()['line5'],
                                    dest, 'https://synthetic.example/api/interpreter', folder, state)
    return source, dest / 'line5.json', state


def test_manual_import_preserves_bytes_and_marks_attested_provenance(acquisition, tmp_path):
    source, target, state = import_synthetic_browser(acquisition, tmp_path, synthetic_browser_response())
    assert source.read_bytes() == target.read_bytes()
    metadata = json.loads(Path(str(target) + '.source.json').read_text())
    assert metadata['retrieval_method'] == 'operator_supplied_browser_download'
    assert metadata['snapshot_request_independently_verified'] is False
    assert 'retrieved_at_utc' not in metadata
    assert 'Operator attests' in metadata['request_evidence']
    assert acquisition.checked_json(target)['version'] == 0.6
    assert len(state['inputs']) == 2
    original = target.read_bytes()
    with pytest.raises(ValueError, match='will not be overwritten'):
        import_synthetic_browser(acquisition, tmp_path, synthetic_browser_response())
    assert target.read_bytes() == original


@pytest.mark.parametrize('failure', ['geojson', 'remark', 'missing_relation', 'tags_only', 'missing_node'])
def test_manual_import_rejects_incomplete_or_wrong_exports(acquisition, tmp_path, failure):
    payload = synthetic_browser_response()
    if failure == 'geojson':
        payload = {'type': 'FeatureCollection', 'features': []}
    if failure == 'remark':
        payload['remark'] = 'synthetic runtime failure'
    if failure == 'missing_relation':
        payload['elements'][-1]['id'] = 99
    if failure == 'tags_only':
        del payload['elements'][-1]['members']
    if failure == 'missing_node':
        payload['elements'][2]['nodes'].append(999)
    with pytest.raises(ValueError):
        import_synthetic_browser(acquisition, tmp_path, payload)
    assert not (tmp_path / 'synthetic-import-cache' / 'line5.json').exists()
    assert (tmp_path / 'synthetic-browser-download.json').exists()
    assert (tmp_path / 'synthetic-import-run' / 'line5-browser-response.json').exists()


def test_browser_plan_pins_queries_skips_cache_and_does_not_auto_run(acquisition, monkeypatch, tmp_path):
    queries = acquisition.historical_queries()
    dest = tmp_path / 'synthetic-plan-cache'
    dest.mkdir()
    url = 'https://synthetic.example/api/interpreter?' + urllib.parse.urlencode({'data': queries['metro']})
    synthetic_download(url, dest / 'metro.json', {'elements': [{'id': 1}]})
    folder = tmp_path / 'synthetic-plan-run'
    folder.mkdir()
    entries = acquisition.browser_plan(queries, list(queries), dest,
                                       'https://synthetic.example/api/interpreter', folder)
    assert [e['input'] for e in entries] == ['line5', 'walk-0-0', 'walk-0-1', 'walk-1-0', 'walk-1-1']
    for entry in entries:
        parameters = urllib.parse.parse_qs(urllib.parse.urlsplit(entry['browser_url']).query)
        assert 'R' not in parameters
        assert '{{data:overpass,server=https://synthetic.example/api/}}' in parameters['Q'][0]
        assert f'[date:"{acquisition.DATE}"]' in parameters['Q'][0]
        assert entry['query'] in parameters['Q'][0]
    assert (folder / 'browser-downloads.html').exists()
    assert (folder / 'browser-plan.json').exists()
