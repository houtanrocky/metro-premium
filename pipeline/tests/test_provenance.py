"""Source-code evidence uses synthetic local files and excludes private data."""
import json
from metropremium import provenance


def test_local_run_preserves_code_snapshot_without_collecting_raw_inputs(monkeypatch,tmp_path):
    monkeypatch.setattr(provenance,'ROOT',tmp_path)
    source=tmp_path/'pipeline/src/example.py'
    source.parent.mkdir(parents=True)
    source.write_text('# SYNTHETIC CODE SNAPSHOT FIXTURE\n',encoding='utf-8')
    raw=tmp_path/'data/raw/synthetic-private.txt'
    raw.parent.mkdir(parents=True)
    raw.write_text('SYNTHETIC PRIVATE FIXTURE',encoding='utf-8')
    original=source.read_bytes()
    with provenance.run_record('synthetic-provenance-test',{}) as (folder,state):
        evidence=state['source_code_snapshot']
        assert len(evidence)==1
        saved=folder/evidence[0]['snapshot_path']
        assert saved.read_bytes()==original
        source.write_text('# CHANGED AFTER SNAPSHOT\n',encoding='utf-8')
    assert saved.read_bytes()==original
    manifest=json.loads((folder/'manifest.json').read_text())
    assert manifest['status']=='completed'
    assert evidence[0]['sha256']==provenance.digest(saved)
    assert not (folder/'source-code/data').exists()
