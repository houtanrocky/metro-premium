# Reproduction contract

## Environments

`pipeline/uv.lock` and `package-lock.json` pin environments. `node scripts/task.mjs setup` runs uv with the repository-root `.venv`, then `npm ci` and safe public-file synchronization. On Windows use the Node wrapper instead of relying on Unix make. The Makefile delegates to exactly the same wrapper. Package installation needs network access once; subsequent scientific commands operate on cached local inputs.

## Commands

| Command after `node scripts/task.mjs` | Prerequisite | Action |
|---|---|---|
| `setup` | uv, Python and Node | Install locked Python/test + web dependencies |
| `acquire` | Network, ~1 GB free for raw CSV | Fetch official pinned metadata/card/CSV, never source rows from a viewer |
| `audit-data` | Official cached CSV | Strict full-source audit, selected Parquet, immutable evidence |
| `acquire-osm` | Network | Cache seven relations and a bounded street XML; no tile fetch |
| `metro-reference --offline` | Cached Alibaba guide/PDF and OSM metro JSON | Extract factual line/branch sequences and compare station-name/order candidates; omit `--offline` for first acquisition |
| `prepare-data` | Completed full audit | Recode and filter a single-month analytical candidate sample |
| `build-networks` | Cached OSM inputs | Build tiny directed metric graph, candidate and validation reports |
| `compute-accessibility` | Audit, optional OSM | Run preparation; empirical routing explicitly blocked while verification incomplete |
| `analyze` | Audit | Descriptive area summary and blocked empirical model status |
| `export-public-data` | Audit, cached OSM | Safe allowlisted aggregate preview + validation reports |
| `report` | Same | Export preview and actual source-count PNG/SVG; written report explains scope |
| `reproduce --offline` | Audit and cached inputs | Re-run all current empirical post-audit work and publication exports |
| `smoke --offline` | Locked Python environment | Generated fixture → cleaning → tiny graph → Dijkstra → 3 models → sensitivity → public JSON/figure |
| `test` | All dependencies | Python, React, type, docs and production build checks |
| `dev` | npm dependencies + safe public assets | Local Vite server |

Browser tests are `npm run test:e2e`. Run `npx playwright install chromium` if needed. The first 2026 run was tested with local installed Chrome via `PLAYWRIGHT_CHANNEL=chrome` where applicable; exact final checks are in [delivery](delivery.md).

## Historical download timeouts

`acquire-historical` requests the OSM database at `2024-12-01T00:00:00Z`. The already cached metro extract is retained. Download the remaining inputs sequentially:

```sh
node scripts/task.mjs acquire-historical --kind line5
node scripts/task.mjs acquire-historical --kind walk
```

Use `--base https://overpass.private.coffee/api/interpreter` to select the alternative provider, which documents attic-data support. Public-service availability is not guaranteed. On Windows, a quick connectivity check is:

```powershell
curl.exe --connect-timeout 10 --max-time 20 --fail-with-body --user-agent "MetroPremium/0.1 (academic local research)" https://overpass-api.de/api/status
```

A plain-text status response confirms that endpoint is reachable; it does not guarantee that a historical query will complete. The main Overpass operator requires scripts to send an identifying User-Agent; the downloader already sends the same project identifier shown above. A 406 response to a request with a default User-Agent can reflect that policy, rather than lack of connectivity. Do not rotate or spoof identities to evade a rejection. See the [operator's guidance](https://github.com/drolbr/Overpass-API/issues/791). If this lightweight request instead times out, check the network/proxy connection or try later before launching a long acquisition. Browser success alone does not establish that command-line requests use the same network/proxy path. Increasing the query timeout alone cannot establish connectivity.

Each missing input gets at most two attempts by default, with a 30-second pause after the first transient failure. `--attempts 1` disables retries; `--request-timeout 240` controls the socket timeout in seconds, independently of the query's 180-second server runtime limit. Progress names the input and endpoint. Successful downloads survive a later failure, so repeating the command resumes at the first missing input.

Responses are downloaded into the ignored run directory first. Only nonempty historical JSON without an Overpass runtime remark, with matching byte count and SHA-256, enters the source cache. Rejected responses and individual failed attempts remain in run evidence; existing sources are never overwritten. Offline runs verify the same checks and never fetch missing files. These changes do not establish historical operation, network completeness or public metro-layer approval.

### Manual browser downloads

When browser requests work while the script requests fail, prepare a local download guide without sending any API requests:

```sh
node scripts/task.mjs acquire-historical --browser-links
```

Open the printed `browser-downloads.html` in your browser. It lists only missing inputs, with prefilled Overpass Turbo queries pinned to the same snapshot, endpoint and spatial scope as the downloader. The links do not run automatically. Run one query at a time, keep it unchanged, and export **raw data** as OSM JSON (not GeoJSON). Save each file in Downloads with the filename shown. If the browser receives a query error or timeout, wait before retrying; a working status page does not guarantee a completed data query.

Use the import command beside each query. For example:

```powershell
node scripts/task.mjs acquire-historical --input line5 --import-file "$env:USERPROFILE\Downloads\line5.json"
```

Importing asserts that the file came from the unchanged prepared query at the recorded endpoint. The sidecar labels this as an operator-supplied browser download and explicitly records that the snapshot request was not independently verified. The original response is preserved in the run directory. The importer checks raw OSM format, byte count/hash, expected Line 5 relation or walking ways, node coordinates, and referenced-object completeness. It refuses to overwrite existing sources. A saved response does not itself prove which query produced it; import time is recorded separately from unknown browser retrieval time.

After importing the four walking tiles, merge them with `node scripts/task.mjs acquire-historical --kind walk --offline`. Manual imports and guide creation never change public network approval or run the empirical model.

### Reproduce the historical mapped-subset extension

With the historical metro/Line 5 sources and merged walking file cached:

```sh
node scripts/task.mjs reproduce --config configs/mapped-reference.yaml --offline
```

This executes exploratory mapped-subset routing, the three models on common complete cases, filtering/snapping sensitivities, 199 spatial-cell wild-bootstrap draws, 30 location draws per candidate and 10 location-model refits. The [results](../research/mapped-reference-findings.md) record successful run `20261023T055844-0795d47b`. The primary operational-access gate remains closed. Default full/development configurations retain the housing-only scope; use the explicit mapped-reference configuration to reproduce this extension.

New runs save scientific Python source, task scripts, YAML configuration and the locked Python environment definitions under their private `source-code` directory, with individual hashes in the manifest. This preserves exact local code even when Git is dirty. No raw dataset is collected into that code snapshot. Individual entrance review CSV files remain in private runs rather than the aggregate report export directory.

### Audit historical evidence and actual topology

```sh
node scripts/task.mjs validate-historical-network
```

This offline audit uses the same cached historical OSM sources/guide and the pinned official article/sidecar named in `configs/historical-evidence.yaml`. It screens real track-way membership/order, line/entrance coverage and walking attachments, then joins explicitly scoped official station-inauguration facts by exact name and line. It does not read housing records, rerun a model or approve operating metro geometry. Output: `artifacts/reports/historical-network-audit.json`; source identifiers and entrance coordinates for manual review stay in the ignored run directory. The [validation report](../research/historical-network-validation.md) documents the findings, remaining evidence and private-cache reproduction requirements.

`--config configs/development.yaml` selects a documented seeded 5,000-row Tehran-category sample. Full mode consumes all category rows. Smoke mode creates 1,200 synthetic records at artificial projected graph coordinates; none are empirical geographic/property records. Do not use development selection counts as a population audit.

Current full/development configs explicitly load `configs/price-contract.yaml`. Its owner-confirmed total-price/toman interpretation is scoped to the pinned dataset revision and selected apartment-sale population. It is hashed in run provenance and is not publisher verification. Empirical reproduction now also generates housing-price medians/IQR, filtering sensitivities, safe neighborhood distributions, CSV/JSON tables and high-resolution figures; metro estimates remain gated. Synthetic fixtures retain their separately declared arbitrary monetary units.

## Offline and restart behavior

Acquisition skips existing files and validates their recorded hashes. `.part` files are never accepted as source inputs. A crashed transfer can be retried; completed bytes remain untouched. Source acquisition is separate from analysis, so `--offline` never downloads implicitly. A fresh clone has public aggregates but no CSV/audit-run cache: download then audit to reproduce scientific calculations. Copy the pinned raw folder and corresponding local audit run/pointer to another offline machine if permitted; otherwise re-audit from cached CSV. Do not commit either.

Raw CSV parsing stores a run-local DuckDB work database and selected Parquet; reserve several GB of disk. Original CSV remains the immutable authority. Avoid simultaneous full-source audits on low-memory machines. Derived public aliases intentionally change when exporting a new run, but old run folders and their manifest hashes remain. Time/UUID metadata changes between runs; numerical tables for the same environment/config/inputs are deterministic. Differences in package versions must be investigated, not described as equivalent by default.

## Provenance

Each run manifest records UTC start/finish, command, config, seed, Git commit/dirty state, Python/package versions, immutable source revision, input hashes, generated output hashes, validation and failures. Graph snapshot/retrieval metadata is copied into graph reports. The earliest bootstrap runs legitimately had no Git commit; subsequent validation runs have one. Public exports carry run ID, revision and observation month. Full validation is not inferred from a zero process exit: scientific gates are separate from engineering completion.

The absolute paths printed by local scripts are not portable data identifiers. The public reports use relative paths and source hashes. `artifacts/audits/latest.json` is a local ignored pointer, not a tracked cross-machine assumption.
