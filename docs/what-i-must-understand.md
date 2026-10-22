# What I must understand to defend MetroPremium

You should be able to explain the following without opening the code. Lead with the actual evidence boundary: this initial release audits real data and validates an implementation, but does not estimate an empirical metro price premium.

## Graph representations

A pedestrian graph is G=(V,E,w). Vertices are source street/path nodes; edges are traversable directed connections and w is nonnegative length in metres. Shape nodes are retained, so node count is not intersection count. Shared coordinates do not create a topological connection; a bridge crossing a road without a shared source node is not a junction. Different weak components may be near each other physically yet unreachable in the graph. A weak component ignores directions; directed reachability is stronger.

A metro graph is different: its nodes can represent stations, with documented adjacent-service edges and supported transfers. A station can have multiple physical entrances. Rail tracks, platforms, stop positions and entrance doors are different OSM objects. The relevant destination for walking is an eligible accessible entrance, not a track center or a centroid. A map picture cannot establish coordinates or walking distance.

Parallel pedestrian edges can matter for access or route length. In our distance-only router, retaining the shortest permitted edge for an ordered node pair preserves shortest distances. This simplification would not preserve attributes needed for wheelchair access, stairs, turn penalties or travel-time modeling without additional handling.

## Shortest paths and optimality

For a fixed origin and destination, path length is the sum of edge lengths. Dijkstra's algorithm is valid for nonnegative edge weights; a negative edge would invalidate its usual settled-distance guarantee and is rejected. Breadth-first search minimizes edge count, which is not walking length when lengths differ. Floyd–Warshall is unnecessary all-pairs work for a large city. A* needs an admissible heuristic and does not by itself solve many-origins/nearest-many-destinations as efficiently as the precomputation used here.

For snapped origin node v and entrance nodes u_e, our target is `min_e d_G(v,u_e)+c_e`, plus origin connector c_p. Reverse the directed graph: `d_G(v,u)=d_Grev(u,v)`. Add a super-source s with an edge of length c_e to each u_e, then run one Dijkstra from s. Every possible source-to-v path corresponds to one entrance and its connector plus a valid original-direction origin-to-entrance path. Taking the shortest of those paths therefore includes every candidate and cannot exclude the optimum. If several entrances snap to one node, keep the smallest connector. Complexity with a heap is approximately O((V+E) log V); tree-based spatial snapping is separate. The current implementation retains paths, increasing memory beyond distance-only storage; metropolitan scaling may need source-label propagation rather than full stored paths.

**Professor:** Why not take the Euclidean nearest station and route to it?

**Answer:** It can be across a wall or disconnected road system. A farther station in a straight line may require a shorter walk. Our test graph has a 10 m straight-line destination requiring 201 m of network travel, while a different 20 m destination needs only 20 m. All eligible destinations participate in the minimum.

**Professor:** Does the globally optimal answer equal a physically correct walk?

**Answer:** Only for the declared graph and snapped-node model. The shortest-path algorithm can be correct while the input graph, entrance eligibility, access restrictions or connector is wrong. Straight connectors can cross barriers; nearest-node snapping can miss the best physical attachment. Real-world validation is a separate scientific gate.

## Coordinate reference systems and units

Longitude and latitude in EPSG:4326 are angles, not metres. A degree of longitude has different physical length at different latitudes. Tehran lies in UTM zone 39N; EPSG:32639 expresses planar x/y in metres. Use `always_xy=True` so source coordinates are longitude first, latitude second. Projection permits distance, radius and spatial indexing in consistent units, with small but nonzero distortion. We use projected segment sums, so triangle checks compare the same planar metric. Elevation and effort are not included.

**Professor:** Why not use Web Mercator for distances because the map uses it?

**Answer:** Web Mercator is a display projection with latitude-dependent scale distortion. Map rendering and scientific measurement can use different CRSs. Scientific distances come from the metric research CRS, and interchange/map features are converted to WGS84.

## Accessibility definitions

Straight-line nearest access E is `min_e ||p−e||`. Modeled walking access D is `c_p + min_e[d_G(v_p,v_e)+c_e]`. If all edge lengths and connectors are consistent Euclidean lengths or longer, D≥E. The destinations achieving the two minima can differ, so D/E compares nearest access under two metrics, rather than a detour to a fixed entrance. E=0 makes the ratio undefined. D/80 gives assumed minutes at 80 m/min (4.8 km/h), not a timetable, elevator wait, walking difficulty or live travel time. No route remains missing, never substituted with E.

**Professor:** Is someone 450 metres away definitely in the near group?

**Answer:** No. Their approximate source center may be uncertain by hundreds of metres, the radius may be unknown, the entrance may be misassociated, or the walking path may be longer. Band labels require both a declared distance definition and uncertainty reporting.

## Spatial uncertainty

The dataset does not tell us a probability density for the true location. Under a *scenario* that the true position lies in a radius-r disk, the nearest-Euclidean-distance function is 1-Lipschitz, giving `[max(0,E−r), E+r]`. The triangle inequality proves this bound relative to the same destination set. This does not transfer automatically to graph routing, whose access point and component can change discontinuously.

To explore a uniform-area disk scenario, draw angle θ~Uniform(0,2π) and radial distance R=r√U, with U~Uniform(0,1). Using R uniform on [0,r] would overrepresent the center. Recompute the nearest reachable entrance for every draw. Report failed draws and band-change fractions separately. Simulation quantiles reflect assumptions, not empirical confidence intervals for the unknown exact property location. Missing radius is not zero. A source value of zero is not independent proof of address precision.

**Professor:** Can you report a low instability rate as certainty?

**Answer:** Only conditional on the scenario, graph and entrance set. Other error distributions or unmapped barriers may change it. The current release executes a synthetic scenario; empirical robustness is not established.

## Price measurement and study population

We audited the entire official revision, not a few viewer rows. Exact predicates select Tehran residential-sale apartments; `property_type` is not assumed to encode that population reliably. The source contains one million rows, 60 columns and 84,586 category-selected Tehran advertisements. For December 2024, fixed positive prices and 20–500 m² give 11,767 candidate records. Only 3,110 also have in-region coordinates and known usable radius. This is a candidate count, not routed n.

**Professor:** Why have you not divided `price_value` by size?

**Answer:** The historical export's total-price semantics are not explicitly established. A plausible magnitude is not proof. Currency denomination is a separate issue: if total price were established but currency unknown, source-unit per-m² might be defensible; at present neither unsupported transformation nor toman/rial claim is published.

**Professor:** Do the advertisements represent the Tehran housing market?

**Answer:** They represent sampled advertised properties, with platform, posting, missingness and agency selection. They are not transactions or a census of dwellings. The same unit can be listed repeatedly, and similar records can be different units. Default duplicate flags are not proof of property identity.

## Statistical controls and interpretation

Our planned model is `log(P_i/A_i)=α+βd_i(km)+γX_i+δ_neighborhood+τ_month+ε_i`. M1 omits controls, M2 adjusts property characteristics, and M3 adds neighborhood/month effects when supported. Use the same complete-case sample to make coefficient changes interpretable as adjustment rather than a different observed population. A single selected month provides no period contrast; a month fixed effect adds no separate information there.

For one additional kilometre, `100(exp(β)−1)%` is the model-implied multiplicative difference in the conditional geometric scale of price/m². It is not necessarily a change in the arithmetic mean or median after retransformation, and not a causal effect. A 95% interval is transformed by exponentiating both endpoints. Do not say there is “no effect” solely because an interval crosses zero. Wide intervals can indicate inadequate information.

**Professor:** Why do neighborhood fixed effects weaken the association?

**Answer:** M1 can reflect between-neighborhood location differences, such as north–south wealth patterns. Fixed effects use within-neighborhood variation. If accessibility barely varies within a neighborhood, β can be weakly identified or unidentifiable. The correct response is to report the lack of variation, not remove controls to recover significance.

**Professor:** Does clustered inference solve spatial bias?

**Answer:** No. Clustered covariance adjusts uncertainty under within-cluster dependence and sufficiently independent clusters. It does not correct omitted variables or measurement error, and cross-neighborhood spatial correlation can remain. Rank, conditioning, influence, heteroskedasticity and residual spatial structure need checks. A spatial block procedure is still planned for stronger empirical inference.

**Professor:** Could you use difference-in-differences to claim causality?

**Answer:** Not merely by adding a before/after indicator. It needs credible treatment timing, comparison groups, parallel-trend assumptions, no problematic anticipation/spillovers and appropriate inference. Existing Tehran opening-based studies use a different design and data; their identification does not transfer to our cross-sectional export.

## Temporal consistency and limits

The primary listings are December 2024. The downloaded map snapshot is October 2026. Unverified station opening dates cannot establish accessibility at listing time. A study using later infrastructure must say “historical listings compared with a later reference network” and avoid implying that sellers experienced that access. Street-network changes also matter, even when a station predates the listings.

**Professor:** What have you demonstrated empirically so far?

**Answer:** Complete-source schema/date/category/quality counts, explicit sample construction, and bounded actual OSM graph checks. The software can run cleaning, routing, three models, sensitivities and export on generated data. No empirical metro premium, affordability ranking or historical routing coverage has yet passed its gate.

**Professor:** What would convince you the result is publishable?

**Answer:** Verified price semantics, an independently checked and temporally defensible destination network, adequate route coverage with failures reported, stable sample/specification results, honest spatial uncertainty, appropriate inference and aggregate-only public output. A reproducible null or indeterminate result is publishable; a polished but unsupported positive headline is not.
