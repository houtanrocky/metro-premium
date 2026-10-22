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
