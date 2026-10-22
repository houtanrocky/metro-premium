# Observed data dictionary

Generated from the complete pinned official CSV audit. CSV raw storage uses VARCHAR to preserve values; the logical column below is independently inferred, not a semantic guarantee. Missing counts refer to all 1,000,000 source rows.

| Field | Inferred logical type | Missing rows |
|---|---|---:|
| cat2_slug | VARCHAR | 0 |
| cat3_slug | VARCHAR | 1 |
| city_slug | VARCHAR | 2 |
| neighborhood_slug | VARCHAR | 562861 |
| created_at_month | TIMESTAMP | 0 |
| user_type | VARCHAR | 711118 |
| description | VARCHAR | 0 |
| title | VARCHAR | 54 |
| rent_mode | VARCHAR | 647006 |
| rent_value | BIGINT | 648678 |
| rent_to_single | BOOLEAN | 999981 |
| rent_type | VARCHAR | 896039 |
| price_mode | VARCHAR | 426394 |
| price_value | BIGINT | 431654 |
| credit_mode | VARCHAR | 647006 |
| credit_value | BIGINT | 647905 |
| rent_credit_transform | BOOLEAN | 647015 |
| transformable_price | BOOLEAN | 647106 |
| transformable_credit | BIGINT | 647915 |
| transformed_credit | BIGINT | 927591 |
| transformable_rent | BIGINT | 648752 |
| transformed_rent | BIGINT | 927591 |
| land_size | BIGINT | 813604 |
| building_size | BIGINT | 19606 |
| deed_type | VARCHAR | 746542 |
| has_business_deed | BOOLEAN | 965321 |
| floor | VARCHAR | 458252 |
| rooms_count | VARCHAR | 154101 |
| total_floors_count | VARCHAR | 695648 |
| unit_per_floor | VARCHAR | 697717 |
| has_balcony | VARCHAR | 493589 |
| has_elevator | BOOLEAN | 458251 |
| has_warehouse | BOOLEAN | 271845 |
| has_parking | BOOLEAN | 271844 |
| construction_year | VARCHAR | 184172 |
| is_rebuilt | BOOLEAN | 470530 |
| has_water | BOOLEAN | 966556 |
| has_warm_water_provider | VARCHAR | 620500 |
| has_electricity | BOOLEAN | 966555 |
| has_gas | BOOLEAN | 966570 |
| has_heating_system | VARCHAR | 631031 |
| has_cooling_system | VARCHAR | 649381 |
| has_restroom | VARCHAR | 593087 |
| has_security_guard | BOOLEAN | 968688 |
| has_barbecue | BOOLEAN | 968802 |
| building_direction | VARCHAR | 676077 |
| has_pool | BOOLEAN | 970610 |
| has_jacuzzi | BOOLEAN | 971272 |
| has_sauna | BOOLEAN | 971521 |
| floor_material | VARCHAR | 594016 |
| property_type | VARCHAR | 972943 |
| regular_person_capacity | BIGINT | 970130 |
| extra_person_capacity | VARCHAR | 975991 |
| cost_per_extra_person | BIGINT | 989759 |
| rent_price_on_regular_days | BIGINT | 981932 |
| rent_price_on_special_days | BIGINT | 989537 |
| rent_price_at_weekends | BIGINT | 986449 |
| location_latitude | DOUBLE | 344392 |
| location_longitude | DOUBLE | 344392 |
| location_radius | BIGINT | 660301 |

## Analytical interpretation

Population uses city_slug, cat2_slug and cat3_slug. property_type is not a reliable substitute. created_at_month is parsed as a Gregorian calendar month with observed values overriding the inconsistent card period. price_mode must equal مقطوع, but this does not by itself verify the denomination or total-price semantics of price_value. building_size is documented in square metres. price/m² stays missing until a total-price contract is established.

construction_year is Solar Hijri; only literal numeric years in the historical validity range become a year control. Censored text is not converted to a precise age. rooms_count Persian words are recoded using an explicit lookup. Missing floor/room/year information is not zero-filled.

location_latitude/longitude are approximate WGS84 centers; location_radius is a reported uncertainty/accuracy field. Its missing value is distinct from zero. A hard disk and uniform-area simulation are sensitivity assumptions.

description, title and user-related fields do not enter downstream selected/public data. source_row is a private run-local row identifier, not a persistent advertisement or property identity. See methodology.md for flags, duplicate key and exclusion rules.
