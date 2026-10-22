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

`--config configs/development.yaml` selects a documented seeded 5,000-row Tehran-category sample. Full mode consumes all category rows. Smoke mode creates 1,200 synthetic records at artificial projected graph coordinates; none are empirical geographic/property records. Do not use development selection counts as a population audit.

Current full/development configs explicitly load `configs/price-contract.yaml`. Its owner-confirmed total-price/toman interpretation is scoped to the pinned dataset revision and selected apartment-sale population. It is hashed in run provenance and is not publisher verification. Empirical reproduction now also generates housing-price medians/IQR, filtering sensitivities, safe neighborhood distributions, CSV/JSON tables and high-resolution figures; metro estimates remain gated. Synthetic fixtures retain their separately declared arbitrary monetary units.

## Offline and restart behavior

Acquisition skips existing files and validates their recorded hashes. `.part` files are never accepted as source inputs. A crashed transfer can be retried; completed bytes remain untouched. Source acquisition is separate from analysis, so `--offline` never downloads implicitly. A fresh clone has public aggregates but no CSV/audit-run cache: download then audit to reproduce scientific calculations. Copy the pinned raw folder and corresponding local audit run/pointer to another offline machine if permitted; otherwise re-audit from cached CSV. Do not commit either.

Raw CSV parsing stores a run-local DuckDB work database and selected Parquet; reserve several GB of disk. Original CSV remains the immutable authority. Avoid simultaneous full-source audits on low-memory machines. Derived public aliases intentionally change when exporting a new run, but old run folders and their manifest hashes remain. Time/UUID metadata changes between runs; numerical tables for the same environment/config/inputs are deterministic. Differences in package versions must be investigated, not described as equivalent by default.

## Provenance

Each run manifest records UTC start/finish, command, config, seed, Git commit/dirty state, Python/package versions, immutable source revision, input hashes, generated output hashes, validation and failures. Graph snapshot/retrieval metadata is copied into graph reports. The earliest bootstrap runs legitimately had no Git commit; subsequent validation runs have one. Public exports carry run ID, revision and observation month. Full validation is not inferred from a zero process exit: scientific gates are separate from engineering completion.

The absolute paths printed by local scripts are not portable data identifiers. The public reports use relative paths and source hashes. `artifacts/audits/latest.json` is a local ignored pointer, not a tracked cross-machine assumption.
