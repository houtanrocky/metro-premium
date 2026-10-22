"""Cached, bounded OSM requests. No map tiles are downloaded."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from acquire import fetch

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/raw/osm"
RELATIONS = {"1": 19967673, "2": 2431321, "3": 5366249, "4": 443307, "5": 443301, "6": 5697303, "7": 7429356}

if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    failures = []
    query = '[out:json][timeout:90];(relation(19967673);relation(2431321);relation(5366249);relation(443307);relation(443301);relation(5697303);relation(7429356););(._;>>;);out body;'
    for base in ["https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter"]:
        try:
            target = DEST / "metro.json"
            if target.exists():
                break
            fetch(base + "?" + urllib.parse.urlencode({"data": query}), target)
            break
        except Exception as e:
            failures.append({"url": base, "error": str(e)})
            print(base, str(e), flush=True)
    # OSM map API is limited to a tiny central-Tehran validation area, not a metropolitan graph.
    try:
        fetch("https://www.openstreetmap.org/api/0.6/map?bbox=51.405,35.694,51.415,35.702", DEST / "walk-smoke.osm")
    except Exception as e:
        failures.append({"source": "OSM map API", "error": str(e)})
    (DEST / (time.strftime("acquisition-%Y%m%dT%H%M%SZ.json", time.gmtime()))).write_text(json.dumps({"failures": failures, "relations_from_wiki": RELATIONS, "reference": "https://wiki.openstreetmap.org/w/index.php?title=Tehran/Tehran_Metro&oldid=3068199"}, indent=2), encoding="utf-8")
