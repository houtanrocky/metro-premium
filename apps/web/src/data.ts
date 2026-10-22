import type {ResearchData} from '../../../packages/shared-types';
export const fa = (n:number, digits=0) => new Intl.NumberFormat('fa-IR',{maximumFractionDigits:digits}).format(n);
export function monthLabel(month:string){
  return new Intl.DateTimeFormat('fa-IR-u-ca-gregory',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(month+'-01T00:00:00Z'));
}
export function validateResearch(value:unknown):ResearchData {
  const d=value as ResearchData;
  if(!d || d.kind!=='empirical_preview'||d.schema_version!==1||!d.scope||!Array.isArray(d.months)||!Array.isArray(d.neighborhoods)||!Array.isArray(d.gates)) throw Error('ساختار داده معتبر نیست.');
  if(!Number.isSafeInteger(d.scope.source_rows)||!d.months.every(m=>Number.isSafeInteger(m.n)&&m.n>=0&&/^\d{4}-\d{2}$/.test(m.month))) throw Error('شمارش یا تاریخ نامعتبر است.');
  if(d.findings_available||d.network.public_routes_enabled||d.network.public_stations_enabled||d.models.length||d.bands.length||d.price_contract.total_price_verified) throw Error('این نسخه فقط خروجی ممیزی تأییدشده را نمایش می‌دهد.');
  if(d.neighborhoods.some(n=>n.n<30||n.median_per_m2!==null||n.median_network_m!==null)) throw Error('خروجی از دروازه انتشار عبور نکرده است.');
  return d;
}
