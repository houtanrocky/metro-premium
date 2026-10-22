# Housing-price interpretation: owner confirmation

Documented 23 October 2026 (Asia/Tehran), after the owner inspected actual official-source price/area records.

The owner stated:

> okay the prices are in toman, and the price is for the whole apartment, not per meter

We adopt this as domain confirmation for Tehran fixed-price residential apartment-sale rows in pinned revision `e9446ee97b8e6eb9bd62bdfd7548f1bc8973be85`. The effective interpretation is **total apartment asking price in toman**, and:

`asking_price_per_m2_toman = price_value / building_size_m2`.

There is no factor-of-ten conversion. Original prices and areas remain unchanged. Missing/nonpositive/nonfinite prices and out-of-scope areas still follow the cleaning rules. Confirmation of the field's meaning does not certify every individual value; conspicuous source-price errors remain in the primary descriptive sample, with prespecified tail and duplicate sensitivities reported separately.

The evidence is **owner confirmation**, not a statement from Divar or a newly discovered publisher document. `configs/price-contract.yaml` records the exact statement, date, selected population, source revision, denomination, meaning and evidence type. Its hash enters run provenance. The loader rejects mismatched dataset revisions/populations and prevents owner evidence from being silently relabeled as publisher verification.

The original full-source audit retains its historical finding that the dataset card did not establish price denomination or total-versus-unit meaning. That describes the publisher-documentation evidence at audit time. It is distinct from the effective analysis contract now supplied by the owner. Earlier private review exports and run records remain preserved.

This change enables real descriptive asking-price-per-m² summaries, sensitivity to price tails/duplicate candidates, and sufficiently populated neighborhood price distributions for a common month. It does not establish transacted prices, market representativeness, verified historical metro access, a metro-price association or causality. Geographic validation gates remain unchanged.
