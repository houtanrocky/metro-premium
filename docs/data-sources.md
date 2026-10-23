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

## Historical mapped-subset extension, 23 October 2026

Overpass attic queries request `2024-12-01T00:00:00Z`. Four walking tiles merge to SHA-256 `a49f5ea4a7bab0b56bdd4b4b2b45c5acffb387bb46743ca2480495f532fce72c`, with 734,532 OSM objects. The historical metro extract and one tile were programmatic downloads; Line 5 and three tiles were imported from operator-supplied raw browser exports. Sidecars label the generating-request evidence as operator-attested and do not claim independent snapshot-request verification. Import timestamps do not invent browser retrieval timestamps. All raw responses remain ignored by Git.

The [mapped-reference report](../research/mapped-reference-findings.md) explains the historical mapping scope; the appended [successful run manifest](../artifacts/reports/reproduction-manifests.json) records every source hash, config, package version and scientific code snapshot. The provider's base-database timestamp is not treated as the requested snapshot date or an operational opening date.

## Scoped official station evidence

The [official presidential event record](https://president.ir/fa/147059) dated 18 Mehr 1402 supports four station-inauguration claims. The exact private HTML capture is pinned in [historical-evidence.yaml](../configs/historical-evidence.yaml), with source URL, SHA-256, byte count, date markers and individually curated station/line claims. It is not an entrance inventory, route geometry source or assurance of uninterrupted December 2024 service. The [validation report](../research/historical-network-validation.md) records exact-match coverage and remaining gaps. An IRNA source candidate returned a Cloudflare challenge rather than the article and was rejected; no fact was inferred from that response.
