# Literature review and positioning

Search conducted 22 October 2026. The entries below were checked against publisher, author or journal pages; only accessible abstracts/metadata were used where full text was unavailable. This is a focused review, not an exhaustive systematic review. Findings in cited studies do not substitute for MetroPremium estimates.

## Hedonic prices and transit capitalization

[Rosen (1974), *Hedonic Prices and Implicit Markets: Product Differentiation in Pure Competition*, Journal of Political Economy 82(1), 34–55](https://www.journals.uchicago.edu/doi/10.1086/260169), DOI 10.1086/260169, provides the foundational interpretation of product characteristics in differentiated-good pricing. A fitted housing characteristic coefficient still requires assumptions and does not itself identify the welfare or causal effect of a transport intervention.

[Debrezion, Pels and Rietveld (2007), *The Impact of Railway Stations on Residential and Commercial Property Value: A Meta-analysis*, Journal of Real Estate Finance and Economics 35, 161–180](https://link.springer.com/article/10.1007/s11146-007-9032-z), DOI 10.1007/s11146-007-9032-z. The review documents variation across settings and specifications. It motivates reporting contextual and specification sensitivity rather than presuming a universal positive premium. The working-paper version uses a different evidence pool; cite the published version consistently.

## Previous Tehran research

[Forouhar (2016), *Estimating the impact of metro rail stations on residential property values: evidence from Tehran*, Public Transport 8, 427–451](https://link.springer.com/article/10.1007/s12469-016-0144-9), DOI 10.1007/s12469-016-0144-9. The publisher abstract describes contrasting northern/southern station contexts with before/after and difference-in-differences comparisons. MetroPremium should treat such contextual heterogeneity as a substantive concern, not assume all neighborhoods have an identical accessibility relationship.

[Forouhar and Hasankhani (2018), *The effect of Tehran metro rail system on residential property values: A comparative analysis between high-income and low-income neighbourhoods*, Urban Studies 55(16), 3503–3524](https://journals.sagepub.com/doi/10.1177/0042098017753089), DOI 10.1177/0042098017753089. The publisher describes a mixed-method comparison of six stations across income contexts. Its findings should not be imported as the answer for this different advertisement sample and period.

[Yazdanifard, Joshaghani and Talebian (2021), *Metro station inauguration, housing prices, and transportation accessibility: Tehran case study*, Journal of Transport and Land Use 14(1), 537–561](https://www.jtlu.org/index.php/jtlu/article/view/1622), DOI 10.5198/jtlu.2021.1622. The open journal paper studies 2010–2018 expansions with a difference-in-differences design and considers pre-existing transit access. Unlike that opening-based design, MetroPremium's initial cross-sectional plan supports adjusted association only. A future causal extension would require an additional design, reliable intervention timing and its own assumptions.

[Soltani, Zali, Mirzaei, Heydari, Rahimi and Hamidi (2023), *Multilevel Impacts of Urban Amenities on Housing Price in Tehran, Iran*, Journal of Urban Planning and Development 149(4)](https://ascelibrary.org/doi/10.1061/JUPDDM.UPENG-4434), DOI 10.1061/JUPDDM.UPENG-4434. The publisher abstract motivates multilevel treatment of housing attributes and urban amenities. This supports the need to distinguish neighborhood structure from property attributes; it does not validate our source variables or solve omitted confounding.

## Street networks and pedestrian measurement

[Boeing (2017), *OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks*, Computers, Environment and Urban Systems 65, 126–139](https://www.sciencedirect.com/science/article/pii/S0198971516303970), DOI 10.1016/j.compenvurbsys.2017.05.004, establishes reproducible spatial graph acquisition and analysis. Current [OSMnx documentation](https://osmnx.readthedocs.io/en/stable/) instead asks package users to cite Boeing (2025), *Modeling and Analyzing Urban Networks and Amenities with OSMnx*, Geographical Analysis 57(4), 567–577, DOI [10.1111/gean.70009](https://doi.org/10.1111/gean.70009). OSMnx is installed for future metropolitan extraction; the current bounded XML importer is custom and its decisions are documented separately.

[Randall and Baetz (2001), *Evaluating Pedestrian Connectivity for Suburban Sustainability*, Journal of Urban Planning and Development 127(1)](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9488%282001%29127%3A1%281%29), DOI 10.1061/(ASCE)0733-9488(2001)127:1(1). Their directness/connectivity framing supports measuring navigable routes instead of assuming that radial proximity captures pedestrian access. Shortest-distance convenience is still narrower than walkability, which also depends on safety, comfort, slope and accessibility for different bodies.

## Spatial confounding

[Paciorek (2010), *The Importance of Scale for Spatial-Confounding Bias and Precision of Spatial Regression Estimators*, Statistical Science 25(1), 107–125](https://projecteuclid.org/journals/statistical-science/volume-25/issue-1/The-Importance-of-Scale-for-Spatial-Confounding-Bias-and-Precision/10.1214/10-STS326.pdf), DOI 10.1214/10-STS326. Spatial adjustment cannot automatically separate an exposure from unmeasured processes at similar spatial scales. This is a reason to report within-neighborhood variation, residual dependence and uncertainty, and to avoid interpreting fixed effects as a causal guarantee.

## What remains to review

Inspect full texts for the Tehran studies before faculty submission; compare their spatial treatments, sale-versus-asking outcomes, data access and identification assumptions. Extend the review to Persian-language journals and local transport records, measurement-error methods for anonymized locations, and OSM completeness in Tehran. No claim of exhaustiveness or novelty is made. The practical contribution is the transparent audit, public communication and reproducible network-versus-Euclidean measurement workflow, conditional on resolving the documented evidence gaps.
