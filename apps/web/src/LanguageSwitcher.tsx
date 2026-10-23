import {changeLanguage,useLocale} from './i18n';
export default function LanguageSwitcher(){
  const {t,language}=useLocale();
  return <div className="language-switch" role="group" aria-label={t('language.label')}>
    <button type="button" lang="fa" dir="rtl" aria-pressed={language==='fa'} onClick={()=>void changeLanguage('fa')}>{t('language.fa')}</button>
    <button type="button" lang="en" dir="ltr" aria-pressed={language==='en'} onClick={()=>void changeLanguage('en')}>{t('language.en')}</button>
  </div>;
}
