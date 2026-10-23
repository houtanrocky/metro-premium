import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('Persian publication, actual data, real street layer and synthetic path',async({page})=>{
  const errors:string[]=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('lang','fa');
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');
  await expect(page.getByRole('heading',{level:1})).toContainText('خانه نزدیک مترو');
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'})).toHaveAttribute('data-rendered-streets','true');
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'})).toBeVisible();
  await expect(page.locator('.map-error')).toHaveCount(0);
  await expect(page.locator('.scope-strip').getByText('۸۴٬۵۸۶',{exact:true})).toBeVisible();
  await page.getByRole('combobox',{name:/^نمایش/}).selectOption('radius');
  await expect(page.locator('.bars').getByText('شعاع نامشخص',{exact:true})).toBeVisible();
  const neighborhood=page.getByLabel('انتخاب محله');
  const value=await neighborhood.locator('option').nth(1).getAttribute('value');
  await neighborhood.selectOption(value!);
  await expect(page.getByTestId('neighborhood-price')).toContainText('میلیون تومان');
  await expect(page.getByTestId('overall-price')).toContainText('میلیون تومان');
  await expect(page.getByText('سنجه معتبر برای شبکه فعال موجود نیست',{exact:true})).toBeVisible();
  await page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true}).uncheck();
  await expect(page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true})).not.toBeChecked();
  await page.getByRole('checkbox',{name:'معابر محدوده آزمایشی',exact:true}).check();
  await expect(page.getByRole('checkbox',{name:/ایستگاه‌ها و خطوط مترو/})).toBeDisabled();
  await expect(page.getByRole('region',{name:'نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران'}).locator('canvas')).toBeVisible();
  await page.getByRole('button',{name:'بستن مسیر میانی'}).click();
  await expect(page.getByRole('button',{name:'باز کردن مسیر میانی'})).toHaveAttribute('aria-pressed','true');
  await expect(page.getByRole('img',{name:/مسیر پیاده ۴۹۰/})).toBeVisible();
  await page.getByText('دیدن خروجی کامل آزمایش با داده‌های کاملاً ساختگی',{exact:true}).click();
  await expect(page.getByText('۱٬۲۰۰',{exact:false})).toBeVisible();
  await expect(page.getByText(/داده ساختگی — این اعداد/)).toBeVisible();
  const source=await page.request.get('/data/source-audit.json');
  expect(source.ok()).toBeTruthy();
  expect((await source.json()).total_observed_rows).toBe(1000000);
  for(const href of ['/research/methodology.md','/research/limitations.md','/data/network-validation.json','/data/source-months.png','/data/housing-price-summary.png','/data/housing-descriptives.json'])expect((await page.request.get(href)).ok()).toBeTruthy();
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

test('exploratory mapped results show uncertainty while operational layers remain disabled',async({page})=>{
  await page.goto('/');
  const section=page.locator('#mapped-research');
  await expect(section).toBeVisible();
  await expect(section.getByText('نتیجه اصلی هنوز تأیید نشده است.',{exact:true})).toBeVisible();
  const response=await page.request.get('/data/research.json');
  const data=await response.json();
  const mapped=data.mapped_reference;
  expect(data.findings_available).toBe(false);
  expect(mapped.primary_quality_gate_passed).toBe(false);
  expect(mapped.public_routes_enabled).toBe(false);
  expect(mapped.public_stations_enabled).toBe(false);
  expect(mapped.bands.every((band:{n:number})=>band.n>=30)).toBe(true);
  await section.getByRole('combobox').selectOption('price');
  const modelDetails=section.locator('details').nth(1);
  await modelDetails.locator('summary').click();
  await expect(modelDetails.getByRole('row')).toHaveCount(mapped.models.models.length+1);
  expect(await modelDetails.locator('td bdi').evaluateAll(nodes=>nodes.every(node=>getComputedStyle(node).direction==='ltr'))).toBe(true);
  await expect(page.getByRole('checkbox',{name:/ایستگاه‌ها و خطوط مترو/})).toBeDisabled();
  for(const href of ['/data/mapped-analysis.json','/data/mapped-accessibility.png','/research/mapped-reference-findings.md','/data/historical-network-audit.json','/research/historical-network-validation.md']){
    expect((await page.request.get(href)).ok()).toBeTruthy();
  }
  const audit=await(await page.request.get('/data/historical-network-audit.json')).json();
  expect(audit.primary_operational_gate_passed).toBe(false);
  expect(audit.public_routes_enabled).toBe(false);
  expect(audit.historical_station_evidence.specific_entrances_with_operation_evidence).toBe(0);
  expect(audit.station_order_checks).toHaveLength(audit.route_geometry_summary.cached_routes);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

test('English publication, translated controls, persistence and accessibility',async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','en');await expect(page.locator('html')).toHaveAttribute('dir','ltr');
  await expect(page.getByRole('heading',{level:1})).toContainText('Does it cost more?');
  await expect(page.locator('.scope-strip')).toContainText('11,767');
  await expect(page.getByRole('region',{name:'Geographic map of the central Tehran street validation area'})).toHaveAttribute('data-rendered-streets','true');
  await expect(page.getByRole('button',{name:'Zoom in',exact:true})).toBeVisible();
  await expect(page.getByRole('checkbox',{name:/Metro stations and routes/})).toBeDisabled();
  await page.getByLabel('Display',{exact:false}).selectOption('radius');
  await expect(page.locator('.bars').getByText('Unknown radius',{exact:true})).toBeVisible();
  const select=page.getByRole('combobox',{name:/^Choose a neighborhood/});const value=await select.locator('option').nth(1).getAttribute('value');await select.selectOption(value!);
  await expect(page.getByTestId('neighborhood-price')).toContainText('million toman');
  await page.getByRole('button',{name:'Close the middle path'}).click();
  await expect(page.getByRole('img',{name:/walking route 490 meters/})).toBeVisible();
  await page.locator('#mapped-research details').nth(1).locator('summary').click();
  const english=await page.locator('body').innerText();expect(english.replaceAll('فارسی','')).not.toMatch(/[\u0600-\u06ff]/);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(results.violations).toEqual([]);
  await page.getByRole('button',{name:'فارسی',exact:true}).click();
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');
  await expect(page.getByLabel('انتخاب محله')).toHaveValue(value!);
  await expect(page.getByRole('button',{name:'باز کردن مسیر میانی'})).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'English',exact:true}).click();
  await page.goto('/');await expect(page.locator('html')).toHaveAttribute('lang','en');
  await page.goto('/?lang=fa');await expect(page.locator('html')).toHaveAttribute('lang','fa');expect(errors).toEqual([]);
});

test('failed data remains usable and translated in English',async({page})=>{
  await page.route('**/data/research.json',route=>route.fulfill({status:200,contentType:'application/json',body:'{"kind":"synthetic_demo"}'}));
  await page.goto('/?lang=en');await expect(page.getByRole('alert')).toHaveText('The research data structure is invalid.');
  await expect(page.getByRole('button',{name:'Try again'})).toBeVisible();await expect(page.locator('canvas')).toHaveCount(0);
  await page.getByRole('button',{name:'فارسی',exact:true}).click();await expect(page.getByRole('alert')).toHaveText('ساختار داده پژوهش معتبر نیست.');
});
