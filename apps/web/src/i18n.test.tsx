import React from 'react';
import {readFileSync,readdirSync} from 'node:fs';
import ts from 'typescript';
import {beforeEach,describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import i18n,{initialLanguage,languageKey,number,percent,price,month} from './i18n';
import App from './App';
import en from './locales/en.json';
import fa from './locales/fa.json';
const payload=JSON.parse(readFileSync('data/public/research.json','utf8'));
vi.mock('./MapView',()=>({default:()=> <div data-testid="map"/>}));
beforeEach(async()=>{localStorage.clear();history.replaceState(null,'','/');await i18n.changeLanguage('fa');});
describe('Bilingual publication',()=>{
  it('keeps all locale keys and interpolation variables in sync',()=>{
    expect(Object.keys(en).sort()).toEqual(Object.keys(fa).sort());
    for(const key of Object.keys(en) as (keyof typeof en)[]){
      expect(en[key].trim(),key).not.toBe('');expect(fa[key].trim(),key).not.toBe('');
      expect(en[key].match(/{{[^}]+}}/g)?.sort(),key).toEqual(fa[key].match(/{{[^}]+}}/g)?.sort());
    }
    for(const g of payload.gates)for(const suffix of ['label','reason'])expect(i18n.exists(`gate.${g.id}.${suffix}`)).toBe(true);
    for(const key of Object.keys(payload.mapped_reference.coverage))expect(i18n.exists(`coverage.${key}`)).toBe(true);
    for(const [i] of payload.limitations.entries())expect(i18n.exists(`limitations.${i}`)).toBe(true);
  });
  it('keeps authored display copy out of component source',()=>{
    for(const file of readdirSync('apps/web/src').filter(f=>f.endsWith('.tsx')&&!f.includes('.test.'))){
      const source=readFileSync(`apps/web/src/${file}`,'utf8');
      const tree=ts.createSourceFile(file,source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX);
      function visit(node:ts.Node){
        if(ts.isJsxText(node)&&/\p{L}/u.test(node.text))expect(['METRO','PREMIUM','METROPREMIUM'],`${file}: ${node.text}`).toContain(node.text.trim());
        if(ts.isJsxAttribute(node)&&['aria-label','title','placeholder','alt'].includes(node.name.getText(tree))&&node.initializer&&ts.isStringLiteral(node.initializer))expect.fail(`${file}: hardcoded ${node.name.getText(tree)}`);
        ts.forEachChild(node,visit);
      }visit(tree);
      expect(source,`${file}: hardcoded Persian`).not.toMatch(/[\u0600-\u06ff]/);
    }
  });
  it('resolves explicit links before saved preferences and ignores invalid values',()=>{
    expect(initialLanguage()).toBe('fa');localStorage.setItem(languageKey,'en');expect(initialLanguage()).toBe('en');
    history.replaceState(null,'','/?lang=fa');expect(initialLanguage()).toBe('fa');
    history.replaceState(null,'','/?lang=invalid');localStorage.setItem(languageKey,'invalid');expect(initialLanguage()).toBe('fa');
    const stub=vi.spyOn(Storage.prototype,'getItem').mockImplementation(()=>{throw Error();});expect(initialLanguage()).toBe('fa');stub.mockRestore();
  });
  it('formats Gregorian months and source-confirmed prices without converting currency',async()=>{
    expect(price(100000000)).toBe('۱۰۰ میلیون تومان');expect(month('2024-12')).toContain('۲۰۲۴');
    await i18n.changeLanguage('en');expect(number(11767)).toBe('11,767');expect(price(100000000)).toBe('100 million toman');expect(month('2024-12')).toBe('December 2024');
    expect(percent(-0.0000467)).toBe('-0.0000467');
  });
  it('switches the whole publication while retaining selections and records',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>payload}));render(<App/>);
    await screen.findByRole('heading',{level:1});fireEvent.change(screen.getByLabelText(fa['neighborhood.select']),{target:{value:payload.neighborhoods[0].neighborhood}});
    fireEvent.click(screen.getByRole('button',{name:'English'}));
    expect(await screen.findByRole('heading',{name:/A home near the metro/})).toBeInTheDocument();
    expect(document.documentElement.dir).toBe('ltr');expect(document.documentElement.lang).toBe('en');expect(document.title).toBe(en['meta.title']);
    expect(localStorage.getItem(languageKey)).toBe('en');expect(location.search).toBe('?lang=en');
    expect(screen.getByLabelText(en['neighborhood.select'])).toHaveValue(payload.neighborhoods[0].neighborhood);
    expect(screen.getByTestId('overall-price')).toHaveTextContent(price(payload.housing_prices.median_per_m2));
    expect(screen.queryByText('mapped.warning')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'فارسی'}));await screen.findByRole('heading',{name:/خانه نزدیک مترو/});expect(document.documentElement.dir).toBe('rtl');
  });
  it('translates a failed-data state without exposing arbitrary network errors',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockRejectedValue(Error('private-url')));render(<App/>);
    expect(await screen.findByRole('alert')).toHaveTextContent(fa['error.fetch']);fireEvent.click(screen.getByRole('button',{name:'English'}));
    expect(await screen.findByRole('alert')).toHaveTextContent(en['error.fetch']);expect(screen.queryByText('private-url')).not.toBeInTheDocument();
  });
});
