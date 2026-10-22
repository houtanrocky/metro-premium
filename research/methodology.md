# Methodology and implementation contract

## Data lineage

The official source is `divarofficial/real_estate_ads`, revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85`. The downloaded CSV is 780,721,338 bytes; SHA-256 `e5760fe1325a195e6682c371457bfecd51d255c518756e3cbea234b8163a801f`. Source bytes stay under ignored `data/raw/`. The audit stores all columns initially as strings in a local DuckDB work database, preserving their source values, and independently infers logical parse types. This separates CSV storage representation from semantic types. Strict parsing rejects malformed rows rather than dropping them.

Audit every row for categories, month and city frequencies, nulls, numeric validity, coordinate availability, radius, exact whole-row duplicates, possible attribute duplicates and available controls. The source card and observed data disagree about period and schema size; never silently edit the card to match observed values. The audit table and [findings](findings.md) document both.

## Population and time

The exact category predicate is `city_slug='tehran' AND cat2_slug='residential-sell' AND cat3_slug='apartment-sell'`. Do not use the sparsely populated `property_type` instead. December 2024 is chosen deterministically as the largest 2024 source month within that population, before looking at price differences. This is an operational sample-size rule, not a claim that December represents all months. Fix the rule and record its outcome. Development mode takes a seeded 5,000-row sample before cleaning; it must not replace full-source conclusions.

Accept only `price_mode='مقطوع'`, finite positive prices, and area 20–500 m². Area limits define the intended ordinary-apartment scope; compare expanded positive-area limits later, rather than claiming these limits identify errors. Missing rooms/years/floors remain missing. Persian and Arabic digits are transliterated. Literal numeric years 1300–1403 are retained for the selected historical period; censored labels are not assigned precise ages. Persian room words are recoded explicitly. Boolean amenities retain a missing category.

Coordinates are WGS84 (EPSG:4326) at interchange. The declared rectangular support is longitude 51.05–51.65, latitude 35.45–35.90, a pragmatic analysis extent rather than a verified municipal boundary. Out-of-rectangle records are flagged. Unknown radius is never coded as zero. Preserve nongeographic rows for coverage reporting; routing requires valid coordinates and known radius 0–500 m. All exclusions have before/after counts.

Price denomination and the total-price interpretation are unresolved for the dataset. Related live Kenar API descriptions are suggestive but do not prove the historical export mapping. Therefore `per_m2` is missing for real rows in this release. There is no currency conversion or empirical price model. Once an explicit source contract is verified, record that evidence and make a versioned implementation change rather than silently interpreting old rows.

## Graphs and distances

Use two distinct structures: a station/line network with supported transfer relations, and a pedestrian graph with road/path connectivity. The initial OSM download contains seven route relations and their recursive members, snapshot `2026-10-22T19:09:21Z`. It has not passed independent route-sequence or historic-opening review. No proximity-based transfer edge is inferred. A reference schematic was not present and was not invented.

The small street extract comes from the OSM map API rectangle 51.405,35.694,51.415,35.702. Node IDs preserve topological crossings; geometric intersections do not manufacture crossing nodes. Disconnected components remain. Access=no/private ways are excluded unless explicit pedestrian permission exists; explicit `foot=no/private` excludes. Motorways and construction ways are excluded. `oneway:foot` is respected; motor-vehicle one-way tags alone do not imply pedestrian one-way movement. Hard wall/fence barrier nodes are excluded. Conditional permissions, opening hours, detailed crossings and all physical barriers are not completely modeled; full use requires additional access review.

Project to UTM zone 39N, EPSG:32639, in metres. Sum projected segment lengths along actual source node sequences, without joining disconnected tracks. This gives consistent planar endpoint comparisons; projection distortion and elevation are limitations. Graph nodes need not be street intersections only: unsimplified shape nodes are retained.

For origin p and eligible entrance e, snap each to its nearest graph node within 100 m and record connector length c. Modeled walking distance is:

`D(p) = c_p + min_e [d_G(v_p,v_e) + c_e]`.

Create a super-source on the reversed directed graph, with weighted edges to every eligible snapped entrance node. One Dijkstra search returns the global minimum for every reachable origin node. Reversing edges converts distances from origin to entrance into distances from entrance to origin; connector weights remain nonnegative. Parallel edges are collapsed by minimum weight. No Euclidean candidate pruning is used. Complexity is approximately O((V+E) log V), plus spatial index queries. The minimum is exact for this snapped-node graph, not for all physically possible routes: straight connectors can cross unmapped barriers and nearest-node snapping can distort distances. Conservative connector checks and edge-based access validation are required for full deployment.

Euclidean distance is the nearest of the same eligible entrance set in the same metric CRS. `D / E` is missing at zero denominator. Minima may select different destinations; describe the ratio as a nearest-access comparison, not a detour to a fixed station. Walking minutes = D / 80. Bands include the upper boundary: ≤500, (500,1000], (1000,1500], >1500 m. No eligible entrance, invalid coordinate, failed snap and unreachable origins are separate statuses, never replaced with straight-line distance.

## Spatial uncertainty

A hard disk of reported radius is a sensitivity interpretation, not a verified error bound. Under it the nearest-Euclidean distance lies between max(0,E−r) and E+r by the triangle inequality. This does not automatically bound graph distance: snapping, barriers and connectivity can change discontinuously.

The implemented perturbation scenario samples uniformly by area in a disk: angle uniform on [0,2π), radius r√U. Repeat globally optimal routing at every perturbed location, count failures separately and compare bands among successful draws. Quantiles are scenario distributions, not confidence intervals or a recovered source-error law. Compare missing-radius and known-radius populations, plus r≤100 and r≤250 subsets. Zero source radius must not be advertised as an exact address.

## Modeling and publication

See the [statistical plan](statistical-analysis-plan.md). Export only allowlisted aggregates and suppress groups below 30. Prices and route summaries need their own minimum denominators; a large group with sparse measured values is insufficient. Unknown measures remain JSON null. No listing descriptions, titles, seller data, row identifiers or property points are public. The only coordinate-bearing public file is OSM street geometry, explicitly separate from housing data. This release makes no neighborhood affordability ranking or housing-price map.

Every run captures configuration, seed, package environment, Git state and input/output hashes. Immutable run folders are preserved; stable public aliases are reproducible publication views, not replacements for run provenance. The synthetic fixture follows the same preparation, routing, model and aggregation functions but is stored separately and labelled at every presentation boundary.
