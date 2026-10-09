import { useTranslation } from 'react-i18next';
import { LANGUAGES, setLanguage } from '@/i18n';

export function LanguageSwitch({ onDark = false }: { onDark?: boolean }) {
  const { t, i18n } = useTranslation();
  return (
    <div role="group" aria-label={t('lang.label')} className="inline-flex rounded-full border border-current p-0.5">
      {LANGUAGES.map((lng) => {
        const active = i18n.language === lng;
        return (
          <button key={lng} type="button" onClick={() => void setLanguage(lng)} aria-pressed={active}
            className={`min-h-[40px] min-w-touch rounded-full px-3 text-sm font-bold ${
              active ? (onDark ? 'bg-lime text-forest' : 'bg-forest text-white') : ''}`}>
            {t(`lang.${lng}`)}
          </button>
        );
      })}
    </div>
  );
}
