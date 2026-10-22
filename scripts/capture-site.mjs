import {chromium} from '@playwright/test';
import {mkdirSync} from 'node:fs';
mkdirSync('artifacts/screenshots',{recursive:true});
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL||'chrome'});
try{
  for(const [name,width,height] of [['desktop',1440,1000],['mobile',390,844]]){
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    await page.goto('http://127.0.0.1:5173/');
    await page.getByRole('heading',{level:1}).waitFor();
    await page.evaluate(()=>document.fonts.ready);
    await page.screenshot({path:`artifacts/screenshots/${name}.png`});
    await page.screenshot({path:`artifacts/screenshots/${name}-full.png`,fullPage:true});
    console.log(`${name}: screenshot captured, ${await page.title()}`);
    await page.close();
  }
}finally{await browser.close();}
