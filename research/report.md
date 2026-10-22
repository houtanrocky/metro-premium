# Metro Accessibility and Residential Asking Prices in Tehran

## Abstract

MetroPremium implements a reproducible platform for studying housing asking prices and metro accessibility using official Divar listings and OSM networks. A complete audit of a pinned one-million-row source identifies 60 columns, temporal inconsistencies with the dataset card, and 84,586 Tehran apartment-sale advertisements. A deterministic December 2024 candidate sample has 11,767 observations after declared price/area filters, of which 3,110 also have in-region coordinates and a known usable location radius. Real metro relations and a bounded walking graph are acquired. Price-total semantics, independent metro validation and historical network eligibility remain unresolved; consequently no empirical metro-price estimate is reported. A synthetic vertical slice and automated tests demonstrate implementation behavior without treating generated data as evidence about Tehran.

## 1. Introduction

Transit accessibility can coincide with both desirable access and local nuisances. Housing characteristics and neighborhood structure can confound proximity comparisons. This project asks whether observed apartment asking prices vary with accessibility, whether walking routes differ from radial measures, and how approximate coordinates affect conclusions. It serves as an open research artifact and Persian public explanation, without established institutional affiliation or peer review.

## 2. Related work

The [literature review](literature-review.md) situates the project in hedonic pricing, transit capitalization, urban graph measurement and spatial confounding. Tehran-specific research already includes [Forouhar (2016)](https://link.springer.com/article/10.1007/s12469-016-0144-9), [Forouhar and Hasankhani (2018)](https://journals.sagepub.com/doi/10.1177/0042098017753089), and [Yazdanifard et al. (2021)](https://www.jtlu.org/index.php/jtlu/article/view/1622). Their different periods, market measurements and intervention designs cannot be treated as results from this sample. The intended contribution is reproducible uncertainty-aware network measurement and transparent communication, not an unsupported novelty claim.

## 3. Data

The [official source](https://huggingface.co/datasets/divarofficial/real_estate_ads) is pinned at revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85`. The CSV hash and complete schema/null/category/month/city audit are in [source-audit.json](../artifacts/audits/source-audit.json). Observed scope differs from the card; this discrepancy is retained rather than hidden.

Exact Tehran residential apartment-sale category selection yields 84,586 advertisements. December 2024 is the largest selected 2024 month before looking at any accessibility-price relationship. Its 11,802 observations become 11,767 after fixed positive price and 20–500 m² area restrictions. The [sample flow](../artifacts/reports/sample-flow.json) reports every exclusion. Missing coordinates and radii are reported separately rather than silently removing rows from the coverage denominator.

## 4. Network construction

Seven OSM route relations are cached at an October 2026 snapshot. Geometry completeness checks do not establish operational correctness. The small actual street extract has 666 nodes, 1,452 directed edges and three weak components; five representative node-pair routes satisfy consistent projected triangle checks. Physical barriers/access and metro eligibility need further validation. The [network report](../artifacts/reports/network-validation.json) keeps metro routes disabled and records inputs/hashes. No schematic was supplied or used as geography.

## 5. Accessibility measures

Projected EPSG:32639 metres support distances. The engine computes nearest eligible-entrance Euclidean distance, modeled walking distance including declared connectors, minutes at 80 m/min, bands and a ratio. A weighted super-source on the reversed directed graph gives a global nearest-reachable-entrance optimum for the modeled node-snapping system. A nearest-Euclidean-only routing shortcut is not used. Failure statuses remain missing rather than replaced with radial estimates. See [methodology](methodology.md) for mathematical definitions and the connector limitations.

## 6. Statistical methodology

The [analysis plan](statistical-analysis-plan.md) specifies descriptive medians/IQR and three log-price models: unadjusted; property-controlled; neighborhood/period-controlled when estimable. Comparisons use shared complete cases. Safeguards check sample and cluster counts, rank and within-neighborhood variation. Clustered confidence intervals, residual and influence diagnostics are implemented; spatial block inference remains outstanding. No empirical model is fit while required input meaning and geography are unresolved.

## 7. Results

Real computed results are data feasibility and quality evidence, not a price premium. Of category-selected Tehran advertisements, 21,460 have no coordinates and 43,349 have no radius. Radius 500 m occurs in 39,100 records; 300 m in 515 and zero in 1,622. No exact whole-row duplicates were found in that population; attribute matching identifies 65 possible duplicate groups and 83 excess rows. No identity claim is inferred from these matches.

![Observed month counts in the official Tehran apartment-sale subset, before analytical filters](../artifacts/figures/source-months.png)

The primary candidate sample contains 9,851 in-region coordinates, but only 3,110 also have known radius within the declared range. No row is publicly presented as an analyzed metro-accessible property. The price contract is unresolved, so real price/m² and regression outputs are absent by design. Full source-month counts and denominators are in [findings](findings.md).

## 8. Sensitivity analysis

The generated 1,200-record fixture executes three models and variants for duplicate flags, tail flags, radius subsets, alternative distance and cutoffs. Known-coefficient tests check numerical recovery. A uniform-area disk scenario evaluates route/band changes and failures on the synthetic graph. These results validate program behavior under stated artificial conditions only. Empirical location-draw refits, temporal/network-vintage comparisons, expanded-area sensitivity and spatial block uncertainty are not completed and cannot support a Tehran conclusion.

## 9. Discussion

The dataset is large enough for further study, but usable geographic information is a stricter requirement than row count. Approximation radii are of the same order as common near-metro thresholds, making deterministic near/far labels questionable. Likewise, a current OSM route relation does not establish that an entrance operated when a listing appeared. An honest public preview can explain these limitations while exposing the evidence and working methods.

## 10. Limitations

Asking versus transacted prices, nonrepresentative platform selection, possible repeat advertising, missing covariates, approximate locations, map completeness, later network vintage and unmeasured confounding constrain inference. Exact shortest paths on an incomplete graph are not exact real-world access. A single month's associations would not characterize today's market. The [limitations register](limitations.md) distinguishes those issues from implementation checks.

## 11. Conclusion

The initial deliverable establishes a complete-source audit, transparent candidate sample, functional routing/statistics engines and a safe Persian publication. It does not yet answer whether metro proximity is associated with higher asking prices in Tehran. Resolving the price contract and geographic/temporal validation is necessary before releasing empirical comparisons. No causal conclusion is claimed.

## 12. Reproducibility and data availability

Code and safe aggregate outputs are included; raw source bytes and private run intermediates are ignored by Git. Follow [reproducibility instructions](../docs/reproducibility.md) to acquire the pinned official file, audit it, acquire cached map inputs and recreate exports. Each run captures config, seed, hashes, Git state and packages. Original code and input-data licenses are separate; read [data notices](../DATA-LICENSE.md) before publication.

## 13. References

Verified bibliographic entries and primary links for Rosen (1974); Debrezion, Pels and Rietveld (2007); Forouhar (2016); Forouhar and Hasankhani (2018); Yazdanifard, Joshaghani and Talebian (2021); Soltani et al. (2023); Boeing (2017, 2025); Randall and Baetz (2001); and Paciorek (2010) appear in the [literature review](literature-review.md). Data sources and exact input identities are listed in [the source inventory](../docs/data-sources.md).
