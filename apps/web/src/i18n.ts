import i18n from 'i18next';
import {initReactI18next, useTranslation} from 'react-i18next';
import en from './locales/en.json';
import fa from './locales/fa.json';

export const languageKey='metropremium.language';
export function initialLanguage(){
  const requested=new URLSearchParams(window.location.search).get('lang');
  if(requested==='en'||requested==='fa')return requested;
  try {const saved=localStorage.getItem(languageKey);if(saved==='en'||saved==='fa')return saved;} catch { /* Storage can be unavailable. */ }
  return 'fa';
}
function updateDocument(language:string){
  document.documentElement.lang=language;
  document.documentElement.dir=language==='fa'?'rtl':'ltr';
  document.title=i18n.t('meta.title');
  document.querySelector('meta[name="description"]')?.setAttribute('content',i18n.t('meta.description'));
}
void i18n.use(initReactI18next).init({resources:{en:{translation:en},fa:{translation:fa}},lng:initialLanguage(),fallbackLng:'fa',supportedLngs:['en','fa'],keySeparator:false,initAsync:false,interpolation:{escapeValue:false}});
updateDocument(i18n.language);
i18n.on('languageChanged',updateDocument);
export async function changeLanguage(language:'en'|'fa'){
  try {localStorage.setItem(languageKey,language);} catch { /* The switch also works without storage. */ }
  const url=new URL(window.location.href);url.searchParams.set('lang',language);
  window.history.replaceState(null,'',url);
  await i18n.changeLanguage(language);
}
export const number=(n:number,digits=0)=>new Intl.NumberFormat(i18n.language==='fa'?'fa-IR':'en-US',{maximumFractionDigits:digits}).format(n);
export const percent=(n:number)=>new Intl.NumberFormat(i18n.language==='fa'?'fa-IR':'en-US',{maximumSignificantDigits:3}).format(n);
export const price=(n:number)=>i18n.t('common.millionToman',{n:number(n/1e6,1)});
export const priceRange=(low:number,high:number)=>i18n.t('common.priceRange',{low:number(low/1e6,1),high:number(high/1e6,1)});
export const month=(value:string)=>new Intl.DateTimeFormat(i18n.language==='fa'?'fa-IR-u-ca-gregory':'en-US-u-ca-gregory',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(value+'-01T00:00:00Z'));
export function useLocale(){const {t,i18n:instance}=useTranslation();return {t,language:instance.language,number,percent,price,priceRange,month};}
export default i18n;
