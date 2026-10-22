# Source inventory

| Source | Exact identifier | Purpose / authority |
|---|---|---|
| Divar official export | [divarofficial/real_estate_ads](https://huggingface.co/datasets/divarofficial/real_estate_ads), revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85` | Sole housing observations; immutable CSV and card downloaded |
| OSM relations | [wiki revision 3068199](https://wiki.openstreetmap.org/w/index.php?title=Tehran/Tehran_Metro&oldid=3068199) | Discovery of line 1–7 relation IDs; not operational truth |
| OSM route members | Overpass `out body` with recursive members | Coordinates/tags/ways; raw JSON cached, timestamp 2026-10-22T19:09:21Z |
| OSM street XML | [map API bounded extract](https://www.openstreetmap.org/api/0.6/map?bbox=51.405,35.694,51.415,35.702) | Small real pedestrian-network software check |
| OSMnx docs | [stable documentation](https://osmnx.readthedocs.io/en/stable/) | Network tooling reference; not a data provider |

CSV bytes: 780,721,338. SHA-256: `e5760fe1325a195e6682c371457bfecd51d255c518756e3cbea234b8163a801f`.

OSM metro SHA-256: `20e771e4af00c9b59d6a63c64955da869c51d00e7b19c8b4f6c174a8a31e2491`.

OSM street XML SHA-256: `5427c1b838b5571ab25aeb9c04bd75db49aa973dd2d1780307cc7cd6f7577a22`.

Download sidecars contain exact URLs, bytes, UTC time and hashes. An initial shared helper incorrectly attached housing repo metadata to OSM sidecars; that source-labeling bug was corrected, preserving the OSM payload bytes. Subsequent manifests capture correct map provenance. Initial download failures and mirror timeouts are recorded locally; no unofficial housing mirror was used.

The source card supplies an ODbL license label but not a dataset-specific monetary denomination or total-price contract. Its cited code/repository links also use naming variants; the actual API repository ID above is authoritative for acquisition. No currency conversion is supported.

The owner subsequently confirmed total apartment asking prices in toman after inspecting actual source examples. This additional evidence is recorded in [the price interpretation](../research/price-interpretation.md) and the scoped configuration, separately from the original publisher-documentation audit. Price/m² is now calculated without any factor-of-ten conversion.

The provided reference image was absent. No replacement was generated. No live Divar records, personal details, guessed coordinates, made-up station sequences, or housing heatmaps were acquired or fabricated.

The owner later supplied [Alibaba's Tehran subway guide](https://www.alibaba.ir/mag/tehran/tehran-ci/tehran-subway-guide/). A cached HTML snapshot and linked schematic PDF now support station-name/order comparisons, with separate source hashes and rights notices. The [reference audit](../research/references/alibaba-guide-audit.md) documents extracted counts, alias candidates and disagreements. The guide does not supply approved entrance coordinates or historical eligibility; its embedded Google map is not ingested.
