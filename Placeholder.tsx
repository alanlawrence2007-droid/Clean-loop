import { useTranslation } from 'react-i18next';

/** Route shell for screens built in later stages. Contains no data. */
export function Placeholder({ titleKey, stage }: { titleKey: string; stage: number }) {
  const { t } = useTranslation();
  return (
    <section className="py-6">
      <h1 className="text-2xl font-extrabold text-forest">{t(titleKey)}</h1>
      <p className="mt-2 text-muted">{t('pages.comingStage', { stage })}</p>
    </section>
  );
}
