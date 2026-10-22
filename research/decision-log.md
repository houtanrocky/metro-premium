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
