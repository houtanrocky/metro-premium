# Statistical analysis plan v0.1

Recorded during implementation, before any empirical metro-price model was fit. Dataset counts and missingness had been inspected. This is not a registered preregistration. Later decisions must be appended in the decision log and labeled exploratory where relevant.

## Primary analysis

Select the largest observed 2024 Tehran apartment-sale month before inspecting accessibility-price associations. Result: December 2024. Restrict to fixed positive prices and 20–500 m². Do not calculate price/m² until total-price semantics are verified. Use source units if denomination remains unverified. Do not pool nominal years. Primary summaries use median/IQR, n and coverage; no p-value-based headline selection.

After independent network verification, use all operational, eligible entrances with a complete buffered walking region. Unknown opening dates remain ineligible for a historical analysis. Alternatively label the analysis as historical listings versus a later reference network, with an independently justified current eligibility set and no historical-access claim. Both options require a versioned scope decision.

## Model equation

For positive valid total asking price P and area A:

`y_i = log(P_i/A_i) = α + β d_i(km) + γᵀX_i + δ_neighborhood(i) + τ_month(i) + ε_i`.

M1 includes only d. M2 adds log(area), rooms, literal construction year, numeric floor, and categorical parking/elevator/storage (including missing amenity category). M3 adds neighborhood and period fixed effects when estimable. Construction year is a recorded-year control, not precisely computed building age. Total floors remains audited but is not in v0.1's primary formula because of missingness and recoding uncertainty. Add it as a declared extension after examining adequacy, not to optimize significance.

Use a common complete-case set across M1–M3 to separate adjustment changes from sample changes. Report input and complete-case n and missingness. A one-month analysis cannot estimate period contrasts; the month term has no additional columns. Multi-month extensions need month effects and comparable neighborhood coverage, with no pooled nominal neighborhood ranking.

The implemented safeguards require n≥100, ≥30 neighborhood clusters, full column rank and n≥5×parameter count. M3 is withheld if within-neighborhood distance SD is <0.01 km. These are conservative engineering gates, not proofs of adequate power or identification. Standardized design conditioning and individual neighborhood variation need substantive review beyond them.

Report β per km and 100[exp(β)−1]%, with transformed endpoints of a 95% interval. This is a conditional association under the specification, not the change caused by moving a station or household. Fixed effects do not remove all within-neighborhood confounding.

## Uncertainty and diagnostics

Neighborhood-clustered CR1 covariance, finite-sample correction and t-based inference are implemented. With few clusters, do not silently fall back to independent-row standard errors; withhold estimates. Cluster covariance is not a remedy for omitted variables, nonrepresentative listings, or dependence across neighborhood boundaries. A spatial block bootstrap/cross-boundary dependence estimator remains required for stronger empirical claims if residual structure persists.

Implemented diagnostics: sample/cluster counts, matrix rank, condition number, within-neighborhood distance SD, residual quantiles, Breusch–Pagan test and maximum Cook's distance. An exploratory row-standardized 8-nearest-neighbor residual Moran I is available when projected origins exist. Self-neighbors are explicitly excluded by row identity, including coordinate ties. It is descriptive, not a calibrated significance test; approximate/coincident origins and tied-neighbor choices require further empirical review. Do not delete influential observations solely to improve a coefficient. Examine nonlinear distance response and partial residual plots before interpreting a linear slope broadly.

## Sensitivity plan

Implemented synthetic-executable variants: all candidate rows versus attribute-deduplicated; no tail removal versus 0.5/99.5 percentile-tail omission; radii ≤100/250 m; Euclidean versus network distance; cutoffs 400/500/800/1000/1500 m. Duplicate candidates are not known repeat properties; default retains them. Tail flags do not imply errors; default retains tails.

Still required before empirical conclusions: expanded area limits, multiple adjacent 2024 months with fixed effects, alternative snapping tolerances and edge-based connectors, adequate map buffer, historical station eligibility versus later-reference scope, low-coverage-area exclusion, spatial block uncertainty, and rerunning models after location perturbation. The perturbation engine currently reports route/band instability; it does not yet refit empirical models across draws. Unsupported variants must not appear as completed sensitivity results.

## Descriptive neighborhood comparisons

No single weighted score. A price/access scatter or Pareto description requires ≥30 valid price rows AND ≥30 valid routed rows per neighborhood-period; no current ranking is eligible. Compare common months and property mix, publish coverage and classification instability, suppress unreliable geographic representations and describe the result as sample-specific. Do not offer purchase advice.
