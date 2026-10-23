import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const python=path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python');
const [command='help',...args]=process.argv.slice(2);
function run(cmd,argv,extra={}){
  const result=spawnSync(cmd,argv,{cwd:root,stdio:'inherit',...extra});
  if(result.error)throw result.error;
  if(result.status!==0)process.exit(result.status??1);
}
const npm=(argv)=>process.platform==='win32'?run(process.env.ComSpec||'cmd.exe',['/d','/s','/c','npm',...argv]):run('npm',argv);
switch(command){
  case 'setup':
    run('uv',['sync','--project','pipeline','--extra','test','--frozen'],{env:{...process.env,UV_PROJECT_ENVIRONMENT:path.join(root,'.venv')}});
    npm(['ci']);
    run('node',['scripts/sync-public.mjs']);
    break;
  case 'acquire': run(python,['scripts/acquire.py',...args]);break;
  case 'acquire-osm': run(python,['scripts/acquire_osm.py',...args]);break;
  case 'acquire-historical': run(python,['scripts/acquire_historical.py',...args]);break;
  case 'validate-historical-network': run(python,['scripts/validate_historical_network.py',...args]);break;
  case 'metro-reference': run(python,['scripts/metro_reference.py',...args]);break;
  case 'test':
    run(python,['-m','pytest','pipeline/tests','-q']);
    npm(['test']);npm(['run','typecheck']);npm(['run','check:docs']);npm(['run','build']);break;
  case 'dev':npm(['run','dev']);break;
  case 'help':console.log('setup | acquire | acquire-osm | acquire-historical | validate-historical-network | metro-reference | audit-data | prepare-data | build-networks | compute-accessibility | analyze | export-public-data | report | reproduce | smoke | test | dev');break;
  default:run(python,['-m','metropremium.cli',command,...args]);
}
