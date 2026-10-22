export interface Neighborhood {
  neighborhood: string; month: string; n: number; price_n:number;
  median_per_m2: number|null; q25_per_m2:number|null; q75_per_m2:number|null;
  routed_n:number; median_network_m:number|null; coordinate_coverage:number;
  known_radius_coverage:number; comparison_eligible:boolean;
}
export interface ResearchData {
  schema_version:2; kind:'empirical_preview'; run_id:string; generated_utc:string;
  source:{repository:string;revision:string;url:string;license:string};
  scope:{source_rows:number;source_columns:number;tehran_apartment_sale_rows:number;analysis_rows:number;period:string;coordinate_valid_rows:number;routable_candidate_rows:number};
  gates:{id:number;status:string;label:string;reason:string}[];
  price_contract:{denomination:'toman';price_basis:'total_apartment_asking_price';total_price_verified:true;per_m2_enabled:true;verification_source:'owner_confirmation';publisher_documentation_verified:false;revision:string;evidence:string;documented_date:string};
  housing_descriptives_available:true;
  housing_prices:{status:'computed';unit:'toman_per_m2';period:string;n:number;median_per_m2:number;q25_per_m2:number;q75_per_m2:number;median_total_asking_price_toman:number;area_median_m2:number;tail_rule:{flagged_n:number;default_excludes_tails:false};variants:{name:string;n:number;status:string;median_per_m2:number|null;q25_per_m2:number|null;q75_per_m2:number|null}[]};
  months:{month:string;n:number}[];radii:{radius:string|null;n:number}[];
  sample_flow:{stage:string;before:number;after:number;excluded:number}[];
  neighborhoods:Neighborhood[];bands:unknown[];models:unknown[];
  network:{public_routes_enabled:boolean;public_stations_enabled:boolean;walking_nodes:number;walking_edges:number;reference_date:string|null;status:string};
  findings_available:boolean;limitations:string[];attribution:string[];
  mapped_reference?:MappedReference;
}

export interface MappedModel {name:string;status:string;n?:number;clusters?:number;distance_coefficient_per_km?:number;confidence_interval_95?:number[];association_percent_per_km?:number;association_percent_ci_95?:number[];exploratory_knn_moran_i?:number}
export interface MappedReference {
  schema_version:1;status:'exploratory_mapped_reference';warning:string;snapshot:string;period:string;unit:'toman_per_m2';
  primary_quality_gate_passed:false;public_routes_enabled:false;public_stations_enabled:false;
  scope:{price_valid_rows:number;coordinate_known_radius_candidates:number;supported_route_rows:number;mapped_entrances:number;retained_entrances_before_snapping:number;retained_entrances_after_snapping:number;distinct_stop_areas:number};
  coverage:Record<string,number>;
  walking:{nodes:number;directed_edges:number;weak_components:number;scope:string};
  network_m:{n:number;median?:number;q25?:number;q75?:number};ratio:{n:number;median?:number;q25?:number;q75?:number};
  bands:{month:string;band:number;n:number;median_per_m2:number;q25:number;q75:number}[];
  models:{status:string;diagnostics:{complete_case_n:number;clusters:number};models:MappedModel[]};
  location_uncertainty:{assumption:string;draws_per_origin:number;origins:number;failure_fraction:number;classification_change_fraction_among_successful_nominal_supported:number|null;fraction_nominal_supported_origins_ever_changing_band:number|null};
}
