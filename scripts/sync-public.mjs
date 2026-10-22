import {copyFileSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
const dest='apps/web/public';
mkdirSync(`${dest}/data`,{recursive:true});
const data=JSON.parse(readFileSync('data/public/research.json','utf8'));
if(data.kind!=='empirical_preview'||data.schema_version!==1) throw Error('Default site requires empirical data');
copyFileSync('data/public/research.json',`${dest}/data/research.json`);
mkdirSync(`${dest}/research`,{recursive:true});
for(const name of ['methodology','limitations','findings','statistical-analysis-plan','literature-review']){
  copyFileSync(`research/${name}.md`,`${dest}/research/${name}.md`);
}
copyFileSync('artifacts/audits/source-audit.json',`${dest}/data/source-audit.json`);
copyFileSync('artifacts/reports/network-validation.json',`${dest}/data/network-validation.json`);
copyFileSync('artifacts/figures/source-months.png',`${dest}/data/source-months.png`);
copyFileSync('data/public/walking-preview.geojson',`${dest}/data/walking-preview.geojson`);
copyFileSync('data/public/synthetic-demo.json',`${dest}/data/synthetic-demo.json`);
