# MetroPremium

**Metro Accessibility and Residential Asking Prices in Tehran: A Network-Based Geospatial Analysis of Public Real Estate Listings**

Exploring Housing Prices Through Urban Network Science.

[فارسی](README.fa.md) · [Research report](research/report.md) · [Actual audit](artifacts/audits/source-audit.json) · [Defense guide](docs/what-i-must-understand.md)

This repository implements an offline-capable Python research pipeline and an English/Persian React data publication. **The release includes housing descriptions and exploratory associations with distance to a retained historical mapped-entrance subset; no operational metro price premium is established.** The entire official Divar CSV was downloaded and audited. After inspecting source records, the owner confirmed that `price_value` is the total apartment asking price in toman. This evidence is recorded explicitly as owner confirmation, without claiming publisher verification. Independent metro topology, entrance completeness and historical operation checks remain incomplete; public metro layers and the primary operational-access claim stay disabled.

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
| Historical walking graph, requested 1 December 2024 | 555,686 nodes, 1,236,780 directed edges |
| Retained mapped entrances / supported routes | 166 / 2,978 |
| Common complete exploratory model sample | 2,962 observations, 281 neighborhoods |

The December 2024 candidate sample has a median asking price of **86.99 million toman/m²**, with an interquartile range of **58.54–126.67 million toman/m²**. These are observed advertisement descriptions under the owner-confirmed price interpretation. In the exploratory mapped-subset analysis, the property/neighborhood-adjusted association is −9.87% per additional km, with a neighborhood-clustered interval of −22.85% to +5.28%; location scenarios change its sign. This does not establish an operational metro premium or causal effect. Radius 0 is a source label, not proof of an exact property address. The original map preview is from October 2026; the separate exploratory inputs request the OSM database at 1 December 2024. See [mapped-reference findings](research/mapped-reference-findings.md), the [price evidence record](research/price-interpretation.md) and [housing summaries](artifacts/reports/housing-descriptives.json).

## Bilingual website

UI text is maintained in `apps/web/src/locales/en.json` and `fa.json`. The language switch supports RTL/LTR, localized numbers and Gregorian months, and a saved preference. Use `?lang=en` or `?lang=fa` to share a language-specific view. Persian is the first-visit default. Scientific exports, original research documents and technical chart downloads retain their source content. See [GitHub Pages deployment](docs/deployment.md).

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

`prepare-data`, `compute-accessibility`, `analyze`, `export-public-data`, and `report` also exist. The default full/development configurations retain the original housing-only scope. The historical mapped-subset extension has a separate configuration:

```sh
node scripts/task.mjs acquire-historical --browser-links
node scripts/task.mjs reproduce --config configs/mapped-reference.yaml --offline
```

The first command prepares manual download/import instructions for missing inputs. The second requires the cached historical metro/Line 5 inputs and merged walking tiles, then runs routing, three observational models, snapping/filtering sensitivities, 30 location draws, 10 model refits and 199 spatial-cell bootstrap draws. Its aggregates appear under a separately scoped `mapped_reference` field; operational network approval remains closed. See [reproduction](docs/reproducibility.md) and the [extension plan](research/mapped-reference-plan.md).

`node scripts/task.mjs validate-historical-network` separately audits actual track-way geometry, entrance membership, walking attachment and the pinned official station-inauguration evidence. The [validation report](research/historical-network-validation.md) documents the Line 3 cached endpoint gap, Line 5 rule exclusion and unverified physical connectors. It preserves the existing model run and keeps operational/public metro gates closed.

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

Gate 1 records owner-confirmed price semantics, adequate records and dates; publisher verification is not claimed. Gates 2 and 3 are partial: the historical mapped-subset exploratory computation has executed, but operational eligibility and network completeness remain unverified. Gate 4 permits the separately qualified exploratory aggregates alongside housing descriptions, quality summaries, actual preview streets and distinctly synthetic examples. Primary operational-access findings and public metro layers remain disabled. Gate 5 records executed engineering checks in [delivery](docs/delivery.md).

No remote repository was assumed, no GitHub push was made and no site was deployed. Set `VITE_REPOSITORY_URL` only after establishing your real public repository. See [deployment](docs/deployment.md), [limitations](docs/known-limitations.md), and [open research decisions](docs/outstanding-decisions.md).

Original code: [MIT](LICENSE). Divar and OSM data: ODbL; see [DATA-LICENSE](DATA-LICENSE.md) and [licensing](docs/licensing.md). Code licensing does not relicense input or derived databases.
