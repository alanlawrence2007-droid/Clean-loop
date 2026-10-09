import { useTranslation } from 'react-i18next';

export function DemoBadge() {
  const { t } = useTranslation();
  return <span className="inline-flex min-h-[28px] items-center rounded-full bg-sanitary-tint px-3 text-xs font-bold text-sanitary-ink">{t('demo.badge')}</span>;
}
