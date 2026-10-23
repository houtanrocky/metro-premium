# Engineering and research status

Implemented: complete official-source download/audit; deterministic one-month candidate cleaning; real small-area walking graph; globally optimal nearest-entrance routing engine; location scenario simulation; three guarded observational models and diagnostics; executable synthetic sensitivity suite; privacy-safe aggregation; actual audit figures; Persian RTL publication, real street map, quality explorer, graph lesson, synthetic view; reproducible tasks and CI.

Price interpretation is now owner-confirmed as total apartment asking price in toman, with real price/m² medians/IQR, tail and duplicate-candidate sensitivities, and aggregate neighborhood summaries computed. Publisher verification is not claimed.

Completed exploratory extension: four-tile historical walking acquisition, 166 retained mapped entrances, 2,978 supported routes, three observational models on 2,962 common complete cases, 30 location draws per candidate, 10 location-model refits and 199 spatial-cell wild-bootstrap draws. These are mapped-subset results; M3's clustered interval spans zero and its sign changes in some location draws. See [findings](../research/mapped-reference-findings.md).

Not completed: historical operational station/entrance eligibility, independent metro topology approval, physical walking/connector and entrance-completeness verification, primary operational metro-access model, price map/access ranking, calibrated spatial uncertainty, expanded-area and full period sensitivities. No field route survey was performed.

Follow-up [historical validation audit](../research/historical-network-validation.md): 17 actual track relations screened, with 15 software passes and the same Line 3 endpoint gap in both directions. Four pinned official station-inauguration facts match three retained stop areas; no individual entrance is verified open. Of 166 retained entrances, 123 use nonzero straight connectors, including 39 over the 25 m review-priority threshold. Private review queues are prepared; the existing 166-entrance model scope is unchanged, including the documented Line 5 metadata exclusion.

The website's version-2 schema permits aggregate housing-price descriptions only with the recorded owner-confirmed total-price/toman evidence. It rejects primary operational metro claims and geographic price layers, while a separately scoped `mapped_reference` field permits the exploratory aggregate results with explicit warnings. Price distributions are not regression-adjusted estimates or a metro premium.

No user image was available; no repository URL or university endorsement was assumed. There is no publication/deployment or remote push. See [research limitations](../research/limitations.md), [decisions](../research/decision-log.md), and [outstanding decisions](outstanding-decisions.md).
