import {readFileSync,readdirSync,existsSync,statSync} from 'node:fs';
import path from 'node:path';
const roots=['README.md','README.fa.md','DATA-LICENSE.md',...['docs','research'].flatMap(folder=>walk(folder))];
function walk(folder){return readdirSync(folder).flatMap(f=>{const p=path.join(folder,f);return statSync(p).isDirectory()?walk(p):p.endsWith('.md')?[p]:[];});}
const failures=[];
for(const file of roots){
  const body=readFileSync(file,'utf8');
  if(body.length<80)failures.push(`${file}: empty or insubstantial`);
  for(const match of body.matchAll(/\]\(([^)]+)\)/g)){
    const href=match[1].replace(/<|>/g,'').split('#')[0];
    if(!href||/^(https?:|mailto:)/.test(href))continue;
    if(!existsSync(path.resolve(path.dirname(file),href)))failures.push(`${file}: missing ${href}`);
  }
}
for(const file of ['docs/what-i-must-understand.md','research/report.md','research/data-dictionary.md','docs/delivery.md'])if(!existsSync(file))failures.push(`Missing ${file}`);
if(failures.length){console.error(failures.join('\n'));process.exit(1);}
console.log(`Checked ${roots.length} research/documentation files and local Markdown targets.`);
