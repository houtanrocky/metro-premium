# Findings: initial evidence, 22 October 2026

These results come from the full official source audit and deterministic cleaning. They do not answer the metro-price association questions yet. Machine-readable evidence: [audit](../artifacts/audits/source-audit.json), [sample flow](../artifacts/reports/sample-flow.json), [network checks](../artifacts/reports/network-validation.json).

## Dataset audit

The pinned CSV contains exactly **1,000,000 rows and 60 columns**. The source card reports 57 columns and six months of 2024. Actual month distributions are included in the audit, including dates outside 2024; no attempt was made to silently reconcile this conflict.

The category predicate selects **84,586** Tehran apartment-sale advertisements. Their observed month range is February 2020–February 2025 (not the full-source range). Counts in the main 2024 months are:

| Month (Gregorian) | Selected ads before cleaning |
|---|---:|
| 2024-05 | 10,024 |
| 2024-06 | 9,743 |
| 2024-07 | 10,117 |
| 2024-08 | 9,846 |
| 2024-09 | 9,447 |
| 2024-10 | 11,028 |
| 2024-11 | 11,467 |
| 2024-12 | 11,802 |

The selected population has 63,126 coordinate pairs, all within world ranges; 62,929 are inside the declared study rectangle. Thus world-valid coordinates alone do not ensure that a Tehran listing is geographically usable. There are 21,460 listings without coordinate pairs.

Reported radii in this category population: 500 m in **39,100** rows, 300 m in **515**, zero in **1,622**, missing in **43,349**. Zero is a source value, not externally verified precision. A hard-radius interpretation and any perturbation distribution remain assumptions.

There are no exact whole-row duplicates in the selected category sample. The prespecified attribute key finds **65 candidate groups and 83 excess rows**. These are possible repeated observations, not verified duplicate properties.

The source-price field includes very small and very large positive values, and property areas reach implausible extremes. Positivity alone does not establish a credible monetary value. The audit records minima, maxima, null counts and quantiles; no currency or total-price interpretation has been inferred from plausible-looking magnitude.

![Actual counts of Tehran apartment-sale listings by observed month; a source audit, not a housing-price trend](../artifacts/figures/source-months.png)

## Primary candidate sample

December 2024 is selected by the largest-2024-month rule. Its 11,802 records all pass the fixed-positive-price filter; **35** are excluded by the 20–500 m² scope, leaving **11,767**. Among these, **9,851** have in-region coordinates and **3,110** have both in-region coordinates and a known usable radius. This latter count is a *routing candidate count*, not a count of successfully routed properties.

No price/m² was calculated for real records because the total-price contract is unverified. No neighborhood price or affordability ranking is eligible.

## Network evidence

The OSM metro extract includes the seven requested route relations and 155 station/stop candidates. A candidate count is not a verified number of unique operational stations: platforms, stop positions, duplicated objects and shared stations can differ. Route station-member counts differ from the OSM wiki summary in places; the wiki's counts are not accepted as an authoritative current inventory. No missing segment was filled by drawing station-to-station lines.

The actual small walking extract creates 666 nodes, 1,452 directed edges and three weak components. Five node-pair shortest-path checks satisfy the modeled triangle inequality. They are route-engine checks using OSM street points, not evidence that every real pedestrian route or metro entrance is valid. The five mapped entrance candidates remain quarantined pending station association and temporal eligibility.

## What can be concluded

The source can support a substantial Tehran apartment-sale audit, but location uncertainty, missingness, price semantics and network vintage constrain the proposed study. The empirical metro-price relationship is **not estimated**. All three planned models and scenario sensitivities run on explicitly generated fixtures only. Their synthetic coefficients are not findings about Tehran.
