"""Audit the entire immutable source with DuckDB. Never publish row-level text."""
import json
import duckdb
from .provenance import write_json, digest

SELECTION = "city_slug='tehran' AND cat2_slug='residential-sell' AND cat3_slug='apartment-sell'"

def audit_source(source, output):
    metadata=json.loads(source.with_suffix('.csv.source.json').read_text(encoding='utf-8'))
    if metadata.get('sha256') and digest(source)!=metadata['sha256']:
        raise ValueError('Source CSV checksum differs from acquisition provenance')
    con = duckdb.connect(str(output / 'audit-work.duckdb'))
    con.execute("SET threads=4")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET enable_progress_bar=false")
    con.execute("CREATE TABLE raw AS SELECT * FROM read_csv(?, header=true, all_varchar=true, sample_size=-1, strict_mode=true)", [str(source)])
    def rows(sql):
        cur = con.execute(sql)
        names = [d[0] for d in cur.description]
        return [dict(zip(names, r)) for r in cur.fetchall()]
    schema = rows("DESCRIBE raw")
    total = con.execute("SELECT count(*) FROM raw").fetchone()[0]
    fields = [x["column_name"] for x in schema]
    missing = rows("SELECT " + ",".join(f'count(*) FILTER (WHERE "{f}" IS NULL) AS "{f}"' for f in fields) + " FROM raw")[0]
    con.execute(f"CREATE VIEW sale AS SELECT * FROM raw WHERE {SELECTION}")
    n_sale = con.execute("SELECT count(*) FROM sale").fetchone()[0]
    numeric = {f: f'try_cast("{f}" AS DOUBLE)' for f in ['price_value', 'building_size', 'location_latitude', 'location_longitude', 'location_radius']}
    numeric_stats = {}
    for field, expr in numeric.items():
        numeric_stats[field] = rows(f"SELECT count(*) FILTER (WHERE {field} IS NULL) AS missing, count(*) FILTER (WHERE {field} IS NOT NULL AND {expr} IS NULL) AS parse_failure, count(*) FILTER (WHERE {expr}<=0 OR NOT isfinite({expr})) AS nonpositive_or_nonfinite, min({expr}) AS min, quantile_cont({expr}, [0.01,0.25,0.5,0.75,0.99]) AS quantiles, max({expr}) AS max FROM sale")[0]
    coordinates = rows("SELECT count(*) FILTER (WHERE location_latitude IS NOT NULL AND location_longitude IS NOT NULL) AS both_present, count(*) FILTER (WHERE try_cast(location_latitude AS DOUBLE) BETWEEN -90 AND 90 AND try_cast(location_longitude AS DOUBLE) BETWEEN -180 AND 180) AS valid_world, count(*) FILTER (WHERE try_cast(location_latitude AS DOUBLE) BETWEEN 35.45 AND 35.9 AND try_cast(location_longitude AS DOUBLE) BETWEEN 51.05 AND 51.65) AS in_study_bbox FROM sale")[0]
    # Exact whole-row duplicates, including original text, are counted locally only.
    dups = rows("SELECT count(*) AS groups, coalesce(sum(n-1),0)::BIGINT AS excess_rows FROM (SELECT count(*) n FROM sale GROUP BY " + ",".join('"'+f+'"' for f in fields) + " HAVING count(*)>1)")[0]
    key = ['neighborhood_slug','created_at_month','price_value','building_size','rooms_count','construction_year','floor','has_parking','has_elevator','has_warehouse','location_latitude','location_longitude']
    near = rows("SELECT count(*) AS groups, coalesce(sum(n-1),0)::BIGINT AS excess_rows FROM (SELECT count(*) n FROM sale GROUP BY " + ",".join(key) + " HAVING count(*)>1)")[0]
    category = {f: rows(f'SELECT "{f}" AS value, count(*) AS n FROM raw GROUP BY 1 ORDER BY n DESC') for f in ['cat2_slug','cat3_slug','price_mode','property_type']}
    report = {"status": "full_source_audit", "total_observed_rows": total, "column_count": len(fields), "source_storage_types": schema, "missing_all": missing, "months": rows("SELECT created_at_month AS month,count(*) AS n FROM raw GROUP BY 1 ORDER BY 1"), "cities": rows("SELECT city_slug AS city,count(*) AS n FROM raw GROUP BY 1 ORDER BY n DESC"), "category_values": category, "selection_sql": SELECTION, "tehran_apartment_sale_rows": n_sale, "selected_months": rows("SELECT substr(created_at_month,1,7) AS month,count(*) AS n FROM sale GROUP BY 1 ORDER BY 1"), "missing_selected": rows("SELECT " + ",".join(f'count(*) FILTER (WHERE "{f}" IS NULL) AS "{f}"' for f in fields) + " FROM sale")[0], "numeric_selected": numeric_stats, "coordinates_selected": coordinates, "radius_selected": rows("SELECT location_radius AS radius,count(*) AS n FROM sale GROUP BY 1 ORDER BY n DESC"), "exact_duplicates_selected": dups, "potential_duplicates_selected": {"key": key, **near, "caution": "Shared coarse coordinates and attributes can describe distinct dwellings; not property identifiers."}, "characteristic_values": {f: rows(f'SELECT "{f}" AS value,count(*) AS n FROM sale GROUP BY 1 ORDER BY n DESC') for f in ['price_mode','rooms_count','construction_year','floor','total_floors_count','has_parking','has_elevator','has_warehouse']}, "price_contract": {"denomination": "source units; not established for the dataset", "total_price_verified": False, "evidence": "Pinned dataset card lists financial fields but gives no denomination or explicit total-versus-unit-price contract. Related live API documentation is not a mapping guarantee for this historical export.", "per_m2_enabled": False}, "date_conflict": "Source card claims six months in 2024. Observed month distributions are authoritative for sample construction; inspect counts before fixing the window."}
    # Infer actual parseable logical types independently of CSV storage strings.
    inferred = rows("DESCRIBE SELECT * FROM read_csv('" + str(source).replace("'","''") + "', header=true, sample_size=-1, strict_mode=true)")
    report["inferred_schema"] = inferred
    report['source'] = metadata
    write_json(output / "audit.json", report)
    # Numeric/categorical source fields only: no descriptions, title or seller information.
    keep = ['cat2_slug','cat3_slug','city_slug','neighborhood_slug','created_at_month','price_mode','price_value','building_size','construction_year','rooms_count','floor','total_floors_count','has_parking','has_elevator','has_warehouse','location_latitude','location_longitude','location_radius']
    dest = output / "tehran-source.parquet"
    con.execute("COPY (SELECT " + ','.join(keep) + ", row_number() OVER () AS source_row FROM sale) TO '" + str(dest).replace("'","''") + "' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.close()
    return report, dest
