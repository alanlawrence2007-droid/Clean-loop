import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import hi from './locales/hi.json';
import mr from './locales/mr.json';

export const LANGUAGES = ['en', 'hi', 'mr'] as const;
export type Language = (typeof LANGUAGES)[number];
const STORAGE_KEY = 'cleanloop.lang';

function initialLanguage(): Language {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && (LANGUAGES as readonly string[]).includes(saved)) return saved as Language;
  } catch { /* storage unavailable */ }
  return 'en';
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi }, mr: { translation: mr } },
  lng: initialLanguage(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

/** Persist locally now; syncing to the user profile is wired when the profile endpoint is confirmed. */
export function setLanguage(lang: Language) {
  try { localStorage.setItem(STORAGE_KEY, lang); } catch { /* ignore */ }
  document.documentElement.lang = lang;
  return i18n.changeLanguage(lang);
}

export default i18n;
