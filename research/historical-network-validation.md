# Historical network validation audit

Computed 23 October 2026 in run `20261023T065027-67bd97e9`, using the cached OSM request snapshot of `2024-12-01T00:00:00Z` and the pinned [official evidence contract](../configs/historical-evidence.yaml). The preceding audit run `20261023T064155-fbb379c4` remains preserved; this follow-up adds station-order compatibility. The [machine-readable audit](../artifacts/reports/historical-network-audit.json) is separate from the earlier exploratory model run. No housing data was read and no earlier coefficient or route result was replaced.

The audit advances source and software verification. Historical operational eligibility, independent topology, entrance completeness and physical walking verification remain incomplete. All primary operational and public metro-geometry gates remain false.

## Dated official evidence

An [official presidential event report](https://president.ir/fa/147059), dated 18 Mehr 1402, records the inauguration of Shahid Arman Ali-Vardi, Shahran and Shahr-e Ziba on Line 6, and Meydan-e Ketab on Line 7. Its source date converts to 10 October 2023 using `System.Globalization.PersianCalendar`, before the study snapshot. The captured page is pinned by SHA-256 `9e29cfd2967f0abdefc1bd23c926e8330ed810bc341af25d7a146bd50aed0831` and 44,288 bytes. Raw HTML remains private.

Exact orthographic name and line checks join Shahran, Shahr-e Ziba and Meydan-e Ketab to three retained stop-area relations. Shahid Arman Ali-Vardi remains unmatched under this specific stop-area-name rule; no semantic alias or geographic proximity was used to force a match. Source facts are curated in the versioned contract and checked against the captured article body, date marker, URL, length and checksum.

This is station-inauguration evidence. It does not identify which OSM entrance opened, certify a pedestrian connector, or establish uninterrupted service during December 2024. Only 3 of the 106 retained stop areas currently have this scoped corroboration; the remaining 103 do not yet have accepted dated station-inauguration evidence in this ledger. All 166 individual entrance-operation records remain unverified. A separate IRNA candidate returned a Cloudflare challenge rather than the article and was rejected as evidence.

## Actual track geometry

The auditor uses actual rail-way node sequences from the pinned OSM relations, projected to EPSG:32639. It never creates a track edge between station dots, fills a missing way, merges nearby nodes or guesses a transfer. Consecutive way-endpoint checks use a dynamic orientation check and honor explicit forward/backward roles. Component checks inspect the actual track graph. These checks cannot independently establish real service, track direction, legal transfers or construction status.

Of 17 directional/branch route relations, 15 pass the software geometry screen. Both Line 3 directional relations, `5366249` and `7770933`, fail: each track graph has two components and an ordered-way chain break. The same endpoint pair separates track-way members `561284303` and `278822219` by **534.59 m** in projected distance. This is one cached endpoint gap appearing in two directions, not evidence of two physical gaps in operating infrastructure. It remains unfilled. Review identifiers and measured separation are preserved privately.

A passing software screen is not independent route-topology approval. All 17 relations remain unapproved for public metro geometry.

### Matched station order

Exact-name stop sequences are also compared with each applicable main-line/branch list in the cached owner-selected guide. Fourteen route relations have at least one forward- or reverse-compatible matched subsequence. Three branch relations have too few distinct exact matches to assess order; none of the assessed subsequences is non-monotone. Unmatched and ambiguous names remain unresolved, with counts retained per reference list. This comparison uses a later reference guide and does not establish the historical station roster, every adjacency or transfer. Both Line 3 directions have compatible matched station order while still failing the actual-track continuity check, illustrating why station order alone cannot justify drawing public track geometry.

## Line and entrance coverage

| Parent line | Cached route relations | Admitted route relations | Stops on admitted routes | Identity-matched stop nodes | Retained unique entrances |
|---|---:|---:|---:|---:|---:|
| 1 | 4 | 4 | 35 | 27 | 36 |
| 2 | 2 | 2 | 22 | 19 | 40 |
| 3 | 2 | 2 | 25 | 23 | 40 |
| 4 | 4 | 4 | 26 | 21 | 37 |
| 5 | 1 | 0 | 0 | 0 | 0 |
| 6 | 2 | 2 | 23 | 14 | 11 |
| 7 | 2 | 2 | 21 | 20 | 29 |

Parent-line groups include directions and airport branches. Stop-node counts are OSM identities, not certified unique operating stations. Shared entrances occur in multiple line groups; the entrance column must not be summed to estimate network totals.

The cached Line 5 relation `443301` has 12 stop nodes and complete connected member-track geometry in this software screen. Its tags lack `network:wikidata=Q714823`, which the current retained-destination rule requires. Therefore the imported Line 5 file does not make Line 5 part of the retained entrance scope. This is a metadata/rule exclusion, not evidence that Line 5 was absent or closed. The prior 166-entrance model remains unchanged; relaxing identity evidence requires a separate documented decision and new sensitivity run.

The existing membership rule examines 142 stop areas, 17 of which have no explicitly attached entrance nodes. Retained destinations cover 106 stop areas and 166 unique entrances. None of the retained entrances belongs to multiple differently normalized station names in this audit; that consistency does not prove physical station completeness or the validity of every source membership.

## Walking attachment

| Retained-entrance attachment check | Count |
|---|---:|
| Entrance node appears in walking graph and is selected as that same node | 43 |
| Nonzero straight nearest-node connector | 123 |
| Connector longer than 25 m | 39 |
| Connector longer than 100 m | 0 |
| Nearest-node ties at the 1 micrometre tolerance | 0 |
| Walking components containing snapped entrances | 12 |
| Independently verified physical connectors | 0 |

Connector distance median is 12.90 m, 95th percentile 45.85 m and maximum 87.12 m. A shared source node is stronger mapped attachment evidence than a straight connector; neither proves that the entrance was open or that the modeled route was physically passable. The 25 m threshold prioritizes human review only. It excludes no observations and changes no model rule. All 123 nonzero connectors need appropriate physical/access evidence, including the 84 at most 25 m.

## Concrete review queue

The audit run contains `entrance-connector-review-private.csv` with all 166 entrances, source identifiers, snap distances, component and tie flags, and explicitly false physical-verification fields. Review the 39 connectors over 25 m first, together with a stratified sample of the shorter and directly attached cases. The separate `track-endpoint-review-private.csv` records both Line 3 directional gap cases. These files contain OSM entrance geography only, no housing records, and remain outside Git and public exports.

Required evidence is still: an official operational inventory valid for the study period; official entrance identifiers/locations and opening or closure records; an independent line/transfer topology reference; and documented pedestrian attachment/crossing checks. A station-inauguration article cannot substitute for these records. Any future eligibility or identity-rule change must receive a new decision-log entry and run; the completed exploratory model remains preserved.

## Reproduction

```sh
node scripts/task.mjs validate-historical-network
```

This is an offline command. It requires the cached historical metro/Line 5 JSON, merged walking sources and their sidecars, the owner-selected guide, and the exact official article capture/sidecar named in the evidence contract. A changed or missing official source fails closed. Restoring a private evidence capsule is necessary if the live page no longer matches the pinned capture. New runs preserve code/config snapshots, source hashes and output hashes. Public output contains derived diagnostics and scoped station facts; coordinates remain in the private review files.
