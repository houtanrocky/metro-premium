# Data notices

Original application and pipeline code are MIT licensed. Input data and databases are not covered by that grant.

- Divar official Real Estate Ads: [source](https://huggingface.co/datasets/divarofficial/real_estate_ads), revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85`, dataset card declares **ODbL**.
- Street geometry and metro source objects: **© OpenStreetMap contributors**, [copyright and attribution](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
- `data/public/walking-preview.geojson` is an OSM-derived street database under ODbL 1.0. Its construction is available in `pipeline/src/metropremium/geographic.py`; exact input URL, retrieval time and SHA-256 are recorded in `artifacts/reports/network-validation.json`. No metro geometry has been approved for public display.
- `data/public/research.json` contains source-derived aggregate counts and quality summaries. Treat database rights in source-derived structured outputs as ODbL, conservatively; preserve these notices. It contains no individual housing rows.
- `data/public/synthetic-demo.json` is generated, explicitly synthetic test data under the original-code license. It is not Divar data.
- Vazirmatn font files are supplied by `@fontsource/vazirmatn` under the SIL Open Font License; retain the package license when distributing built font assets.

No raw housing CSV or listing-level derived database is distributed here. Review the [publication policy](docs/licensing.md) before releasing larger derived databases or adding a tile provider.
