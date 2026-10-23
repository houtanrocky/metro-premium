# Decision log

Append dated entries; do not silently rewrite previous empirical conclusions.

## 2026-10-22 — Initial implementation

- Empty workspace inspected; no prior repository or metro reference image existed. Created a local Git repository and retained all subsequently downloaded raw bytes outside Git.
- Pinned the official Divar repository revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85`. Initial TLS failure was retried successfully. The complete CSV, not a viewer sample or unofficial copy, supplies the audit.
- Chose DuckDB with all-string raw storage and separately inferred logical types. Observed 60 columns, so the card's 57-column claim was not used as a hard schema.
- Fixed apartment-sale category slugs based on actual source values. Selected the largest 2024 category month before examining any metro-price result: December 2024. A single month avoids cross-year nominal ranking and simplifies interpretation.
- Price-total semantics and denomination are unresolved. General live API terminology is insufficient to establish this export's exact field mapping. Disabled real price/m², price maps and models. This is a research blocker, not a request to guess a currency.
- Kept possible attribute duplicates and price tails in the default candidate sample; flags support sensitivity. Area 20–500 m² is a declared scope rule, not an assertion that all excluded areas are data errors.
- Preserved missing-coordinate records for selection-bias reporting. Restricted routing candidates to known radii, while reporting that restriction. Do not call source radius zero precise.
- Retrieved seven OSM relations identified in the revisioned wiki page. Two Overpass mirrors timed out; the third succeeded. Small API street download is cached. No metropolitan walking download was attempted before validating this bounded slice.
- Independent line-sequence, station-transfer and historical-opening checks are incomplete. Metro layers stay quarantined. The publicly displayed geometry is only actual small-area OSM streets. No station-link lines or housing heatmap were invented.
- Custom unsimplified XML graph importer makes access/foot-direction choices inspectable. Reverse super-source Dijkstra gives exact minimum entrance routing for its declared snapped-node graph. Straight connectors remain a limitation.
- Installed and executed a seeded synthetic full vertical slice. Synthetic results live in a distinct file and require an explicit educational view. Passing synthetic tests is never reported as empirical validation.
- Built a static Persian React/Vite site with self-hosted fonts, aggregate data and a lazy MapLibre map. Default has no external tile requests or credentials. No backend is justified for the current product.
- First dependency audit identified advisories in initially selected MapLibre/Vitest versions. Updated dependency constraints rather than using an unreviewed forced audit fix. Exact installed dependencies are locked.
- All public source/derived database notices remain separate from MIT code. Publication remains local; no remote repository, sponsor affiliation or deployment was invented.
- Visual QA caught a MapLibre v6 worker-loading failure and a lazy-CSS container-height conflict that a canvas-existence test missed. Bundled the worker using the official Vite worker URL approach and fixed map-container sizing. Strengthened browser tests to require rendered street features, a visible map region and no map error. Re-ran desktop/mobile accessibility and interaction tests.

## 2026-10-22 — Owner-supplied Alibaba metro reference

- Acquired the owner-selected guide and its linked schematic PDF, keeping original copyrighted page/assets in ignored raw storage. Added deterministic extraction, cache/hash verification and offline comparison commands.
- Extracted 150 main-line station entries, eight branch entries and twelve alias-table claims. These are memberships/claims, not 158 unique operating stations. Found 116 exact orthographic-name candidates against cached OSM route members; fuzzy suggestions remain unaccepted.
- Recorded internal guide count conflicts on lines 3 and 6, endpoint presentation ambiguities on lines 5 and 7, and conflicting metadata/visible-title years. None were resolved by inventing an opening date or connection.
- Added secondary-reference evidence to network reports. No public metro geometry, transfers, entrance eligibility or historical-access gate was promoted solely on this evidence. No guide prose, schematic image or proprietary embedded map was added to public assets. Earlier feasibility findings remain unchanged.

## 2026-10-22 — Owner price-field inspection

- At the owner's request, exported the 11,767 December 2024 candidate records with original price, area and property-category fields for private inspection. Added a seeded 500-row sample and one seeded record in each of twelve high-count neighborhoods. Extreme source values were retained, not replaced with plausible-looking examples.
- Outputs stay under an ignored per-run folder; no coordinates, listing descriptions, titles or seller data were exported. Original field strings and source provenance accompany the CSV files. No currency conversion, price/m² calculation or analytical gate change was made. Owner knowledge can provide a documented interpretation without silently being relabeled as an official publisher statement.

## 2026-10-23 — Owner confirms total apartment asking price in toman

- The owner explicitly stated that prices are in toman and cover the whole apartment. Accepted this clarification for the pinned Tehran fixed-price apartment-sale population, recording the exact evidence and scope in configs/price-contract.yaml. No further owner action or publisher reply is required to use this interpretation; publisher corroboration remains a distinct evidence category.
- Enabled real price/m² as price_value divided by building_size, with no currency rescaling. Preserved raw inputs, prior audit evidence and private review exports. Earlier statements that price calculation was blocked describe the initial evidence state; the current report now identifies this dated change.
- Recomputed the same 11,767 December 2024 candidates: median 86,986,301.37 toman/m²; IQR 58,541,019.96–126,666,666.67. Price-tail sensitivity retains 11,650 records with unchanged median; attribute deduplication retains 11,731 with median 87,142,857.14. The primary sample still retains extremes and duplicate candidates.
- Upgraded the empirical public contract to schema version 2 for owner-evidenced housing-only descriptions and sufficiently populated neighborhood distributions. Added JSON/CSV and actual high-resolution median/IQR figures, Persian units and filtering-sensitivity explanations. Runtime validation rejects wrong units, false publisher verification and metro estimates.
- Metro topology/entrance, historical eligibility and full pedestrian coverage gates remain unchanged. No metro coefficient, housing-price map or price/access ranking is enabled by confirming the price field.

## 2026-10-23 — Historical acquisition failure handling

- Following a reported socket read timeout, added bounded sequential retries, progress messages, configurable socket timeouts and per-attempt run evidence to historical acquisition. Downloaded responses now pass the existing checksum, historical-date and completeness checks before entering the source cache. Rejected/partial responses remain private run evidence; earlier sources and results are preserved.
- Lightweight status requests timed out locally at both the main and alternative Overpass endpoints; a bounded live Line 5 request to the main endpoint also timed out. These observations do not distinguish server load from network-path problems. No missing input was fabricated or historical/operational gate promoted. The snapshot, spatial bounds and query content remain unchanged.

## 2026-10-23 — Human-operated historical download fallback

- Browser-header diagnostics returned a successful status response while project-identified terminal requests still failed. These are request-level observations; they do not establish the actual query-worker load or isolate the responsible network layer. The automated downloader retains its project identity.
- Added a local guide with the exact historical queries prefilled in Overpass Turbo, plus an offline import of raw browser-saved OSM JSON. Imports record the operator's attestation to the prepared query, SHA-256, byte count and import time; snapshot-request verification is explicitly not independent. Saved files cannot prove their generating query. Structure/reference checks reject incomplete exports, original bytes remain private, and existing sources are never overwritten.
- No snapshot, study rectangle, route geometry, station-operation assumption, model result or public quality gate is changed by this acquisition fallback.

## 2026-10-23 — Executed historical mapped-subset extension

- Completed the four-tile historical acquisition and merged 734,532 OSM objects without replacing any source bytes. The conservative walking graph has 555,686 nodes, 1,236,780 directed edges and 1,532 weak components. Explicit membership/name rules retain 166 mapped entrances in 106 stop-area relations; no station-operation date is inferred from mapping.
- The first empirical execution `20261023T055412-07a8b0a7` failed closed before public export because unit-leverage fixed effects produced undefined Cook distances. Corrected this diagnostic to report a maximum over defined values with explicit undefined counts; no coefficient, observation or model gate was changed. Added regression tests for singleton fixed effects. New runs snapshot scientific code/configuration to preserve dirty-tree provenance.
- Corrected boundary-sensitive route bands to remain missing, excluding these unsupported origins from nominal band-change denominators. Threshold price comparisons now suppress both-sided summaries if either side has fewer than 30 measured records. Individual station-entrance review coordinates stay private.
- Successful run `20261023T055844-0795d47b` supports 2,978 of 3,110 routing candidates, with 2,962 common complete observations across 281 neighborhoods. It executes 30 location draws, 10 model refits and 199 spatial-cell bootstrap draws. The neighborhood-adjusted association is −9.87% per km with a clustered interval of −22.85% to +5.28%; location-refit point associations range from −7.38% to +3.02%. These scoped observations do not establish a robust operational metro premium or a causal effect.
- Published only aggregate exploratory results in the separate `mapped_reference` field and appended successful-run evidence. Primary `findings_available`, station and track-geometry gates remain false. Updated current status documents; earlier audits, failed runs and earlier numerical results remain preserved in their original runs.

## 2026-10-23 — Historical evidence and topology validation audit

- Added an offline audit of the cached historical route members, entrance membership and walking attachment without reading housing data or changing the completed model run. All track edges come from actual OSM way-node sequences; missing members, disconnections, endpoint gaps and ambiguous joins remain explicit.
- Pinned the official presidential report `https://president.ir/fa/147059`, SHA-256 `9e29cfd2967f0abdefc1bd23c926e8330ed810bc341af25d7a146bd50aed0831`, 44,288 bytes. Its 18 Mehr 1402 date converts to 10 October 2023 using `System.Globalization.PersianCalendar`. Accepted four station-inauguration facts only; three join retained stop areas by exact orthographic name and line. No entrance identity, uninterrupted period service or physical connection is verified by this source. The cached IRNA candidate is a challenge page and supplies no accepted evidence.
- Screened 17 directional/branch track relations. Fifteen pass the software geometry screen; both Line 3 directions have two track components and the same 534.59 m endpoint gap. No artificial edge, node merge or transfer was introduced. Line 5's missing required network Wikidata tag is documented as an exclusion under the existing rule, not an absence of the real service; no identity exception was silently added.
- Audited all 166 retained entrances: 43 share their actual source node with the walking graph; 123 require nonzero straight connectors, including 39 over 25 m. The 25 m threshold is human-review triage only and changes no eligibility/model cutoff. Physical verification remains missing for every entrance. Private connector and endpoint review queues contain OSM geography only and stay outside public exports.
- Successful audit run `20261023T064155-fbb379c4` preserves code/configuration and input/output hashes. The original empirical run `20261023T055844-0795d47b` is unchanged. Primary operational and public metro-geometry gates remain false; source and software verification are not promoted to field validation.
- Follow-up audit `20261023T065027-67bd97e9` adds exact-name station-order comparison against each applicable cached guide list. Fourteen route relations have a compatible matched subsequence; three branch relations lack enough exact matches. No assessed subsequence is non-monotone, but unmatched names and missing adjacencies remain unresolved. This later reference is not relabeled historical operational evidence; previous audit runs remain preserved.

## 2026-10-23 — Bilingual public presentation and GitHub Pages

- The owner requested a public GitHub repository, GitHub Pages publication, and an English/Persian UI with JSON translation catalogs. Added i18next/react-i18next, complete authored UI catalogs, language-aware formatting, persisted preferences, shareable language links, and RTL/LTR layouts. Reviewed Persian prose for natural, consistent wording while preserving evidence qualifications.
- Updated the introductory copy to acknowledge the completed exploratory models while explicitly retaining the unverified primary operational result. Localized gate explanations and the six existing limitations in the presentation without rewriting the saved empirical payload, source artifacts or numerical results. Price remains owner-confirmed total asking price in toman divided by area.
- Prepared a revision-pinned deployment workflow that runs scientific and engineering checks before publishing only the static distribution. Private raw data, housing coordinates, original source files, run directories and review queues are excluded. GitHub publication is explicitly authorized by the owner; this changes distribution only, with no change to scientific eligibility or public metro geometry gates.
