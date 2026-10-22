"""Download official immutable inputs; no scraping of live Divar."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

REPO = "divarofficial/real_estate_ads"
REV = "e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85"
ROOT = Path(__file__).resolve().parents[1]

def fetch(url, path):
    if path.exists():
        sidecar=path.with_suffix(path.suffix+'.source.json')
        if not sidecar.exists():
            raise ValueError(f'Cached input has no provenance sidecar: {path}')
        metadata=json.loads(sidecar.read_text(encoding='utf-8'))
        with path.open('rb') as stream:
            actual=hashlib.file_digest(stream,'sha256').hexdigest()
        if actual!=metadata['sha256'] or path.stat().st_size!=metadata['bytes']:
            raise ValueError(f'Cached input failed hash/length verification: {path}')
        print(f"Cached: {path}", flush=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "MetroPremium/0.1 (academic local research)"})
    part = path.with_suffix(path.suffix + ".part")
    total = 0
    last = time.monotonic()
    with urllib.request.urlopen(req, timeout=90) as response, part.open("wb") as out:
        while chunk := response.read(4 * 1024 * 1024):
            out.write(chunk)
            total += len(chunk)
            if time.monotonic() - last > 10:
                print(f"Downloaded {total / 1e6:.1f} MB", flush=True)
                last = time.monotonic()
    part.rename(path)
    digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
    meta = {"url": url, "sha256": digest, "bytes": total, "retrieved_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if 'huggingface.co/' in url:
        meta.update(repository=REPO, revision=REV)
    path.with_suffix(path.suffix + ".source.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta), flush=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--metadata-only", action="store_true")
    args = p.parse_args()
    dest = ROOT / "data/raw/divar" / REV
    fetch(f"https://huggingface.co/api/datasets/{REPO}/revision/{REV}", dest / "repository.json")
    fetch(f"https://huggingface.co/datasets/{REPO}/raw/{REV}/README.md", dest / "README.md")
    if not args.metadata_only:
        fetch(f"https://huggingface.co/datasets/{REPO}/resolve/{REV}/real_estate_ads.csv?download=true", dest / "real_estate_ads.csv")
