# MetroPremium

**Metro Accessibility and Residential Asking Prices in Tehran: A Network-Based Geospatial Analysis of Public Real Estate Listings**

Exploring Housing Prices Through Urban Network Science.

[فارسی](README.fa.md) · [Research report](research/report.md) · [Actual audit](artifacts/audits/source-audit.json) · [Defense guide](docs/what-i-must-understand.md)

This repository implements an offline-capable Python research pipeline and a Persian React data publication. **The release includes descriptive housing-price results; no metro price premium has been estimated.** The entire official Divar CSV was downloaded and audited. After inspecting source records, the owner confirmed that `price_value` is the total apartment asking price in toman. This evidence is recorded explicitly as owner confirmation, without claiming publisher verification. Independent metro topology and historical opening checks remain incomplete, so metro layers and price/access associations remain disabled.

## Computed evidence

| Measurement | Observed result |
|---|---:|
| Entire official source | 1,000,000 rows, 60 columns |
| Tehran `residential-sell` / `apartment-sell` | 84,586 listings |
| Those listings with coordinates | 63,126 |
| Those listings inside declared study rectangle | 62,929 |
| Those listings missing location radius | 43,349 |
| December 2024, before area filtering | 11,802 |
| December 2024, fixed positive price and 20–500 m² | 11,767 |
| Candidate rows with in-region coordinates AND known radius 0–500 m | 3,110 |
| Small OSM walking graph | 666 nodes, 1,452 directed edges, 3 weak components |

The December 2024 candidate sample has a median asking price of **86.99 million toman/m²**, with an interquartile range of **58.54–126.67 million toman/m²**. These are observed advertisement descriptions under the owner-confirmed price interpretation. No metro regression coefficients, affordability/access ranking or causal result have been computed. Radius 0 is a source label, not proof of an exact property address. The OSM snapshot is October 2026, while listings are historical. See the [price evidence record](research/price-interpretation.md) and [housing summaries](artifacts/reports/housing-descriptives.json).

## Quick start

Prerequisites: Node 22.12+ (tested on 24), Python 3.11+ (tested on 3.13), [uv](https://docs.astral.sh/uv/). Windows PowerShell, macOS and Linux are supported by the Node task wrapper. No paid API, backend, credentials, map tiles or raw housing data are required to run the website.

```sh
node scripts/task.mjs setup
npm run dev
```

Open http://127.0.0.1:5173. The tracked aggregate research data makes the site work immediately. Self-hosted Vazirmatn fonts avoid remote font requests. MapLibre is loaded separately and renders a real, small OSM street extract with attribution; metro and price layers are visibly disabled.

```sh
node scripts/task.mjs smoke                 # offline, explicitly synthetic full vertical slice
node scripts/task.mjs test                  # Python + React + types + docs + production build
npm run test:e2e                            # Chromium desktop/mobile, accessibility and failures
```

If Playwright's Chromium is absent, run `npx playwright install chromium` once. `PLAYWRIGHT_CHANNEL=chrome` uses an existing Chrome instead.

## Reproduce the real audit and sample

```sh
node scripts/task.mjs acquire               # immutable official CSV, ~781 MB + hashes
node scripts/task.mjs audit-data            # all rows, strict DuckDB parsing
node scripts/task.mjs acquire-osm           # cached route relations + tiny street XML
node scripts/task.mjs reproduce --offline  # sample, network checks, honest gated export, figure
```

No command scrapes live Divar. Downloads have separate commands. Repeating research commands creates new `artifacts/runs/<UTC>-<id>/` directories; each contains config, source hashes, package versions, seed, Git state, failures and output hashes. Stable public files are explicit derived views of those immutable runs. Raw inputs are ignored by Git. For the complete command contract, see [reproducibility](docs/reproducibility.md).

`prepare-data`, `compute-accessibility`, `analyze`, `export-public-data`, and `report` also exist. Empirical stage commands rerun post-audit preparation and real housing-price descriptions while retaining the network gates. They **do not bypass validation or produce empirical metro measures**. The numerical routing/model/sensitivity engine runs end to end in `smoke` mode. Expanding and validating metropolitan network coverage remains required before publishing metro results.

## Repository

```text
apps/web/                   Persian RTL React/TypeScript/Vite publication
packages/shared-types/      Public aggregate TypeScript contract
pipeline/src/metropremium/  Audit, cleaning, geography, routing, statistics, exports
pipeline/tests/             Known-answer and scientific boundary tests
configs/                    Smoke, development (seeded sample), full-source configs
data/public/                Safe aggregate preview and isolated synthetic output
data/raw/                   Ignored immutable official downloads (local)
artifacts/audits/            Full-source quality report (no source rows)
artifacts/reports/           Sample flow, graph checks, analysis gate status
artifacts/figures/           Actual source-month figure, PNG and SVG
artifacts/runs/              Ignored per-execution evidence and private intermediates
research/                   Proposal, methods, plan, literature, findings, report
docs/                       Reproduction, privacy, licensing, deployment, defense
scripts/                    Cross-platform tasks, download, export and QA helpers
```

## Publication status

Gate 1 records owner-confirmed price semantics, adequate records and dates; publisher verification is not claimed. Gate 2 is partial: bounded real graph validation works, but a historically eligible metropolitan metro/walking network has not been verified. Gate 3 blocks metro association inference. Gate 4 permits audit counts, aggregate housing-price distributions, data-quality summaries, actual street geometry and distinctly synthetic educational examples. Gate 5 records executed engineering checks in [delivery](docs/delivery.md).

No remote repository was assumed, no GitHub push was made and no site was deployed. Set `VITE_REPOSITORY_URL` only after establishing your real public repository. See [deployment](docs/deployment.md), [limitations](docs/known-limitations.md), and [open research decisions](docs/outstanding-decisions.md).

Original code: [MIT](LICENSE). Divar and OSM data: ODbL; see [DATA-LICENSE](DATA-LICENSE.md) and [licensing](docs/licensing.md). Code licensing does not relicense input or derived databases.
