import {copyFileSync,existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
const dest='apps/web/public';
mkdirSync(`${dest}/data`,{recursive:true});
const data=JSON.parse(readFileSync('data/public/research.json','utf8'));
if(data.kind!=='empirical_preview'||data.schema_version!==2) throw Error('Default site requires versioned empirical data');
copyFileSync('data/public/research.json',`${dest}/data/research.json`);
mkdirSync(`${dest}/research`,{recursive:true});
for(const name of ['methodology','limitations','findings','statistical-analysis-plan','literature-review','mapped-reference-plan']){
  copyFileSync(`research/${name}.md`,`${dest}/research/${name}.md`);
}
copyFileSync('artifacts/audits/source-audit.json',`${dest}/data/source-audit.json`);
copyFileSync('artifacts/reports/network-validation.json',`${dest}/data/network-validation.json`);
copyFileSync('artifacts/figures/source-months.png',`${dest}/data/source-months.png`);
copyFileSync('artifacts/figures/housing-price-summary.png',`${dest}/data/housing-price-summary.png`);
copyFileSync('artifacts/reports/housing-descriptives.json',`${dest}/data/housing-descriptives.json`);
copyFileSync('data/public/walking-preview.geojson',`${dest}/data/walking-preview.geojson`);
copyFileSync('data/public/synthetic-demo.json',`${dest}/data/synthetic-demo.json`);
if(data.mapped_reference){
  copyFileSync('artifacts/reports/mapped-analysis.json',`${dest}/data/mapped-analysis.json`);
  copyFileSync('artifacts/figures/mapped-accessibility.png',`${dest}/data/mapped-accessibility.png`);
}
mkdirSync(`${dest}/licenses`,{recursive:true});
copyFileSync('node_modules/@fontsource/vazirmatn/LICENSE',`${dest}/licenses/vazirmatn.txt`);
copyFileSync('DATA-LICENSE.md',`${dest}/data/notices.md`);
