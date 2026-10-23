import {chromium,expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {mkdirSync} from 'node:fs';
const origin=process.env.PAGES_URL||'http://127.0.0.1:4175'+(process.env.VITE_BASE_PATH||'/');
const server=process.env.PAGES_URL?null:spawn(process.execPath,['node_modules/vite/bin/vite.js','preview','--config','apps/web/vite.config.ts','--outDir','apps/web/dist','--host','127.0.0.1','--port','4175','--strictPort'],{windowsHide:true,stdio:['ignore','pipe','pipe']});
let output='';server?.stdout.on('data',b=>output+=b);server?.stderr.on('data',b=>output+=b);
let browser;
try{
  let ready=false;
  for(let i=0;i<100;i++){
    if(server&&server.exitCode!==null)throw Error(output);
    try{if((await fetch(origin)).ok){ready=true;break;}}catch{}
    await new Promise(resolve=>setTimeout(resolve,200));
  }
  if(!ready)throw Error('Pages preview unavailable: '+output);
  browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL||undefined,headless:true});
  mkdirSync('artifacts/screenshots',{recursive:true});
  for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]])for(const lang of ['en','fa']){
    const page=await browser.newPage({viewport:{width,height}});const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    await page.goto(`${origin}?lang=${lang}`);
    await expect(page.locator('html')).toHaveAttribute('lang',lang);
    await expect(page.locator('html')).toHaveAttribute('dir',lang==='fa'?'rtl':'ltr');
    await expect(page.locator('[data-rendered-streets=true]')).toBeVisible({timeout:30000});
    await expect(page.locator('#mapped-research')).toBeVisible();
    await page.locator('#mapped-research details').nth(1).locator('summary').click();
    await page.evaluate(()=>document.fonts.ready);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    expect(await page.locator('.confidence-interval').evaluateAll(nodes=>nodes.every(n=>getComputedStyle(n).direction==='ltr'))).toBe(true);
    const data=await(await page.request.get(new URL('data/research.json',origin).href)).json();
    expect(data.findings_available).toBe(false);expect(data.mapped_reference.primary_quality_gate_passed).toBe(false);
    const paths=await page.locator('a[href]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')).filter(h=>h&&!h.startsWith('#')&&!/^https?:/.test(h)));
    for(const path of [...new Set(paths)]){
      expect(path.startsWith(new URL(origin).pathname),path).toBe(true);
      const response=await page.request.get(new URL(path,origin).href);expect(response.ok(),path).toBe(true);
    }
    expect(errors).toEqual([]);
    await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:`artifacts/screenshots/pages-${name}-${lang}.png`});
    console.log(`${name} ${lang}: rendered streets, gated results, asset paths and layout passed`);
    await page.close();
  }
}finally{await browser?.close();server?.kill();}
