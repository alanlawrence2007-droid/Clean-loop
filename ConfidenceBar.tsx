import { useTranslation } from 'react-i18next';

/** Always labelled as an AI estimate, never as fact. `value` is 0–1. */
export function ConfidenceBar({ value }: { value: number }) {
  const { t } = useTranslation();
  const pct = Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm font-semibold text-muted">
        <span>{t('ai.estimate')}</span>
        <span>{t('ai.confidence')}: {pct}%</span>
      </div>
      <div role="meter" aria-label={`${t('ai.estimate')} – ${t('ai.confidence')}`}
        aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct}
        className="h-2.5 overflow-hidden rounded-full bg-line">
        <div className="h-full rounded-full bg-forest-2" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
