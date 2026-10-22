# Alibaba guide: station-reference audit

The owner supplied [Alibaba's Tehran subway guide](https://www.alibaba.ir/mag/tehran/tehran-ci/tehran-subway-guide/) as a station source. It was downloaded successfully via local HTTPS on 22 October 2026; the browsing service itself timed out. Source HTML and the linked schematic PDF are cached under ignored `data/raw/references/alibaba/`, with checksums and acquisition records. The HTML timestamp records provenance registration after the initial successful request; that first request's exact instant was not captured. Original article prose, images and PDF are not committed or copied to public website assets.

## What was extracted

The reproducible parser extracts ordered station identifiers from the seven main-line sections, the three branch sections, and an alternative-name table. Main lines contain **150 entries** and branch lists contain **eight entries**. These are source-listed line memberships, not unique operational stations. Shared station names generate transfer *candidates* only. Twelve alias-table rows are preserved as unreviewed source claims.

| Main line | Guide prose count | Guide list entries | Cached OSM stop members | Exact name candidates | Order among exact matches |
|---|---:|---:|---:|---:|---|
| 1 | 29 | 29 | 29 | 25 | Forward |
| 2 | 22 | 22 | 22 | 17 | Forward |
| 3 | 25 | 24 | 25 | 24 | Forward |
| 4 | 20 | 20 | 20 | 16 | Reverse |
| 5 | 13 | 13 | 13 | 2 | Forward |
| 6 | 17 | 20 | 26 | 15 | Reverse |
| 7 | 22 | 22 | 22 | 17 | Forward |

There are **116 exact normalized-name candidates out of 150 main-line entries**. This number is deliberately conservative: normalization handles Persian/Arabic letter variants, diacritics, spaces, punctuation and zero-width marks; it does not guess semantic aliases, remove meaningful station titles, or accept fuzzy spelling matches. Low match counts can reflect naming conventions rather than missing stations. The complete unmatched records and scored suggestions support manual review. Reverse order is compatible with listing the same line in opposite directions; only the matched subsequence was checked. This does not validate every adjacency or omitted station.

## Source discrepancies

- Line 3 prose reports 25 stations while its arrow-separated list has 24.
- Line 6 prose reports 17 while its list has 20.
- The line 5 heading mentions Golshahr as an endpoint, while the main list includes the extension beyond it; the guide also lists that extension separately as a branch. Those presentations must not be merged into duplicate station/service edges without review.
- The line 7 heading mentions Basij while its list continues to Takhti. This does not establish the operating status of that continuation.
- The page's metadata title contains Persian year 1404 while its visible heading contains 1405. Source modification metadata is retained in its original Persian-calendar form. Neither title year nor a page update proves a station opening date.

## Use in MetroPremium

This source adds independent station-name/order evidence to the OSM comparison workflow. It does **not** by itself verify station entrances, line geometry, transfers, individual opening dates, complete current service, or accessibility during December 2024. A schematic's locations are not geographic coordinates. The embedded Google map was identified but its data was not extracted or presumed ODbL-licensed. Geographic source coordinates continue to come from OSM; public metro layers remain disabled.

Machine-readable factual outputs: [station reference](../../artifacts/reports/alibaba-station-reference.json) and [OSM comparison](../../artifacts/reports/metro-reference-comparison.json). The [network report](../../artifacts/reports/network-validation.json) records this additional reference while retaining its validation gates.

```sh
node scripts/task.mjs metro-reference          # acquire cached guide/PDF and compare with existing OSM input
node scripts/task.mjs metro-reference --offline
node scripts/task.mjs build-networks --offline
```

The parser fails on missing article containers, missing route lists, unknown branches and ambiguous repeated sequences instead of silently generating a partial network. Fuzzy matches and alias claims are suggestions only. Original content rights remain with the source; no license grant is inferred for narrative, diagrams or embedded maps. This is a station-identifier research comparison, not redistribution of the guide.
