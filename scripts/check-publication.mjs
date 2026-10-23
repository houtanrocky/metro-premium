import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
const git=(args)=>execFileSync('git',args,{encoding:'utf8'}).trim();
const files=git(['ls-files','--cached']).split('\n').filter(Boolean);
const forbidden=/^(?:data\/(?:raw|intermediate|processed)\/|artifacts\/(?:runs|screenshots)\/|(?:.*\/)?\.env$)|(?:^|\/)(?:id_rsa|id_ed25519|credentials\.json)$|\.part$/i;
const history=git(['log','--all','--name-only','--pretty=format:']).split('\n').filter(Boolean);
for(const file of [...new Set([...files,...history])])if(forbidden.test(file))throw Error(`Private path in publication tree/history: ${file}`);
for(const file of files){
  if(/\.(?:png|woff2?|jpg|ico)$/.test(file))continue;
  const content=readFileSync(file,'utf8');
  if(/(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)/.test(content))throw Error(`Possible credential in ${file}`);
}
const data=JSON.parse(readFileSync('data/public/research.json','utf8'));
if(data.kind!=='empirical_preview'||data.findings_available||data.network.public_routes_enabled||data.network.public_stations_enabled)throw Error('Unapproved primary findings or metro layers');
if(data.neighborhoods.some(n=>n.n<30||(n.median_per_m2!==null&&n.price_n<30)))throw Error('Neighborhood privacy failure');
if(data.mapped_reference?.bands.some(b=>b.n<30))throw Error('Distance-band privacy failure');
function visit(value){
  if(!value||typeof value!=='object')return;
  for(const [key,item] of Object.entries(value)){
    if(/^(?:lat|latitude|lon|lng|longitude|coordinates|listing_id|ad_id|token)$/i.test(key))throw Error(`Individual data field in public housing payload: ${key}`);
    visit(item);
  }
}visit(data);
console.log(`Publication boundary passed: ${files.length} tracked files, historical paths, credentials and aggregate housing export.`);
