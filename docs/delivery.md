# Delivery record

Local repository: `S:\Repos\metro-premium`. The initial implementation is a working research preview, with full-source audit and synthetic end-to-end computation. Engineering verification and the final Git identity are recorded here after the final checks; the evidence gates remain explicit in the published data.

See [README](../README.md) for setup, command contract, source/sample counts and the directory tree. The [research report](../research/report.md), [actual audit](../artifacts/audits/source-audit.json), [network validation](../artifacts/reports/network-validation.json), [defense guide](what-i-must-understand.md), [deployment instructions](deployment.md), and [outstanding research decisions](outstanding-decisions.md) form the delivery bundle.

No remote push or site publication is part of this local delivery. Historical price and metro claims remain blocked until their scientific evidence is established. Raw housing data and private run intermediates are not tracked.

## Executed verification

| Check | Actual outcome |
|---|---|
| Official source acquisition | Complete CSV, 780,721,338 bytes, pinned revision and SHA-256 recorded |
| Full-source audit | 1,000,000 rows strictly parsed, 60 fields, distributions and data-quality report saved |
| Real-data candidate workflow | December 2024 sample of 11,767; 3,110 known-radius in-region candidates; no empirical price/access model |
| Cached OSM graph build | Seven route relations acquired; 666 walking nodes, 1,452 directed edges, five node-pair software route checks |
| Synthetic end-to-end | 1,200 generated records → cleaning → graph routing → M1/M2/M3 → sensitivity → aggregate JSON and figure |
| Python | 18 tests passed, including actual temporary CSV audit, checksum rejection, known-answer directed routing, privacy boundary and model recovery |
| React | 4 tests passed: real aggregate contract, filtering/missing state, errors and graph lesson |
| TypeScript | `npm run typecheck` passed |
| Browser | 6 tests passed on desktop and Pixel 7 mobile emulation in installed headless Chrome |
| Accessibility | axe WCAG 2 A/AA and 2.1 AA checks found no violations on tested views; this is not a complete accessibility certification |
| Map rendering | Tests require rendered real street features and nonzero visible map, not just canvas presence; no public OSM tile calls |
| Documentation | 25 Markdown documents and their local link targets checked |
| Setup | Locked uv sync and `npm ci` completed; an initial retry hit a running-server file lock, resolved after stopping that owned server |
| Dependencies | `npm audit` reported zero vulnerabilities after reviewed package updates |
| Production | Vite build passed; MapLibre worker emitted as its own asset; production HTTP 200 and rendered-street smoke passed with no page errors |
| Visual review | Desktop, mobile, actual street map and source-count figure inspected from screenshots |

The map chunk is approximately 1.06 MB minified (about 291 KB gzip), plus a separate 517 KB worker; Vite emits a chunk-size warning. It is split from the main reading interface. Further viewport-triggered loading can reduce initial transfer; this engineering limit does not change the data claims.

The initial pipeline implementation commit is `cea32e9`. The final delivery commit is reported in the handoff and can be retrieved with `git rev-parse HEAD`; a document cannot embed the hash of its own containing commit without changing that hash. Scientific manifests use the commit at the start of each run and mark dirty state honestly. Early bootstrap runs have no commit. Final publication assets record their run ID and source revision.

The final scientific execution evidence is preserved in [reproduction-manifests.json](../artifacts/reports/reproduction-manifests.json). It captures execution at implementation commit `fd44f81`, exact dependency versions, source/input/output hashes, config, timestamps and validation. The empirical reproduction started from a clean tree; the following smoke execution correctly records a dirty tree because the empirical export had just refreshed publication files. The change is generated metadata/results, not an unrecorded analysis-code edit.

## Scientific gates

Gate 1: partial, source/sample/date feasibility established, price semantics unresolved. Gate 2: partial, small real graph tested, operational metro topology and historical eligibility unverified. Gate 3: blocked for real price/access associations. Gate 4: passed for the restricted audit-only preview and separate conceptual demonstrations; price and metro layers stay disabled. Gate 5: local engineering checks listed above passed, with the map bundle warning disclosed.

No empirical metro-price coefficients, purchase recommendations, housing-price map or historical metro-access claim were generated. The report is a research implementation/feasibility report, not a completed empirical paper. Required follow-up evidence and owner decisions are in [outstanding-decisions.md](outstanding-decisions.md).

## Follow-up: owner-supplied metro guide

The Alibaba guide and its linked schematic were acquired privately and audited. A factual extractor covers seven main and three branch lists; 116 of 150 main-line entries have exact normalized-name candidates in cached OSM data. Internal count conflicts, endpoint ambiguity and title-year disagreement are documented, with no change to public metro approval. See [the guide audit](../research/references/alibaba-guide-audit.md). The expanded Python suite passes 23 tests, including five source-parser/comparison tests; 26 documentation files and the production build pass. Earlier audit/sample figures and the original delivery's test record remain historical evidence.

## Follow-up: owner-confirmed housing-price meaning

Documented 23 October 2026: the owner confirmed total apartment asking prices in toman after inspecting actual records. The scoped [price interpretation](../research/price-interpretation.md) now enables real housing-only medians/IQR and filtering sensitivities, without relabeling the evidence as publisher verification or converting currency. Source bytes and the initial audit are unchanged. The same 11,767 candidates have median 86.99 million toman/m² and IQR 58.54–126.67; metro associations remain blocked by network validation.

The Persian site uses public schema version 2 for aggregate housing prices and price distributions in the neighborhood explorer, while retaining disabled metro/price-map layers. New tables and actual figures are in [housing-descriptives.json](../artifacts/reports/housing-descriptives.json), [CSV](../artifacts/reports/housing-descriptives.csv), and [the median/IQR figure](../artifacts/figures/housing-price-summary.png). The expanded Python suite passes 28 tests, React 4 tests, and desktop/mobile browser 6 tests, including owner-evidence/units checks and continued metro gating. Type checking, production build and 27-document link checks pass. This follow-up supersedes the initial price-blocked status above, while preserving its dated evidence record.

## Follow-up: executed historical mapped-entrance extension

Documented 23 October 2026: the historical acquisition is complete, including operator-attested browser imports with explicit source evidence labels. The four-tile walking union contains 734,532 OSM objects and produces 555,686 nodes and 1,236,780 directed edges. The retained mapped subset has 166 entrances; 2,978 of 3,110 routing candidates have supported baseline routes. Three observational models share 2,962 complete cases across 281 neighborhoods. Thirty location draws, ten model refits and 199 spatial-cell wild-bootstrap draws executed.

The adjusted association is −9.87% per additional km, with a neighborhood-clustered interval of −22.85% to +5.28%; location perturbations change its sign. This is exploratory mapped-subset evidence, without operational metro-access approval or a causal interpretation. See the [full findings and limitations](../research/mapped-reference-findings.md) and appended [execution manifest](../artifacts/reports/reproduction-manifests.json), run `20261023T055844-0795d47b`.

The earlier failed run is preserved: strict JSON export stopped on undefined influence diagnostics. Defined Cook distances and explicit missing counts now handle singleton fixed-effect groups. Boundary-sensitive routes have no nominal band. Threshold-price comparisons require 30 measured observations on both sides. Scientific code/config snapshots preserve the exact local dirty-tree implementation. Individual entrance review coordinates remain private.

| Follow-up verification | Executed outcome |
|---|---|
| Python | 57 tests passed, including directed/disconnected routing, singleton influence, boundary bands, privacy suppression, browser import and code-provenance cases |
| React | 5 tests passed, including separate mapped-subset contract and closed operational gates |
| TypeScript / production build | Passed; existing MapLibre bundle-size warning remains |
| Browser | 8 desktop/mobile Chrome tests passed; new results, model table, source links and disabled operating metro layers checked |
| Documentation | 29 research/documentation files and local link targets checked |
| Production preview | Desktop/mobile actual street rendering, exploratory results and assets passed; no page errors or page overflow; signed intervals use explicit left-to-right direction |
| Visual review | Actual aggregate figure and desktop/mobile exploratory section inspected; small nonzero interval bounds preserve significant digits |
| Data boundary | Aggregate payload and minimum-group comparisons checked; raw inputs and private runs remain untracked; primary findings and public metro geometry gates remain false |

No source bytes or previous run evidence were erased. No remote push or deployment occurred. Historical operational eligibility, independent topology/entrance completeness, physical route checks, geographic selection, calibrated spatial uncertainty and expanded-area/period sensitivities remain outstanding.

## Follow-up: historical evidence and network audit

Documented 23 October 2026: offline validation run `20261023T065027-67bd97e9` audits actual track ways, station-order compatibility, line coverage, memberships and all 166 entrance attachments. The [validation report](../research/historical-network-validation.md) and [machine-readable output](../artifacts/reports/historical-network-audit.json) document 15 of 17 software geometry passes, the same Line 3 endpoint gap in two directions, 14 compatible matched station subsequences and three insufficient branch comparisons. Line 5's missing network identifier remains an explicit exclusion under the existing retained-destination rule. No edge, transfer, alias or service date was invented to repair these findings.

An exact cached official presidential report supplies four scoped inauguration facts, matching three retained stop areas. It verifies no individual entrance or uninterrupted December 2024 service. Private review CSVs contain the 123 nonzero connectors (39 over 25 m) and the Line 3 endpoint cases; no housing records were read. The preceding empirical payload remains byte-identical to its saved successful run. The latest audit manifest is appended to the reproduction bundle; all prior runs and source bytes remain intact.

Validation: 70 Python tests, five React tests, TypeScript checks, production build, 30-document link checks and eight desktop/mobile browser tests passed. Browser checks include the new validation report/JSON and closed operational gates. The existing map bundle-size warning remains. Raw official HTML, source coordinates and private review files are not tracked or served; public output contains derived diagnostics and narrowly scoped station facts only.

## Follow-up: bilingual interface and publication preparation

Documented 23 October 2026: the owner authorized GitHub and GitHub Pages publication. Added English and Persian i18next catalogs, revised the Persian prose, and made all authored UI copy, errors, map controls and metadata translatable. Language links, saved preferences, RTL/LTR layouts and locale formatting work without changing the immutable empirical export (`660b878b2a0aaf3da86a464900f39c90dec1a327cea515d66dc835c23e5ea633`). Original scientific documents and technical chart exports keep their source language.

The production build supports the GitHub Pages project path. A revision-pinned workflow validates Python, React, types, documentation, browser behavior and the production artifact before deployment. The publication check audits private paths in Git history, possible credentials and aggregate privacy thresholds. Failure artifacts exclude private runs. Only the static distribution is deployed; raw source data, listing coordinates and private review queues remain local.

Local preparation checks: 70 Python and 11 React/localization tests passed; TypeScript, documentation links and production builds passed. English/Persian desktop/mobile production previews rendered actual streets, retained closed operational gates, and passed path/overflow checks. Browser accessibility checks cover both languages, including keyboard access to wide model tables. The pre-existing MapLibre chunk-size warning remains.

## Published release — 23 October 2026

The owner-authorized repository is public at [houtanrocky/metro-premium](https://github.com/houtanrocky/metro-premium). GitHub Pages serves the [English](https://houtanrocky.github.io/metro-premium/?lang=en) and [Persian](https://houtanrocky.github.io/metro-premium/?lang=fa) versions. This supersedes the earlier local-only delivery statements, which remain as the historical record.

The first deployment of commit `9475982` passed [GitHub's scientific checks and Pages workflow](https://github.com/houtanrocky/metro-premium/actions/runs/39919736584): 70 Python tests, 11 React/localization tests, 12 desktop/mobile browser tests, TypeScript, documentation, production builds, private-path/aggregate checks and four production locale/viewport checks. After deployment, the same four browser checks passed against the actual HTTPS site, including rendered streets, same-origin assets and downloads, LTR confidence intervals, no page errors or horizontal overflow, and closed primary metro gates.

There are 282 JSON translation keys per language, including branding, accessible labels, errors and map controls. The UI has no authored prose hardcoded in JSX. The final catalog-only cleanup retains the tested visible text and is followed by the same gated deployment workflow.

Git normalizes public text artifacts to LF. The canonical tracked public research JSON has SHA-256 `af3076a593875b9012e9e924ccd356e051d61aff3a1404bca17c3bfd6ff0eb66`; the locally preserved original run export has SHA-256 `660b878b2a0aaf3da86a464900f39c90dec1a327cea515d66dc835c23e5ea633`. They contain identical research values. Private source bytes, previous run artifacts and the initial evidence records were not rewritten. Publication does not change the operational-network or causal limitations.
