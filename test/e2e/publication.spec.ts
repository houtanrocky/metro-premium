import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('Persian publication, actual data, real street layer and synthetic path',async({page})=>{
  const errors:string[]=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('lang','fa');
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');
  await expect(page.getByRole('heading',{level:1})).toContainText('خونه نزدیک مترو');
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'})).toHaveAttribute('data-rendered-streets','true');
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'})).toBeVisible();
  await expect(page.locator('.map-error')).toHaveCount(0);
  await expect(page.locator('.scope-strip').getByText('۸۴٬۵۸۶',{exact:true})).toBeVisible();
  await page.getByRole('combobox',{name:/^نمایش/}).selectOption('radius');
  await expect(page.locator('.bars').getByText('شعاع نامشخص',{exact:true})).toBeVisible();
  const neighborhood=page.getByLabel('انتخاب محله');
  const value=await neighborhood.locator('option').nth(1).getAttribute('value');
  await neighborhood.selectOption(value!);
  await expect(page.getByText('تأیید نشده',{exact:true})).toBeVisible();
  await page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true}).uncheck();
  await expect(page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true})).not.toBeChecked();
  await page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true}).check();
  await expect(page.getByRole('checkbox',{name:/ایستگاه‌ها و خطوط مترو/})).toBeDisabled();
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'}).locator('canvas')).toBeVisible();
  await page.getByRole('button',{name:'بستن مسیر میانی'}).click();
  await expect(page.getByRole('button',{name:'باز کردن مسیر میانی'})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('img',{name:/مسیر پیاده ۴۹۰/})).toBeVisible();
  await page.getByText('دیدن خروجی مسیر کامل آزمون با داده کاملاً ساختگی',{exact:true}).click();
  await expect(page.getByText('۱٬۲۰۰',{exact:false})).toBeVisible();
  await expect(page.getByText(/داده ساختگی — این اعداد/)).toBeVisible();
  const source=await page.request.get('/data/source-audit.json');
  expect(source.ok()).toBeTruthy();
  expect((await source.json()).total_observed_rows).toBe(1000000);
  for(const href of ['/research/methodology.md','/research/limitations.md','/data/network-validation.json','/data/source-months.png'])expect((await page.request.get(href)).ok()).toBeTruthy();
  const externalTiles=await page.evaluate(()=>performance.getEntriesByType('resource').map(x=>x.name).filter(n=>n.includes('tile.openstreetmap.org')));
  expect(externalTiles).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  expect(errors).toEqual([]);
});

test('keyboard navigation, mobile menu and accessibility',async({page},testInfo)=>{
  await page.goto('/');
  await expect(page.getByRole('heading',{level:1})).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link',{name:'رفتن به محتوای اصلی'})).toBeFocused();
  if(testInfo.project.name==='mobile'){
    await page.getByRole('button',{name:'فهرست بخش‌ها'}).click();
    await expect(page.getByRole('navigation')).toBeVisible();
    await page.getByRole('navigation').getByRole('link',{name:'روش پژوهش'}).click();
    await expect(page.getByRole('button',{name:'فهرست بخش‌ها'})).toHaveAttribute('aria-expanded','false');
  }
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  expect(results.violations).toEqual([]);
});

test('bad public data fails closed with retry',async({page})=>{
  await page.route('**/data/research.json',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({kind:'synthetic_demo'})}));
  await page.goto('/');
  await expect(page.getByRole('alert')).toBeVisible();
  await expect(page.getByRole('button',{name:'تلاش دوباره'})).toBeVisible();
  await expect(page.locator('canvas')).toHaveCount(0);
});
