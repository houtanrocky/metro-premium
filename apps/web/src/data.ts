import type {ResearchData} from '../../../packages/shared-types';
export {number as fa,price as perM2,month as monthLabel} from './i18n';
export class ResearchDataError extends Error {constructor(public key:string){super(key);this.name='ResearchDataError';}}
export function validateResearch(value:unknown):ResearchData {
  const d=value as ResearchData;
  if(!d || d.kind!=='empirical_preview'||d.schema_version!==2||!d.scope||!Array.isArray(d.months)||!Array.isArray(d.neighborhoods)||!Array.isArray(d.gates)) throw new ResearchDataError('error.structure');
  if(!Number.isSafeInteger(d.scope.source_rows)||!d.months.every(m=>Number.isSafeInteger(m.n)&&m.n>=0&&/^\d{4}-\d{2}$/.test(m.month))) throw new ResearchDataError('error.count');
  if(d.findings_available||d.network.public_routes_enabled||d.network.public_stations_enabled||!Array.isArray(d.models)||!Array.isArray(d.bands)||d.models.length||d.bands.length) throw new ResearchDataError('error.gates');
  const c=d.price_contract;
  if(!c||c.denomination!=='toman'||c.price_basis!=='total_apartment_asking_price'||c.verification_source!=='owner_confirmation'||c.publisher_documentation_verified!==false||c.total_price_verified!==true||c.per_m2_enabled!==true||c.revision!==d.source.revision||!c.evidence) throw new ResearchDataError('error.contract');
  const h=d.housing_prices;
  const validPrice=(n:unknown):n is number=>typeof n==='number'&&Number.isFinite(n)&&n>0;
  if(d.housing_descriptives_available!==true||!h||h.status!=='computed'||h.unit!=='toman_per_m2'||h.period!==d.scope.period||h.n!==d.scope.analysis_rows||h.n<30||![h.q25_per_m2,h.median_per_m2,h.q75_per_m2].every(validPrice)||h.q25_per_m2>h.median_per_m2||h.median_per_m2>h.q75_per_m2||!Array.isArray(h.variants)) throw new ResearchDataError('error.housing');
  if(h.variants.some(v=>!Number.isSafeInteger(v.n)||v.n<0||v.n>h.n||(v.status==='computed'&&(v.n<30||![v.q25_per_m2,v.median_per_m2,v.q75_per_m2].every(validPrice)||v.q25_per_m2!>v.median_per_m2!||v.median_per_m2!>v.q75_per_m2!)))) throw new ResearchDataError('error.sensitivity');
  const baseline=h.variants.find(v=>v.name==='all_candidate_records');
  if(!baseline||baseline.n!==h.n||baseline.median_per_m2!==h.median_per_m2) throw new ResearchDataError('error.baseline');
  const invalidNeighborhood=d.neighborhoods.some(n=>{
    if(!Number.isSafeInteger(n.n)||n.n<30||!Number.isSafeInteger(n.price_n)||n.price_n<0||n.price_n>n.n||n.month!==d.scope.period||n.median_network_m!==null||n.comparison_eligible)return true;
    if(n.median_per_m2===null)return n.price_n!==0||n.q25_per_m2!==null||n.q75_per_m2!==null;
    const q1=n.q25_per_m2, q3=n.q75_per_m2;
    return n.price_n<30||!validPrice(q1)||!validPrice(n.median_per_m2)||!validPrice(q3)||q1>n.median_per_m2||n.median_per_m2>q3;
  });
  if(invalidNeighborhood) throw new ResearchDataError('error.privacy');
  const m=d.mapped_reference;
  if(m){
    const integer=(v:unknown)=>Number.isSafeInteger(v)&&Number(v)>=0;
    const probability=(v:unknown)=>typeof v==='number'&&Number.isFinite(v)&&v>=0&&v<=1;
    if(m.schema_version!==1||m.status!=='exploratory_mapped_reference'||m.primary_quality_gate_passed!==false||m.public_routes_enabled!==false||m.public_stations_enabled!==false||m.period!==d.scope.period||m.unit!=='toman_per_m2'||m.snapshot!=='2024-12-01T00:00:00Z'||typeof m.warning!=='string'||m.warning.length<60||!m.scope||m.scope.price_valid_rows!==d.scope.analysis_rows||!Object.values(m.scope).every(integer)||m.scope.supported_route_rows>m.scope.coordinate_known_radius_candidates||m.scope.coordinate_known_radius_candidates>d.scope.analysis_rows||m.scope.retained_entrances_after_snapping>m.scope.retained_entrances_before_snapping||!m.coverage||!Object.values(m.coverage).every(integer)||Object.values(m.coverage).reduce((a,b)=>a+b,0)!==d.scope.analysis_rows||m.coverage.ok!==m.scope.supported_route_rows)throw new ResearchDataError('error.mappedScope');
    if(!m.network_m||m.network_m.n!==m.scope.supported_route_rows||!validPrice(m.network_m.median)||!m.ratio||m.ratio.n!==m.network_m.n||!validPrice(m.ratio.median)||!Array.isArray(m.bands)||new Set(m.bands.map(b=>b.band)).size!==m.bands.length||m.bands.some(b=>!integer(b.band)||b.band>3||!integer(b.n)||b.n<30||b.month!==m.period||![b.q25,b.median_per_m2,b.q75].every(validPrice)||b.q25>b.median_per_m2||b.median_per_m2>b.q75)||m.bands.reduce((a,b)=>a+b.n,0)>m.scope.supported_route_rows)throw new ResearchDataError('error.mappedSummary');
    const u=m.location_uncertainty;
    if(!u||!integer(u.draws_per_origin)||u.draws_per_origin<1||!probability(u.failure_fraction)||!(u.classification_change_fraction_among_successful_nominal_supported===null||probability(u.classification_change_fraction_among_successful_nominal_supported)))throw new ResearchDataError('error.uncertainty');
    if(!m.models?.diagnostics||!Array.isArray(m.models.models)||m.models.models.some(model=>model.status==='estimated'&&(!integer(model.n)||model.n!<100||!integer(model.clusters)||model.clusters!<30||!Number.isFinite(model.association_percent_per_km)||!Array.isArray(model.association_percent_ci_95)||model.association_percent_ci_95.length!==2||!model.association_percent_ci_95.every(Number.isFinite)||model.association_percent_ci_95[0]>model.association_percent_ci_95[1])))throw new ResearchDataError('error.models');
  }
  return d;
}
