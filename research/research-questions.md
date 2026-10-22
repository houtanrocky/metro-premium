# Questions, estimands and evidence requirements

| Question | Target quantity | Evidence required | Initial status |
|---|---|---|---|
| RQ1 | Median and IQR of advertised price/m² within distance categories, a common month | Verified total-price semantics and eligible destinations | Blocked |
| RQ2 | Distribution of walking minus Euclidean distance and ratio, and station-choice disagreements | Same entrance universe, valid directed pedestrian graph, coverage accounting | Algorithm tested; empirical scope blocked |
| RQ3 | Two-dimensional neighborhood price/access comparisons | n≥30 for each measure, comparable month, supported routes, quality and uncertainty | Counts, price medians/IQR and quality available; metro comparison/ranking blocked |
| RQ4 | Change in log-price association across M1/M2/M3 on shared observations | Sufficient clusters and within-neighborhood variation, valid covariates, diagnostics | Implemented and tested synthetically |
| RQ5 | Accessibility-band instability and specification sensitivity | Known radii plus explicit perturbation assumptions; repeat all eligible-destination routes | Synthetic scenario executed |

The target is the observed advertisement sample, not all households or transacted properties. A one-month primary analysis has no between-month variation; month fixed effects are relevant only in the prespecified multi-month extensions. No causal estimand is identified by this cross-sectional design.
