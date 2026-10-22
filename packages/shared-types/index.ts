export interface Neighborhood {
  neighborhood: string; month: string; n: number; price_n:number;
  median_per_m2: number|null; q25_per_m2:number|null; q75_per_m2:number|null;
  routed_n:number; median_network_m:number|null; coordinate_coverage:number;
  known_radius_coverage:number; comparison_eligible:boolean;
}
export interface ResearchData {
  schema_version:1; kind:'empirical_preview'; run_id:string; generated_utc:string;
  source:{repository:string;revision:string;url:string;license:string};
  scope:{source_rows:number;source_columns:number;tehran_apartment_sale_rows:number;analysis_rows:number;period:string;coordinate_valid_rows:number;routable_candidate_rows:number};
  gates:{id:number;status:string;label:string;reason:string}[];
  price_contract:{denomination:string;total_price_verified:boolean;per_m2_enabled:boolean};
  months:{month:string;n:number}[];radii:{radius:string|null;n:number}[];
  sample_flow:{stage:string;before:number;after:number;excluded:number}[];
  neighborhoods:Neighborhood[];bands:unknown[];models:unknown[];
  network:{public_routes_enabled:boolean;public_stations_enabled:boolean;walking_nodes:number;walking_edges:number;reference_date:string|null;status:string};
  findings_available:boolean;limitations:string[];attribution:string[];
}
