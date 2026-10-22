# Research proposal

## Motivation and scope

Tehran residents face both costly housing and uneven access to transit. A public research artifact should make the relationship inspectable without turning an observational association into a purchase recommendation. Advertised prices measure seller expectations and sample selection, not completed transaction values or willingness to pay in a representative population.

The initial population is official Divar Tehran residential apartment-sale advertisements, with fixed positive prices, valid areas and explicit monthly observations. Rentals, commercial space, villas and land are outside scope. No live-platform scraping or identity inference is needed. The platform is independent and has no established institutional endorsement.

## Research questions and contributions

RQ1 concerns descriptive differences in asking-price-per-m² by proximity. RQ2 compares straight-line and walking-network access to eligible metro entrances. RQ3 asks which sufficiently observed neighborhoods combine lower prices and better access within a common period, without a composite score. RQ4 compares unadjusted, property-adjusted and neighborhood-adjusted associations. RQ5 quantifies how approximate coordinates change classifications and model conclusions.

The contribution sought is a reproducible measurement comparison with explicit uncertainty and evidence gates. Neither using Divar nor applying Dijkstra makes the work intrinsically novel. Existing Tehran metro studies are discussed in [the literature review](literature-review.md).

## Proposed design

Audit the entire revision-pinned CSV before selecting a period. Separate original fields from numeric recodings. Construct a projected pedestrian graph and a distinct metro graph. Verify station-to-line identities, entrance associations and opening dates. Compute all eligible-destination path distances with a reverse multi-source search, rather than choosing a straight-line nearest station first.

Begin with monthly counts, missingness and sample coverage. After price semantics and network checks pass, compare medians and distributions. Fit log-price models on a shared complete-case sample and report excluded observations. Treat within-neighborhood variation as an identification requirement for fixed effects, not as a nuisance to remove. Check tails, duplicate candidates, metric choice, spatial uncertainty and infrastructure vintage.

## Feasibility outcome of initial implementation

There are enough Tehran apartment-sale records to investigate the questions. A single December 2024 window avoids pooling nominal years. Price semantics were initially unresolved; the owner subsequently confirmed total apartment asking price in toman after inspecting source examples, enabling real housing-only descriptions with an explicit evidence label. The acquired October 2026 network is not a historical reconstruction, and independent network validation remains incomplete. A full synthetic vertical slice tests the implementation without filling those geographic gaps.

## Scientific and practical value

The project makes difficult measurement choices visible to researchers and to a Persian-speaking public. Its nearest-entrance algorithm, privacy boundary and falsifiable test cases can support future work even if the final association is weak or poorly identified. A negative or uncertain finding is a valid outcome. Sample representativeness, anonymous coordinates, unmeasured neighborhood characteristics, street mapping completeness and unknown source-price semantics are central limitations rather than footnotes.
